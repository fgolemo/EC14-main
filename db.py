import mysql.connector

class DB():
    cur = False
    con = False
    def __init__(self, connectionString):
        components = connectionString.split("@")
        if (len(components) != 2):
            raise ValueError("connection string did have more or less than 1 @ symbol")

        auth = components[0].split(":")
        hostdb = components[1].split("/")
        if (len(auth) != 2):
            raise ValueError("connection string did have more or less than 1 : symbol")
        if (len(hostdb) != 2):
            raise ValueError("connection string did have more or less than 1 / symbol")

        config = {
          'user': auth[0],
          'password': auth[1],
          'host': hostdb[0],
          'database': hostdb[1],
          'raise_on_warnings': True,
        }

        self.con = mysql.connector.connect(**config)
        self.cur = self.con.cursor()

    def test(self):
        #TODO: test db connection
        pass
    def createTables(self):
        self.cur.execute("CREATE TABLE RobotLocationData(RobotID int, timestep int, x float, y float, z float, child int, HNeat int, VCad int, JobID int)")
        self.cur.execute("CREATE TABLE NewRobotLocationData(ID int, timestep int, x float, y float, z float, child int)")
        self.cur.execute("CREATE TABLE CloseBy (RobotID int, timestep int, x float, y float, NewID int, Newx float, Newy float)")
        self.cur.execute("CREATE TABLE NewChildren (ChildID, ParentOne int, ParentTwo int, timestep int, HNeat int)")
    def close(self):
        self.con.close()
