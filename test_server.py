import socket
from multiprocessing import Process

class Market(Process):
    def __init__(self, nb_days, day, HOST, PORT):
        super().__init__()
        self.nb_days = nb_days
        self.day = day
        self.HOST = HOST
        self.PORT = PORT

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.HOST, self.PORT))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    while True:
                        self.day.wait()
                        data = conn.recv(1024)
                        print("Data received:", data.decode())