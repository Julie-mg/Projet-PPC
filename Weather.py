import random
from multiprocessing import Process, Array

class WeatherSimulator(Process):
    def __init__(self, shared_memory, nb_days, temp_variation, day):
        super().__init__()
        self.shared_memory = shared_memory
        self.temp_variation = temp_variation # temperature variation per update
        self.nb_days = nb_days
        self.day = day

    def run(self):
        self.temperature = random.randrange(0,30)
        for i in range (self.nb_days):
            print(f'------- Start of day {i} -------\n')
            # update temperature
            self.temperature += random.randint(-self.temp_variation, self.temp_variation)
            if self.temperature < -15:
                self.temperature = -15
            if self.temperature > 40:
                self.temperature = 40
            # update shared memory with current temperature
            self.shared_memory[i] = self.temperature
            print(f'Temperature today : {self.shared_memory[i]}\n')

            self.day.wait()
            print(f'\n------- End of day {i} -------\n')
