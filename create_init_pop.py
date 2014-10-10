# Create initial population
def create_init_population():

    RobotID = 1%(#)03d
    
	for i in range(1,int(init_pop_size)+1):
        #Run hyperneat with no input however many times is indicated
		run_hyperneat = Popen("hn",cwd="./HyperNeat",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)  #TODO Adjust for wherever HNeat is
		run_hyperneat.wait()
        
        #If there is an error, print to output and abort process
		if (run_hyperneat.returncode != 0):
			print run_hyperneat.returncode
			run_hyperneat.kill()
		else:
		    #If HNeat produces the population without error, the output is written to a file with the ID as a name (with 5 digits)
			with io.open(pop_path, '%(ID)05d.xml', 'w', encoding='utf-8') as f: %\
			    f.write(str(run_hyperneat.STDOUT()))
				io.close()
				{'ID':RobotID}
				RobotID += 1
	
	# Change population path into a string understandable by the glob command
	pop_path_string = str(pop_path+'*.xml')		
	# Retrieve a list of XML filenames (excluding the path)
	data = [os.path.basename(x) for x in glob.glob(pop_path_string)] 
	
	# Input initial population into database
	InputInitialPopulationData(data) 

