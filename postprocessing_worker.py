import ConfigParser
import shutil
import threading, time, os
from db import DB
from preprocessing import Preprocessor
import cPickle as pickle


class PostprocessingWorker(threading.Thread):
    """ Python script for Postprocessing worker... runs until cancelled or till max waiting time
    """

    pause_time = 2
    max_waiting_time = 60 * 60  # 60seconds * 60min = 1 hour in seconds
    base_path = ""
    saves_path = "mating_progress/"
    pickle_prefix = ""
    get_save = False
    pop_path = "population/"
    traces_path = "traces_afterVox/"
    traces_backup_path = "traces_afterVox_backup/"
    traces_during_pp_path = "traces_duringPP/"
    traces_after_pp_path = "traces_afterPP/"
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
    one_child = False
    infertile_birth = False
    infertile_birth_percent = 0.1
    area_birthcontrol = False
    area_birthcontrol_radius = 0.05
    area_birthcontrol_cutoff = 25
    pp = Preprocessor()
    indiv_max_age = 0
    indiv_infertile_span = 0.25
    queue_length = 1
    timestep = 0.002865

    def readConfig(self, config_path):
        self.config.read(config_path)
        self.exp_name = self.config.get('Experiment', 'name')
        self.path_prefix = self.config.get('Experiment', 'path_prefix')
        self.debug = self.config.get('Experiment', 'debug')
        self.end_time = self.config.getfloat('Experiment', 'end_time')

        self.base_path = os.path.expanduser(self.path_prefix + self.exp_name) + "/"
        self.queue_length = self.config.getint('Postprocessing', 'queue_len')
        self.pop_path = self.config.get('Postprocessing', 'pop_path')
        self.traces_path = self.config.get('Postprocessing', 'traces_path')
        self.traces_backup_path = self.config.get('Postprocessing', 'traces_backup_path')
        self.traces_during_pp_path = self.config.get('Postprocessing', 'traces_during_pp_path')
        self.traces_after_pp_path = self.config.get('Postprocessing', 'traces_after_pp_path')
        self.vox_preamble = self.config.getint('Postprocessing', 'vox_preamble')
        self.timestep = self.config.getfloat('Postprocessing', 'timestep')

        self.pause_time = self.config.getint('Workers', 'pause_time')
        self.max_waiting_time = self.config.getint('Workers', 'max_waiting_time')

        self.timeTolerance = self.config.getfloat('Mating', 'timeTolerance')
        self.spaceTolerance = self.config.getfloat('Mating', 'spaceTolerance')
        self.indiv_infertile_span = self.config.getfloat('Mating', 'indiv_infertile_span')
        self.one_child = self.config.getboolean('Mating', 'onlyOneChildPerParents')
        self.infertile_birth = self.config.getboolean('Mating', 'infertileAfterBirth')
        self.infertile_birth_percent = self.config.getfloat('Mating', 'infertileAfterBirthPercentage')
        self.area_birthcontrol = self.config.getboolean('Mating', 'areaBirthControl')
        self.area_birthcontrol_radius = self.config.getfloat('Mating', 'areaBirthControlRadius')
        self.area_birthcontrol_cutoff = self.config.getfloat('Mating', 'areaBirthControlCutoff')

        self.arena_x = self.config.getfloat('Arena', 'x')
        self.arena_y = self.config.getfloat('Arena', 'y')
        self.arena_type = self.config.get('Arena', 'type')

        self.indiv_max_age = self.config.getfloat('Population', 'indiv_max_age')

    def __init__(self, dbParams, config_path):
        threading.Thread.__init__(self)
        self.db = DB(dbParams[0], dbParams[1], dbParams[2], dbParams[3])
        self.readConfig(config_path)

        self.stopRequest = threading.Event()

    def compareQueue(self, item1, item2):
        id1 = int(self.getIDfromTrace(item1))
        id2 = int(self.getIDfromTrace(item2))
        if (id1 < id2):
            return -1
        elif (id1 > id2):
            return 1
        else:
            return 0

    def gotSave(self):
        self.pickle_prefix = self.base_path + self.saves_path
        self.got_save = self.pickleExists("queue_partition")
        return self.got_save

    def pickleExists(self, name):
        return os.path.isfile(self.pickle_prefix + name + ".pickle")

    def unpickle(self, name):
        return pickle.load(open(self.pickle_prefix + name + ".pickle", "rb"))

    def pickle(self, var, name):
        if (self.pickleExists(name)):
            os.remove(self.pickle_prefix + name + ".pickle")
        pickle.dump(var, open(self.pickle_prefix + name + ".pickle", "wb"))

    def clearPickles(self):
        shutil.rmtree(self.pickle_prefix)
        os.makedirs(self.pickle_prefix)

    def run(self):
        """ main thread function
        :return: None
        """
        waitCounter = 0
        startTime = time.time()

        obs_path = os.path.normpath(self.base_path + self.traces_path)

        while (not self.stopRequest.isSet() and waitCounter < self.max_waiting_time):
            if (self.gotSave()):
                queue_partition = self.unpickle("queue_partition")
                babies = self.calculateOffspring(queue_partition)
                if self.one_child:
                    self.makeBabies(babies)
                self.moveFilesToFinal(queue_partition)
                self.markAsPostprocessed(queue_partition)
                waitCounter = 0
                self.clearPickles()
            else:
                self.dirCheck(obs_path)

                if (len(self.queue) > 0):
                    self.queue = sorted(self.queue, cmp=self.compareQueue)
                    queue_partition = self.queue[:self.queue_length]
                    self.queue = self.queue[self.queue_length:]
                    if (self.debug):
                        print("PP: found " + str(len(queue_partition)) + " todo(s)")
                    self.markAsVoxelyzed(queue_partition)
                    self.moveFilesToTmp(queue_partition)
                    self.adjustTraceFile(queue_partition)
                    self.traceToDatabase(queue_partition)
                    self.pickle(queue_partition, "queue_partition")
                    babies = self.calculateOffspring(queue_partition)
                    if self.one_child:
                        self.makeBabies(babies)
                    self.moveFilesToFinal(queue_partition)
                    self.markAsPostprocessed(queue_partition)
                    waitCounter = 0
                    self.clearPickles()
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
        unprocessed = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
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

    def markAsPostprocessed(self, todos):
        """ mark all the individuals as postprocessed, i.e. all offspring has been calculated, files have been moved and the individuals are basically done
        :param todos: list of strings with trace file paths
        :return: None
        """
        for todo in todos:
            id = self.getIDfromTrace(todo)
            self.db.markAsPostprocessed(id)
            self.db.setFinalTime(id)

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
            self.pp.addStartingPointArenaAndTime(self.getPathDuringPP(id),
                                                 self.vox_preamble,
                                                 self.arena_x,
                                                 self.arena_y,
                                                 self.arena_type,
                                                 first_trace["x"],
                                                 first_trace["y"],
                                                 indiv["born"],
                                                 self.end_time,
                                                 self.timestep)

    def traceToDatabase(self, todos):
        """ put the individuals into the database
        :param todos: list of strings with the individual trace filepaths
        :return: None
        """

        for todo in todos:
            id = self.getIDfromTrace(todo)
            with open(self.getPathDuringPP(id), 'r') as inputFile:
                traces = []

                fileAsList = inputFile.readlines()
                fileLen = len(fileAsList)
                for i in range(0, fileLen):
                    fertile = 1
                    if (self.infertile_birth):
                        if (i <= self.infertile_birth_percent * fileLen):
                            fertile = 0
                    traceLine = fileAsList[i].split()
                    traces.append([id, traceLine[1], traceLine[2], traceLine[3], traceLine[4], fertile])
            if (len(traces) == 0):
                print("PP-WARNING: individual {indiv} has 0 traces, so skipping... please check this though!".format(
                    len=len(traces), indiv=id))
            else:
                if (self.debug):
                    print("PP: adding {len} traces for individual {indiv} to DB".format(len=len(traces), indiv=id))
                self.db.addTraces(id, traces)

    def getPotentialBirthplace(self, parent1, parent2):
        x = (parent1["x"] + parent2["x"]) / 2
        y = (parent1["y"] + parent2["y"]) / 2
        return [x, y]

    def calculateOffspring(self, todos):
        """ yeah, well... generate offspring, calculate where the new individuals met friends on the way
        :param todos: list of strings with the individual IDs
        :return: None
        """
        babies = []
        if (self.got_save):
            babies = self.unpickle("babies")
        else:
            self.pickle(babies,"babies")

        for todo in todos:
            if (os.path.getsize(todo) == 0):
                continue
            id = self.getIDfromTrace(todo)
            if (self.debug):
                print("PP: looking for mates for individual {indiv}...".format(indiv=id))

            if (self.got_save):
                mates = self.unpickle("mates")
                i = self.unpickle("i")
                positive_mates = self.unpickle("positive_mates")
            else:
                mates = self.db.findMate(id, self.timeTolerance, self.spaceTolerance, 0, self.one_child)
                i = 0
                positive_mates = []
                self.pickle(mates, "mates")
                self.pickle(i, "i")
                self.pickle(positive_mates, "positive_mates")

            while (len(mates) != 0):
                mate = mates[0]
                parent2 = {}
                parent2["id"] = mate["mate_id"]
                parent2["indiv_id"] = mate["mate_indiv_id"]
                parent2["ltime"] = mate["mate_ltime"]
                parent2["x"] = mate["mate_x"]
                parent2["y"] = mate["mate_y"]
                parent2["z"] = mate["mate_z"]

                abcOkay = True  # if the area birth control is okay with the mating
                if (self.area_birthcontrol):
                    if (self.debug):
                        print("PP: birth control is activated, checking vicinity for other bots")
                    birthCoords = self.getPotentialBirthplace(mate, parent2)
                    otherBotsInArea = self.db.getOtherBotsInArea(mate["ltime"], birthCoords[0], birthCoords[1],
                                                                 self.area_birthcontrol_radius)
                    if (self.debug):
                        print("PP: found {bots} other bots at the potential birth place".format(bots=otherBotsInArea))
                    if (otherBotsInArea > self.area_birthcontrol_cutoff):
                        abcOkay = False
                        if (self.debug):
                            print("PP: CANNOT ALLOW MATING IN THIS AREA. Too many other bots.")

                if not abcOkay or (self.one_child and (mate["mate_indiv_id"] in positive_mates or
                                           self.db.haveMatedBefore(mate, parent2) or
                                           self.db.isParentOf(id, parent2["indiv_id"])) ):
                    pass # don't create a mate with this partner.
                else:
                    i += 1
                    self.pickle(i, "i")
                    if (self.debug):
                        print("PP: found mate ({mate}) for individual {indiv} at {time}s".format(
                            len=i, indiv=id, mate=mate["mate_indiv_id"], time=mate["mate_ltime"]))
                    if not self.one_child:
                        self.db.makeBaby(mate, parent2, mate["ltime"], self.one_child,
                                         self.indiv_max_age * self.indiv_infertile_span)
                    else:
                        positive_mates.append(mate["mate_indiv_id"])
                        self.pickle(positive_mates, "positive_mates")
                        babies.append([mate, parent2, mate["ltime"]])
                        self.pickle(babies, "babies")

                newStart = mate["id"]
                if self.one_child and self.debug:
                    print("PP: looking for more mates for individual {indiv}...".format(indiv=id))

                if self.one_child:
                    mates.pop(0)
                else:
                    mates = self.db.findMate(id, self.timeTolerance, self.spaceTolerance, newStart, self.one_child)
                self.pickle(mates, "mates")

            if (self.debug):
                print("PP: found {len} mating occurances for individual {indiv}".format(len=i, indiv=id))
        self.db.flush()
        return babies

    def makeBabies(self, babies):
        for baby in babies:
            self.db.makeBaby(baby[0], baby[1], baby[2], self.one_child, self.indiv_max_age * self.indiv_infertile_span)

    def getPathDuringPP(self, id):
        return self.base_path + self.traces_during_pp_path + str(id) + ".trace"

    def moveFilesToTmp(self, todos):
        """ once all preprocessing is done, move the files to their target destination
        :param todos: list of strings with the individual IDs
        :return: None
        """
        for indiv in todos:
            id = self.getIDfromTrace(indiv)
            shutil.copy2(indiv, self.base_path + self.traces_backup_path + str(id) + ".trace")
            shutil.copy2(indiv, self.getPathDuringPP(id))

    def moveFilesToFinal(self, todos):
        """ once all preprocessing is done, move the files to their target destination
        :param todos: list of strings with the individual IDs
        :return: None
        """
        for indiv in todos:
            id = self.getIDfromTrace(indiv)
            shutil.move(self.getPathDuringPP(id),
                        self.base_path + self.traces_after_pp_path + str(id) + ".trace")
            os.remove(indiv)

    def addFile(self, path):
        self.queue.append(path)
