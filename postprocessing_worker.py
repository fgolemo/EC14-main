import threading, time, os
from db import DB
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class PostprocessingWorker(threading.Thread):
    """ Python script for Postprocessing worker... runs until cancelled or till max waiting time
    """

    pause_time = 2
    max_waiting_time = 60 * 60  # 60seconds * 60min = 1 hour in seconds
    base_path = ""
    pop_path = "population/"
    debug = False
    db = None

    def __init__(self, dbParams, base_path, debug=False):
        threading.Thread.__init__(self)
        self.db = DB(dbParams[0], dbParams[1], dbParams[2])
        self.base_path = base_path
        self.debug = debug
        self.stopRequest = threading.Event()
        self.observer = Observer()

    def run(self):
        """ main thread function
        :return: None
        """
        waitCounter = 0
        startTime = time.time()

        self.observer.schedule(ChangeHandler(), path=os.path.normpath(self.base_path+self.pop_path) )
        print("PP: startin file observer on path:\n" + self.base_path+self.pop_path)
        self.observer.start()
        while (not self.stopRequest.isSet() and waitCounter < self.max_waiting_time):
            # todos = self.checkForTodos()
            #
            # if (len(todos) > 0):
            #     if (self.debug):
            #         print("PP: found " + str(len(todos)) + " todos")
            #     self.adjustTraceFile(todos)
            #     self.calculateOffspring(todos)
            #     self.moveFiles(todos)
            #     waitCounter = 0
            # else:
            #     if (self.debug):
            #         print("PP: found nothing")

            waitCounter += time.time() - startTime
            startTime = time.time()

            #
            if (self.debug):
                print("PP: sleeping now for " + str(self.pause_time) + "s")
            self.stopRequest.wait(self.pause_time)

        # TODO: final steps after kill signal
        print ("Thread: got exist signal... here I can do some last cleanup stuff before quitting")
        self.observer.join()

    def join(self, timeout=None):
        """ function to terminate the thread (softly)
        :param timeout: not implemented yet
        :return: None
        """
        if (self.debug):
            print("PP: got kill request for thread")
        self.stopRequest.set()
        self.observer.stop()
        super(PostprocessingWorker, self).join(timeout)

    def checkForTodos(self):
        """ checks the filesystem if there are any new files created after a job batch has finished on Lisa
        :return: simple python list with the names of the individuals that finished voxelyzation
        """
        if (self.debug):
            print("PP: checking for todos")

        todos = []


        # TODO: implement

        return todos

    def adjustTraceFile(self, todos):
        """ put the individuals into an arena, correct their coordinates, etc.
        :param todos: list of strings with the individual IDs
        :return: None
        """
        # TODO: implement (Tom's code)

        pass

    def calculateOffspring(self, todos):
        """ yeah, well... generate offspring, calculate where the new individuals met friends on the way
        :param todos: list of strings with the individual IDs
        :return: None
        """
        # TODO: implement

        pass

    def moveFiles(self, todos):
        """ once all preprocessing is done, move the files to their target destination
        :param todos: list of strings with the individual IDs
        :return: None
        """
        # TODO: implement

        pass


class ChangeHandler(PatternMatchingEventHandler):
    patterns=["*.trace","*.txt"]

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        print ("PP: found new file:"+event.src_path)

    def on_created(self, event):
        self.process(event)
