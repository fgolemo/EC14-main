import ConfigParser
import shutil
import threading, time, os
from db import DB
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from preprocessing import Preprocessor


class PostprocessingWorker(threading.Thread):
    """ Python script for Postprocessing worker... runs until cancelled or till max waiting time
    """

    pause_time = 2
    max_waiting_time = 60 * 60  # 60seconds * 60min = 1 hour in seconds
    base_path = ""
    pop_path = "population/"
    traces_path = "traces_afterVox/"
    debug = False
    db = None
    queue = []
    vox_preamble = 8  # number of lines that voxelyze adds before the actual output in a trace file
    config = ConfigParser.RawConfigParser()
    arena_x = 0
    arena_y = 0
    arena_type = ""
    end_time = 0
    timeTolerance = 0.0  # maximum mating time distance
    spaceTolerance = 0.01  # maximum mating distance radius
    pp = Preprocessor()

    def __init__(self, dbParams, base_path, debug=False):
        threading.Thread.__init__(self)
        self.db = DB(dbParams[0], dbParams[1], dbParams[2])
        self.base_path = base_path
        self.debug = debug
        self.stopRequest = threading.Event()
        self.observer = Observer()
        self.config.read(self.base_path + 'config/config.ini')
        self.arena_x = self.config.getfloat('Arena', 'arena_x')
        self.arena_y = self.config.getfloat('Arena', 'arena_y')
        self.arena_type = self.config.get('Arena', 'arena_type')
        self.end_time = self.config.getfloat('Experiment', 'end_time')

    def run(self):
        """ main thread function
        :return: None
        """
        waitCounter = 0
        startTime = time.time()

        obs_path = os.path.normpath(self.base_path + self.traces_path)
        self.observer.schedule(ChangeHandler(self), path=obs_path)
        print("PP: starting file observer on path:\n" + obs_path)
        self.observer.start()

        self.initialDirCheck(obs_path)

        while (not self.stopRequest.isSet() and waitCounter < self.max_waiting_time):
            if (len(self.queue) > 0):
                queue_partition = self.queue
                self.queue = self.queue[len(
                    queue_partition):]  # to make sure that in the short fraction of time no new file was added
                if (self.debug):
                    print("PP: found " + str(len(queue_partition)) + " todos")
                self.markAsVoxelyzed(queue_partition)
                self.adjustTraceFile(queue_partition)
                self.traceToDatabase(queue_partition)
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

    def getIDfromTrace(self, file_path):
        path, filename = os.path.split(file_path)
        name_parts = filename.split(".")
        return name_parts[0]

    def initialDirCheck(self, path):
        """ upon start check if there are files in the target diretory, because the watcher only notices files being moved there while running
        :return: None
        """
        unprocessed = [ os.path.join(path,f) for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) ]
        for todo in unprocessed:
            self.addFile(todo)

    def markAsVoxelyzed(self, todos):
        """ mark all the individuals as voxelyzed, i.e. as successfully processed by Voxelyze
        :param todos: list of strings with trace file paths
        :return: None
        """
        for todo in todos:
            id = self.getIDfromTrace(todo)
            self.db.markAsVoxelyzed(id)

    def adjustTraceFile(self, todos):
        """ put the individuals into an arena, correct their coordinates, etc.
        :param todos: list of strings with the individual trace filepaths
        :return: None
        """

        for todo in todos:
            id = self.getIDfromTrace(todo)
            # get initial coordinates from DB
            indiv = self.db.getIndividual(id)
            first_trace = self.db.getFirstTrace(id)
            self.pp.addStartingPointArenaAndTime(todo, self.vox_preamble, self.arena_x, self.arena_y, self.arena_type,
                                                 first_trace["x"], first_trace["y"], indiv["born"], self.end_time)

    def traceToDatabase(self, todos):
        """ put the individuals into the database
        :param todos: list of strings with the individual trace filepaths
        :return: None
        """

        for todo in todos:
            id = self.getIDfromTrace(todo)
            with open(todo, 'r') as inputFile:
                traces = []

                fileAsList = inputFile.readlines()
                for i in range(0, len(fileAsList)):
                    traceLine = fileAsList[i].split()
                    traces.append([id, traceLine[1], traceLine[2], traceLine[3], traceLine[4]])
            if (self.debug):
                print("PP: adding {len} traces for individual {indiv} to DB".format(len=len(traces), indiv=id))
            self.db.addTraces(id, traces)

    def calculateOffspring(self, todos):
        """ yeah, well... generate offspring, calculate where the new individuals met friends on the way
        :param todos: list of strings with the individual IDs
        :return: None
        """
        for todo in todos:
            id = self.getIDfromTrace(todo)
            if (self.debug):
                print("PP: looking for mates for individual {indiv}...".format(indiv=id))
            mates = self.db.findMates(id, self.timeTolerance, self.spaceTolerance)
            if (self.debug):
                print("PP: found {len} mating occurances for individual {indiv}".format(len=len(mates), indiv=id))
            for mate in mates:
                parent2 = {}
                parent2["id"] = mate["mate_id"]
                parent2["ltime"] = mate["mate_ltime"]
                parent2["x"] = mate["mate_x"]
                parent2["y"] = mate["mate_y"]
                parent2["z"] = mate["mate_z"]
                # if (self.debug): #this can get too much
                #     print("PP: adding mate:")
                #     print(parent2)
                self.db.makeBaby(mate, parent2, mate["ltime"])
        self.db.flush()

    def moveFiles(self, todos):
        """ once all preprocessing is done, move the files to their target destination
        :param todos: list of strings with the individual IDs
        :return: None
        """
        for indiv in todos:
            id = self.getIDfromTrace(indiv)
            shutil.move(indiv, self.base_path + self.pop_path + str(id) + ".trace")

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
