import sys
import os

if len(sys.argv) != 2:
    print "you need to invoke this script with 1 parameter: the path to the offspring.csv file you want to convert"
    quit()

offspringFile = os.path.abspath(sys.argv[1])
if not os.path.isfile(offspringFile):
    print "couldn't find file: " + offspringFile
    quit()

with open(offspringFile, 'r') as inputFile:
    firstRun = True
    output = ["digraph familyTree {"]
    for line in inputFile:
        if firstRun:
            firstRun = False
            continue
        lineSplit = line.split("\t")
        parent1 = lineSplit[0]
        parent2 = lineSplit[1]
        child = lineSplit[2]
        output.append("\t"+parent1+" -> "+child+";")
        output.append("\t"+parent2+" -> "+child+";")
        # output.append("\t"+child+" -> "+parent1+";")
        # output.append("\t"+child+" -> "+parent2+";")
    output.append("}")

with open(offspringFile[:-3]+"dot", 'w') as outputFile:
    for item in output:
        outputFile.write("%s\n" % item)

print "done, i wrote " + str(len(output)) + " lines"
