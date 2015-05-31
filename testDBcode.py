import sys
import os
import math
from EC14skeleton import Skeletor
from distanceCalc import DistanceCalc

class TestDbCode(Skeletor):

    def test(self):
        self.db.getRandomMate()

if __name__ == "__main__":
    dbt = TestDbCode()
    dbt.start()
    dbt.test()


