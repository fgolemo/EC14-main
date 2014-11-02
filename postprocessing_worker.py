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
    queue = []

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

        self.observer.schedule(ChangeHandler(self), path=os.path.normpath(self.base_path + self.pop_path))
        print("PP: starting file observer on path:\n" + self.base_path + self.pop_path)
        self.observer.start()

        while (not self.stopRequest.isSet() and waitCounter < self.max_waiting_time):
            if (len(self.queue) > 0):
                queue_partition = self.queue
                self.queue = self.queue[len(queue_partition):] # to make sure that in the short fraction of time no new file was added
                if (self.debug):
                    print("PP: found " + str(len(queue_partition)) + " todos")
                self.adjustTraceFile(queue_partition)
                self.calculateOffspring(queue_partition)
                self.moveFiles(queue_partition)
                waitCounter = 0
            else:
                if (self.debug):
                    print("PP: found nothing")
                waitCounter += time.time() - startTime
                startTime = time.time()

            if (self.debug):
                print("PP: sleeping now for " + str(self.pause_time) + "s")
            self.stopRequest.wait(self.pause_time)

        print ("PP: got exit signal... cleaning up")
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

    def addFile(self, path):
        self.queue.append(path)


class ChangeHandler(PatternMatchingEventHandler):
    patterns = ["*.trace"]
    pp_worker = None

    def __init__(self, pp_worker, patterns=None, ignore_patterns=None, ignore_directories=False, case_sensitive=False):
        self.pp_worker = pp_worker
        super(ChangeHandler, self).__init__(patterns, ignore_patterns, ignore_directories, case_sensitive)

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        print ("PP: found new trace file:" + event.src_path)
        self.pp_worker.addFile(event.src_path)

    def on_created(self, event):
        self.process(event)
