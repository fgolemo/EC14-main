#Data format must be described yet and this function's for-loop must be changed according.
#At this moment I expect the data to be: ID, timestep, x, y, z


def InputInitialPopulationData(data)
#This function does not return any data.
#Insert the initial population (robots not yet simulated) into table RobotLocationData

	import MySQLdb
	mdb = MySQLdb.connect(...)
	cur = mdb.cursor()

	for row in data:
		#change parts of the code to fit in the data parameter
		IntID = row[0]
		IntID = IntID[0:5]
		cur.execute("INSERT INTO RobotLocationData (RobotID, timestep, x, y, z, child, HNeat, VCad) VALUES (%s,%s,%d,%d,%d,%s,1,0)", (IntID,row[1],row[2],row[3],row[4],1))

	cur.close()
	mdb.close()