#return children ready for VoxCad simulation


def GetNextChildrenVoxCad(endtime)
#This function returns rows of children that are ready to be simulated: ChildID, timestep, x, y, z
	import MySQLdb
	mdb = MySQLdb.connect(...)
	cur = mdb.cursor()

	cur.execute("SELECT ChildID, timestep, x, y, z FROM SimulateChildData WHERE timestep < endtime")
	children = cur.fetchall()
	cur.exectue("DELETE FROM SimulateChildData WHERE timestep < endtime")

	cur.close()
	mdb.close()

	return children