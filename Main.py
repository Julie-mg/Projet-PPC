from multiprocessing import Barrier, Lock, Array
import sysv_ipc
from Home import Home
from Market import Market
from Weather import WeatherSimulator
import time

if __name__ == "__main__":
    num_homes = 10
    nb_days = 10
    barrier_init = Barrier(num_homes)
    barrier_boucle = Barrier(num_homes)
    barrier_act = Barrier(num_homes)
    barrier_day = Barrier(num_homes+2)
    lock = Lock()
    key_ask = 771
    key_give = 770
    mq_ask = sysv_ipc.MessageQueue(key_ask, sysv_ipc.IPC_CREAT)
    mq_give = sysv_ipc.MessageQueue(key_give, sysv_ipc.IPC_CREAT)
    price = 10
    coeff = [1.1, 0.9]
    nb_days = 10
    barrier_day = Barrier(1)

    shared_memory = Array('i', nb_days)
    
    weather = WeatherSimulator(shared_memory, nb_days, barrier_day)
    weather.start()

    HOST = 'localhost'
    PORT = 17890

    market = Market(price, coeff, nb_days, barrier_day, HOST, PORT)

    market.start()
    print("Market started")

    # Wait for the Market to start listening for connections
    time.sleep(1)

    home_processes = [Home(i+1, mq_give, mq_ask, barrier_init, barrier_boucle, barrier_act, lock, shared_memory, nb_days, barrier_day, HOST, PORT) for i in range(num_homes)]

    for home in home_processes:
        home.start()

    for home in home_processes:
        home.join()

    market.serve = False
    market.join()

    mq_ask.remove()
    mq_give.remove()
    

    