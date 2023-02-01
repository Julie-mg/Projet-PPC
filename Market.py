import socket
from multiprocessing import Process
import select
import concurrent.futures
import time
import signal
from External import External

class Market(Process):
    def __init__(self, price, coeff, nb_days, nb_homes, barrier_day, HOST, PORT):
        super().__init__()
        self.nb_days = nb_days
        self.price = price
        self.coeff = coeff
        self.long_term_coeff = 0.99
        self.price = 0.145
        self.HOST = HOST
        self.PORT = PORT
        self.nb_conn = 0
        self.nb_homes = nb_homes
        self.barrier_day = barrier_day
        self.event = [0,0]

    def handler(self, sig, frame):
        if sig == signal.SIGUSR1:
                print(f"Event today: hurricane")
                self.price += 0.1
        else:
            print("no hurricane today")

        if sig == signal.SIGUSR2: 
                print(f"Event today: fuel shortage")
                self.price += 0.1
                #print(f"price: {self.price}")
        else:print("no fuel shortage today")
        
    def run(self):
        for i in range (self.nb_days):
            self.nb_conn = 0
            self.sell = 0
            self.buy = 0
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.setblocking(False)
                server_socket.bind((self.HOST, self.PORT))
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
                                #print("break")
                                break
                            #print("test1")
                        #print("test2")
                    #print("test3")
                    server_socket.close()
                server_socket.close()
                #print("test4")
            #print("start calculate price")

            self.external = External(self.nb_days)
            self.external.start()
            signal.signal(signal.SIGUSR1, self.handler)
            signal.signal(signal.SIGUSR2, self.handler)

            self.price = self.price*self.long_term_coeff 
            self.event = [0,0]
            if self.price > 1:
                self.price = 1
            elif self.price < 0.1:
                self.price = 0.1

            print(f'Homes ask for {self.sell} and sell {self.buy}')
            print(f'Price for today: {self.price}')
            #print(f'---------day {i} off')


            self.barrier_day.wait()
        #print(f'end of day {i} market')

    def socket_handler(self, s, a):
        with s:
            #print("Connected to client: ", a)
            data = ''
            while data == '':
                data = s.recv(1024)
                m = int(data.decode())
                print(f"Market received: {m}")
                if m > 0:
                    self.buy += m
                elif m < 0:
                    self.sell += m
            #print("Disconnecting from client: ", a)
            #print("nb_conn : ", self.nb_conn)