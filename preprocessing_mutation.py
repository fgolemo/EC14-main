__author__ = 'meta'

import xml.etree.cElementTree as ET
# except ImportError:
#     import xml.etree.ElementTree as ET
from random import shuffle
import random
import os


def concat(args):
    string = ""
    for each in args:
        string += str(each)
    return string

# for file in os.listdir("./"):
#     if file.endswith(".txt"):
#         print file
#
#
# class Preprocessor_temp():
#
#
#
    # def mutateMuscles(self,indiv):
    #     """Mutates muscle tissue voxels according to some probability in each layer
    #     """
for dna_file in os.listdir("./Tests"):
    if dna_file.endswith(".vxa"):
        print dna_file

        tree = ET.ElementTree(file="./Tests/" + dna_file) #self.pop_path + str(indiv) + self.suffix_vox))
        root = tree.getroot()
        layers = root.find('VXC').find('Structure').find('Data').findall('Layer')
        probability = 0.1

        dna_list = ""
        for layer in layers:
            dna_list = list(layer.text.strip())
            #TODO Insert mutation code which picks layers

            index_list = list(range(0,99))
            shuffle(index_list)

            # print index_list

            mutations_count = 5
            position_to_check = 0
            for i in range(mutations_count):
                found_mutation = False
                not_found = False

                while not found_mutation:
                    index_number = index_list[position_to_check]
                    tissue = dna_list[index_number]
                    print tissue # TESTING
                    if tissue == '3' or tissue == '4':
                        if random.random() < probability:
                            dna_list[index_number] = 'LOAF' # TODO: new value
                            print "Atrophied a muscle at index " + str(index_number) + "."
                        else:
                            pass
                        found_mutation = True
                        print "Tissue is now  " + str(dna_list[index_number]) + "." # TESTING

                    else:
                        position_to_check += 1
                        print "Trying next index.." # TESTING
                        if position_to_check == len(index_list):
                            not_found = True
                            print "I could not find a muscle voxel!" # TESTING
                            break
                if not_found:
                    print "I could not find a muscle voxel!" # TESTING
                    break
            layer.text = concat(dna_list)
            tree.write("./Tests/" + dna_file)
              # TESTING

            #TODO re-merge list into string and write to .xml file

#
#     try:
#         i = index_list.index(3 or 4) #TODO This function iterates over the index_list, which is fine, but you want it to check whether that number corresponds to a 3 or a 4 in the layer list.
#     except ValueError:
#         i = -1 # no match
#
