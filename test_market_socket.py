import threading
import queue
import socket
import signal
import time
import random
from multiprocessing import Process, Barrier

class Market(Process):
    def __init__(self, price, coeff, nb_days, barrier_day, HOST, PORT):
        super().__init__()
        self.nb_days = nb_days
        self.barrier_day = barrier_day
        self.price = price
        self.coeff = coeff
        self.long_term_coeff = 0.99
        self.price = 0.145
        self.HOST = HOST
        self.PORT = PORT

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.HOST, self.PORT))
        self.s.listen(2)
        self.conn, self.addr = self.s.accept()

    def handle_event(self, sig, frame):
        for event, signal in self.events.items():
            if sig == signal:
                print(f"Received event: {event}")
        
    def run(self):
        #internal factor temperature
        #external factor fuel shortage
        
        with self.conn:
            print('Connected by', self.addr)
            for i in range(self.nb_days):
                data = self.conn.recv(1024)
                if data != b'':
                    result_demand = int(data.decode())
                    print(f'Market received demand : {result_demand}')
                data = self.conn.recv(1024)
                if data != b'':
                    result_vend = int(data.decode())
                    print(f'Market received vend : {result_vend}')

                self.price = self.price*self.long_term_coeff + result_demand/100 * self.coeff[0] + result_vend/100 * self.coeff[1]

                if self.price > 1:
                    self.price = 1
                elif self.price < 0.1:
                    self.price = 0.1

                print(f'New Price: {self.price}')

                self.barrier_day.wait()
        self.conn.close()

if __name__ == "__main__":
    price = 0.17
    coeff = [0.01, -0.01]
    nb_days = 10
    barrier_day = Barrier(1)
    HOST = 'localhost'
    PORT = 17892

    market = Market(price, coeff, nb_days, barrier_day, HOST, PORT)

    market.start()