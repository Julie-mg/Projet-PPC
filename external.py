import signal
import os
import sys
import time
import random
from multiprocessing import Process

class External(Process):
    def __init__(self, market):
        super().__init__()
        self.market = market
        self.event_types = {"hurricane", "fuel shortage"}
    
    def run(self):
        while True:
            for event in self.event_types:
                if event == "hurricane":
                    if random.random() > 0.95:
                        os.kill(os.getppid(), signal.SIGUSR1)
                        print("event is hurricane")
                    
                elif event == "fuel shortage":
                    if random.random() > 1:
                        os.kill(os.getppid(), signal.SIGUSR2)
                        print("event is fuel shortage")
            time.sleep(5)