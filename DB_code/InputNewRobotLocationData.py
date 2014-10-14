#Data format must be described yet and this function's for-loop must be changed according.
#At this moment I expect the data to be: timestep, x, y, z


def InputNewRobotLocationData(ChildID, data, childtime, arena_height, arena_width)
#This function does not return any data.

	import MySQLdb
	mdb = MySQLdb.connect(...)
	cur = mdb.cursor()

	#Update the Voxcad marker in the DB
	ChildID = ChildID[0:5]
	cur.execute("UPDATE RobotLocationData SET VCad = 1 WHERE RobotID = %s", ChildID)

	#Get the creation time of the child
	cur.execute("SELECT MIN(timestep) AS timestep FROM RobotLocationData WHERE RobotID = %s", ChildID)
	timestep = cur.fetchone()
	counttime = 0
	child = 1

	#Put the simulated data into Table NewRobotLocationData
	for row in data:
		#change parts of the code to fit in the data parameter
		
		#Modulo also works for numbers < 0. It then adds instead of subtracts
		newx = row[1] % arena_width
		newy = row[2] % arena_height
		
		cur.execute("INSERT INTO NewRobotLocationData (ChildID, timestep, x, y, z, child) VALUES (%s,%s,%d,%d,%d,%s)",(ChildID,row[0]+timestep,newx,newy,row[3],childtime))
		counttime = counttime + 1
  		if counttime == childtime
   			child = 0

	cur.close()
	mdb.close()