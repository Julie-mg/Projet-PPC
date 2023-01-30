import threading
import queue
import socket
import signal
import time
import random
from external import External
from multiprocessing import Process

class Market(Process):
    def __init__(self, price, coeff, nb_days, barrier_day):
        super().__init__()
        self.nb_days = nb_days
        self.barrier_day = barrier_day
        self.price = price
        self.coeff = coeff
        self.long_term_coeff = 0.99
        self.price = 0.145
        #external
        self.events = {"hurricane": signal.SIGUSR1, "fuel shortage": signal.SIGUSR2}
        for event, sig in self.events.items():
            signal.signal(sig, self.handle_event)
        self.external = External(self)
        self.external.start()

    def handle_event(self, sig, frame):
        for event, signal in self.events.items():
            if sig == signal:
                print(f"Received event: {event}")
        

    def run(self):
        #internal factor temperature
        #external factor fuel shortage
        for i in range(self.nb_days):
            transaction = 10
            self.price = self.price*self.long_term_coeff + (1/transaction)*self.coeff[0] + self.events['hurricane'] * self.coeff[1] + self.events['fuel shortage'] * self.coeff[2]
            print(f'New Price: {self.price}')
            time.sleep(5)
            self.barrier_day.wait()
