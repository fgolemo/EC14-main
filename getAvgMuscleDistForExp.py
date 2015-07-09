import random
import sys
import os
import xml.etree.cElementTree as etree
import math


lookForCells = ["3", "4"]  # what cells to measure the distance for

if len(sys.argv) != 2:
    print "you need to invoke this script with 1 parameter: the path to the offspring.csv file you want to analyze"
    quit()

expFolder = os.path.abspath(sys.argv[1])
if not os.path.isdir(expFolder):
    print "couldn't find directory: " + expFolder
    quit()

vxaFiles = os.listdir(expFolder)

output = ["Indiv_ID,AvgMuscleDist"]


def calcDistToCenter(x, y, z):
    # 4.5 is the center of the cube if each dimension starts at 0 and ends at 9
    return math.sqrt(math.pow(x - 4.5, 2) + math.pow(y - 4.5, 2) + math.pow(z - 4.5, 2))


for vxaFile in vxaFiles:
    fileName = vxaFile.split(".")
    if len(fileName) != 2 or fileName[1] != "vxa":
        continue
    fileNameParts = fileName[0].split("_")
    expNumber = fileNameParts[0]

    vxaRoot = etree.ElementTree(file=expFolder + "/" + vxaFile).getroot()
    layers = vxaRoot.find("VXC").find("Structure").find("Data").findall("Layer")

    muscleDist = []
    for z in range(0, len(layers) - 1):
        layer = layers[z].text
        n = 10
        lines = [layer[i:i + n] for i in range(0, len(layer), n)]
        for x in range(0, n - 1):
            for y in range(0, n - 1):
                cell = lines[x][y]
                if cell in lookForCells:
                    dist = calcDistToCenter(x, y, z)
                    muscleDist.append(dist)

    avgMuscleDist = sum(muscleDist) / float(len(muscleDist))
    output.append(str(expNumber) + "," + str(avgMuscleDist))

outputFileName = expFolder + "/" + "avgMuscleDist.csv"
with open(outputFileName, 'w') as outputFile:
    for item in output:
        outputFile.write("%s\n" % item)

print "done, i wrote " + str(len(output)) + " lines to file " + outputFileName

