import socket
from multiprocessing import Process
import select
import concurrent.futures

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
        self.serve = True

    def handle_event(self, sig, frame):
        for event, signal in self.events.items():
            if sig == signal:
                print(f"Received event: {event}")
        
    def run(self):
        for i in range (self.nb_days):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.setblocking(False)
                server_socket.bind((self.HOST, self.PORT))
                server_socket.listen(4)
                with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor:
                    while self.serve:
                        readable, writable, error = select.select([server_socket], [], [], 1)
                        if server_socket in readable:
                            client_socket, address = server_socket.accept()
                            executor.submit(self.socket_handler, client_socket, address)

                    self.price = self.price*self.long_term_coeff

                    if self.price > 1:
                        self.price = 1
                    elif self.price < 0.1:
                        self.price = 0.1

                    print(f'New Price: {self.price}')
            self.conn.close()
        self.barrier_day.wait()
        print(f'end of day {i} market')

    def socket_handler(self, s, a):
        with s:
            data = ''
            while data == '':
                print("Connected to client: ", a)
                data = s.recv(1024)
                m = data.decode()
                print(f"Market demand: received {m}")
                s.sendall(b"Received: " + data)
                print("Disconnecting from client: ", a)