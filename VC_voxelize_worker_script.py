#Python script for Voxelize worker... runs until cancelled

# insert while here
indiv = db_get_unprocessed_indiv() #gives back array/tuple with
#ID, birthTime, hasBeenSimulated = 0, hasBeenProcessed = 0, hasBeenHNed = 0

voxelize_queue = []
waiting_time = 0
queue_length = 12
max_waiting_time = 60 * 60 # 60seconds * 60min = 1 hour in seconds

while (true): # so basically run until cancelled
	if (indiv == NULL)
		continue

	if (indiv[1] > sim_time_limit)
		db_set_indiv_processed(indiv)
		continue

	voxelize_queue.push(indiv_file)

	if (voxelize_queue.length == queue_length or waiting_time > max_waiting_time):
		waiting_time = 0
		qsub_create_job(voxelize_queue)
		for (i=0 to queue_length) # mark all idividuals that we just submitted to simulation as simulated
			db_set_indiv_simulated(indiv)

	db_set_indiv_processed(indiv)
	sleep(1 second)
	waiting_time += 1 #add 1 sec waiting time
	indiv = db_get_unprocessed_indiv()
