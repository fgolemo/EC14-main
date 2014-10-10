import MySQLdb
mdb = MySQLdb.connect(...)
cur = mdb.cursor()
#Python script for Voxelize worker... runs until cancelled

voxelize_queue = []
waiting_time = 0
queue_length = 12
max_waiting_time = 60 * 60 # 60seconds * 60min = 1 hour in seconds


while True:
    
    GetNextChildren(endtime) #gives back array/tuple with
    #ID, birthTime, hasBeenSimulated = 0, hasBeenProcessed = 0, hasBeenHNed = 0

	if GetNextChildren(endtime) == NULL:
		continue
		
	else:
	    for ind in children:
            voxelize_queue.append("./"+str(exp_name)+"/"+str(ChildID))
    	
 	if (voxelize_queue.length == queue_length or waiting_time > max_waiting_time):
		waiting_time = 0
		
		# TODO Spawn parallel processes instead of for loop
		### TRY IN LISA ###
#        proc_per_node = "#PBS -lnodes=1:ppn=12"
#    	subprocess.Popen(proc_per_node.split(),stdout=STDOUT,shell=True)
    	###################
    	# Note: Not using scratch space because operations are not I/O intensive.
    	
		for x in voxelize_queue:
		    subprocess.Popen(["gsub","voxelize","./VoxCad/"+voxelize_queue(x),"-lnodes=1:ppn=12"],cwd="./VoxCad",shell=True) #TODO Need to test, string input may be an issue since it isnt in STDIN
    	  	
    	voxelize_queue = []

    time.sleep(1)
	waiting_time += 1 #add 1 sec waiting time

	

