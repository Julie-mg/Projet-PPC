from multiprocessing import Barrier, Lock, Array
import sysv_ipc
from Home import Home
from Market import Market
from Weather import WeatherSimulator
import time
import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    num_homes = 4
    nb_days = 8
    barrier_init = Barrier(num_homes)
    barrier_boucle = Barrier(num_homes)
    barrier_day = Barrier(num_homes+2)
    lock = Lock()
    key_ask = 771
    key_give = 770
    mq_ask = sysv_ipc.MessageQueue(key_ask, sysv_ipc.IPC_CREAT)
    mq_give = sysv_ipc.MessageQueue(key_give, sysv_ipc.IPC_CREAT)
    price = 0.17
    coeff = [0.1, 0.1]

    HOST = 'localhost'
    PORT = 17890

    shared_memory = Array('i', nb_days)
    shared_memory_price = Array('f', nb_days)
    
    weather = WeatherSimulator(shared_memory, nb_days, barrier_day)
    weather.start()


    market = Market(price, coeff, nb_days, num_homes, barrier_day, HOST, PORT, shared_memory_price)

    market.start()
    print("Market started")

    # Wait for the Market to start listening for connections
    time.sleep(1)

    home_processes = [Home(i+1, mq_give, mq_ask, barrier_init, barrier_boucle, lock, shared_memory, nb_days, barrier_day, HOST, PORT) for i in range(num_homes)]

    for home in home_processes:
        home.start()

    market.join()

    for home in home_processes:
        home.join()

    mq_ask.remove()
    mq_give.remove()

    # Create the price graph
    xpoints = np.array(range(0,nb_days))
    ypoints = np.array(shared_memory_price)

    plt.plot(xpoints, ypoints)
    plt.show()
    

    