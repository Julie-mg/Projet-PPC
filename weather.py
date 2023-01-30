import random
from multiprocessing import Process, Array
import time

class WeatherSimulator(Process):
    def __init__(self, shared_memory):
        super().__init__()
        self.shared_memory = shared_memory
        self.temperature = 10 # starting temperature
        self.temp_variation = 6 # temperature variation per update

    def run(self):
        # update temperature
        self.temperature += random.randint(-1 * self.temp_variation, self.temp_variation)
        if self.temperature < -15:
            self.temperature = -15
        if self.temperature > 40:
            self.temperature = 40
        # update shared memory with current temperature
        self.shared_memory[0] = self.temperature

if __name__ == "__main__":
    shared_memory = Array('i', [0])

    weather = WeatherSimulator(shared_memory)

    weather.start()
    weather.join()

    print(f"Temperature in shared memory: {shared_memory[0]}")
