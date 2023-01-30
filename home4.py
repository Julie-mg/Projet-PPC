from multiprocessing import Process, Barrier, Lock, Array
import sysv_ipc
import random

class Home(Process):
    def __init__(self, id, mq_offre, mq_demande, barrier_init, barrier_while, barrier_act, lock, shared_temperature):
        super().__init__()
        self.conso = random.randrange(6000,24000)
        self.id = id
        self.trade_policy = random.randint(1,3)
        self.prod = random.randrange(0,24000)
        self.mq_offre = mq_offre
        self.mq_demande = mq_demande
        self.offre = self.prod - self.conso
        self.barrier_init = barrier_init
        self.barrier_while = barrier_while
        self.barrier_act = barrier_act
        self.lock = lock
        self.temperature = shared_temperature

    def run(self):
        # behavior of the process
        print(f'{self.name} has offre of {self.offre}. Its trade policy is {self.trade_policy}')

        if (self.temperature[0] < 10 or self.temperature[0] > 38):
            self.conso += random.randrange(0,6000)
        elif self.conso > 24000:
            self.conso -= random.randrange(0, 6000)
        self.offre = self.prod - self.conso
        print(f'offre : {self.offre}, temperature : {self.temperature[0]}')


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
                print(f'{self.name} has offre of {self.offre} - trade policy : {self.trade_policy}')

                m, t = self.mq_offre.receive(type=self.id)               #récupère son message d'offre d'énergie dans la liste d'offre
                print("a trouve son propre message")

                (e, t) = self.mq_demande.receive()                             #récupère une demande en énergie
                num_home = t
                ask_energy = int(e.decode())

                left_ask = ask_energy - self.offre                         #left = demande_lue - offre

                if left_ask > 0:                                                #si il manque encore de l'énergie à la maison
                    l = str(left_ask).encode()
                    self.mq_demande.send(l, num_home)
                    self.offre = 0
                    print("manque de l'énergie")
                elif left_ask < 0:                                           #si il reste de l'énergie à donner
                    l = str(-left_ask).encode()
                    self.mq_offre.send(l, type=self.id)
                    self.offre = -left_ask
                    print("encore de l'énergie à donner")
                else :
                    self.offre = 0
            self.lock.release()
        
        self.barrier_while.wait()

        if (self.trade_policy == 1 and self.offre > 0):
            m, t = self.mq_offre.receive(type=self.id)
            print(f'remove : {self.offre}')

        self.barrier_act.wait()

        if self.id == 1:
            res = 0
            while self.mq_demande.current_messages:
                (r, t) = self.mq_demande.receive()
                result = int(r.decode())
                res += result
            print("Demande:", res)
            
            res = 0
            while self.mq_offre.current_messages:
                (r, t) = self.mq_offre.receive()
                result = int(r.decode())
                res += result
            print("Vend:", res)

if __name__ == "__main__":
    num_homes = 10
    barrier_init = Barrier(num_homes)
    barrier_boucle = Barrier(num_homes)
    barrier_act = Barrier(num_homes)
    lock = Lock()
    key_ask = 771
    key_give = 770
    mq_ask = sysv_ipc.MessageQueue(key_ask, sysv_ipc.IPC_CREAT)
    mq_give = sysv_ipc.MessageQueue(key_give, sysv_ipc.IPC_CREAT)

    shared_memory = Array('i', [0])
    shared_memory[0] = 40

    home_processes = [Home(i+1, mq_give, mq_ask, barrier_init, barrier_boucle, barrier_act, lock, shared_memory) for i in range(num_homes)]

    for home in home_processes:
        home.start()
    for home in home_processes:
        home.join()

    mq_ask.remove()
    mq_give.remove()
