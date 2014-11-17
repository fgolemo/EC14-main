from db import DB

db = DB("ec141:ec141@192.168.0.44/ec141", "test", 100, 50)
db.dropTables()
db.createTables()
# quit()
print(1)
id1 = db.createIndividual(1,2,3)
id2 = db.createIndividual(2,3,4)
id3 = db.createIndividual(3,4,5)
id4 = db.createIndividual(0,1,2)
id5 = db.createIndividual(0,1,1)
print(2)
print("id:"+str(id1))
indiv = db.getIndividual(id3)
print(3)
print(indiv)

traces = db.getTraces(id3)
print(4)
print(traces)

toHN = db.getHNtodos()
print(5)
print(toHN)

db.markAsHyperneated(toHN[0])

toHN = db.getHNtodos()
print(7)
print(toHN)

toVox = db.getVoxTodos()
print(8)
print(toVox)

indiv1 = db.makeFakeBaby(1)
indiv2 = db.makeFakeBaby(1,2)
print(9)

parents0 = db.getParents(1)
parents1 = db.getParents(indiv1)
parents2 = db.getParents(indiv2)
print(10)
print(parents0)
print(parents1)
print(parents2)

todos = [indiv1, indiv2]
for todo in todos:
    id = todo
    print("PP: looking for mates for individual {indiv}...".format(indiv=id))
    mates = db.findMate(id, 5, 10)
    i = 0
    while (len(mates) != 0):
        i+=1
        mate = mates[0]
        parent2 = {}
        parent2["id"] = mate["mate_id"]
        parent2["indiv_id"] = mate["mate_indiv_id"]
        parent2["ltime"] = mate["mate_ltime"]
        parent2["x"] = mate["mate_x"]
        parent2["y"] = mate["mate_y"]
        parent2["z"] = mate["mate_z"]
        db.makeBaby(mate, parent2, mate["ltime"], 2)

        newStart = mate["id"]
        mates = db.findMate(id, 5, 10, newStart)

    print("PP: found {len} mating occurances for individual {indiv}".format(len=i, indiv=id))
db.flush()
print(11)

db.addJob("123456", "qsub dqwpdjwpd -qdqwdq {} qdwqwd $! qwodjq")
db.addJob("123457", "qsub dqoiwdj [];.,<>\'")
db.addJob("123457", "qsub job3 blabli", ["20","21","22"])
openjobs = db.getJobsWaitingCount()
print(openjobs)
print(12)

db.setJobDone("22")
openjobs = db.getJobsWaitingCount()
print(openjobs)
print(13)

unfinished = db.getUnfinishedIndividuals()
print(unfinished)
print(14)


print("done")
