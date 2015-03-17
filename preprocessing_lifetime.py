__author__ = 'meta'
import random
import sys
import math
import xml.etree.cElementTree as ET
# except ImportError:
#     import xml.etree.ElementTree as ET



class Preprocessor_temp():
    def calculateLifetime(self,filename):
        tree = ET.ElementTree(file='Tests/97_vox.vxa')
        root = tree.getroot()

        layers = root.find('VXC').find('Structure').find('Data').findall('Layer')
        dna = ""
        for layer in layers:
            dna += str(layer.text).strip()
        print dna

        dna_length = len(dna)
        print dna_length

        count_empty = dna.count('0')
        count_soft = dna.count('1')
        count_hard = dna.count('2')
        count_active = dna.count('3') + dna.count('4')
        count_length = count_empty + count_soft + count_hard + count_active
        print count_length

        if dna_length != count_length:
            print "DNA length count error!"

        cost_muscle = 1.8
        cost_soft = 1
        cost_hard = 1
        weight = 0.002

        lifetime_cost = ((count_soft * cost_soft) + (count_hard * cost_hard) + (count_active * cost_muscle)) * weight
        lifetime = 5 - lifetime_cost
        print lifetime
        # text_file = open("Output.txt", "w")
        # text_file.write(dna)
        # text_file.close()

        stopcond = root.find('Simulator').find('StopCondition').find('StopConditionValue')
        stopcond.text = 2.5
        print stopcond.text

