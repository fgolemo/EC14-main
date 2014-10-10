import subprocess
from subprocess import Popen
import os.path
import time
import io



RobotID = 1
init_pop_size = 3
path = os.path.expanduser("~/Dropbox/")
    
for i in range(1,int(init_pop_size)+1):
    #Run hyperneat with no input however many times is indicated
	run_hyperneat = subprocess.check_output(["python", "Simple_test.py"],cwd="/home/jharvard/Pop_files/Scripts/").splitlines()  #TODO Adjust for wherever HNeat is
	HN_out = run_hyperneat
	    
#	#If there is an error, print to output and abort process
#	if (run_hyperneat.returncode != 0):
#		print run_hyperneat.returncode
#		run_hyperneat.kill()
#	else:
	#If HNeat produces the population without error, the output is written to a file with the ID as a name (with 5 digits)
	with io.open(path+"/"+str(RobotID).zfill(5)+".xml",mode='w') as f:
		f.write(HN_out)
		io.close()
		RobotID += 1
	
	print run_hyperneat
