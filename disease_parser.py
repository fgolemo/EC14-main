__author__ = 'meta'

import xml.etree.cElementTree as ET
from random import shuffle
import random
import os


class plagueVirus():

    def concat(self, args):
        string = ""
        for each in args:
            string += str(each)
        return string

    def atrophyMuscles(self):
        """Mutates muscle tissue voxels according to some probability in each layer
        """
        for dna_file in os.listdir("./population"):
            if dna_file.endswith(".vxa"):
                print dna_file

                tree = ET.ElementTree(file="./population/" + dna_file)
                root = tree.getroot()
                layers = root.find('VXC').find('Structure').find('Data').findall('Layer')
                probability = 1

                dna_list = ""
                for layer in layers:
                    dna_list = list(layer.text.strip())
                    position_to_check = 0
                    for index in range(len(dna_list)):
                        tissue = dna_list[index]
                        if tissue == '3' or tissue == '4':
                            if random.random() <= probability:
                                dna_list[index] = '-'
                                print "Atrophied a muscle at index " + str(index) + " to " + str(dna_list[index]) + "."
                            else:
                                print "Muscle at index " + str(index) + " unchanged."
                                pass

                        else:
                            continue

                    layer.text = self.concat(dna_list)
                    tree.write("./population/" + dna_file)

    def initialize(self):
        self.atrophyMuscles()

virus = plagueVirus()
virus.initialize()