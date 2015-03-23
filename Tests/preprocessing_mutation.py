__author__ = 'meta'

import xml.etree.cElementTree as ET
# except ImportError:
#     import xml.etree.ElementTree as ET
from random import shuffle


def concat(args):
    string = ""
    for each in args:
        string += str(each)
    return string

#
#
# class Preprocessor_temp():
#
#
#
    # def mutateMuscles(self,indiv):
    #     """Mutates muscle tissue voxels according to some probability in each layer
    #     """
tree = ET.ElementTree(file='97_vox.vxa')#self.pop_path + str(indiv) + self.suffix_vox)
root = tree.getroot()
layers = root.find('VXC').find('Structure').find('Data').findall('Layer')

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
                dna_list[index_number] = "MUTANT!" # TODO: new value
                found_mutation = True
                print dna_list[index_number] # TESTING

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

    #TODO re-merge list into string and write to .xml file

#
#     try:
#         i = index_list.index(3 or 4) #TODO This function iterates over the index_list, which is fine, but you want it to check whether that number corresponds to a 3 or a 4 in the layer list.
#     except ValueError:
#         i = -1 # no match
#
#     layer_text = concat(dna_list)
#     # tree.write('output.xml')
#     print layer_text  # Delete after testing
#
#
# # root.find('Simulator').find('StopCondition').find('StopConditionValue').text = str()
# # tree.write('output.xml')
#
