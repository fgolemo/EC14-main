__author__ = 'meta'

import xml.etree.cElementTree as ET
from random import shuffle
import random
import os


class plagueVirus():

    def concat(args):
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
                probability = 0.1

                dna_list = ""
                for layer in layers:
                    dna_list = list(layer.text.strip())
                    index_list = list(range(0,99))
                    shuffle(index_list)
                    mutations_count = 5
                    position_to_check = 0
                    for i in range(mutations_count):
                        found_mutation = False
                        not_found = False

                        while not found_mutation:
                            index_number = index_list[position_to_check]
                            tissue = dna_list[index_number]
                            if tissue == '3' or tissue == '4':
                                if random.random() < probability:
                                    dna_list[index_number] = '2'
                                    print "Atrophied a muscle at index " + str(index_number) + " to " + str(dna_list[index_number]) + "."
                                else:
                                    print "Muscle at index " + str(index_number) + " unchanged."
                                    pass
                                found_mutation = True
                            else:
                                position_to_check += 1
                                # print "Trying next index.."
                                if position_to_check == len(index_list):
                                    not_found = True
                                    # print "I could not find a muscle voxel!"
                                    break
                        if not_found:
                            print "I could not find a muscle voxel!"
                            break
                    layer.text = self.concat(dna_list)
                    tree.write("./population/" + dna_file)

    def initialize(self):
        self.atrophyMuscles()

virus = plagueVirus()
virus.initialize()