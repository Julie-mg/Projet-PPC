# Projet-PPC

The goal of this programming project is to design and implement a multi-process and multithread simulation in Python with multiple ways of communication between them. The program simulates an energy market where energy-producing and consuming homes, weather conditions, and random events contribute to the evolution of energy price over time.

## Requirements
To run the application, you will need to have Python3 and the following libraries installed:

* matplotlib
* sysv-ipc

## Installation
Download all the files of this project in the same repository.
Install matplotlib and sysv-ipc libraries using the following commands in the terminal:

* `python3 -m pip install matplotlib --user`
* `pip install sysv-ipc`

Open a terminal in the directory of the files and type the following command to start the simulation:

`python3 Main.py`

## Classes
Homes: Each home process has a unique ID and randomly takes a trade policy (0: Always sell, 1: Always give, 2: Sell if no takers). At the time of their creation and each day, the homes are assigned two random ints that define their production and consumption of energy, which vary according to the temperature of the day. The offer represents the difference between these two values. If it's negative, the home will look for a way to gain energy, and if it's positive, the home will get rid of it according to its trade policy.

Weather: This process is the first to start each day, it fills a shared memory with today's temperature.

External: This process is started by the Market. It sends signals to its parent (the Market) if an event occurs.

Market: The energy price varies according to events, and energy asks and sells from the Home classes. The energy price starts at 17 cents/kWatt. This process starts threads that take care of transactions from the Homes to the Market.

Main: This process starts the other processes. In this class, you can change all the values of the variables and constants used in the program.

## Communication
Homes communicate with each other using message queues and exchange their energy freely before selling it to or buying it from the Market using sockets.
Weather updates a shared memory with the temperature, and the Homes read it.
External process, a child of the Market process, sends signal events to its parent, each signal corresponding to an event.

## Functionality
The user can try to modify the variables in the Main.py to show how each number can influence the price of the energy over time (number of houses, number of days of the simulation, initial price of the energy...)
