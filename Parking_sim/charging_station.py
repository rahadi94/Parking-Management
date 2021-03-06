import simpy
import pandas as pd

class ChargingStation:

    def __init__(self, id, env, power, Number_of_chargers):
        self.env = env
        self.plugs = simpy.PriorityResource(self.env, capacity=Number_of_chargers)
        self.id = id
        self.power = power  # kwh/min
        self.queue = []
        # self.position = self.location.find_zone(zones)
