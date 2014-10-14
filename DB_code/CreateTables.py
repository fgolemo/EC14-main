

def createTables ():
	import MySQLdb
 	mdb = MySQLdb.connect(...)
 	cur = mdb.cursor()	

	cur.execute("CREATE TABLE RobotLocationData(RobotID int, timestep int, x float, y float, z float, child int, HNeat int, VCad int)")
	cur.execute("CREATE TABLE NewRobotLocationData(ID int, timestep int, x float, y float, z float, child int)")
	cur.execute("CREATE TABLE CloseBy (RobotID int, timestep int, x float, y float, NewID int, Newx float, Newy float)")
	cur.execute("CREATE TABLE NewChildren (ChildID, ParentOne int, ParentTwo int, timestep int, HNeat int)")

	cur.close()
	mdb.close()

