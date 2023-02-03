import socket
from multiprocessing import Process, Barrier
import select
import concurrent.futures
import time
import signal
from External import External
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np

class Market(Process):
    def __init__(self, price, coeff, nb_days, nb_homes, barrier_day, long_term_coeff, HOST, PORT):
        super().__init__()
        self.nb_days = nb_days
        self.price = price
        self.coeff = coeff
        self.long_term_coeff = long_term_coeff
        self.HOST = HOST
        self.PORT = PORT
        self.nb_homes = nb_homes
        self.barrier_day = barrier_day
        self.event = [0,0,0,0]
        self.signals = [1,2,3,4]
        self.barrier_signal = Barrier(2)

    #  External event
    def handler(self, sig, frame):
        print("Event of the day", end=" : ")
        if sig == self.signals[0]:
            self.event[0] = 25
            print("War (Price increase by 25%)")
        if sig == self.signals[1]:
            self.event[1] = 10
            print("Snowstorm (Price increase by 10%)")
        if sig == self.signals[2]:
            self.event[2] = -10
            print("Law (Price decrease by 10%)")
        if sig == self.signals[3]:
            self.event[3] = 15
            print("Fuel shortage (Price increase by 15%)")
        
    def run(self):
        # Initialize the signal handler for each event
        for sig in range(len(self.signals)):
            signal.signal(self.signals[sig], self.handler)

        plt.axis([0, self.nb_days, 0, 1])

        for i in range (self.nb_days):
            self.nb_conn = 0
            self.sell = 0
            self.buy = 0
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.setblocking(False)
                server_socket.bind((self.HOST, self.PORT))
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.listen(4)
                with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor:
                    while True:
                        readable, writable, error = select.select([server_socket], [], [], 1)
                        if server_socket in readable:
                            client_socket, address = server_socket.accept()
                            executor.submit(self.socket_handler, client_socket, address)
                            time.sleep(0.1)
                            self.nb_conn += 1
                            if self.nb_conn == self.nb_homes:
                                break
            time.sleep(2)

            self.external = External(self.nb_days, self.signals)
            self.external.start()
            self.external.join()

            self.price = self.price*self.long_term_coeff
            
            if self.sell != 0:
                self.price += 0.05*abs(self.sell/100)
            if self.buy != 0:
                self.price -= 0.1*abs(self.buy/100)

            # Impact of the events
            eventToday = False
            for events in range(len(self.event)):
                if self.event[events] != 0:
                    self.price = round(self.price * (1 + self.event[events]/100),5)
                    self.event[events] = 0
                    eventToday = True
            if not eventToday:
                print("No event this day")


            if self.price > 1:
                self.price = 1
            elif self.price < 0.1:
                self.price = 0.1

            print(f'Homes ask for {self.sell} and sell {self.buy}')
            print(f'\nPrice for today: {self.price}')

            self.event = [0,0,0,0]

            # Create the price graph
            plt.scatter(i, self.price)
            plt.pause(0.05)
            plt.title("Real Time plot of price and day")
            plt.xlabel("day")
            plt.ylabel("price")
            
            time.sleep(1)

            self.barrier_day.wait()
        plt.show()

    def socket_handler(self, s, a):
        with s:
            data = ''
            while data == '':
                data = s.recv(1024)
                m = int(data.decode())
                if m > 0:
                    self.buy += m
                elif m < 0:
                    self.sell += m