import signal
import os
import time
import random
from multiprocessing import Process

class External(Process):
    def __init__(self, nb_days):
        super().__init__()
        self.event_types = {"hurricane", "fuel shortage"}
        self.nb_days = nb_days
    
    def run(self):
            for event in self.event_types:
                if event == "hurricane":
                    if random.random() > 0.9:
                        os.kill(os.getppid(), signal.SIGUSR1)
                        #print("event is hurricane")
                    
                elif event == "fuel shortage":
                    if random.random() > 0.5:
                        os.kill(os.getppid(), signal.SIGUSR2)
                        #print("event is fuel shortage")
            os.kill(os.getpid(), signal.SIGKILL)