import sys, subprocess, time, os

print("current PID:" + str(os.getpid()) )

maxRuntime = 10
currentRuntime = 0
while currentRuntime < maxRuntime:
    currentRuntime += 2
    print("doing something...")
    time.sleep(2)

cmd = "qsub -o {logpath}.output.log -e {logpath}.error.log -l walltime=4:59 -v file={file},params={params} {relhome}/.flo/lsresub.sh"
home = os.environ.get('HOME')
#home = subprocess.check_output("echo $HOME", shell=True)
if (home == '/home/jheinerm'):
    relhome = home
else:
    relhome = os.environ.get('PBS_O_HOME')

qsub = subprocess.check_output(cmd.format(logpath = relhome + "/.flo/lisaSelfResub", file = os.path.basename(__file__), params = " ".join(sys.argv[1:]), relhome = relhome), shell=True)
print(qsub)
print("done")