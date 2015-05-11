import sys
import os
from distanceCalc import DistanceCalc

class TraceDistance():
    def calcDistance(self, filename):
        dc = DistanceCalc()
        distEuclideanStep = dc.distanceStep(filename, "euclidean")
        distManhattanStep = dc.distanceStep(filename, "manhattan")
        distEuclideanTotal = dc.distanceTotal(filename, "euclidean")
        distManhattanTotal = dc.distanceTotal(filename, "manhattan")
        return [distEuclideanStep, distManhattanStep, distEuclideanTotal, distManhattanTotal]

if __name__ == "__main__":
    if not len(sys.argv) == 2:
        print "I take 1 argument: the relative or absolute path to a trace file"
    filename = os.path.abspath(sys.argv[1])
    dc = TraceDistance()
    distances = dc.calcDistance(filename)
    print " ".join([str(dist) for dist in distances])

