import time
from weather import WeatherSimulator
#from market import Market
from home4 import Home
from multiprocessing import Process, Barrier, Lock, Array
import sysv_ipc
import random

if __name__ == "__main__":
    num_homes = 10
    barrier_init = Barrier(num_homes)
    barrier_boucle = Barrier(num_homes)
    barrier_act = Barrier(num_homes)
    key_ask = 771
    key_give = 770
    mq_ask = sysv_ipc.MessageQueue(key_ask, sysv_ipc.IPC_CREAT)
    mq_give = sysv_ipc.MessageQueue(key_give, sysv_ipc.IPC_CREAT)
    lock = Lock()

    shared_memory = Array('i', [0])
    weather = WeatherSimulator(shared_memory)
    #market = Market(100, shared_memory, [0.001, 0.01])

    home_processes = [Home(i+1, mq_give, mq_ask, barrier_init, barrier_boucle, barrier_act, lock) for i in range(num_homes)]

    weather.start()
    weather.join()

    print(f"Temperature in shared memory: {shared_memory[0]}")
    
    for home in home_processes:
        home.start()
    for home in home_processes:
        home.join()

    #while True:
        #market.update_price()
        #time.sleep(5) # wait for 1 minute before updating again
