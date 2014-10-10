#This function is not yet changed to the arena we decided on.
#I have to test my code first on an sql database. Which I will do tomorrow (26/09).

def CloseRobots (distance, waittime, childtime):
#This function does not return any data, but calculates the new children and places them in a database.
#After that it will put in all the new robot data into the overall database.

	import MySQLdb
 	mdb = MySQLdb.connect(...)
 	cur = mdb.cursor()

 	timestep = 0
	
 	cur.execute(“SELECT RobotID, timestep, x, y, NewID, Newx, Newy FROM RobotLocationData JOIN NewRobotLocationData ON timestep = newtime WHERE child = 0 AND newchild = 0 GROUP BY RobotID, timestep, NewID, x, y, Newx, Newy HAVING SQRT((x-Newx)^2 + (y-Newy)^2) <= distance”)
 	var_CloseBy = cur.fetchall()
 	cur.executemany(“INSERT INTO T_CloseBy (RobotID, timestep, x, y, NewID, Newx, Newy) VALUES (%s,%s,%d,%d,%s,%d,%d)”, var_CloseBy)

 	cur.execute(“SELECT RobotID FROM T_CloseBy GROUP BY RobotID”)
 	ParentIDs = cur.fetchall()
 	for ParentID in ParentIDs:
  		timestep = 0
  		cur.execute(“SELECT RobotID, timestep, x, y, NewID, Newx, Newy FROM T_CloseBy WHERE RobotID = %s”, ParentID)
  		matingtimes = cur.fetchall()
   
  		for matingtime in matingtimes:
   			row = matingtime
   			if row[1] >= timestep:
    				cur.execute(“INSERT INTO T_x (RobotID, NewID, timestep, x, y) VALUES (%s,%s,%s,%d,%d)”, (row[0],row[4],row[1],(row[2]+row[5])/2,(row[3]+row[6])/2))
    				timestep = row[1]+1+waittime
  
 	cur.execute(“SELECT MAX(RobotID) FROM RobotLocationData”)
 	childID = cur.fetchone()

 	cur.execute(“SELECT RobotID, NewID, timestep, x, y FROM T_x”)
 	children = cur.fetchall()
 	for child in children:
  		row = child
  		childID = childID + 1
  		cur.execute(“INSERT INTO RobotLocationData (RobotID, timestep, x, y, z, child) VALUES (%s,%s,%d,%d,0,1)”, (childID,row[2],row[3],row[4]))
		cur.execute(“INSERT INTO NewChildData (ChildID, firstID, secondID, timestep, x, y, z) VALUES (%s,%s,%s,%s,%d,%d,0)”, (childID,row[0],row[1],row[2],row[3],row[4]))

 	cur.execute(“SELECT * FROM NewRobotLocationData GROUP BY timestep HAVING timestep > MIN(timestep)”)
 	new = cur.fetchall()
 	for time in new:
  		row = time
  		cur.execute(“INSERT INTO RobotLocationData (RobotID, timestep, x, y, z, child) VALUES (%s,%s,%d,%d,0,%s)”, (row[0],row[1],row[2],row[3],row[4]))
 
 	cur.execute(“DELETE FROM NewRobotLocationData”)

	cur.close()
	mdb.close()
