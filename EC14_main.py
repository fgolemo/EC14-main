# Python main script
from subprocess import Popen
import os.path
import time
import io
# from threading import Thread # Not necessary, both workers are very light.


#TODO write out all the other python files to be called
# import GetNextChildren.py
# import FillNewRobotLocationData.py
# import CreateTables.py
# import CloseRobotsArena.py
# import CloseRobots.py

#TODO include preprocessing.py somewhere - figure out how to do that: 1. From VoxCad output [difficult] 2. When VoxCad worker processes the individual [easier]



# Ask user for experiment name:
exp_name = raw_input("Please name your experiment: ") #TODO Make sure no special characters are used (except for - and _)

#Check if file name is taken:
while os.path.isdir(exp_name) == True:
	exp_name = raw_input("That name is taken, please try again:")

exp_path = os.path.expanduser("./"+exp_name+"/")

# Ask user to define pop time and simulation time limit

init_pop_size = get_int("Initial population size [100]: ")

print "Population size set at " + init_pop_size

endtime = get_int("Experiment time limit (in seconds) [100]:")

print "Time limit set at " + sim_time_limit

# Ask user if they are continuing a previous experiment
db_given = raw_input("Are you continuing with an existing database? [Y/N]")

while db_given != "Y" or "N":
    print "That is not a valid answer.",
    db_given = raw_input("Are you continuing with an existing database (type Y for yes and N for no)?")

# Ask user to specify population .xml file path and making it writable to:
if db_given == "Y":
    pop_path = raw_input("Path to population XML folder (e.g. ~/Experiment1/Pop_files/:"))
    while not os.path.exists(pop_path):
        pop_path = raw_input("I can't find that folder, please try again:") 

# Copy script files into experiment directory #TODO make sure files are not duplicates or overwritten
files = glob.iglob("./*.py")
os.makedirs(exp_path+"Scripts/")
for file in files:
    if os.path.isfile(file):
        shutil.copy(file, exp_path+"Scripts/")
		
# If starting a new experiment, initialise population and empty database:
if db_given == "N":	
    pop_path = os.path.expanduser(exp_path+"Pop_files/")
    if not os.path.exists(pop_path): 
        os.makedirs(pop_path)
    create_init_population()
    CreateTables()

# Call workers
vox_worker = execfile("voxelize_worker.py")
hyp_worker = execfile("hyperneat_worker.py")


# If there are no individuals to be created or processed and there are no running jobs in lisa, send terminate request to the workers:
while True:
	time.sleep(2) # Delay for 2 seconds
	count = # Number of individuals not yet HNed or virtualized (get from db) #TODO
	if count == 0:
		running_proc = # Check on running processes in Lisa (Check on jobs: "showq -u jheinerm") #TODO - Need to translate lisa output into bool
		if running_proc == 0:
		    vox_worker.terminate()
		    hyp_worker.terminate()
		    print "Done"
		    exit()
		    
		    
		    
		    
		    
		    
		    
		    
################## Minor Functions ###################
# Function to call in case the workers need to be stopped ABRUPTLY
processes = [vox_worker,hyp_worker]
def kill_subprocesses():
    for item in processes:
        item.kill()

# Function to make sure input is an integer
def get_int(msg):
    while True:
        line = raw_input(msg) or 100
        try:
            return int(line)
        except ValueError:
            print line, "is not a valid number"
