# Python main script
from subprocess import Popen
import os.path, time, glob, shutil
import io
# from threading import Thread # Not necessary, both workers are very light.


# TODO write out all the other python files to be called
# import GetNextChildren.py
# import FillNewRobotLocationData.py
# import CreateTables.py
# import CloseRobotsArena.py
# import CloseRobots.py

#TODO include preprocessing.py somewhere - figure out how to do that: 1. From VoxCad output [difficult] 2. When VoxCad worker processes the individual [easier]

def get_int(msg, default):
    while True:
        line = raw_input(msg) or default
        try:
            return int(line)
        except ValueError:
            print line, "is not a valid number"

def askExperimentName():
    """ asks the user for the experiment name/location
    :return: string Path to the project
    """
    exp_name = raw_input("Please name your experiment: ")  #TODO Make sure no special characters are used (except for - and _)

    #Check if file name is taken:
    while exp_name == '' and os.path.isdir(exp_name) == True:
        exp_name = raw_input("That name is taken or empty, please try again: ")

    exp_path = os.path.expanduser("~/EC14-Exp-" + exp_name + "/")
    return exp_path


def askPopulationSize():
    """ ask for population size
    :return: integer Population size
    """
    init_pop_size = get_int("Initial population size [100]: ", 100)
    print "Population size set at " + str(init_pop_size)
    return init_pop_size


def askEndTime(): #TODO: this is currently the experiment time, but it should be the in-simulation time
    """ ask for max script runtime
    :return: integer Maximum script runtime
    """
    endtime = get_int("Experiment time limit (in seconds) [100]: ", 100)
    print "Time limit set at " + str(endtime) + "s"
    return endtime


def askWorkingDir():
    """ aks the user if there are existing files for this experiment
    :return:
    """

    yes = {'yes', 'y', 'ye'}
    no = {'no', 'n', ''}

    #Ask user if they are continuing a previous experiment
    db_given = raw_input("Are you continuing with an existing database? [y/N]: ")
    while db_given not in yes and db_given not in no:
        print "That is not a valid answer.",
        db_given = raw_input("Are you continuing with an existing database (type Y for yes and N for no)? ").lower()

    # Ask user to specify population .xml file path and making it writable to:
    if db_given in yes:
        base_path = raw_input("Path to population XML folder (e.g. ~/EC14-Experiment-1):")
        while not os.path.exists(os.path.expanduser(base_path)):
            base_path = raw_input("I can't find that folder, please try again:")
    else:
        # If starting a new experiment, initialise population, empty database and copy the scripts:
        base_path = askExperimentName()
        pop_path = base_path + "population/"
        if not os.path.exists(pop_path):
            os.makedirs(pop_path)
        installFiles(base_path)
        # create_init_population() //TODO
        # CreateTables() //TODO

    print "Working directory: " + base_path
    return base_path


def installFiles(base_path):
    """ Copy script files into experiment directory
    :return: void
    """

    files = glob.iglob("./*.py")
    os.makedirs(base_path + "scripts/")
    for file in files:
        if os.path.isfile(file):
            shutil.copy(file, base_path + "scripts/")

base_path = askWorkingDir()
end_time = askEndTime()
pop_size = askPopulationSize()
quit()

# Call workers
vox_worker = execfile("voxelize_worker.py")
hyp_worker = execfile("hyperneat_worker.py")


# If there are no individuals to be created or processed and there are no running jobs in lisa, send terminate request to the workers:
while True:
    time.sleep(2)  # Delay for 2 seconds
    count =  4# Number of individuals not yet HNed or virtualized (get from db) #TODO
    if count == 0:
        running_proc = 3# Check on running processes in Lisa (Check on jobs: "showq -u jheinerm") #TODO - Need to translate lisa output into bool
        if running_proc == 0:
            vox_worker.terminate()
            hyp_worker.terminate()
            print "Done"
            exit()








################## Minor Functions ###################
# Function to call in case the workers need to be stopped ABRUPTLY
processes = [vox_worker, hyp_worker]


def kill_subprocesses():
    for item in processes:
        item.kill()


# Function to make sure input is an integer

