from multiprocessing import Process
import sysv_ipc
import random
import socket

class Home(Process):
    def __init__(self, id, mq_offer, mq_demande, barrier_init, barrier_while, lock, shared_temperature, nb_days, barrier_day, HOST, PORT):
        super().__init__()
        self.id = id
        self.mq_offer = mq_offer
        self.mq_demande = mq_demande
        self.offer = self.prod - self.conso
        self.barrier_init = barrier_init
        self.barrier_while = barrier_while
        self.lock = lock
        self.temperature = shared_temperature
        self.nb_days = nb_days
        self.barrier_day = barrier_day
        self.HOST = HOST
        self.PORT = PORT
        
    def run(self):
        self.trade_policy = random.randint(1,3)
        for i in range (self.nb_days):
            # behavior of the process
            self.prod = random.randrange(20,80)
            self.conso = random.randrange(6,60)
            if (self.temperature[i] < 10 or self.temperature[i] > 38):
                self.conso += random.randrange(0,25)
            elif self.conso > 50:
                self.conso -= random.randrange(0, 25)
            self.offer = self.prod - self.conso
            print(f'{self.name} has offer of {self.offer} - trade policy : {self.trade_policy}')


            if self.offer > 0:
                o = str(abs(self.offer)).encode()
                self.mq_offer.send(o, type=self.id)
            else:
                d = str(-self.offer).encode()
                self.mq_demande.send(d, type=self.id)
                
            self.barrier_init.wait()

            if (self.trade_policy == 1 or self.trade_policy == 3):           #si doit donner sa production aux autres homes
                self.lock.acquire()
                while (self.mq_demande.current_messages and self.offer > 0):

                    m, t = self.mq_offer.receive(type=self.id)               #récupère son message d'offer d'énergie dans la liste d'offer

                    (e, t) = self.mq_demande.receive()                             #récupère une demande en énergie
                    num_home = t
                    ask_energy = int(e.decode())

                    left_ask = ask_energy - self.offer                         #left = demande_lue - offer

                    if left_ask > 0:                                                #si il manque encore de l'énergie à la maison
                        l = str(left_ask).encode()
                        self.mq_demande.send(l, num_home)
                        self.offer = 0

                    elif left_ask < 0:                                           #si il reste de l'énergie à donner
                        l = str(-left_ask).encode()
                        self.mq_offer.send(l, type=self.id)
                        self.offer = -left_ask
                    else :
                        self.offer = 0
                self.lock.release()
            
            self.barrier_while.wait()

            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.HOST, self.PORT))

            if self.offer > 0:
                if self.trade_policy == 1:
                    m, t = self.mq_offer.receive(type=self.id)
                else:
                    m, t = self.mq_offer.receive(type=self.id)
                    data =f'{self.offer} '
                    self.s.sendall(data.encode())
                    print(f'{self.name} send offer: {data} to Market')
                
            elif self.offer < 0:
                data =f'{self.offer} '
                self.s.sendall(data.encode())
                print(f'{self.name} send demand: {data} to Market')

            else :
                data =f'{-self.offer} '
                self.s.sendall(data.encode())

            self.lock.acquire()
            while self.mq_demande.current_messages:
                m, t = self.mq_demande.receive()
            self.lock.release()

            self.s.close()
            self.barrier_day.wait()
