import random
import sys

def makeRobotStartAtZero(filename, firstLocation=8):
    with open(filename, 'r') as inputFile:
        fileAsList = inputFile.readlines()
        lastLocation = len(fileAsList)-1
        startPos = fileAsList[firstLocation].split()
        startX = float(startPos[2])
        startY = float(startPos[3])
        for i in range(firstLocation, lastLocation):
            coordinates = fileAsList[i].split()
            coordinates[2] = str(float(coordinates[2]) - startX)    
            coordinates[3] = str(float(coordinates[3]) - startY)    
            fileAsList[i] = "\t".join(coordinates)+"\n"
        inputFile.close()
    
    with open(filename, 'w') as outputFile:
        outputFile.write("".join(fileAsList))
        outputFile.close()


def addRandomStartingPoint(filename, firstLocation=8, arenaXsize=5, arenaYsize=5):
    xStart = random.uniform(0,arenaXsize)
    yStart = random.uniform(0,arenaYsize)
    
    with open(filename, 'r') as inputFile:
        fileAsList = inputFile.readlines()
        lastLocation = len(fileAsList)-1
        for i in range(firstLocation, lastLocation):
            coordinates = fileAsList[i].split()
            coordinates[2] = str(float(coordinates[2]) + xStart)
            coordinates[3] = str(float(coordinates[3]) + yStart)
            fileAsList[i] = "\t".join(coordinates)+"\n"
        inputFile.close()
                
    with open(filename, 'w') as outputFile:
        outputFile.write("".join(fileAsList))
        outputFile.close()
 
        
def addParentStartingPoint(filename, firstLocation=8, arenaXsize=5, arenaYsize=5, birthX=0, birthY=0):
    with open(filename, 'r') as inputFile:
        fileAsList = inputFile.readlines()
        lastLocation = len(fileAsList)-1
        for i in range(firstLocation, lastLocation):
            coordinates = fileAsList[i].split()
            coordinates[2] = str(float(coordinates[2]) + birthX)
            coordinates[3] = str(float(coordinates[3]) + birthY)
            fileAsList[i] = "\t".join(coordinates)+"\n"
        inputFile.close()
                
    with open(filename, 'w') as outputFile:
        outputFile.write("".join(fileAsList))
        outputFile.close()


def correctArenaBoundaries(filename, firstLocation=8, arenaXsize=5, arenaYsize=5):
    with open(filename, 'r') as inputFile:
        fileAsList = inputFile.readlines()
        lastLocation = len(fileAsList)-1
        for i in range(firstLocation, lastLocation):
            coordinates = fileAsList[i].split()
            if float(coordinates[2]) < 0:
                coordinates[2] = str(float(coordinates[2]) + arenaXsize)
            if float(coordinates[2]) > arenaXsize:
                coordinates[2] = str(float(coordinates[2]) - arenaXsize)
            if float(coordinates[3]) < 0:
                coordinates[3] = str(float(coordinates[3]) + arenaYsize)
            if float(coordinates[3]) > arenaYsize:
                coordinates[3] = str(float(coordinates[3]) - arenaYsize)    
            fileAsList[i] = "\t".join(coordinates)+"\n"
        inputFile.close()
        
    with open('testOutput.trace', 'w') as outputFile:
        outputFile.write("".join(fileAsList))
        outputFile.close()

if __name__ == "__main__": #if the script is being run standalone
    #parse command line parameters and make sure there is at least 1 parameter,
    #and this parameter is a filename for a trace file
    #and we can read and write to that trace file
    filename = sys.argv[1]
    if len(sys.argv)>2:
        firstLocation = int(sys.argv[2])
    else: firstLocation = 8
    if len(sys.argv)>3:
        arenaXsize = int(sys.argv[3])
    else: arenaXsize = 5
    if len(sys.argv)>4:
        arenaYsize = int(sys.argv[4])
    else: arenaYsize = 5
    if len(sys.argv)>5:
        birthX = int(sys.argv[5])
    else: birthX = 0
    if len(sys.argv)>6:
        birthY = int(sys.argv[6])
    else: birthY = 0
        
    makeRobotStartAtZero(filename, firstLocation)
    addRandomStartingPoint(filename, firstLocation, arenaXsize, arenaYsize)
    correctArenaBoundaries(filename, firstLocation, arenaXsize, arenaYsize)
     
    

