import random
from multiprocessing import Process, Array
import time

class WeatherSimulator(Process):
    def __init__(self, shared_memory, nb_days, day):
        super().__init__()
        self.shared_memory = shared_memory
        self.temperature = 10 # starting temperature
        self.temp_variation = 6 # temperature variation per update
        self.nb_days = nb_days
        self.day = day

    def run(self):
        for i in range (self.nb_days):
            # update temperature
            self.temperature += random.randint(-self.temp_variation, self.temp_variation)
            if self.temperature < -15:
                self.temperature = -15
            if self.temperature > 40:
                self.temperature = 40
            # update shared memory with current temperature
            self.shared_memory[i] = self.temperature
            print(self.shared_memory[i])

            self.day.wait()
            print(f'day {i} off_________________________________________')

if __name__ == "__main__":
    nb_days = 10
    shared_memory = Array('i', nb_days)

    weather = WeatherSimulator(shared_memory, nb_days)

    weather.start()
    weather.join()

    for i in range (nb_days):
        print(f"Temperature in shared memory: {shared_memory[i]}")
