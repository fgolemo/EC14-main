

def createTables ():
	import MySQLdb
 	mdb = MySQLdb.connect(...)
 	cur = mdb.cursor()	

	cur.execute("CREATE TABLE RobotLocationData(ID int, timestep int, x float, y float, z float, child int)")
	cur.execute("CREATE TABLE NewRobotLocationData(ID int, timestep int, x float, y float, z float, child int)")
	cur.execute("CREATE TABLE T_CloseBy (RobotID int, timestep int, x float, y float, NewID int, Newx float, Newy float)")
	cur.execute("CREATE TABLE NewChildData (ChildID int, firstID int, secondID int, timestep int, x float, y float, z float)")
	cur.execute("CREATE TABLE SimulateChildData (ChildID int, timestep int, x float, y float, z float)")

	cur.close()
	mdb.close()

