import mysql.connector
from datetime import datetime
import random


class DB():
    cur = False
    con = False
    maxSimTime = 0
    maxAge = 0
    timeBuffer = 0
    keys_individuals = []
    keys_traces = []
    keys_offspring = []
    tablePrefix = ""
    maxQueries = 1
    currentQueries = 0
    connectionString = ""

    def connect(self):
        if (self.cur):
            self.cur.close()
            print("DB: closed cursor")
        if (self.con):
            self.con.close()
            print("DB: closed conn")
        self.cur = None
        self.con = None

        components = self.connectionString.split("@")
        if len(components) != 2:
            raise ValueError("connection string did have more or less than 1 @ symbol")

        auth = components[0].split(":")
        hostdb = components[1].split("/")
        if len(auth) != 2:
            raise ValueError("connection string did have more or less than 1 : symbol")
        if len(hostdb) != 2:
            raise ValueError("connection string did have more or less than 1 / symbol")

        config = {
            'user': auth[0],
            'password': auth[1],
            'host': hostdb[0],
            'database': hostdb[1],
            'raise_on_warnings': True,
        }

        self.con = mysql.connector.connect(**config)
        self.cur = self.con.cursor(dictionary=True)

    def __init__(self, connectionString, tablePrefix, maxSimTime=0, maxAge=0):
        self.maxSimTime = maxSimTime
        self.maxAge = maxAge
        self.tablePrefix = tablePrefix
        self.connectionString = connectionString
        self.connect()

    def test(self):
        # TODO: test db connection
        pass

    def close(self):
        self.con.close()

    def onlyGetIDs(self, results):
        out = []
        for indiv in results:
            out.append(indiv["id"])
        return out

    def getHNtodos(self):
        """ retrieve individuals that need to be created (that only exist in the database so far)
        :return: list with strings (individual names)
        """
        self.flush()
        self.cur.execute("SELECT * FROM " + self.tablePrefix + "_individuals AS i " +
                         "WHERE i.hyperneated = 0 AND born < '" + str(self.maxSimTime) + "'")
        results = self.cur.fetchall()
        return self.onlyGetIDs(results)

    def getVoxTodos(self, resubmit=False):
        """ retrieve individuals that need to be voxelyzed
        :return: list with strings (individual names)
        """
        searchString = "SELECT * FROM " + self.tablePrefix + "_individuals AS i " + \
                       "WHERE i.hyperneated = 1"
        if (resubmit):
            searchString += " AND i.vox_submitted = 1 AND i.voxelyzed = 0"
        else:
            searchString += " AND i.vox_submitted = 0"
        self.flush()
        self.cur.execute(searchString)
        results = self.cur.fetchall()
        return self.onlyGetIDs(results)

    def getParents(self, indiv):
        """ get parents, if they exist, for a given individual
        :return: list of strings (parent IDs), length of this list is either 0, 1 or 2, for no parents, has been mutated from 1 parent and was created by mating,
        """
        self.flush()
        self.cur.execute("SELECT * FROM " + self.tablePrefix + "_offspring AS o " +
                         "WHERE o.child_id = " + str(indiv))
        result = self.cur.fetchone()
        if result == None:
            return []
        else:
            out = [str(result['parent1_id'])]
            if (result['parent2_id'] != None):
                out.append(str(result['parent2_id']))
            return out


    def markAsHyperneated(self, indiv):
        """ marks the individual as been processed by HyperNEAT. I.e. an actual file was created from database
        :param indiv: string, ID of an individual
        :return: None
        """
        self.cur.execute(
            "UPDATE " + self.tablePrefix + "_individuals SET hyperneated = 1 WHERE id = " + str(indiv) + ";")

    def markAsVoxelyzed(self, indiv):
        """ marks the individual as been actually processed by Voxelyze
        :param indiv: string, ID of an individual
        :return: None
        """
        self.cur.execute("UPDATE " + self.tablePrefix + "_individuals SET voxelyzed = 1 WHERE id = " + str(indiv) + ";")

    def markAsVoxSubmitted(self, indiv):
        """ marks the individual as been submitted to Lisa
        :param indiv: string, ID of an individual
        :return: None
        """
        self.cur.execute(
            "UPDATE " + self.tablePrefix + "_individuals SET vox_submitted = 1 WHERE id = " + str(indiv) + ";")

    def unmarkAsVoxSubmitted(self):
        """ re-enable all individuals for resubmission to the cluster by removing the submitted flag
        :return: None
        """
        self.cur.execute(
            "UPDATE " + self.tablePrefix + "_individuals SET vox_submitted = 0 WHERE postprocessed = 0;")

    def markAsPostprocessed(self, indiv):
        """ marks the individual as successfully mates, trace file moved and corrected
        :param indiv: string, ID of an individual
        :return: None
        """
        self.cur.execute(
            "UPDATE " + self.tablePrefix + "_individuals SET postprocessed = 1 WHERE id = " + str(indiv) + ";")

    def setFinalTime(self, indiv):
        """ calculate the total time it took to process this individual
        :param indiv: string, ID of an individual
        :return: None
        """
        indiv_obj = self.getIndividual(indiv)
        start_time = datetime.strptime(str(indiv_obj['created_time']), "%Y-%m-%d %H:%M:%S")
        diff_time = datetime.now() - start_time
        self.cur.execute("UPDATE " + self.tablePrefix + "_individuals SET total_time = " + str(
            self.getTotalSeconds(diff_time)) + " WHERE id = " + str(indiv) + ";")

    def getTotalSeconds(self, timedelta):
        # hack because the total_seconds method only came in python 2.7 and DAS-4 runs 2.6
        return int((timedelta.microseconds + (timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6)

    def markAsDead(self, indiv):
        """ marks the individual as unusable
        :param indiv: string, ID of an individual
        :return: None
        """
        self.cur.execute("UPDATE " + self.tablePrefix + "_individuals SET postprocessed = 1, hyperneated = 1, " + \
                         "voxelyzed = 1, vox_submitted =1 WHERE id = " + str(indiv) + ";")

    def dropTables(self):
        self.cur.execute("SET sql_notes = 0")
        self.cur.execute("DROP TABLE IF EXISTS " + self.tablePrefix + "_individuals")
        self.cur.execute("DROP TABLE IF EXISTS " + self.tablePrefix + "_traces")
        self.cur.execute("DROP TABLE IF EXISTS " + self.tablePrefix + "_firsttraces")
        self.cur.execute("DROP TABLE IF EXISTS " + self.tablePrefix + "_offspring")
        self.cur.execute("DROP TABLE IF EXISTS " + self.tablePrefix + "_jobs")
        self.cur.execute("SET sql_notes = 1")
        self.flush()

    def createTables(self, spaceTolerance):
        self.cur.execute("SET sql_notes = 0")
        self.cur.execute("CREATE TABLE IF NOT EXISTS " +
                         self.tablePrefix + "_individuals " +
                         "(id INT NOT NULL AUTO_INCREMENT, " +
                         "born FLOAT NOT NULL, " +
                         "hyperneated TINYINT(1) DEFAULT 0 NOT NULL, " +
                         "vox_submitted TINYINT(1) DEFAULT 0 NOT NULL, " +
                         "voxelyzed TINYINT(1) DEFAULT 0 NOT NULL, " +
                         "postprocessed TINYINT(1) DEFAULT 0 NOT NULL, " +
                         "created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, " +
                         "total_time INT, " +
                         "PRIMARY KEY (id) )")
        self.cur.execute("CREATE TABLE IF NOT EXISTS " +
                         self.tablePrefix + "_traces " +
                         "(id INT NOT NULL AUTO_INCREMENT, " +
                         "indiv_id INT NOT NULL, " +
                         "ltime FLOAT NOT NULL, " +
                         "x FLOAT NOT NULL, " +
                         "y FLOAT NOT NULL, " +
                         "z FLOAT NOT NULL, " +
                         "fertile TINYINT(1) DEFAULT 1 NOT NULL, " +
                         "PRIMARY KEY (id), " +
                         "INDEX `individ` (`indiv_id`) )")
        self.cur.execute("CREATE TABLE IF NOT EXISTS " +
                         self.tablePrefix + "_firsttraces " +
                         "(id INT NOT NULL AUTO_INCREMENT, " +
                         "indiv_id INT NOT NULL, " +
                         "ltime FLOAT NOT NULL, " +
                         "x FLOAT NOT NULL, " +
                         "y FLOAT NOT NULL, " +
                         "z FLOAT NOT NULL, " +
                         "fertile TINYINT(1) DEFAULT 1 NOT NULL, " +
                         "PRIMARY KEY (id), " +
                         "INDEX `individ` (`indiv_id`) )")
        self.cur.execute("CREATE TABLE IF NOT EXISTS " +
                         self.tablePrefix + "_offspring " +
                         "(id INT NOT NULL AUTO_INCREMENT, " +
                         "parent1_id INT NOT NULL, " +
                         "parent2_id INT, " +
                         "child_id INT NOT NULL, " +
                         "ltime FLOAT NOT NULL, " +
                         "PRIMARY KEY (id) )")
        self.cur.execute("CREATE TABLE IF NOT EXISTS " +
                         self.tablePrefix + "_jobs " +
                         "(id INT NOT NULL AUTO_INCREMENT, " +
                         "jname VARCHAR(20), " +
                         "cmd TEXT, " +
                         "start TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, " +
                         "done DATETIME DEFAULT NULL, " +
                         "individuals TEXT DEFAULT NULL, " +
                         "PRIMARY KEY (id) )")
        self.cur.execute("CREATE TABLE IF NOT EXISTS " +
                         self.tablePrefix + "_mates " +
                         "(line INT NOT NULL AUTO_INCREMENT, " +
                         "id INT NOT NULL, " +
                         "indiv_id INT NOT NULL, " +
                         "ltime FLOAT NOT NULL, " +
                         "x FLOAT NOT NULL, " +
                         "y FLOAT NOT NULL, " +
                         "z FLOAT NOT NULL, " +
                         "mate_id INT NOT NULL, " +
                         "mate_indiv_id INT NOT NULL, " +
                         "mate_ltime FLOAT NOT NULL, " +
                         "mate_x FLOAT NOT NULL, " +
                         "mate_y FLOAT NOT NULL, " +
                         "mate_z FLOAT NOT NULL, " +
                         "fertile TINYINT(1) DEFAULT 1 NOT NULL, " +
                         "PRIMARY KEY (line), " +
                         "INDEX `individ` (`indiv_id`) )")
        self.cur.execute("CREATE TRIGGER `" + self.tablePrefix + "_findmates` " +
                         "BEFORE INSERT ON " + self.tablePrefix + "_traces " +
                         "FOR EACH ROW " +
                         "BEGIN " +
                         "DECLARE next_id INT; " +
                         "SET next_id = (SELECT AUTO_INCREMENT FROM information_schema.TABLES " +
                         "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='" + self.tablePrefix + "_traces'); " +
                         "SET NEW.id=next_id; " +
                         "INSERT INTO " + self.tablePrefix + "_mates (line, indiv_id, id, ltime, x, y, z, " +
                         "mate_indiv_id, mate_id, mate_ltime, mate_x, mate_y, mate_z, fertile) " +
                         "SELECT null, NEW.indiv_id, NEW.id, NEW.ltime, NEW.x, NEW.y, NEW.z, " +
                         "t2.indiv_id as mate_indiv_id, t2.id as mate_id, t2.ltime as mate_ltime, " +
                         "t2.x as mate_x, t2.y as mate_y, t2.z as mate_z, 1 FROM " + self.tablePrefix + "_traces AS t2 " +
                         "WHERE t2.indiv_id!=NEW.indiv_id AND NEW.ltime = t2.ltime " +
                         "AND SQRT( POW(NEW.x - t2.x,2) + POW(NEW.y - t2.y,2) ) <= " + str(spaceTolerance) + " " +
                         "GROUP BY mate_indiv_id; " +
                         "END;")
        self.cur.execute("SET sql_notes = 1")
        self.flush()

    def createIndividual(self, born, x, y):
        self.cur.execute("INSERT INTO " + self.tablePrefix + "_individuals VALUES (NULL, '" + str(
            born) + "', 0, 0, 0, 0, NULL, NULL);")
        individual_id = self.getLastInsertID()
        self.cur.execute(
            "INSERT INTO " + self.tablePrefix + "_firsttraces VALUES (NULL, " + individual_id + ", '" + str(
                born) + "', '" + str(x) + "', '" + str(
                y) + "', 0, 1);")
        self.flush()
        print ("created individual: " + individual_id)

        return individual_id

    def addTraces(self, id, traces):
        firstTrace = self.getFirstTrace(id)
        insertSting = "INSERT INTO " + self.tablePrefix + "_traces VALUES (NULL, %s, %s, %s, %s, %s, %s);"
        self.cur.executemany(insertSting, traces)
        # self.cur.execute("DELETE FROM "+self.tablePrefix+"_traces WHERE id={id};".format(id=firstTrace["id"]))
        self.flush()

    def getPopulationTotal(self):
        self.flush()
        self.cur.execute("SELECT COUNT(id) FROM " + self.tablePrefix + "_individuals")
        result = self.cur.fetchall()
        return result[0]['COUNT(id)']

    def getIndividual(self, id):
        self.flush()
        self.cur.execute("SELECT * FROM " + self.tablePrefix + "_individuals AS i WHERE i.id = '" + str(id) + "' ")
        return self.cur.fetchone()

    def getTraces(self, id):
        self.flush()
        self.cur.execute("SELECT * FROM " + self.tablePrefix + "_traces AS t WHERE t.indiv_id = '" + str(id) + "' ")
        return self.cur.fetchall()


    def getFirstTrace(self, id):
        self.flush()
        self.cur.execute("SELECT * FROM " + self.tablePrefix + "_firsttraces AS t WHERE t.indiv_id = '" + str(
            id) + "' ORDER BY t.id ASC LIMIT 1")
        return self.cur.fetchone()

    def getLastTrace(self, id):
        self.flush()
        self.cur.execute("SELECT * FROM " + self.tablePrefix + "_traces AS t WHERE t.indiv_id = '" + str(
            id) + "' ORDER BY t.id DESC LIMIT 1")
        return self.cur.fetchone()

    def getUnfinishedIndividuals(self):
        self.flush()
        self.cur.execute("SELECT COUNT(id) FROM " + self.tablePrefix + "_individuals WHERE postprocessed = 0")
        result = self.cur.fetchall()
        return result[0]['COUNT(id)']

    def flush(self):
        self.con.commit()

    def addJob(self, name, cmd, individuals=[]):
        name = name.replace("'", "\\'")
        cmd = cmd.replace("'", "\\'")
        indivs = ""
        indivsAsString = []
        for indiv in individuals:
            indivsAsString.append(str(indiv))
        if (len(indivsAsString) > 0):
            indivs = "," + ",".join(
                indivsAsString) + ","  # the comma at beginning and end are important, see self.setJobDone
        insertSting = "INSERT INTO " + self.tablePrefix + "_jobs VALUES (NULL, '{name}', '{cmd}', NOW(), NULL, '{indivs}');"
        self.cur.execute(insertSting.format(name=name, cmd=cmd, indivs=indivs))
        self.flush()

    def getJobsWaitingCount(self):
        querySting = "SELECT COUNT(id) FROM " + self.tablePrefix + "_jobs WHERE done IS NULL;"
        self.cur.execute(querySting)
        result = self.cur.fetchall()
        return result[0]['COUNT(id)']

    def setJobDone(self, indiv):
        querySting = "UPDATE " + self.tablePrefix + "_jobs SET done=NOW() WHERE individuals LIKE '%,{indiv},%';"
        self.cur.execute(querySting.format(indiv=indiv))

    def getLastInsertID(self):
        self.cur.execute("SELECT LAST_INSERT_ID();")
        individual_id = self.cur.fetchone()['LAST_INSERT_ID()']
        return str(individual_id)

    def makeFakeBaby(self, parent1, parent2="NULL"):
        id = self.createIndividual(0, 1, 2)
        self.cur.execute(
            "INSERT INTO " + self.tablePrefix + "_offspring VALUES (NULL, " + str(parent1) + ", " + str(
                parent2) + ", " + str(id) + ", 0);")
        return id

    def makeBaby(self, parent1, parent2, ltime, single=False, infertileSpan=0.25, arena_x=5, arena_y=5, randomPlace=False):
        if randomPlace:
            x = random.uniform(0, arena_x)
            y = random.uniform(0, arena_y)
        else:
            x = (parent1["x"] + parent2["x"]) / 2
            y = (parent1["y"] + parent2["y"]) / 2
        id = self.createIndividual(ltime, x, y)
        insertString = "INSERT INTO " + self.tablePrefix + "_offspring VALUES (NULL, {parent1}, {parent2}, {child}, {ltime});"
        self.cur.execute(
            insertString.format(parent1=parent1["indiv_id"], parent2=parent2["indiv_id"], child=id, ltime=ltime))
        if not single:
            self.infertilize(parent1["indiv_id"], ltime, infertileSpan)
            self.infertilize(parent2["indiv_id"], ltime, infertileSpan)
        self.flush()
        return id

    def infertilize(self, parent, start, timespan):
        updateString = "UPDATE " + self.tablePrefix + "_traces SET fertile = 0 WHERE indiv_id = {indiv} AND ltime >= {start} AND ltime < {end}"
        self.cur.execute(updateString.format(indiv=parent, start=start, end=start + timespan))

    def getMates(self, indiv):
        querySting = "SELECT * FROM " + self.tablePrefix + "_mates WHERE indiv_id={indiv};"
        self.cur.execute(querySting.format(indiv=indiv))
        result = self.cur.fetchall()
        return result

    def getRandomMate(self):
        querySting = "SELECT * FROM " + self.tablePrefix + "_mates WHERE id >= (SELECT FLOOR( MAX(id) * RAND()) FROM " + self.tablePrefix + "_mates ) ORDER BY id LIMIT 1;"
        self.cur.execute(querySting)
        result = self.cur.fetchall()
        result = result[0]
        print(result)
        return result

    def findMate(self, id, timeTolerance=0.0, spaceTolerance=0.01, startTrace=0, single=False):
        # self.currentQueries += 1
        # if self.currentQueries > self.maxQueries:
        # print ("DB: reached max numbers of long queries, reconnecting...")
        # self.connect()
        # print ("DB: ...reconnect done.")
        # self.currentQueries = 1

        query = "SELECT t1.*, t2.indiv_id as mate_indiv_id, t2.id as mate_id, t2.ltime as mate_ltime, t2.x as mate_x, t2.y as mate_y, t2.z as mate_z " + \
                "FROM " + self.tablePrefix + "_traces AS t1 INNER JOIN " + self.tablePrefix + "_traces as t2 " + \
                "WHERE t1.indiv_id={indiv_id} and t2.indiv_id!={indiv_id} "
        #if not single:
        query += "AND t1.fertile = 1 AND t2.fertile = 1 "

        query += "AND t1.id > {start} "

        if timeTolerance > 0:
            query += "AND t1.ltime >= t2.ltime-{timeTol} AND t1.ltime <= t2.ltime+{timeTol} "
        else:
            query += "AND t1.ltime = t2.ltime "

        query += "AND SQRT( POW(t1.x - t2.x,2) + POW(t1.y - t2.y,2) ) <= {spaceTol} "

        if not single:
            query += "LIMIT 1"
        else:
            query += "GROUP BY mate_indiv_id"

        print ("DB: query:")
        print (query.format(indiv_id=id, timeTol=timeTolerance, spaceTol=spaceTolerance, start=startTrace))
        self.cur.execute(query.format(indiv_id=id, timeTol=timeTolerance, spaceTol=spaceTolerance, start=startTrace))
        return self.cur.fetchall()

    def haveMatedBefore(self, parent1, parent2):
        self.flush()
        query = "SELECT id FROM " + self.tablePrefix + "_offspring " + \
                "WHERE (parent1_id = {parent1} AND parent2_id = {parent2}) " + \
                "OR (parent1_id = {parent2} AND parent2_id = {parent1})"
        query_filled = query.format(parent1=parent1["indiv_id"], parent2=parent2["indiv_id"])
        self.cur.execute(query_filled)
        res = self.cur.fetchall()
        if len(res) > 0:
            return True
        else:
            return False

    def isParentOf(self, child, parent):
        self.flush()
        query = "SELECT id FROM " + self.tablePrefix + "_offspring " + \
                "WHERE child_id = {child} AND " + \
                "(parent1_id = {parent} OR parent2_id = {parent})"
        query_filled = query.format(parent=parent, child=child)
        self.cur.execute(query_filled)
        res = self.cur.fetchall()
        if len(res) > 0:
            return True
        else:
            return False

    def getOtherBotsInArea(self, ltime, x, y, radius):
        self.flush()
        # TODO: this ltime+0...1 -0...1 is dirty, I KNOW, any better solutions are welcome
        query = "SELECT COUNT(id) FROM " + self.tablePrefix + "_{TABLE} " + \
                "WHERE ltime >= {ltime}-0.0001 AND ltime <= {ltime}+0.0001 AND " + \
                "SQRT( POW(x - {x},2) + POW(y - {y},2) ) <= {radius}"
        query_filled = query.format(ltime=ltime, x=x, y=y, radius=radius, table="traces")
        self.cur.execute(query_filled)
        result = self.cur.fetchall()
        voxed = result[0]['COUNT(id)']

        query_filled = query.format(ltime=ltime, x=x, y=y, radius=radius, table="firsttraces")
        self.cur.execute(query_filled)
        result = self.cur.fetchall()
        unvoxed = result[0]['COUNT(id)']

        return voxed + unvoxed
