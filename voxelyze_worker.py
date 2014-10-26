import threading, time
from db import DB

class VoxWorker(threading.Thread):
    """ Python script for Voxelize worker... runs until cancelled or till max waiting time
    """

    voxelize_queue = []
    pause_time = 2
    queue_length = 12
    queue = []
    max_waiting_time = 60 * 60  # 60seconds * 60min = 1 hour in seconds
    base_path = ""
    debug = False
    db = None

    def __init__(self, dbParams, base_path, debug=False):
        threading.Thread.__init__(self)
        self.db = DB(dbParams[0], dbParams[1], dbParams[2])
        self.base_path = base_path
        self.debug = debug
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
        self.queue += todos

        if (len(self.queue) > self.queue_length):
            if (self.debug):
                print ("vox: got " + str(
                    self.queue_length) + " individuals in queue. Sending them to the Lisa queue to be voxelyzed")
            self.sendQueue(self.queue[:self.queue_length])
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

    def sendQueue(self, sendList):
        """ submits the queue (or part of it) to the Lisa job queue
        :param sendList: simple python list with the names of the individuals to be voxelyzed right now
        :return: None
        """
        # TODO: write pool file (12 lines, each line is a call to voxelyze)
        #TODO: run stopos/ submit.sh / everts script that qsubs the stuff in the pool
        #TODO: mark all those individuals in the DB as submitted

        if (self.debug):
            print("VOX: sending queue to the job system")
        pass


# while True:
#
# GetNextChildren(endtime) #gives back array/tuple with
#     #ID, birthTime, hasBeenSimulated = 0, hasBeenProcessed = 0, hasBeenHNed = 0
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

	

