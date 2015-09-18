import subprocess
import sys
import os
import math
from skeleton import Skeletor


class IndivSimulater(Skeletor):

    def __init__(self):
        Skeletor.__init__(self, False)
        self.individual = "0"
        self.simPath = ""
        self.traces_after_vox_path = "traces_afterVox/"
        self.traces_after_pp_path = "traces_afterPP/"
        self.pop_path = "population/"
        self.pool_path = "pool/"
        self.pool_filename = 'vox.{0}.pool'
        self.logs_path = "logs/"
        self.lastPoolFile = 0
        self.voxelyze_path = "~/EC14-voxelyze/voxelyzeMain"
        self.voxelyze_stepping = 100
        self.voxelyze_cmd = "{id}"
        self.voxelyze_walltime = 1000
        self.submit_script = "scripts/submit.sh"

    def handleParams(self):
        if len(sys.argv) != 3:
            print(
                "I take 2 argument: the configuration file for the experiment and file system path to the folder with the individuals to simulate.\n"
                "The vxa files have to be in a subfolder called 'population'.")
            quit()

        self.configPath = sys.argv[1]
        self.configPath = os.path.abspath(self.configPath)
        self.simPath = os.path.abspath(sys.argv[2]) + "/"

    def readConfig(self, filename):
        Skeletor.readConfig(self, self.configPath)
        self.traces_after_pp_path = self.config.get('Postprocessing', 'traces_after_pp_path')
        if self.base_path in self.simPath:
            quit("I can't not run with this population folder. Please first copy the individuals to simulate into a new directory.")
        self.pool_path = self.simPath + self.pool_path
        self.pool_file_path = self.pool_path + self.pool_filename
        self.pop_path = self.simPath + self.pop_path
        self.logs_path = self.simPath + self.logs_path
        self.traces_after_vox_path = self.simPath + self.traces_after_vox_path

    def simulate(self):
        print "1"
        if not os.path.exists(self.traces_after_vox_path):
            os.makedirs(self.traces_after_vox_path)
        if not os.path.exists(self.pool_path):
            os.makedirs(self.pool_path)
        if not os.path.exists(self.logs_path):
            os.makedirs(self.logs_path)
        outQueue = []
        files = os.listdir(self.pop_path)
        files.sort()
        for file in files:
            if file.endswith(".vxa"):
                fileSplit = file.split("_")
                fileTrace = self.traces_after_vox_path + fileSplit[0] + ".trace"
                if os.path.isfile(fileTrace) and os.path.getsize(fileTrace) > 0:
                    continue
                outQueue.append(fileSplit[0])
                if (len(outQueue) == 12):
                    print "submitting:"
                    print "\n".join(outQueue) + "\n\n"
                    self.sendQueue(outQueue)
                    outQueue = []
        if (len(outQueue) > 0):
            print "submitting:"
            print "\n".join(outQueue) + "\n\n"
            self.sendQueue(outQueue)

    def getLastPoolFile(self):
        if self.lastPoolFile == 0:  # this means is hasn't been set
            self.lastPoolFile = 1  # try 1 first, then incr
            print("looking at pool file:" + (self.pool_file_path.format(self.lastPoolFile)) )
            while (os.path.isfile(self.pool_file_path.format(self.lastPoolFile))):
                self.lastPoolFile += 1
            print("VOX: found last pool file number:" + str(self.lastPoolFile))
        else:
            self.lastPoolFile += 1

    def createPoolFile(self, sendList):
        self.getLastPoolFile()
        f = open(self.pool_file_path.format(self.lastPoolFile), 'w+')

        for indiv in sendList:
            f.write(self.voxelyze_cmd.format(id=indiv) + "\n")
        f.close()

    def runQsub(self, sendList):
        vox_string = "{base_path} {pool_file} {walltime}"
        vox_string = vox_string.format(base_path=self.simPath, exp_name=self.exp_name,
                                       pool_file=str(self.lastPoolFile), walltime=self.voxelyze_walltime)
        print("VOX: calling submit script like this:\n" + self.submit_script + " " + vox_string)
        try:
            cmd = self.submit_script + " " + vox_string
            output = subprocess.Popen(cmd,
                                      stderr=open(
                                          self.simPath + "logs/" + "submit." + str(self.lastPoolFile) + ".stderr.log",
                                          "w"),
                                      stdin=open(os.devnull),
                                      shell=True,
                                      stdout=subprocess.PIPE).communicate()[0]

            print "submitted job: "
            print output
            # self.db.addJob(jobname, cmd, sendList)
        except subprocess.CalledProcessError as e:
            print ("Vox: during submit.sh execution there was an error:")
            print (str(e.returncode))
            quit()
            # TODO: better error handling, but so far, we dont allow submit.sh to fail -
            # TODO: and if it fails, we can check the logs immediately

    def sendQueue(self, sendList):
        """ submits the queue (or part of it) to the Lisa job queue
        :param sendList: simple python list with the names of the individuals to be voxelyzed right now
        :return: None
        """
        print("VOX: sending queue to the job system")

        # write pool file (12 lines, each line is a call to voxelyze) - correction, each line is an indiv ID
        self.createPoolFile(sendList)

        # run submit.sh that qsubs the stuff in the recent pool
        self.runQsub(sendList)


if __name__ == "__main__":
    insim = IndivSimulater()
    insim.start()
    insim.simulate()


