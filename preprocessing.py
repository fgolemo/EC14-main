import random
import sys
import math


class Preprocessor():
    def makeRobotStartAtZero(self, filename, firstLocation=8):
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


    def addRandomStartingPoint(self, filename, firstLocation=8, arenaXsize=5, arenaYsize=5):
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

    def forceStep(self, val, step):
        a = val/step
        b = math.floor(a)
        c = b * step
        return c


    def correctBirth(self, coordinates, birthX, birthY, birthTime, endTime, step):
        coordinates[1] = self.forceStep(float(coordinates[1]) + birthTime, step)
        if (coordinates[1] > endTime):
            return False
        coordinates[2] = float(coordinates[2]) + birthX
        coordinates[3] = float(coordinates[3]) + birthY
        return coordinates

    def correctArenaBouncy(self, coordinates, arenaX, arenaY):
        #TODO: implement bouncy
        pass

    def correctArenaInfinite(self, coordinates, arenaX, arenaY):
        if coordinates[2] < 0:
            coordinates[2] = float(coordinates[2]) + arenaX
        if coordinates[2] > arenaX:
            coordinates[2] = float(coordinates[2]) - arenaX
        if coordinates[3] < 0:
            coordinates[3] = float(coordinates[3]) + arenaY
        if coordinates[3] > arenaY:
            coordinates[3] = float(coordinates[3]) - arenaY
        return coordinates

    def correctArena(self, coordinates, arenaX, arenaY, arenaType):
        if (arenaType == "i"):
            return self.correctArenaInfinite(coordinates, arenaX, arenaY)
        else:
            return self.correctArenaBouncy(coordinates, arenaX, arenaY)

    def stringify(self, coordinates):
        coordinates[1] = str(coordinates[1])
        coordinates[2] = str(coordinates[2])
        coordinates[3] = str(coordinates[3])
        return coordinates

    def addStartingPointArenaAndTime(self, filename, vox_preamble=8, arenaX=5, arenaY=5, arenaType="i", birthX=0, birthY=0, birthTime=0, endTime=120, timestep=0.002865):
        with open(filename, 'r') as inputFile:
            fileAsList = inputFile.readlines()
            lastLocation = len(fileAsList)-1
            out = []
            for i in range(vox_preamble, lastLocation):
                coordinates = fileAsList[i].split()

                # birth correction
                coordinates = self.correctBirth(coordinates, birthX, birthY, birthTime, endTime, timestep)
                if (coordinates == False): # then the individual lived past the time limit
                    break

                # arena correction
                coordinates = self.correctArena(coordinates, arenaX, arenaY, arenaType)

                # convert the elements into strings again
                coordinates = self.stringify(coordinates)

                # fileAsList[i] = "\t".join(coordinates)+"\n"
                out.append("\t".join(coordinates)+"\n")

            inputFile.close()

        with open(filename, 'w') as outputFile:
            # outputFile.write("".join(fileAsList))
            outputFile.write("".join(out))
            outputFile.close()


    def addParentStartingPoint(self, filename, firstLocation=8, arenaXsize=5, arenaYsize=5, birthX=0, birthY=0):
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


    def correctArenaBoundaries(self, filename, firstLocation=8, arenaXsize=5, arenaYsize=5):
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


    pp = Preprocessor()
    pp.makeRobotStartAtZero(filename, firstLocation)
    pp.addRandomStartingPoint(filename, firstLocation, arenaXsize, arenaYsize)
    pp.correctArenaBoundaries(filename, firstLocation, arenaXsize, arenaYsize)
     
    

