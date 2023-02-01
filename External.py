import signal
import os
import random
from multiprocessing import Process

class External(Process):
    def __init__(self, nb_days, events):
        super().__init__()
        self.event_types = events
        self.nb_days = nb_days
        self.proba = [0.95, 0.75, 0.6, 0.5]
    
    def run(self):
        for event in self.event_types:
            for i in range(len(self.event_types)):
                if event == self.event_types[i]:
                    if random.random() > self.proba[i]:
                        os.kill(os.getppid(), self.event_types[i])
        os.kill(os.getpid(), signal.SIGKILL)