import random
import sys
import os

if len(sys.argv) != 2:
    print "you need to invoke this script with 1 parameter: the path to the offspring.csv file you want to analyze"
    quit()

offspringFile = os.path.abspath(sys.argv[1])
if not os.path.isfile(offspringFile):
    print "couldn't find file: " + offspringFile
    quit()


def iterateThroughFile(action, search):
    with open(offspringFile, 'r') as inputFile:
        firstRun = True
        max = 0
        for line in inputFile:
            if firstRun:
                firstRun = False
                continue
            lineSplit = line.split("\t")
            parent1 = int(lineSplit[0])
            parent2 = int(lineSplit[1])
            child = int(lineSplit[2])
            if action == "max":
                if child > max:
                    max = child
            if action == "find":
                if child == search:
                    return [parent1,parent2]
        if action == "max":
            return max
        if action == "find":
            return None


max = iterateThroughFile("max", None)
print "max:", max

findable = True
previousIndiv = max
while findable:
    parents = iterateThroughFile("find", previousIndiv)
    if parents == None:
        findable = False
        break
    previousIndiv = random.choice(parents)
    print "parents:",parents,"  picked:",previousIndiv
print "done"

