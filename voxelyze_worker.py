import os
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
    base_path = ""
    pool_path = "pool/"
    pool_filename = 'vox.{0}.pool'
    pop_path = "population/"
    voxelyze_path = "~/EC14-voxelyze/voxelyzeMain"
    voxelyze_stepping = 100
    #voxelyze_cmd = "./voxelyze -f {path}{id}_vox.vxa -p {stepping} > {id}.trace"
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

    def run(self):
        """ main thread function
        :return: None
        """
        waitCounter = 0
        startTime = time.time()
        while (not self.stopRequest.isSet() and waitCounter < self.max_waiting_time):
            todos = self.checkForTodos()

            if (len(todos) > 0):
                if (self.debug):
                    print("VOX: found " + str(len(todos)) + " todos")
                self.addToQueue(todos)
                waitCounter = 0
            else:
                if (self.debug):
                    print("VOX: found nothing")
                waitCounter += time.time() - startTime
                startTime = time.time()

            if (self.debug):
                print("VOX: sleeping now for " + str(self.pause_time) + "s")
            self.stopRequest.wait(self.pause_time)

        # TODO: final steps after kill signal
        print ("Thread: got exist signal... here I can do some last cleanup stuff before quitting")

    def join(self, timeout=None):
        """ function to terminate the thread (softly)
        :param timeout: not implemented yet
        :return: None
        """
        if (self.debug):
            print("VOX: got kill request for thread")
        self.stopRequest.set()
        super(VoxWorker, self).join(timeout)

    def addToQueue(self, todos):
        """ adds elements to the to-be-voxelyzed queue
        :param todos: simple python list with the names of the individuals to be voxelyzed
        :return: None
        """
        if (self.debug):
            print ("VOX: found " + str(len(todos)) + " new individuals.")

        for todo in todos:
            if (not todo in self.queue and not todo in self.queue_sent):
                self.queue.append(todo)

        if (len(self.queue) > self.queue_length):
            if (self.debug):
                print ("vox: got " + str(
                    self.queue_length) + " individuals in queue. Sending them to the Lisa queue to be voxelyzed")
            self.sendQueue(self.queue[:self.queue_length])

            # now splice them apart, move the sent id into a separate list
            self.queue_sent += self.queue[:self.queue_length]
            self.queue = self.queue[self.queue_length:]  # keep only the first N elements in list
        else:
            if (self.debug):
                print("VOX: queue not full yet, waiting for more before submitting")
            pass
        if (self.debug):
            print("VOX: current queue:")
            print(self.queue)

    def checkForTodos(self):
        """ check the DB or the filesystem and look if there are any new individuals that need to be voxelyzed
        :return: simple python list with the names of the individuals that are new and need to be voxelyzed
        """
        todos = self.db.getVoxTodos()

        if (self.debug):
            print("VOX: checking for TODOs")

        return todos

    def getLastPoolFile(self):
        if (self.lastPoolFile == 0):  # this means is hasn't been set
            self.lastPoolFile = 1  # try 1 first, then incr
            print("looking at pool file:"+ (self.poolFilePath.format(self.lastPoolFile)) )
            while (os.path.isfile(self.poolFilePath.format(self.lastPoolFile))):
                self.lastPoolFile += 1
            if (self.debug):
                print("VOX: found last pool file number:" + str(self.lastPoolFile))
        else:
            self.lastPoolFile += 1

    def createPoolFile(self, sendList):
        self.getLastPoolFile()
        f = open(self.poolFilePath.format(self.lastPoolFile), 'w+')
        path = (self.base_path + self.pop_path)
        if (os.name == "nt"):  # then we are on windows
            path = path.replace("/", "\\")
        else:
            path = path.replace("\\", "/")  # IDK if we ever need this...
        for indiv in sendList:
            # f.write(self.voxelyze_cmd.format(path=path, id=indiv, stepping=self.voxelyze_stepping) + "\n")
            f.write(self.voxelyze_cmd.format(id=indiv) + "\n")
        f.close()

    def sendQueue(self, sendList):
        """ submits the queue (or part of it) to the Lisa job queue
        :param sendList: simple python list with the names of the individuals to be voxelyzed right now
        :return: None
        """
        if (self.debug):
            print("VOX: sending queue to the job system")

        # write pool file (12 lines, each line is a call to voxelyze)
        self.createPoolFile(sendList)

        # TODO: run stopos/ submit.sh / everts script that qsubs the stuff in the pool

        #TODO: mark all those individuals in the DB as submitted - do we still need this?

        pass


# while True:
#
# GetNextChildren(endtime) #gives back array/tuple with
# #ID, birthTime, hasBeenSimulated = 0, hasBeenProcessed = 0, hasBeenHNed = 0
#
# 	if GetNextChildren(endtime) == NULL:
# 		continue
#
# 	else:
# 	    for ind in children:
#             voxelize_queue.append("./"+str(exp_name)+"/"+str(ChildID))
#
#  	if (voxelize_queue.length == queue_length or waiting_time > max_waiting_time):
# 		waiting_time = 0
#
# 		# TODO Spawn parallel processes instead of for loop
# 		### TRY IN LISA ###
# #        proc_per_node = "#PBS -lnodes=1:ppn=12"
# #    	subprocess.Popen(proc_per_node.split(),stdout=STDOUT,shell=True)
#     	###################
#     	# Note: Not using scratch space because operations are not I/O intensive.
#
# 		for x in voxelize_queue:
# 		    subprocess.Popen(["gsub","voxelize","./VoxCad/"+voxelize_queue(x),"-lnodes=1:ppn=12"],cwd="./VoxCad",shell=True) #TODO Need to test, string input may be an issue since it isnt in STDIN
#
#     	voxelize_queue = []
#
#     time.sleep(1)
# 	waiting_time += 1 #add 1 sec waiting time

	

