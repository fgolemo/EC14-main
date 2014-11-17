import ConfigParser
import shutil
import threading, time, os
from db import DB
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
    indiv_max_age = 0
    indiv_infertile_span = 0.25

    def readConfig(self, config_path):
        self.config.read(config_path)
        self.exp_name = self.config.get('Experiment', 'name')
        self.path_prefix = self.config.get('Experiment', 'path_prefix')
        self.debug = self.config.get('Experiment', 'debug')
        self.base_path = os.path.expanduser(self.path_prefix + self.exp_name) + "/"
        self.pop_path = self.config.get('Postprocessing', 'pop_path')
        self.traces_path = self.config.get('Postprocessing', 'traces_path')
        self.vox_preamble = self.config.getint('Postprocessing', 'vox_preamble')
        self.pause_time = self.config.getint('Workers', 'pause_time')
        self.queue_length = self.config.getint('Workers', 'queue_len')
        self.max_waiting_time = self.config.getint('Workers', 'max_waiting_time')
        self.arena_x = self.config.getfloat('Arena', 'x')
        self.arena_y = self.config.getfloat('Arena', 'y')
        self.arena_type = self.config.get('Arena', 'type')
        self.end_time = self.config.getfloat('Experiment', 'end_time')
        self.indiv_max_age = self.config.getfloat('Population', 'indiv_max_age')

    def __init__(self, dbParams, config_path):
        threading.Thread.__init__(self)
        self.db = DB(dbParams[0], dbParams[1], dbParams[2], dbParams[3])
        self.readConfig(config_path)

        self.stopRequest = threading.Event()

    def run(self):
        """ main thread function
        :return: None
        """
        waitCounter = 0
        startTime = time.time()

        obs_path = os.path.normpath(self.base_path + self.traces_path)

        while (not self.stopRequest.isSet() and waitCounter < self.max_waiting_time):
            self.dirCheck(obs_path)

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

            jobsRunning = self.db.getJobsWaitingCount()

            if (self.debug):
                print("PP: {n} jobs currently waiting in LISA queue...".format(n=jobsRunning))
                print("PP: sleeping now for " + str(self.pause_time) + "s")

            self.stopRequest.wait(self.pause_time)

        print ("PP: got exit signal... cleaning up")

    def join(self, timeout=None):
        """ function to terminate the thread (softly)
        :param timeout: not implemented yet
        :return: None
        """
        if (self.debug):
            print("PP: got kill request for thread")
        self.stopRequest.set()
        super(PostprocessingWorker, self).join(timeout)

    def getIDfromTrace(self, file_path):
        path, filename = os.path.split(file_path)
        name_parts = filename.split(".")
        return name_parts[0]

    def dirCheck(self, path):
        """ upon start check if there are files in the target diretory, because the watcher only notices files being moved there while running
        :return: None
        """
        unprocessed = [ os.path.join(path,f) for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) ]
        for todo in unprocessed:
            if todo not in self.queue:
                self.addFile(todo)

    def markAsVoxelyzed(self, todos):
        """ mark all the individuals as voxelyzed, i.e. as successfully processed by Voxelyze
        :param todos: list of strings with trace file paths
        :return: None
        """
        for todo in todos:
            id = self.getIDfromTrace(todo)
            self.db.markAsVoxelyzed(id)
            self.db.setJobDone(id)

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
            mates = self.db.findMate(id, self.timeTolerance, self.spaceTolerance)
            i = 0
            while (len(mates) != 0):
                i+=1
                mate = mates[0]
                parent2 = {}
                parent2["id"] = mate["mate_id"]
                parent2["indiv_id"] = mate["mate_indiv_id"]
                parent2["ltime"] = mate["mate_ltime"]
                parent2["x"] = mate["mate_x"]
                parent2["y"] = mate["mate_y"]
                parent2["z"] = mate["mate_z"]
                self.db.makeBaby(mate, parent2, mate["ltime"], self.indiv_max_age*self.indiv_infertile_span)

                newStart = mate["id"]
                mates = self.db.findMate(id, self.timeTolerance, self.spaceTolerance, newStart)

            if (self.debug):
                print("PP: found {len} mating occurances for individual {indiv}".format(len=i, indiv=id))

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
