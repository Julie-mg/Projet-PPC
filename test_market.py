import threading
import queue
import socket
import signal
import time
import random
import os
from multiprocessing import Process, Barrier
from test_external import External

class Market(Process):
    def __init__(self, price, coeff, nb_days, HOST, PORT,barrier):
        super().__init__()
        self.nb_days = nb_days
        self.price = price
        self.coeff = coeff
        self.long_term_coeff = 1 #0.99
        self.price = 0.145
        self.HOST = HOST
        self.PORT = PORT
        self.event = [0,0]
        self.barrier = barrier

    
    def handler(self, sig, frame):
        if sig == signal.SIGUSR1:
                print(f"Received event: hurricane")
                self.price += 0.1

                print(f"price: {self.price}")
        if sig == signal.SIGUSR2: 
                print(f"Received event: fuel shortage")
                self.price += 0.1
                print(f"price: {self.price}")

        
    def run(self):
        for i in range(self.nb_days):
            self.external = External()
            self.external.start()
            signal.signal(signal.SIGUSR1, self.handler)
            signal.signal(signal.SIGUSR2, self.handler)

            self.price = self.price*self.long_term_coeff 
            self.event = [0,0]
            if self.price > 1:
                self.price = 1
            elif self.price < 0.1:
                self.price = 0.1

            print(f'New Price: {self.price}')
            print(f'---------day {i} off')
            self.barrier.wait()


if __name__ == "__main__":
    price = 0.17
    coeff = [0.1, 0.1]
    nb_days = 10
    HOST = 'localhost'
    PORT = 17892

    barrier = Barrier(1)
    market = Market(price, coeff, nb_days, HOST, PORT,barrier)

    market.start()
    market.join()