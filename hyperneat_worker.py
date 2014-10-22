import threading, time

class HNWorker(threading.Thread):
    """ Thread for HyperNEAT worker... runs until cancelled or till max waiting time
    """

    pause_time = 2
    max_waiting_time = 60 * 60 # 60seconds * 60min = 1 hour in seconds
    base_path = ""
    debug = False

    def __init__(self, base_path, debug = False):
        threading.Thread.__init__(self)
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
                    print("HN: found "+str(len(todos))+" todos")
                self.execHN(todos)
                self.cleanupAfterHN(todos)
                self.preprocessBeforeVox(todos)
                self.saveToDB(todos)
                waitCounter = 0
            else:
                if (self.debug):
                    print("HN: found no todos")
                waitCounter += time.time() - startTime
                startTime = time.time()

            if (self.debug):
                print("HN: sleeping now for "+str(self.pause_time)+"s")
            self.stopRequest.wait(self.pause_time)

        #TODO: final steps after kill signal
        print ("Thread: got exist signal... here I can do some last cleanup stuff before quitting")

    def join(self, timeout=None):
        """ function to terminate the thread (softly)
        :param timeout: not implemented yet
        :return: None
        """
        if (self.debug):
            print("HN: got kill request for thread")
        self.stopRequest.set()
        super(HNWorker, self).join(timeout)


    def checkForTodos(self):
        """ check the DB or the filesystem and look if there are any new individuals that need to be hyperneated
        :return: simple python list with the names of the individuals that are new and need to be hyperneated
        """
        todos = []
        
        #TODO: implement, first pseudo - to be testable on any machine
        if (self.debug):
            print("HN: checking for todos")

        return todos

    def execHN(self, todos):
        """ execute HyperNEAT for all the individuals in the input list
        :param todos: list with strings containing the names of the individuals to be hyperneated
        :return: None
        """
        #TODO: implement, first pseudo - to be testable on any machine
        if (self.debug):
            print("HN: executing hyperneat for the following individuals:")
            print(todos)
        pass

    def cleanupAfterHN(self, todos):
        """ clean HyperNEAT leftover files and move individuals
        :param todos: list with strings containing the names of the individuals from the last HN run
        :return: None
        """
        #TODO: implement
        if (self.debug):
            print("HN: cleaning up")
        pass


    def preprocessBeforeVox(self, todos):
        """ run all the freshly-generated individuals through preprocessing to place them in an arena etc.
        :param todos: list with strings containing the names of the individuals from the last HN run
        :return: None
        """
        #TODO: implement
        if (self.debug):
            print("HN: preprocessing")
        pass

    def saveToDB(self, todos):
        '''
         write all the freshly-generated individuals'names to DB for further procesing
        :param todos: list with strings containing the names of the individuals from the last HN run
        :return: None
        '''
        #TODO: implement
        if (self.debug):
            print("HN: saving to DB")
        pass

# Function keeps checking database for new encounters:

#PY#
# while True:
#
#     CloseRobots(distance, waittime, childtime)
#
#     GetParents(endtime) #TODO Change for new code
#
# 	if parents == NULL:
# 		continue
#     else:
#         spawn_child()
	

################# FUNCTIONS ####################
	
    
# def spawn_child()
# #SH#
# for ind in parents:
#
#     run_hyperneat = Popen("gsub hn",cwd="./HyperNeat",stdin=subprocess.PIPE,stdout=subprocess.PIPE,shell=True)  # Double check this, may brick the whole thing
#         run_hyperneat.STDIN("./"+str(exp_name)+"/"+str(firstID)+" ./"+str(exp_name)+"/"+str(secondID))
#
#         if (run_hyperneat.returncode != 0):
# 		    print run_hyperneat.returncode
# 			    run_hyperneat.kill()
#         else:
#             with io.open(pop_path, str(ChildID) + ".xml", 'w', encoding='utf-8') as f:
#                 f.write(str(run_hyperneat.STDOUT()))
#                 io.close()


