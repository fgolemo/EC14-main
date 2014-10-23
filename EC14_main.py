# Python main script
from subprocess import Popen
import os.path, time, glob, shutil, mysql.connector, ConfigParser

# import workers
from db import DB
import hyperneat_worker as hn
import voxelyze_worker as vox
import postprocessing_worker as pp


class EC14controller():
    base_path = ""
    db = None
    dbString = ""
    hnWorker = None
    voxWorker = None
    ppWorker = None
    newExperiment = False

    def get_int(self, msg, default):
        while True:
            line = raw_input(msg) or default
            try:
                return int(line)
            except ValueError:
                print line, "is not a valid number"

    def askExperimentName(self):
        """ asks the user for the experiment name/location
        :return: string Path to the project
        """

        exp_name = raw_input(
            "Please name your experiment: ")  # TODO Make sure no special characters are used (except for - and _)

        # Check if file name is taken:
        while exp_name == '' and os.path.isdir(exp_name) == True:
            exp_name = raw_input("That name is taken or empty, please try again: ")

        exp_path = os.path.expanduser("~/EC14-Exp-" + exp_name + "/")

        return exp_path


    def askDatabaseString(self):
        """ asks the user for the database parameters
        :return: string A JDBC-formatted string like username:password@host/databasename
        """

        db_string = raw_input(
            "Please give me your database connection string in JDBC format (i.e. username:password@host/database): ")
        working = False
        while (not working):
            try:
                dbo = DB(db_string)  # ec141:ec141@192.168.0.44/ec141
                dbo.close()
                working = True
            except mysql.connector.Error as err:
                print (err)
                db_string = raw_input("That didn't work, please try again (i.e. username:password@host/database): ")

        return db_string


    def askPopulationSize(self):
        """ ask for population size
        :return: integer Population size
        """

        init_pop_size = self.get_int("Initial population size [100]: ", 100)
        print "Population size set at " + str(init_pop_size)
        return init_pop_size


    def askEndTime(self):  # TODO: this is currently the experiment time, but it should be the in-simulation time
        """ ask for max script runtime
        :return: integer Maximum script runtime
        """
        endtime = self.get_int("Experiment time limit (in seconds) [100]: ", 100)
        print "Time limit set at " + str(endtime) + "s"
        return endtime


    def askWorkingDir(self):
        """ aks the user if there are existing files for this experiment
        :return: None
        """

        yes = {'yes', 'y', 'ye'}
        no = {'no', 'n', ''}

        # Ask user if they are continuing a previous experiment
        db_given = raw_input("Are you continuing with an existing Experiment? [y/N]: ")
        while db_given not in yes and db_given not in no:
            print "That is not a valid answer.",
            db_given = raw_input("Are you continuing with an existing database (type Y for yes and N for no)? ").lower()

        # Ask user to specify population .xml file path and making it writable to:
        if db_given in yes:
            base_path = raw_input("Path to experiment folder (e.g. ~/EC14-Exp-1):")
            while not os.path.exists(os.path.expanduser(base_path)):
                base_path = raw_input("I can't find that folder, please try again:")
        else:
            self.newExperiment = True
            base_path = self.askExperimentName()

        print "Working directory: " + base_path
        self.base_path = base_path


    def installFiles(self):
        """ Copy script files into experiment directory and saves config
        :return: None
        """

        files = glob.iglob("./*.py")
        os.makedirs(self.base_path + "scripts/")
        os.makedirs(self.base_path + "config/")
        os.makedirs(self.base_path + "population/")
        for file in files:
            if os.path.isfile(file):
                shutil.copy(file, self.base_path + "scripts/")


    def installConfig(self):
        """ Copy script files into experiment directory and saves config
        :return: None
        """

        db_string = self.askDatabaseString()
        self.dbString = db_string
        end_time = self.askEndTime()
        pop_size = self.askPopulationSize()

        config = ConfigParser.RawConfigParser()
        config.add_section('DB')
        config.set('DB', 'db_string', db_string)
        config.add_section('Experiment')
        config.set('Experiment', 'end_time', str(end_time))
        config.set('Experiment', 'pop_size', str(pop_size))
        with open(self.base_path + 'config/config.ini', 'wb') as configfile:
            config.write(configfile)


    def getDB(self):
        """ retrieve database string from config or cache
        :return: None
        """

        if (self.dbString == ""): # this is the case, when the experiment exists
            config = ConfigParser.RawConfigParser()
            config.read(self.base_path + 'config/config.ini')
            self.dbString = config.getfloat('DB', 'db_string')

        self.db = DB(self.dbString)

        if (self.newExperiment):
            self.db.createTables()

    def createPopulaton(self):
        """ creates the initial population in the database
        :return: None
        """
        #TODO: implement
        pass

    def start(self):
        self.askWorkingDir()

        if (self.newExperiment):
            self.installFiles()
            self.installConfig()
            self.createPopulaton()

        self.getDB()

        # launch workers
        self.hnWorker = hn.HNWorker(self.db, self.base_path, True)
        self.hnWorker.start()
        self.voxWorker = vox.VoxWorker(self.db, self.base_path, True)
        self.voxWorker.start()
        self.ppWorker = pp.PostprocessingWorker(self.db, self.base_path, True)
        self.ppWorker.start()


    # If there are no individuals to be created or processed and there are no running jobs in lisa, send terminate request to the workers:
    # while True:
    # time.sleep(2)  # Delay for 2 seconds
    #     count =  4# Number of individuals not yet HNed or virtualized (get from db) #TODO
    #     if count == 0:
    #         running_proc = 3# Check on running processes in Lisa (Check on jobs: "showq -u jheinerm") #TODO - Need to translate lisa output into bool
    #         if running_proc == 0:
    #             vox_worker.terminate()
    #             hyp_worker.terminate()
    #             print "Done"
    #             exit()
    # this will pause the main script until the user does summin


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

