__author__ = 'Florian'

import subprocess
from subprocess import CalledProcessError

class Test():

    hn_binary="python HyperNEATdummy.py"
    base_path= "~/Documents/dev/EC14-main/Tests"
    hn_path=""


    def runHN(self,hn_params):
        """ run hyperneat with its parameters
        :param hn_params:
        :return: error code
        """
        try:
            subprocess.check_call(self.hn_binary + hn_params,cwd=self.base_path + self.hn_path,shell=True)  # Double check this, may brick the whole thing
        except CalledProcessError as e:
            print ("HN: during HN execution there was an error:")
            print (str(e.returncode))
            quit() #TODO: better error handling, but so far, we dont HN to fail


t = Test()
t.runHN(" -I parameters.dat -R $RANDOM -O indiv1 -ORG")