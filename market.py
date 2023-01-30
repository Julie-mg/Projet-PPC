import threading
import queue
import socket
import signal
import time
import random
from external import External
from multiprocessing import Process

class Market:
    def __init__(self, price, shared_memory, coeff):
        self.price = price
        #self.shared_memory = shared_memory
        self.coeff = coeff
        """ self.coeff[0] = 0.001 #internal factor temperature
        self.coeff[1] = 0.01 #external factor fuel shortage """
        self.long_term_coeff = 0.99
        self.price = 0.145
        #external
        SIGUSR1 = 10
        SIGUSR2 = 20
        self.event1 = 0
        self.event2 = 0
        signal.signal(signal.SIGUSR1, self.handle_event)
        signal.signal(signal.SIGUSR2, self.handle_event)
        self.external = External(self)
        self.external.start()

    def handle_event(self, sig, frame):
        if sig == signal.SIGUSR1:
            self.event1 = 1
            print("hurricane")
        if sig == signal.SIGUSR2:
            self.event2 = 1
            print("fuel shortage")
        

    def update_price(self):
        #internal factor temperature
        #external factor fuel shortage
        time.sleep(1)
        """ temperature = self.shared_memory["temperature"]
        if temperature < -15 or temperature > 40:
            print("Temperature out of range")
            return """
        #self.handle_event(self.external)#!!!!
        print(self.event1)
        print(self.event2)
        transaction = 10
        self.price = self.price*self.long_term_coeff + (1/transaction)*self.coeff[0] + self.event1 * self.coeff[1] + self.event2 * self.coeff[2]
        print(f'New Price: {self.price}')
        self.event1 = 0
        self.event2 = 0

 
