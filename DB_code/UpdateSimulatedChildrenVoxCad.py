#return children ready for VoxCad simulation


def UpdateSimulatedChildrenVoxcad(ID)
#This function updates the marker on a specific child that has been simulated by voxcad
	import MySQLdb
	mdb = MySQLdb.connect(...)
	cur = mdb.cursor()

	#Update Table RobotLocationData with the voxcad marker for the children that have been simulated by voxcad
	#In the case that the child already has been put in the database this code still works.
	ID = ID[0:5]
	cur.execute("UPDATE RobotLocationData SET VCad = 1 WHERE RobotID = %s AND child = 1 AND HNeat = 1 AND VCad = 0", ID)

	cur.close()
	mdb.close()

	return childrenVoxCad