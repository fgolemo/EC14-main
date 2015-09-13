import os.path
import ConfigParser
import sys

from db import DB


class Skeletor():
    withDB = True
    base_path = ""
    db = None
    dbParams = None
    configPath = ""
    exp_name = ""
    dbString = ""
    path_prefix = ""

    def __init__(self, withDB = True):
        self.config = ConfigParser.RawConfigParser()
        self.withDB = withDB

    def getDB(self):
        """ retrieve database string from config or cache
        :return: None
        """
        self.db = DB(self.dbString, self.exp_name, 0, 0)
        self.dbParams = (self.dbString, self.exp_name, 0, 0)

    def readConfig(self, filename):
        self.config.read(filename)
        self.path_prefix = self.config.get('Experiment', 'path_prefix')
        self.dbString = self.config.get('DB', 'db_string')
        self.exp_name = self.config.get('Experiment', 'name')
        self.base_path = os.path.expanduser(self.path_prefix + self.exp_name) + "/"

    def initialize(self):
        self.readConfig(self.configPath)
        if self.withDB:
            self.getDB()

    def handleParams(self):
        if len(sys.argv) != 2:
            print(
                "I take 1 argument: the configuration file for the experiment")
            quit()

        self.configPath = sys.argv[1]
        self.configPath = os.path.abspath(self.configPath)

        print("using config file: " + self.configPath)

    def start(self):
        self.handleParams()
        self.initialize()


