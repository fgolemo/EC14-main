#Data format must be described yet and this function's for-loop must be changed according.
#At this moment I expect the data to be: timestep, x, y, z


def InputNewRobotLocationData(NewID, data, childtime, arena_height, arena_width)
#This function does not return any data.

	import MySQLdb
	mdb = MySQLdb.connect(...)
	cur = mdb.cursor()

	cur.execute("SELECT TOP 1 timestep FROM RobotLocationData WHERE RobotID = %s", NewID)
	timestep = cur.fetchone()
	counttime = 0
	child = 1

	for row in data:
		#change parts of the code to fit in the data parameter
		
		newx = row[1]
		newy = row[2]
		if newx > arena_width:
			newx = newx - arena_width
		elif newx < 0:
			newx = newx + arena_width
		if newy > arena_height:
			newy = newy - arena_height
		elif newy < 0:
			newy = newy + arena_height
		
		cur.execute("INSERT INTO NewRobotLocationData (NewID, timestep, x, y, z, child) VALUES (%s,%s,%d,%d,%d,%s)",(NewID,row[0]+timestep,newx,newy,row[3],childtime))
		counttime = counttime + 1
  		if counttime == childtime
   			child = 0

	cur.close()
	mdb.close()