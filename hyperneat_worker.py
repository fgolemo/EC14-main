from subprocess import CalledProcessError
import threading, time, subprocess, os
from db import DB


class HNWorker(threading.Thread):
    """ Thread for HyperNEAT worker... runs until cancelled or till max waiting time
    """

    pause_time = 2
    max_waiting_time = 60 * 60  # 60seconds * 60min = 1 hour in seconds
    base_path = ""
    pop_path = "population/"
    hn_path = "~/EC14-HyperNEAT/out/"
    # hn_binary = "./HyperNEAT"
    hn_binary = "python HyperNEATdummy.py"
    debug = False
    db = None

    def __init__(self, dbParams, base_path, debug=False):
        threading.Thread.__init__(self)
        self.db = DB(dbParams[0], dbParams[1], dbParams[2])
        self.base_path = base_path
        # individuals will be found here: self.base_path + self.pop_path + str(indiv)

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
                    print("HN: found " + str(len(todos)) + " todos")
                self.execHN(todos)
                self.cleanupAfterHN(todos)
                self.preprocessBeforeVox(todos)
                waitCounter = 0
            else:
                if (self.debug):
                    print("HN: found no todos")
                waitCounter += time.time() - startTime
                startTime = time.time()

            if (self.debug):
                print("HN: sleeping now for " + str(self.pause_time) + "s")
            self.stopRequest.wait(self.pause_time)

        # TODO: final steps after kill signal
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
        if (self.debug):
            print("HN: checking for todos")


        todos = self.db.getHNtodos()
        print (todos)
        return todos

    def execHN(self, todos):
        """ execute HyperNEAT for all the individuals in the input list
        :param todos: list with strings containing the names of the individuals to be hyperneated
        :return: None
        """
        if (self.debug):
            print("HN: executing hyperneat for the following individuals:")
            print(todos)

        for indiv in todos:
            hn_params = " ".join(self.db.getParents(indiv))  # parent will be a list of size 0|1|2
            self.runHN(indiv, hn_params)
            # TODO (later): error check the hyperneat output

        pass

    def cleanupAfterHN(self, todos):
        """ clean HyperNEAT leftover files and move individuals
        :param todos: list with strings containing the names of the individuals from the last HN run
        :return: None
        """
        if (self.debug):
            print("HN: cleaning up")

        # TODO: run the real hyperneat on lisa, list all the stray files that HN generates
        # TODO: and here write a few lines to clean them up (i.e. just delete unused HN-generated files)
        # probably the todos parameter is not necessary, but keep it for now
        pass


    def preprocessBeforeVox(self, todos):
        """ run all the freshly-generated individuals through preprocessing to place them in an arena etc.
        :param todos: list with strings containing the names of the individuals from the last HN run
        :return: None
        """
        if (self.debug):
            print("HN: preprocessing")

        for indiv in todos:
            # TODO: move the final files somewhere else
            self.db.markAsHyperneated(indiv)
        self.db.flush()
        pass


    def runHN(self, indiv, hn_params):
        """ run hyperneat with its parameters
        :param hn_params:
        :return: error code
        """
        hn_string = "-I params.dat -R $RANDOM -O "+str(indiv)+" -ORG "+hn_params
        try:
            subprocess.check_call(self.hn_binary + " " + hn_string, cwd=os.path.expanduser(self.hn_path),
                                  shell=True)  # Double check this, may brick the whole thing
        except CalledProcessError as e:
            print ("HN: during HN execution there was an error:")
            print (str(e.returncode))
            quit()  # TODO: better error handling, but so far, we dont allow HN to fail

# Function keeps checking database for new encounters:

# PY#
# while True:
#
# CloseRobots(distance, waittime, childtime)
#
#     GetParents(endtime) #TODO Change for new code
#
# 	if parents == NULL:
# 		continue
#     else:
#         spawn_child()
	


	
    



