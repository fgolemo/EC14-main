from __future__ import division
import ConfigParser
import shutil
from subprocess import CalledProcessError
import threading, time, subprocess, os
from db import DB
import random
import xml.etree.cElementTree as ET
# except ImportError:
#     import xml.etree.ElementTree as ET


class HNWorker(threading.Thread):
    """ Thread for HyperNEAT worker... runs until cancelled or till max waiting time
    """

    config = ConfigParser.RawConfigParser()
    pause_time = 2
    queue_len = 12
    max_waiting_time = 60 * 60  # 60seconds * 60min = 1 hour in seconds
    base_path = ""
    pop_path = "population/"
    hn_path = "~/EC14-HyperNEAT/out/"
    hn_binary = "./Hypercube_NEAT"
    hn_params_file = "softbotTest.dat"
    suffix_genome = "_genome.xml"
    suffix_vox = "_vox.vxa"
    hn_trash_file = "Softbots--{0}---gen-Genchamp-AvgFit.txt"
    hn_stray_files =["md5sumTMP.txt"]
    # hn_binary = "python HyperNEATdummy.py"
    debug = False
    db = None
    mutate = False

    def readConfig(self, config_path):

        self.config.read(config_path)

        self.exp_name = self.config.get('Experiment', 'name')
        self.path_prefix = self.config.get('Experiment', 'path_prefix')
        self.debug = self.config.get('Experiment', 'debug')

        self.base_path = os.path.expanduser(self.path_prefix + self.exp_name) + "/"

        self.hn_path = self.config.get('Hyperneat', 'hn_path')
        self.hn_binary = self.config.get('Hyperneat', 'hn_binary')
        self.hn_params_file = self.config.get('Hyperneat', 'hn_params_file')
        self.suffix_genome = self.config.get('Hyperneat', 'suffix_genome')
        self.suffix_vox = self.config.get('Hyperneat', 'suffix_vox')

        self.pause_time = self.config.getint('Workers', 'pause_time')
        self.queue_length = self.config.getint('Workers', 'queue_len')
        self.max_waiting_time = self.config.getint('Workers', 'max_waiting_time')

        self.pl_path = self.config.get('Lifetimes', 'pl_path')
        self.cost_muscle = self.config.getfloat('Lifetimes', 'cost_muscle')
        self.cost_soft = self.config.getfloat('Lifetimes', 'cost_soft')
        self.energy_unit = self.config.getfloat('Lifetimes', 'energy_unit')
        self.starting_energy = self.config.getfloat('Lifetimes', 'starting_energy')

        self.mutate = self.config.getboolean('Mutation', 'mutate')


    def __init__(self, dbParams, config_path):
        threading.Thread.__init__(self)
        self.db = DB(dbParams[0], dbParams[1], dbParams[2], dbParams[3])
        self.readConfig(config_path)

        # individuals will be found here: self.base_path + self.pop_path + str(indiv)
        self.hn_path = os.path.expanduser(self.hn_path)
        self.pop_path = os.path.expanduser(self.base_path + self.pop_path)
        self.pl_path = os.path.expanduser(self.base_path + self.pl_path)

        self.stopRequest = threading.Event()

    def run(self):
        """ main thread function
        :return: None
        """
        waitCounter = 0
        startTime = time.time()
        todos = []
        while not self.stopRequest.isSet() and waitCounter < self.max_waiting_time:
            newTodos = self.checkForTodos()
            for newTodo in newTodos:
                if newTodo not in todos:
                    todos.append(newTodo)

            if len(todos) > 0:
                todoTmp = todos[:self.queue_len]
                if self.debug:
                    print("HN: found " + str(len(todoTmp)) + " todos")
                self.execHN(todoTmp)
                self.preprocessBeforeVox(todoTmp)
                waitCounter = 0
                todos = todos[self.queue_len:]
            else:
                if self.debug:
                    print("HN: found no todos")
                waitCounter += time.time() - startTime
                startTime = time.time()

                if self.debug:
                    print("HN: sleeping now for " + str(self.pause_time) + "s")
                self.stopRequest.wait(self.pause_time)

        print ("Thread: got exit signal... here I can do some last cleanup stuff before quitting")

    def join(self, timeout=None):
        """ function to terminate the thread (softly)
        :param timeout: not implemented yet
        :return: None
        """
        if self.debug:
            print("HN: got kill request for thread")
        self.stopRequest.set()
        super(HNWorker, self).join(timeout)

    def checkForTodos(self):
        """ check the DB or the filesystem and look if there are any new individuals that need to be hyperneated
        :return: simple python list with the names of the individuals that are new and need to be hyperneated
        """
        if self.debug:
            print("HN: checking for todos")

        todos = self.db.getHNtodos()
        print "HN: Found", len(todos), "todo(s)"
        return todos

    def execHN(self, todos):
        """ execute HyperNEAT for all the individuals in the input list
        :param todos: list with strings containing the names of the individuals to be hyperneated
        :return: None
        """
        if self.debug:
            print("HN: executing hyperneat for the following individuals:")
            print(todos)

        for indiv in todos:
            parents = self.db.getParents(indiv)
            hn_params = " ".join(parents)  # parent will be a list of size 0|1|2
            print("HN: creating individual (calling HN binary): " + str(indiv) )
            self.runHN(indiv, hn_params)
            print("HN: finished creating individual: " + str(indiv))

            if (len(parents) == 2): # mutate if the indiv has 2 parents
                print("HN: mutating individual: " + str(indiv) )
                self.runHN(indiv, str(indiv))
                print("HN: finished mutating individual: " + str(indiv))

            # TODO (later): error check the hyperneat output

        pass

    def preprocessBeforeVox(self, todos):
        """ run all the freshly-generated individuals through preprocessing to place them in an arena etc.
        :param todos: list with strings containing the names of the individuals from the last HN run
        :return: None
        """
        if self.debug:
            print("HN: preprocessing")
        for indiv in todos:
            if (not os.path.isfile(self.hn_path + str(indiv) + self.suffix_vox)):
                print ("HH: individual " + str(indiv) + " born dead")
                self.db.markAsDead(indiv)
                continue
            if self.debug:
                print("HN: preprocessing individual " + str(indiv))
            if (os.path.isfile(self.hn_path + str(indiv) + self.suffix_vox)):
                shutil.copy2(self.hn_path + str(indiv) + self.suffix_vox, self.pl_path + str(indiv) + self.suffix_vox)
                shutil.move(self.hn_path + str(indiv) + self.suffix_vox, self.pop_path + str(indiv) + self.suffix_vox)
                self.calculateLifetime(indiv)
                if self.mutate:
                    self.atrophyMuscles(indiv)
                #TODO self.db.calculatedLifetime(indiv)
            if (os.path.isfile(self.hn_path + str(indiv) + self.suffix_genome)):
                shutil.copy2(self.hn_path + str(indiv) + self.suffix_genome, self.pop_path + str(indiv) + self.suffix_genome)
            if (os.path.isfile(self.hn_path + self.hn_trash_file.format(indiv))):
                os.remove(self.hn_path + self.hn_trash_file.format(indiv))

            self.db.markAsHyperneated(indiv)

        for f in self.hn_stray_files:
            if (os.path.isfile(self.hn_path + f)):
                os.remove(self.hn_path + f)

        self.db.flush()
        pass

    def calculateLifetime(self,indiv):
        """Calculates and edits an individual's lifetime based on its genome
        """
        tree = ET.ElementTree(file=self.pop_path + str(indiv) + self.suffix_vox)
        root = tree.getroot()
        layers = root.find('VXC').find('Structure').find('Data').findall('Layer')

        dna = ""
        for layer in layers:
            dna += str(layer.text).strip()

        dna_length = len(dna)

        count_empty = dna.count('0')
        count_soft = dna.count('1')
        count_hard = dna.count('2')
        count_active = dna.count('3') + dna.count('4')
        count_length = count_empty + count_soft + count_hard + count_active

        if dna_length != count_length:
            print "DNA length count error!"

        lifetime = self.energy_unit * (self.starting_energy - ((count_soft * self.cost_soft) + (count_active * self.cost_muscle)))

        root.find('Simulator').find('StopCondition').find('StopConditionValue').text = str(lifetime)
        try:
            tree.write(self.pop_path + str(indiv) + self.suffix_vox)
        except:
            print 'HN (ERROR): Could not write to', self.pop_path + str(indiv) + self.suffix_vox
        
    def atrophyMuscles(self,indiv):
        """Mutates muscle tissue voxels according to some probability in each layer
        """
        tree = ET.ElementTree(file=self.pop_path + str(indiv) + self.suffix_vox) #file="./population/" + dna_file
        root = tree.getroot()
        layers = root.find('VXC').find('Structure').find('Data').findall('Layer')

        """Calculates probability based on amount of fat tissue
        """
        dna = ""
        for layer in layers:
            dna += str(layer.text).strip()
        count_soft = dna.count('1')
        probability = (count_soft / 1000) * 0.5 # or 0.0005 * count_soft


        dna_list = ""
        for layer in layers:
            dna_list = list(layer.text.strip())
            position_to_check = 0
            for index in range(len(dna_list)):
                tissue = dna_list[index]
                if tissue == '3' or tissue == '4':
                    if random.random() <= probability:
                        dna_list[index] = '2'
                        #print "Atrophied a muscle at index " + str(index) + " to " + str(dna_list[index]) + "."
                    else:
                        #print "Muscle at index " + str(index) + " unchanged."
                        pass

                else:
                    continue

            layer.text = "".join(dna_list)
        try:
            tree.write(self.pop_path + str(indiv) + self.suffix_vox)
        except:
            print 'HN (ERROR): Could not write to', self.pop_path + str(indiv) + self.suffix_vox

    def runHN(self, indiv, hn_params):
        """ run hyperneat with its parameters
        :param hn_params: string with either 0, 1 or 2 parents, just the IDs (no file suffix), separated by a space
        :return: None
        """
        hn_string = "-I " + self.hn_params_file + " -R $RANDOM -O " + str(indiv) + " -ORG " + hn_params
        try:
            subprocess.check_call(self.hn_binary + " " + hn_string,
                                  cwd=self.hn_path,
                                  stdout=open(self.base_path + "logs/" + "hn.stdout.log", "w"),
                                  stderr=open(self.base_path + "logs/" + "hn.stderr.log", "w"),
                                  stdin=open(os.devnull),
                                  shell=True)
        except CalledProcessError as e:
            print ("HN: during HN execution there was an error:")
            print (str(e.returncode))
            quit()
            # TODO: better error handling, but so far, we dont allow HN to fail -
            # TODO: and if it fails, we can check the logs immediately
