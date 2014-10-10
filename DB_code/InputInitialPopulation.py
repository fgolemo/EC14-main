#Data format must be described yet and this function's for-loop must be changed according.
#At this moment I expect the data to be: ID, timestep, x, y, z


def InputInitialPopulationData(data)
#This function does not return any data.

	import MySQLdb
	mdb = MySQLdb.connect(...)
	cur = mdb.cursor()

	for row in data:
		#change parts of the code to fit in the data parameter
		cur.execute("INSERT INTO RobotLocationData (RobotID, timestep, x, y, z, child) VALUES (%s,%s,%d,%d,%d,%s)", (row[0],row[1],row[2],row[3],row[4],1))
		cur.execute("INSERT INTO SimulateChildData (ChildID, timestep, x, y, z) VALUES (%s,%s,%d,%d,%d,%s)", (row[0],row[1],row[2],row[3],row[4]))
	

	cur.close()
	mdb.close()