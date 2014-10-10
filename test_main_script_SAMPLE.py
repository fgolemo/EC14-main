#Python main script
from subprocess import Popen
import os.path
import time
from threading import Thread

# Ask user for experiment name:
exp_name = raw_input("Please name your experiment: ")

#Check if file name is taken:
if os.path.isfile("./" + exp_name) == True:
	exp_name = raw_input("That name is taken, please try again:")

# Function to call in case the workers need to be stopped
processes = [vox_worker,hype_worker]
def kill_subprocesses():
    for item in processes:
        item.kill()

# Ask user to define pop time and simulation time limit

init_pop_size = raw_input("Initial population size [100]: ") or 100

print "Population size set at " + init_pop_size

init_pop_size = raw_input("Experiment time limit (in seconds):  [100]") or 100

print "Time limit set at " + sim_time_limit

# Create initial population
def create_init_population():

	for (i in range 1:init_pop_size):

		run_hyperneat = Popen("Simple_test",cwd="./",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)  #or whatever dir hyperneat is in
		run_hyperneat.wait()

		if (run_hyperneat.returncode != 0):
			print run_hyperneat.returncode
			run_hyperneat.kill()
		else:
			with io.open(exp_name + str(i) + ".dat", 'w', encoding='utf-8') as f:
				f.write(run_hyperneat.STDOUT())
		#individual_xml_file = run_hyperneat()

		save_xml_to_pop_folder(individual_xml_file)

		id = get_individual_id(individual_xml_file)

		db_add_new_individual(id)


#TODO

# Ask for input as Experiment name

# Ask db for last ID

# If there is no starting db, start from 0

# Increment by 1 each HN run

# Make ID Experiment name + "ID"


db_exists = db_check_if_exists()
if (!db_exists):
	db_create()
	create_init_population()
	init_ID = 0

vox_worker = subprocess.check_call("voxelize_worker.py")

spawn_voxlize_worker()
spawn_hyperneat_worker()

while(true)
	sleep(1 second)
	count = db_get_individuals_that_arent_HNed_or_processed()
	if (count == 0)
		kill_voxelize_worker()
		kill_hyperneat_worker()
		print ("done")
		exit()