from db import DB

db = DB("ec141:ec141@192.168.0.44/ec141", 100, 50)
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


print("done")
