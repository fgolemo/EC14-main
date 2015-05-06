import sys
import os
import math
from EC14skeleton import Skeletor


class DistanceCalc(Skeletor):

    def __init__(self):
        Skeletor.__init__(self)
        self.individual = "0"
        self.traces_after_pp_path = "traces_afterPP/"

    def handleParams(self):
        if len(sys.argv) != 3:
            print(
                "I take 2 argument: the configuration file for the experiment and an individual number/id, separated with a space")
            quit()

        self.configPath = sys.argv[1]
        self.configPath = os.path.abspath(self.configPath)
        self.individual = str(int(sys.argv[2]))

    def readConfig(self, filename):
        Skeletor.readConfig(self, self.configPath)
        self.traces_after_pp_path = self.config.get('Postprocessing', 'traces_after_pp_path')

    def calcDistance(self):
        filename = self.base_path + self.traces_after_pp_path + self.individual + ".trace"

        distEuclideanStep = self.distanceStep(filename, "euclidean")
        distManhattanStep = self.distanceStep(filename, "manhattan")
        distEuclideanTotal = self.distanceTotal(filename, "euclidean")
        distManhattanTotal = self.distanceTotal(filename, "manhattan")
        return [distEuclideanStep, distManhattanStep, distEuclideanTotal, distManhattanTotal]

    def distanceStep(self, filename, type):
        with open(filename, 'r') as inputFile:
            firstRun = True
            dist = 0
            for line in inputFile:
                lineSplit = line.split("\t")
                if len(lineSplit) == 0:
                    continue
                if not firstRun:
                    x_diff = x - float(lineSplit[2])
                    y_diff = y - float(lineSplit[3])
                    if type == "euclidean":
                        dist += math.sqrt((x_diff**2) + (y_diff**2))
                    if type == "manhattan":
                        dist += math.fabs(x_diff) + math.fabs(y_diff)

                x = float(lineSplit[2])
                y = float(lineSplit[3])
                firstRun = False
            return dist

    def distanceTotal(self, filename, type):
        with open(filename, 'r') as inputFile:
            firstRun = True
            firstLine = []
            lastLine = []
            lineSplit = []
            for line in inputFile:
                lineSplit = line.split("\t")
                if len(lineSplit) == 0:
                    continue

                if firstRun:
                    firstLine = lineSplit
                else:
                    pass
                firstRun = False

            lastLine = lineSplit
            x_diff = float(firstLine[2]) - float(lastLine[2])
            y_diff = float(firstLine[3]) - float(lastLine[3])
            if type == "euclidean":
                return  math.sqrt((x_diff**2) + (y_diff**2))
            if type == "manhattan":
                return math.fabs(x_diff) + math.fabs(y_diff)


if __name__ == "__main__":
    dc = DistanceCalc()
    dc.start()
    distances = dc.calcDistance()
    print " ".join([str(dist) for dist in distances])

