import subprocess
import time, sys, os

print("script starting")
pid = os.getpid()
print("pid: "+str(pid))
time.sleep(5)
print("script restarting")
python = sys.executable
#os.execl(python, python, * sys.argv) # get's the same PID everyt ime
restart = raw_input("want to restart?")
if (restart == "y"):
    subprocess.Popen(python + " " + " ".join(sys.argv), shell=True)
print("done with main script")
