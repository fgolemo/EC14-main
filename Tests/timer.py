from sys import stdout
import time

__author__ = 'Florian'

def printTime(s):
    stdout.write('\rtime elapsed:' + str(s) + 's ')
    stdout.flush()

i = 0
while True:
    printTime(i)
    time.sleep(1)
    i += 1