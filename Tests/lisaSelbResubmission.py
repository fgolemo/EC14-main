import sys, subprocess, time

maxRuntime = 10
currentRuntime = 0
while currentRuntime < maxRuntime:
    currentRuntime += 1
    print("doing something...")
    time.sleep(2)

cmd = "qsub -o {logpath}.output.log -e {logpath}.error.log -l walltime=4:59 'python {filename} {parameters}"
subprocess.Popen(cmd.format(logpath = "~/.flo/lisaSelfResub", filename = __file__, parameters = " ".join(sys.argv[1:])), shell=True)