import math


class DistanceCalc:
    def distanceStep(self, filename, type):
        with open(filename, 'r') as inputFile:
            firstRun = True
            dist = 0
            for line in inputFile:
                lineSplit = line.split("\t")
                if len(lineSplit) != 5 or str(float(lineSplit[2])) != str(lineSplit[2]):
                    lineSplit = line.split(" ")
                    if len(lineSplit) != 5 or str(float(lineSplit[2])) != str(lineSplit[2]):
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
                if len(lineSplit) != 5 or str(float(lineSplit[2])) != str(lineSplit[2]):
                    lineSplit = line.split(" ")
                    if len(lineSplit) != 5 or str(float(lineSplit[2])) != str(lineSplit[2]):
                        continue
                goodline = lineSplit
                if firstRun:
                    firstLine = lineSplit
                else:
                    pass
                firstRun = False

            lastLine = goodline
            x_diff = float(firstLine[2]) - float(lastLine[2])
            y_diff = float(firstLine[3]) - float(lastLine[3])
            if type == "euclidean":
                return  math.sqrt((x_diff**2) + (y_diff**2))
            if type == "manhattan":
                return math.fabs(x_diff) + math.fabs(y_diff)