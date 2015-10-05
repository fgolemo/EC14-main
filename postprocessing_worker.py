import ConfigParser
import random
import shutil
import threading, time, os
from db import DB
from preprocessing import Preprocessor
import cPickle as pickle
import math


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
    population_cap = False
    pp = Preprocessor()
    indiv_max_age = 0
    indiv_infertile = False
    indiv_infertile_span = 0.25
    random_birth_place = False
    queue_length = 1
    timestep = 0.002865
    pick_from_pool = False

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
        self.indiv_infertile = self.config.getboolean('Mating', 'indiv_infertile')
        self.indiv_infertile_span = self.config.getfloat('Mating', 'indiv_infertile_span')
        self.one_child = self.config.getboolean('Mating', 'onlyOneChildPerParents')
        self.infertile_birth = self.config.getboolean('Mating', 'infertileAfterBirth')
        self.infertile_birth_percent = self.config.getfloat('Mating', 'infertileAfterBirthPercentage')
        self.area_birthcontrol = self.config.getboolean('Mating', 'areaBirthControl')
        self.area_birthcontrol_radius = self.config.getfloat('Mating', 'areaBirthControlRadius')
        self.area_birthcontrol_cutoff = self.config.getfloat('Mating', 'areaBirthControlCutoff')
        self.population_cap = self.config.getboolean('Mating', 'populationCap')
        self.random_birth_place = self.config.getboolean('Mating', 'randomBirthPlace')
        self.pick_from_pool = self.config.getboolean('Mating', 'pickFromPool')

        self.arena_x = self.config.getfloat('Arena', 'x')
        self.arena_y = self.config.getfloat('Arena', 'y')
        self.arena_type = self.config.get('Arena', 'type')

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

        while not self.stopRequest.isSet(): # and waitCounter < self.max_waiting_time):
            self.dirCheck(obs_path)

            if (len(self.queue) > 0):
                print 'PP:',map(self.getIDfromTrace,self.queue)
                self.queue = sorted(self.queue, key=lambda id : int(self.getIDfromTrace(id)))
                item = self.queue[0]
                self.queue = self.queue[1:]
                if self.debug:
                    print "PP: working on id", item
                self.markAsVoxelyzed(item)
                self.moveFilesToTmp(item)
                self.adjustTraceFile(item)
                self.traceToDatabase(item)
                self.findMates(item)
                babies = self.calculateOffspring(item)
                self.makeBabies(babies)
                self.moveFilesToFinal(item)
                self.markAsPostprocessed(item)
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
        unprocessed = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith('.trace')]
        for todo in unprocessed:
            if todo not in self.queue:
                self.addFile(todo)

    def markAsVoxelyzed(self, todo):
        """ mark all the individuals as voxelyzed, i.e. as successfully processed by Voxelyze
        :param todos: list of strings with trace file paths
        :return: None
        """
        id = self.getIDfromTrace(todo)
        self.db.markAsVoxelyzed(id)
        self.db.setJobDone(id)

    def markAsPostprocessed(self, todo):
        """ mark all the individuals as postprocessed, i.e. all offspring has been calculated, files have been moved and the individuals are basically done
        :param todos: list of strings with trace file paths
        :return: None
        """
        id = self.getIDfromTrace(todo)
        self.db.markAsPostprocessed(id)
        self.db.setFinalTime(id)

    def adjustTraceFile(self, todo):
        """ put the individuals into an arena, correct their coordinates, etc.
        :param todos: list of strings with the individual trace filepaths
        :return: None
        """

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

    def traceToDatabase(self, todo):
        """ put the individuals into the database
        :param todos: list of strings with the individual trace filepaths
        :return: None
        """

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

    def filterGlobalInfertility(self, id, mates):
        pass

    def filterIncestControl(self, id, mates):
        pass

    def filterAreaBirthControl(self, id, mates):
        pass

    def filterPopulationCap(self, id, mates):
        if len(mates) > 0:
            mate = random.choice(mates)
        else:
            if not self.pick_from_pool: # then we mate the individual with itself
                lastTrace = self.db.getLastTrace(id)
                mate = {}
                mate["id"] = 0
                mate["indiv_id"] = id
                mate["ltime"] = lastTrace["ltime"]
                mate["x"] = lastTrace["x"]
                mate["y"] = lastTrace["y"]
                mate["z"] = lastTrace["z"]
                mate["mate_id"] = 0
                mate["mate_indiv_id"] = id
                mate["mate_ltime"] = lastTrace["ltime"]
                mate["mate_x"] = lastTrace["x"]
                mate["mate_y"] = lastTrace["y"]
                mate["mate_z"] = lastTrace["z"]
            else:
                return [None]
        return [mate]

    def calculateOffspring(self, todo):
        """ yeah, well... generate offspring, calculate where the new individuals met friends on the way
        :param todos: list of strings with the individual IDs
        :return: list of babies to make
        """

        babies = []

        if (not os.path.exists(todo)) or os.path.getsize(todo) == 0:
            return babies 
        id = self.getIDfromTrace(todo)
        if self.debug:
            print("PP: looking for mates for individual {indiv}...".format(indiv=id))
        mates = self.db.getMates(id)

        # population cap is exclusive - if it is on, no other control works
        if self.population_cap:
            mates = self.filterPopulationCap(id, mates)
        else:
            if self.indiv_infertile:
                mates = self.filterGlobalInfertility(id, mates)
            if self.one_child:
                mates = self.filterIncestControl(id, mates)
            if self.area_birthcontrol:
                mates = self.filterAreaBirthControl(id, mates)
        if mates != [None]: # this happens only if self.pick_from_pool is True and if no mate was found
            babies += self.matesToBabies(id, mates)
        else:
            randomMate = self.db.getRandomMate(id)
            babies += self.matesToBabies(randomMate["id"], [randomMate])
        return babies

    def close_in_time(self, t1, t2):
        return abs(t1['ltime']-t2['ltime']) <= self.timeTolerance

    def close_in_space(self, t1, t2):
        return math.sqrt((t1['x'] - t2['x'])**2 + (t1['y'] - t2['y'])**2) <= self.spaceTolerance

    def findMates(self, indiv_path):
        id = self.getIDfromTrace(indiv_path)
        traces = self.db.getTraces(id)
        territory = self.db.getTerritory(id)
        lifetime = self.db.getLifetime(id)
        if not all(territory.values()) or not all(lifetime.values()):
            return
        possibleMates = self.db.getPossibleMates(id, territory, lifetime)
        mates = []
        for t in traces:
            for p in possibleMates:
                if self.close_in_time(t, p) and self.close_in_space(t, p):
                    mates.append((t,p))
        print 'PP: found', len(mates), 'possible mates for individual', id
        self.db.insertMates(mates)

    def matesToBabies(self, id, mates):
        babies = []
        for mate in mates:
            parent2 = {}
            parent2["id"] = mate["mate_id"]
            parent2["indiv_id"] = mate["mate_indiv_id"]
            parent2["ltime"] = mate["mate_ltime"]
            parent2["x"] = mate["mate_x"]
            parent2["y"] = mate["mate_y"]
            parent2["z"] = mate["mate_z"]
            babies.append([mate, parent2, mate["ltime"]])
        return babies

    def makeBabies(self, babies):
        for baby in babies:
            self.db.makeBaby(baby[0], baby[1], baby[2], self.one_child,
                             self.indiv_max_age * self.indiv_infertile_span,
                             self.arena_x, self.arena_y, self.random_birth_place)

    def getPathDuringPP(self, id):
        return self.base_path + self.traces_during_pp_path + str(id) + ".trace"

    def moveFilesToTmp(self, indiv):
        """ once all preprocessing is done, move the files to their target destination
        :param todos: list of strings with the individual IDs
        :return: None
        """
        id = self.getIDfromTrace(indiv)
        try:
            shutil.copy2(indiv, self.base_path + self.traces_backup_path + str(id) + ".trace")
            shutil.copy2(indiv, self.getPathDuringPP(id))
        except:
            pass

    def moveFilesToFinal(self, indiv):
        """ once all preprocessing is done, move the files to their target destination
        :param todos: list of strings with the individual IDs
        :return: None
        """
        id = self.getIDfromTrace(indiv)
        if os.path.isfile(self.getPathDuringPP(id)):
            shutil.move(self.getPathDuringPP(id),
                        self.base_path + self.traces_after_pp_path + str(id) + ".trace")
        if os.path.isfile(indiv):
            os.remove(indiv)

    def addFile(self, path):
        self.queue.append(path)
