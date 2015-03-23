__author__ = 'meta'
import random
import sys
import math
import xml.etree.cElementTree as ET
# except ImportError:
#     import xml.etree.ElementTree as ET

#
#
# class Preprocessor_temp():
#
#
#
    # def calculateLifetime(self,indiv):
    #     """Calculates and edits an individual's lifetime based on its genome
    #     """
tree = ET.ElementTree(file='97_vox.vxa')#self.pop_path + str(indiv) + self.suffix_vox)
root = tree.getroot()
layers = root.find('VXC').find('Structure').find('Data').findall('Layer')

dna = ""
for layer in layers:
    dna += str(layer.text).strip()
print dna  # Delete after testing
dna_length = len(dna) # Delete after testing
print dna_length  # Delete after testing

count_empty = dna.count('0')
count_soft = dna.count('1')
count_hard = dna.count('2')
count_active = dna.count('3') + dna.count('4')
count_length = count_empty + count_soft + count_hard + count_active
print count_length  # Delete after testing

if dna_length != count_length:
    print "DNA length count error!"

cost_muscle = 0.8 # Delete after testing
cost_soft = 1 # Delete after testing
cost_hard = 1 # Delete after testing
lifetime_weight = 0.0025 # Delete after testing

lifetime = ((count_soft * cost_soft) + (count_active * cost_muscle)) * lifetime_weight
# lifetime = 5 - lifetime_cost
print lifetime # Delete after testing
# text_file = open("Output.txt", "w")
# text_file.write(dna)
# text_file.close()

# stopcond = root.find('Simulator').find('StopCondition').find('StopConditionValue')
# stopcond.text = lifetime
# tree.write('97_vox.vxa') #self.pop_path + str(indiv) + self.suffix_vox
# tree.find('.//begdate').text = '1/1/2011'
# print stopcond.text # Delete after testing

root.find('Simulator').find('StopCondition').find('StopConditionValue').text = str(lifetime)
tree.write('output.xml')

