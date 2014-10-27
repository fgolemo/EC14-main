import os
import subprocess
import threading, time
from db import DB


class VoxWorker(threading.Thread):
    """ Python script for Voxelize worker... runs until cancelled or till max waiting time
    """

    pause_time = 2
    queue_length = 12
    queue = []
    queue_sent = []
    max_waiting_time = 60 * 60  # 60seconds * 60min = 1 hour in seconds
    queue_force_submit_time = 60 * 10  # after 10 minutes just submit the queue as it is
    base_path = ""
    pool_path = "pool/"
    pool_filename = 'vox.{0}.pool'
    pop_path = "population/"
    submit_script = "scripts/submit.sh"
    voxelyze_path = "~/EC14-voxelyze/voxelyzeMain"
    voxelyze_stepping = 100
    voxelyze_cmd = "{id}"
    debug = False
    db = None
    lastPoolFile = 0

    def __init__(self, dbParams, base_path, debug=False):
        threading.Thread.__init__(self)
        self.db = DB(dbParams[0], dbParams[1], dbParams[2])
        self.base_path = base_path
        self.debug = debug
        self.poolFilePath = self.base_path + self.pool_path + self.pool_filename
        self.stopRequest = threading.Event()
        self.submit_script = os.path.dirname(os.path.realpath(__file__)) + "/" + self.submit_script

    def run(self):
        """ main thread function
        :return: None
        """
        waitCounter = 0
        startTime = time.time()
        while not self.stopRequest.isSet() and waitCounter < self.max_waiting_time:
            todos = self.checkForTodos()

            if len(todos) > 0:
                if self.debug:
                    print("VOX: found " + str(len(todos)) + " todos")
                self.addToQueue(todos)
                waitCounter = 0
            else:
                if self.debug:
                    print("VOX: found nothing")
                waitCounter += time.time() - startTime
                startTime = time.time()
                if waitCounter > self.queue_force_submit_time:
                    self.addToQueue([], True)
                    waitCounter = 0

            if self.debug:
                print("VOX: sleeping now for " + str(self.pause_time) + "s")
            self.stopRequest.wait(self.pause_time)

        # TODO: final steps after kill signal
        print ("Thread: got exist signal... here I can do some last cleanup stuff before quitting")

    def join(self, timeout=None):
        """ function to terminate the thread (softly)
        :param timeout: not implemented yet
        :return: None
        """
        if self.debug:
            print("VOX: got kill request for thread")
        self.stopRequest.set()
        super(VoxWorker, self).join(timeout)

    def addToQueue(self, todos, forced=False):
        """ adds elements to the to-be-voxelyzed queue
        :param todos: simple python list with the names of the individuals to be voxelyzed
        :param forced: boolean true in case the queue has to be flushed (queued items waiting for too long)
        :return: None
        """
        if self.debug:
            print ("VOX: found " + str(len(todos)) + " new individuals.")

        for todo in todos:
            if not todo in self.queue and not todo in self.queue_sent:
                self.queue.append(todo)

        if len(self.queue) > self.queue_length or forced:
            if self.debug:
                print ("vox: got " + str(
                    self.queue_length) + " individuals in queue. Sending them to the Lisa queue to be voxelyzed")
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

    def getExperimentName(self):
        return os.path.basename(self.base_path[:-1])

    def runQsub(self):
        vox_string = self.getExperimentName() + " " + str(self.lastPoolFile)
        if self.debug:
            print("VOX: calling submit script like this: " + self.submit_script + " " + vox_string)
        try:
            subprocess.check_call(self.submit_script + " " + vox_string,
                                  stdout=open(self.base_path + "logs/" + "submit."+str(self.lastPoolFile)+".stdout.log", "w"),
                                  stderr=open(self.base_path + "logs/" + "submit."+str(self.lastPoolFile)+".stderr.log", "w"),
                                  stdin=open(os.devnull),
                                  shell=True)
        except subprocess.CalledProcessError as e:
            print ("Vox: during submit.sh execution there was an error:")
            print (str(e.returncode))
            quit()
            # TODO: better error handling, but so far, we dont allow submit.sh to fail -
            # TODO: and if it fails, we can check the logs immediately

    def sendQueue(self, sendList):
        """ submits the queue (or part of it) to the Lisa job queue
        :param sendList: simple python list with the names of the individuals to be voxelyzed right now
        :return: None
        """
        if self.debug:
            print("VOX: sending queue to the job system")

        # write pool file (12 lines, each line is a call to voxelyze) - correction, each line is an indiv ID
        self.createPoolFile(sendList)

        # run submit.sh that qsubs the stuff in the recent pool
        self.runQsub()

        # TODO: mark all those individuals in the DB as submitted - do we still need this?

        pass
