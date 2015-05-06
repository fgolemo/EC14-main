import os.path
import ConfigParser
import sys

from db import DB


class ResubEnabler():
    base_path = ""
    db = None
    dbParams = None
    configPath = ""
    exp_name = ""
    dbString = ""

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()

    def getDB(self):
        """ retrieve database string from config or cache
        :return: None
        """

        self.db = DB(self.dbString, self.exp_name, 0, 0)
        self.dbParams = (self.dbString, self.exp_name, 0, 0)

    def readConfig(self, filename):
        self.config.read(filename)
        self.dbString = self.config.get('DB', 'db_string')
        self.exp_name = self.config.get('Experiment', 'name')

    def initialize(self):
        self.readConfig(self.configPath)
        self.getDB()

    def handleParams(self):
        if len(sys.argv) != 2:
            print(
                "I take 1 argument: the configuration file for the experiment")
            quit()

        self.configPath = sys.argv[1]
        self.configPath = os.path.abspath(self.configPath)

        print("using config file: " + self.configPath)

    def enableResubmissions(self):
        self.db.unmarkAsVoxSubmitted()

    def start(self):
        self.handleParams()
        self.initialize()
        self.enableResubmissions()
        print "done, now run the experiment again"


if __name__ == "__main__":
    rs = ResubEnabler()
    rs.start()
