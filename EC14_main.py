# Python main script
import random
from subprocess import Popen
import os.path, time, glob, shutil, mysql.connector, ConfigParser

# import workers
from db import DB
import hyperneat_worker as hn
import voxelyze_worker as vox
import postprocessing_worker as pp


class EC14controller():
    base_path = ""
    db = None
    dbString = ""
    dbParams = ""
    hnWorker = None
    voxWorker = None
    ppWorker = None
    newExperiment = False
    end_time = 0
    pop_size = 0
    pop_random = 0
    pop_random_start_end = (0, 0)
    indiv_max_age = 0
    arena_x = 0
    arena_y = 0
    arena_type = ""
    config = None
    path_prefix = "~/EC14-Exp-"

    random_granularity = 10.0

    yes = {'yes', 'y', 'ye'}
    no = {'no', 'n', ''}

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()

    def get_int(self, msg, default):
        while True:
            line = raw_input(msg) or default
            try:
                return int(line)
            except ValueError:
                print line, "is not a valid number"

    def askExperimentName(self):
        """ asks the user for the experiment name/location
        :return: string Path to the project
        """

        exp_name = raw_input(
            "Please name your experiment: ")  # TODO Make sure no special characters are used (except for - and _)

        # Check if file name is taken:
        while exp_name == '' and os.path.isdir(exp_name) == True:
            exp_name = raw_input("That name is taken or empty, please try again: ")

        exp_path = exp_name

        return exp_path

    def askDatabaseString(self):
        """ asks the user for the database parameters
        :return: string A JDBC-formatted string like username:password@host/databasename
        """

        db_string = raw_input(
            "Please give me your database connection string in JDBC format (i.e. username:password@host/database): ")
        working = False
        while (not working):
            try:
                dbo = DB(db_string)  # ec141:ec141@192.168.0.44/ec141
                dbo.close()
                working = True
            except mysql.connector.Error as err:
                print (err)
                db_string = raw_input("That didn't work, please try again (i.e. username:password@host/database): ")

        return db_string

    def askNumber(self, question, defaultVal):
        """ ask for input (expects an integer number)
        :return: an integer number
        """
        input = self.get_int(question + " [" + str(defaultVal) + "]: ", defaultVal)
        print "okay, I got: " + str(input)
        return input

    def askPopulationSize(self):
        """ ask for population size
        :return: integer Population size
        """

        init_pop_size = self.get_int("Initial population size [100]: ", 100)
        print "Population size set at " + str(init_pop_size)
        return init_pop_size

    def askWorkingDir(self):
        """ aks the user if there are existing files for this experiment
        :return: None
        """

        # Ask user if they are continuing a previous experiment
        db_given = raw_input("Are you continuing with an existing Experiment? [y/N]: ").lower()
        while db_given not in self.yes and db_given not in self.no:
            print "That is not a valid answer.",
            db_given = raw_input("type Y for yes and N for no: ").lower()

        if db_given in self.yes:
            # base_path = raw_input("Path to experiment folder (e.g. ~/EC14-Exp-1):")
            base_path = raw_input("Name of the experiment (will look for " + self.path_prefix + "[name] ):")
            while not os.path.exists(os.path.expanduser(self.path_prefix + base_path)):
                base_path = raw_input("I can't find that folder, please try again:")
        else:
            self.newExperiment = True
            base_path = self.askExperimentName()

        self.base_path = os.path.expanduser(self.path_prefix + base_path + "/")
        print "Working directory: " + self.base_path

    def installFiles(self):
        """ Copy script files into experiment directory and saves config
        :return: None
        """

        os.makedirs(self.base_path + "scripts/")
        os.makedirs(self.base_path + "config/")
        os.makedirs(self.base_path + "population/")
        os.makedirs(self.base_path + "traces_tmp/")
        os.makedirs(self.base_path + "pool/")
        os.makedirs(self.base_path + "logs/")

        files = glob.iglob("./*.py")
        for f in files:
            if os.path.isfile(f):
                shutil.copy(f, self.base_path + "scripts/")

    def installConfig(self):
        """ Copy script files into experiment directory and saves config
        :return: None
        """

        db_string = self.askDatabaseString()
        self.dbString = db_string
        self.end_time = self.askNumber("Experiment time limit (in seconds)", 120)
        self.indiv_max_age = self.askNumber("Lifetime of an individual (in seconds, current max: 25s)", 5)
        self.pop_size = self.askNumber("Initial population size", 100)
        self.pop_random = self.askPopulationRandom()
        self.pop_random_start_end = (0, 0)
        if self.pop_random:
            self.pop_random_start_end = self.askPopulationRandomStartEnd()
        self.arena_x = self.askNumber("Arena size (x)", 1)
        self.arena_y = self.askNumber("Arena size (y)", 1)
        self.arena_type = self.askArenaType()

        self.config.add_section('DB')
        self.config.set('DB', 'db_string', db_string)
        self.config.add_section('Experiment')
        self.config.set('Experiment', 'end_time', str(self.end_time))
        self.config.set('Experiment', 'indiv_max_age', str(self.indiv_max_age))
        self.config.set('Experiment', 'pop_size', str(self.pop_size))
        self.config.set('Experiment', 'pop_random', str(self.pop_random))
        self.config.set('Experiment', 'pop_random_start', str(self.pop_random_start_end[0]))
        self.config.set('Experiment', 'pop_random_end', str(self.pop_random_start_end[1]))
        self.config.add_section('Arena')
        self.config.set('Arena', 'arena_x', str(self.arena_x))
        self.config.set('Arena', 'arena_y', str(self.arena_y))
        self.config.set('Arena', 'arena_type', str(self.arena_type))
        with open(self.base_path + 'config/config.ini', 'wb') as configfile:
            self.config.write(configfile)

    def askPopulationRandom(self):
        """ ask if the initial population should have randomized birth time
        :return: boolean True for random, False for all will be born at time 0.000s
        """

        question = "Do you want the individuals to have random birth time within a time window? [y/N]: "

        birth_random = raw_input(question).lower()
        while birth_random not in self.yes and birth_random not in self.no:
            print "That is not a valid answer. Please give it another shot...",
            birth_random = raw_input(question).lower()

        if birth_random in self.yes:
            return True
        else:
            return False

    def askArenaType(self):
        """ ask if arena edges should be bouncy (reflecting) or infinite (when leaving the edge on one end, appear on the other end)
        :return: string (character), either b - for bouncy, or i - for infinite
        """

        question = "Do you want the arena to be bouncy or infinite? [b/I]: "

        ans = raw_input(question).lower()
        while ans not in ["b", "i", ""]:
            print "That is not a valid answer. Please respond with either the letter 'b' or 'i'",
            ans = raw_input(question).lower()
        if ans == '':
            ans = 'i'
        return ans

    def askPopulationRandomStartEnd(self):
        """ ask for start and end of the random population birth time
        :return: tuple, first val is start, second is end in integer seconds
        """

        starttime = self.get_int("Earliest possible birth time (in seconds) [0]: ", 0)
        endtime = self.get_int("Latest possible birth time (in seconds) [3]: ", 3)

        print "Birth time random window set to " + str(starttime) + " - " + str(endtime) + "s"

        return starttime, endtime

    def getDB(self):
        """ retrieve database string from config or cache
        :return: None
        """

        self.db = DB(self.dbString, self.end_time, self.indiv_max_age)
        self.dbParams = (self.dbString, self.end_time, self.indiv_max_age)

        if self.newExperiment:
            self.db.createTables()

    def createPopulaton(self):
        """ creates the initial population in the database
        :return: None
        """

        for i in range(self.pop_size):
            birth = 0
            if (self.pop_random):
                birth = (random.randrange(self.pop_random_start_end[0] * self.random_granularity,
                                          self.pop_random_start_end[1] * self.random_granularity)
                         / self.random_granularity)
            x = random.randrange(0, self.arena_x * self.random_granularity) / self.random_granularity
            y = random.randrange(0, self.arena_y * self.random_granularity) / self.random_granularity
            self.db.createIndividual(birth, x, y)

    def readConfig(self):
        print("config path: " + self.base_path + 'config/config.ini')
        self.config.read(self.base_path + 'config/config.ini')

        if (self.pop_size == 0):  # this is the case, when the experiment exists
            self.arena_x = self.config.getfloat('Arena', 'arena_x')
            self.arena_y = self.config.getfloat('Arena', 'arena_y')
            self.arena_type = self.config.get('Arena', 'arena_type')
            self.end_time = self.config.getfloat('Experiment', 'end_time')
            self.indiv_max_age = self.config.getfloat('Experiment', 'indiv_max_age')
            self.pop_size = self.config.getint('Experiment', 'pop_size')
            self.pop_random = self.config.get('Experiment', 'pop_random')
            self.pop_random_start_end = (
                self.config.getfloat('Experiment', 'pop_random_start'),
                self.config.getfloat('Experiment', 'pop_random_end')
            )

        if (self.dbString == ""):  # this is the case, when the experiment exists
            self.dbString = self.config.get('DB', 'db_string')

    def start(self):
        self.askWorkingDir()

        if (self.newExperiment):
            self.installFiles()
            self.installConfig()

        self.readConfig()
        self.getDB()

        if (self.newExperiment):
            self.createPopulaton()


        # launch workers
        self.hnWorker = hn.HNWorker(self.dbParams, self.base_path, True)
        self.hnWorker.start()
        self.voxWorker = vox.VoxWorker(self.dbParams, self.base_path, True)
        self.voxWorker.start()
        self.ppWorker = pp.PostprocessingWorker(self.dbParams, self.base_path, True)
        self.ppWorker.start()


ctrl = EC14controller()
ctrl.start()

time.sleep(2)
print ("main script doing something in the background")
stop = raw_input("want to stop? just press enter: ")
print("user stopped")
ctrl.hnWorker.join()
ctrl.voxWorker.join()
ctrl.ppWorker.join()
print("end of script")

