from multiprocessing import Process
import sysv_ipc
import random
import socket

class Home(Process):
    def __init__(self, id, mq_offre, mq_demande, barrier_init, barrier_while, barrier_act, lock, shared_temperature, nb_days, day, HOST, PORT):
        super().__init__()
        self.conso = random.randrange(6,60)
        self.id = id
        self.trade_policy = random.randint(1,3)
        self.prod = random.randrange(40,80)
        self.mq_offre = mq_offre
        self.mq_demande = mq_demande
        self.offre = self.prod - self.conso
        self.barrier_init = barrier_init
        self.barrier_while = barrier_while
        self.barrier_act = barrier_act
        self.lock = lock
        self.temperature = shared_temperature
        self.nb_days = nb_days
        self.day = day
        self.HOST = HOST
        self.PORT = PORT
        
    def run(self):

        for i in range (self.nb_days):
            # behavior of the process
            #print(f'{self.name} has offre of {self.offre}. Its trade policy is {self.trade_policy}')

            if (self.temperature[i] < 10 or self.temperature[i] > 38):
                self.conso += random.randrange(0,25)
            elif self.conso > 50:
                self.conso -= random.randrange(0, 25)
            self.offre = self.prod - self.conso
            #print(f'offre : {self.offre}, temperature : {self.temperature[i]}')


            if self.offre > 0:
                o = str(abs(self.offre)).encode()
                self.mq_offre.send(o, type=self.id)
                print(f'Offre : {self.offre}, {self.id}')
            else:
                d = str(-self.offre).encode()
                self.mq_demande.send(d, type=self.id)
                print(f'Demande : {-self.offre}, {self.id}')
                
            self.barrier_init.wait()

            if (self.trade_policy == 1 or self.trade_policy == 3):           #si doit donner production aux autres homes
                self.lock.acquire()
                while (self.mq_demande.current_messages and self.offre > 0):
                    #print(f'{self.name} has offre of {self.offre} - trade policy : {self.trade_policy}')

                    m, t = self.mq_offre.receive(type=self.id)               #récupère son message d'offre d'énergie dans la liste d'offre
                    #print("a trouve son propre message")

                    (e, t) = self.mq_demande.receive()                             #récupère une demande en énergie
                    num_home = t
                    ask_energy = int(e.decode())

                    left_ask = ask_energy - self.offre                         #left = demande_lue - offre

                    if left_ask > 0:                                                #si il manque encore de l'énergie à la maison
                        l = str(left_ask).encode()
                        self.mq_demande.send(l, num_home)
                        self.offre = 0
                        #print("manque de l'énergie")
                    elif left_ask < 0:                                           #si il reste de l'énergie à donner
                        l = str(-left_ask).encode()
                        self.mq_offre.send(l, type=self.id)
                        self.offre = -left_ask
                        #print("encore de l'énergie à donner")
                    else :
                        self.offre = 0
                self.lock.release()
            
            self.barrier_while.wait()

            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.HOST, self.PORT))

            if self.offre > 0:
                if self.trade_policy == 1:
                    m, t = self.mq_offre.receive(type=self.id)
                else:
                    m, t = self.mq_offre.receive(type=self.id)
                    data =f'{self.offre} '
                    self.s.sendall(data.encode())
                    print("Offre:", data)
                
            elif self.offre < 0:
                m, t = self.mq_demande.receive(type=self.id)
                data =f'{-self.offre} '
                self.s.sendall(data.encode())
                print("Vend:", data)

            else :
                data =f'{-self.offre} '
                self.s.sendall(data.encode())
                print("Rien:", data)

            self.s.close()
            self.day.wait()
            print(f'end of day {i} {self.name}')
