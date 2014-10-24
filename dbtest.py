from db import DB

db = DB("ec141:ec141@192.168.0.44/ec141")
db.dropTables()
db.createTables()
print(1)
id1 = db.createIndividual(1,2,3)
id2 = db.createIndividual(2,3,4)
id3 = db.createIndividual(3,4,5)
print(2)
print("id:"+str(id1))
indiv = db.getIndividual(id3)
print(3)
print(indiv)

traces = db.getTraces(id3)
print(4)
print(traces)




print("done")
