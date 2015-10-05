import ConfigParser
import os
import re
import subprocess
import threading, time
from db import DB


class VoxWorker(threading.Thread):
    """ Python script for Voxelize worker... runs until cancelled or till max waiting time
    """

    config = ConfigParser.RawConfigParser()
    pause_time = 2
    queue_length = 12
    queue = []
    queue_sent = []
    max_waiting_time = 60 * 60  # 60seconds * 60min = 1 hour in seconds
    queue_force_submit_time = 20  # after 10 minutes just submit the queue as it is
    base_path = ""
    pool_path = "pool/"
    pool_filename = 'vox.{0}.pool'
    pop_path = "population/"
    submit_script = "scripts/submit.sh"
    voxelyze_path = "~/EC14-voxelyze/voxelyzeMain"
    voxelyze_stepping = 100
    voxelyze_cmd = "{id}"
    voxelyze_walltime = 299
    debug = False
    db = None
    lastPoolFile = 0
    qreturn_pattern = None

    def readConfig(self, config_path):
        self.config.read(config_path)
        self.exp_name = self.config.get('Experiment', 'name')
        self.path_prefix = self.config.get('Experiment', 'path_prefix')
        self.debug = self.config.get('Experiment', 'debug')
        self.base_path = os.path.expanduser(self.path_prefix + self.exp_name) + "/"
        self.queue_force_submit_time = self.config.getint('Voxelyze', 'queue_force_submit_time')
        self.voxelyze_cmd = self.config.get('Voxelyze', 'voxelyze_cmd')
        self.voxelyze_stepping = self.config.getint('Voxelyze', 'voxelyze_stepping')
        self.voxelyze_path = self.config.get('Voxelyze', 'voxelyze_path')
        self.voxelyze_walltime = self.config.getint('Voxelyze', 'voxelyze_walltime')
        self.submit_script = self.config.get('Voxelyze', 'submit_script')
        self.pop_path = self.config.get('Voxelyze', 'pop_path')
        self.pool_filename = self.config.get('Voxelyze', 'pool_filename')
        self.pool_path = self.config.get('Voxelyze', 'pool_path')
        self.pause_time = self.config.getint('Workers', 'pause_time')
        self.queue_length = self.config.getint('Workers', 'queue_len')
        self.max_waiting_time = self.config.getint('Workers', 'max_waiting_time')

    def __init__(self, dbParams, config_path):
        threading.Thread.__init__(self)
        self.db = DB(dbParams[0], dbParams[1], dbParams[2], dbParams[3])
        self.readConfig(config_path)

        self.poolFilePath = self.base_path + self.pool_path + self.pool_filename
        self.stopRequest = threading.Event()
        self.submit_script = os.path.dirname(os.path.realpath(__file__)) + "/" + self.submit_script
        self.qreturn_pattern =  re.compile('\D*([0-9]{6,})\D*')

    def run(self):
        """ main thread function
        :return: None
        """
        waitCounter = 0
        startTime = time.time()
        while not self.stopRequest.isSet() and waitCounter < self.max_waiting_time:
            todos = self.checkForTodos()
            addedSomethingNew = self.addToQueue(todos)
            forced = False
            if addedSomethingNew:
                waitCounter = 0
            else:
                waitCounter += time.time() - startTime
                startTime = time.time()
                if len(self.queue) > 0 and waitCounter > self.queue_force_submit_time:
                    if self.debug:
                        print("VOX: slept long enough... now FLUSHING THE QUEUE")
                    forced = True
                    waitCounter = 0
            self.processQueue(forced)
            if not addedSomethingNew:
                if self.debug:
                    print("VOX: sleeping now for " + str(self.pause_time) + "s")
                self.stopRequest.wait(self.pause_time)

        # TODO: final steps after kill signal
        print ("Thread: got exit signal")

    def join(self, timeout=None):
        """ function to terminate the thread (softly)
        :param timeout: not implemented yet
        :return: None
        """
        if self.debug:
            print("VOX: got kill request for thread")
        self.stopRequest.set()
        super(VoxWorker, self).join(timeout)

    def addToQueue(self, todos):
        new = 0
        for todo in todos:
            if not todo in self.queue and not todo in self.queue_sent:
                self.queue.append(todo)
                new += 1
        if (new > 0):
            if self.debug:
                print("VOX: found " + str(new) + " new individuals.")
            return True
        else:
            if self.debug:
                print("VOX: found nothing new")
            return False

    def processQueue(self, forced=False):
        """ adds elements to the to-be-voxelyzed queue
        :param todos: simple python list with the names of the individuals to be voxelyzed
        :param forced: boolean true in case the queue has to be flushed (queued items waiting for too long)
        :return: None
        """
        if len(self.queue) >= self.queue_length or forced:
            if self.debug:
                print ("vox: got " + str(
                    len(self.queue)) + " individuals in queue. Sending them to the Lisa queue to be voxelyzed")
            self.sendQueue(self.queue[:self.queue_length])

            if not forced:
                # now splice them apart, move the sent id into a separate list
                self.queue_sent += self.queue[:self.queue_length]
                self.queue = self.queue[self.queue_length:]  # keep only the first N elements in list
            else:
                # just purge everything
                self.queue_sent += self.queue
                self.queue = []
        else:
            if self.debug:
                print("VOX: queue not full yet, waiting for more before submitting")
            pass
        if self.debug:
            print("VOX: current queue:")
            print(self.queue)

    def checkForTodos(self):
        """ check the DB or the filesystem and look if there are any new individuals that need to be voxelyzed
        :return: simple python list with the names of the individuals that are new and need to be voxelyzed
        """
        todos = self.db.getVoxTodos()

        if self.debug:
            print("VOX: checking for TODOs")

        return todos

    def getLastPoolFile(self):
        if self.lastPoolFile == 0:  # this means is hasn't been set
            self.lastPoolFile = 1  # try 1 first, then incr
            print("looking at pool file:" + (self.poolFilePath.format(self.lastPoolFile)) )
            while (os.path.isfile(self.poolFilePath.format(self.lastPoolFile))):
                self.lastPoolFile += 1
            if self.debug:
                print("VOX: found last pool file number:" + str(self.lastPoolFile))
        else:
            self.lastPoolFile += 1

    def createPoolFile(self, sendList):
        self.getLastPoolFile()
        f = open(self.poolFilePath.format(self.lastPoolFile), 'w+')

        for indiv in sendList:
            f.write(self.voxelyze_cmd.format(id=indiv) + "\n")
        f.close()

    def runQsub(self, sendList):
        vox_string = "{base_path} {pool_file} {walltime}"
        vox_string = vox_string.format(base_path=self.base_path, exp_name=self.exp_name,
                                       pool_file=str(self.lastPoolFile), walltime=self.voxelyze_walltime)
        if self.debug:
            print("VOX: calling submit script like this:\n" + self.submit_script + " " + vox_string)
        try:
            cmd = self.submit_script + " " + vox_string
            output = subprocess.Popen(cmd,
                                      stderr=open(
                                          self.base_path + "logs/" + "submit." + str(self.lastPoolFile) + ".stderr.log",
                                          "w"),
                                      stdin=open(os.devnull),
                                      shell=True,
                                      stdout=subprocess.PIPE).communicate()[0]

            jobname = self.splitOutputIntoJobname(output)
            self.db.addJob(jobname, cmd, sendList)
        except subprocess.CalledProcessError as e:
            print ("Vox: during submit.sh execution there was an error:")
            print (str(e.returncode))
            quit()
            # TODO: better error handling, but so far, we dont allow submit.sh to fail -
            # TODO: and if it fails, we can check the logs immediately

    def splitOutputIntoJobname(self, output):
        match = self.qreturn_pattern.match(output)

        if not match:
            print("VOX: probably serious error... submitting the job" + \
                  " to the lisa queue didn't return an expected format: ")
            print(output)
            print("...while we expected something like 1234.batch1.lisa.surfsara.nl")
            return "0"
        else:
            return match.group(1)

    def sendQueue(self, sendList):
        """ submits the queue (or part of it) to the Lisa job queue
        :param sendList: simple python list with the names of the individuals to be voxelyzed right now
        :return: None
        """
        if self.debug:
            print("VOX: sending queue to the job system")

        self.createPoolFile(sendList)
        self.runQsub(sendList)
        
        for indiv in sendList:
            self.db.markAsVoxSubmitted(indiv)

