import threading

class HyperNEATworker(threading.Thread):

    def __init__(self, param):
        threading.Thread.__init__(self)
        self.param = param #just for demo purposes
        self.stopRequest = threading.Event()

    def run(self):
    	while (not self.stopRequest.isSet()):
	        print("Thread: checking for {} stuff in the background".format(self.param))
	        self.stopRequest.wait(2)
        print ("Thread: got exist signal... here I can do some last cleanup stuff before quitting")

    def join(self, timeout=None):
        self.stopRequest.set()
        super(HyperNEATworker, self).join(timeout)

hnWorker = HyperNEATworker('HyperNEAT') # the parameter is just for demo purp
hnWorker.start()

#this will pause the main script until the user does summin
stop = raw_input("stop? insert 'y' and press enter: ") 
#if (stop == "y"):
print("user stopped")
hnWorker.join()

print("end of script")
