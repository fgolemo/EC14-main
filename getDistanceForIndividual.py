import sys
import os
import math
from EC14skeleton import Skeletor
from distanceCalc import DistanceCalc

class IndivDistance(Skeletor):

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

        dc = DistanceCalc()
        distEuclideanStep = dc.distanceStep(filename, "euclidean")
        distManhattanStep = dc.distanceStep(filename, "manhattan")
        distEuclideanTotal = dc.distanceTotal(filename, "euclidean")
        distManhattanTotal = dc.distanceTotal(filename, "manhattan")
        return [distEuclideanStep, distManhattanStep, distEuclideanTotal, distManhattanTotal]




if __name__ == "__main__":
    dc = IndivDistance()
    dc.start()
    distances = dc.calcDistance()
    print " ".join([str(dist) for dist in distances])

