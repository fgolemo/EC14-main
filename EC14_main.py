# Python main script
import random
from subprocess import Popen
import os.path, time, glob, shutil, mysql.connector, ConfigParser

# import workers
import sys
from db import DB
import hyperneat_worker as hn
import voxelyze_worker as vox
import postprocessing_worker as pp


class EC14controller():
    base_path = ""
    db = None
    dbString = ""
    dbParams = ""
    exp_name = ""
    hnWorker = None
    voxWorker = None
    ppWorker = None
    newExperiment = False
    pop_size = 0
    pop_random = 0
    pop_random_start_end = (0, 0)
    indiv_max_age = 0
    arena_x = 0
    arena_y = 0
    arena_type = ""
    config = None
    path_prefix = "~/EC14-Exp-"

    random_granularity = 10000.0

    yes = {'yes', 'y', 'ye'}
    no = {'no', 'n', ''}

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()

    def installFiles(self):
        """ Copy script files into experiment directory and saves config
        :return: None
        """

        os.makedirs(self.base_path)
        os.makedirs(self.base_path + "scripts/")
        os.makedirs(self.base_path + "config/")
        os.makedirs(self.base_path + "population/")
        os.makedirs(self.base_path + "traces_duringVox/")
        os.makedirs(self.base_path + "traces_afterVox/")
        os.makedirs(self.base_path + "pool/")
        os.makedirs(self.base_path + "logs/")

        shutil.copy(self.configPath, self.base_path + "config/config.ini")

        files = glob.iglob("./*.py")
        for f in files:
            if os.path.isfile(f):
                shutil.copy(f, self.base_path + "scripts/")

    def getDB(self):
        """ retrieve database string from config or cache
        :return: None
        """

        self.db = DB(self.dbString, self.exp_name, self.end_time, self.indiv_max_age)
        self.dbParams = (self.dbString, self.exp_name, self.end_time, self.indiv_max_age)

    def createPopulaton(self):
        """ creates the initial population in the database
        :return: None
        """

        for i in range(self.pop_size):
            birth = 0
            if (self.pop_random):
                birth = (random.randrange(self.pop_random_start * self.random_granularity,
                                          self.pop_random_end * self.random_granularity)
                         / self.random_granularity)
            x = random.randrange(0, self.arena_x * self.random_granularity) / self.random_granularity
            y = random.randrange(0, self.arena_y * self.random_granularity) / self.random_granularity
            self.db.createIndividual(birth, x, y)

    def readConfig(self, filename):
        self.config.read(filename)
        self.dbString =     self.config.get('DB', 'db_string')
        self.exp_name =     self.config.get('Experiment', 'name')
        self.path_prefix =  self.config.get('Experiment', 'path_prefix')
        self.debug =        self.config.getboolean('Experiment', 'debug')
        self.wall_time =    self.config.getint('Experiment', 'self_wall_time')
        self.end_time =     self.config.getfloat('Experiment', 'end_time')
        self.random_granularity = self.config.getfloat('Experiment', 'random_granularity')
        self.arena_y =      self.config.getfloat('Arena', 'x')
        self.arena_x =      self.config.getfloat('Arena', 'y')
        self.arena_type =   self.config.get('Arena', 'type')
        self.pop_size =     self.config.getint('Population', 'size')
        self.pop_random =   self.config.getboolean('Population', 'random')
        self.pop_random_start = self.config.getfloat('Population', 'random_start')
        self.pop_random_end = self.config.getfloat('Population', 'random_end')

    def isNewExperiment(self):
        self.base_path = os.path.expanduser(self.path_prefix + self.exp_name) + "/"
        print(self.base_path)
        if not os.path.isdir(self.base_path):
            return True
        return False

    def start(self):
        if len(sys.argv) > 2:
            print("I take exactly 1 argument and that is the relative path to the config file... quitting.")
            quit()

        if len(sys.argv) == 2:
            self.configPath = sys.argv[1]
        else:
            self.configPath = "./config.ini"
        print("using config file: " + self.configPath)

        self.readConfig(self.configPath)
        self.getDB()
        if (self.isNewExperiment()):
            self.installFiles()
            self.db.dropTables()
            self.db.createTables()
            self.createPopulaton()

        # launch workers
        # self.hnWorker = hn.HNWorker(self.dbParams, self.base_path, True)
        # self.hnWorker.start()
        # self.voxWorker = vox.VoxWorker(self.dbParams, self.base_path, True)
        # self.voxWorker.start()
        # self.ppWorker = pp.PostprocessingWorker(self.dbParams, self.base_path, True)
        # self.ppWorker.start()


ctrl = EC14controller()
ctrl.start()

time.sleep(2)
print ("main script doing something in the background")
stop = raw_input("want to stop? just press enter: ")
print("user stopped")
ctrl.hnWorker.join()
ctrl.voxWorker.join()
ctrl.ppWorker.join()
print("end of script")

