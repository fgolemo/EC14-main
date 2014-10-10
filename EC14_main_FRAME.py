#Python main script

init_pop_size = 100
sim_time_limit = 100 #seconds

def create_init_population():
	for (i=0 to init_pop_size):
		individual_xml_file = run_hyperneat()
		save_xml_to_pop_folder(individual_xml_file)
		id = get_individual_id(individual_xml_file)
		db_add_new_individual(id)


db_exists = db_check_if_exists()
if (!db_exists):
	db_create()
	create_init_population()


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