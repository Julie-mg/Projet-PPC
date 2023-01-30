import time
from weather import WeatherSimulator
#from market import Market
from home4 import Home
from multiprocessing import Process, Barrier, Lock, Array
import sysv_ipc
import random
import socket

def handle(connection, address):
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("process-%r" % (address,))
    try:
        logger.debug("Connected %r at %r", connection, address)
        while True:
            data = connection.recv(1024)
            if data == "":
                logger.debug("Socket closed remotely")
                break
            logger.debug("Received data %r", data)
            connection.sendall(data)
            logger.debug("Sent data")
    except:
        logger.exception("Problem handling request")
    finally:
        logger.debug("Closing socket")
        connection.close()

if __name__ == "__main__":
    nb_days = 10

    num_homes = 10
    barrier_init = Barrier(num_homes)
    barrier_boucle = Barrier(num_homes)
    barrier_act = Barrier(num_homes)
    barrier_day = Barrier(num_homes+2)                  # mettre à jour !!!!!!
    key_ask = 771
    key_give = 770
    mq_ask = sysv_ipc.MessageQueue(key_ask, sysv_ipc.IPC_CREAT)
    mq_give = sysv_ipc.MessageQueue(key_give, sysv_ipc.IPC_CREAT)
    lock = Lock()

    HOST = "localhost"
    PORT = 17890

    shared_memory = Array('i', nb_days)
    weather = WeatherSimulator(shared_memory, nb_days, barrier_day)
    #market = Market(100, shared_memory, [0.001, 0.01])

    home_processes = [Home(i+1, mq_give, mq_ask, barrier_init, barrier_boucle, barrier_act, lock, shared_memory, nb_days, barrier_day, HOST, PORT) for i in range(num_homes)]

    weather.start()

    for home in home_processes:
            home.start()

    weather.join()
    for home in home_processes:
        home.join()
    
    for i in range (nb_days):
        print(f"Temperature in shared memory: {shared_memory[i]}")

    #while True:
        #market.update_price()
        #time.sleep(5) # wait for 1 minute before updating again

    #Handler for Ctrl-c interruption
    """except KeyboardInterrupt:
        weather.terminate()
        #market_process.terminate()
        for process in home_processes :
            process.terminate()"""

            
    """while True:
        connection, address = server_socket.accept()
        client_process = Process(target=handle, args=(connection, address))
        client_process.start()"""