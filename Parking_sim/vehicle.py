from Parking_sim.location import find_zone
import numpy as np

from Parking_sim.log import lg
from Parking_sim.read import charging_cost


class Vehicle:
    speed = 0.5  # km/min
    parking_cost = 5

    def __init__(self, id, env, capacity, charge_state, mode, departure_time):
        self.env = env
        self.info = dict()
        self.info['SOC'] = []
        self.info['location'] = []
        self.info['position'] = []
        self.info['mode'] = []
        self.id = id
        self.mode = mode
        self.battery_capacity = capacity
        self.charge_state = charge_state
        self.t_start_charging = None
        self.t_arriving_CS = None
        self.departure_time = departure_time
        self.costs = dict()
        self.charging_interruption = env.event()
        self.queue_interruption = env.event()
        self.charging_start = env.event()
        self.charging_end = env.event()
        self.charging_count = 0

    def SOC_consumption(self, distance):
        return float(distance * self.fuel_consumption * 100.0 / self.battery_capacity)

    def charging(self, charging_station):
        self.mode = 'charging'
        charge_duration = (((self.SOC_preference - self.charge_state) * self.battery_capacity / 100)
                                / charging_station.power)
        self.charge_duration = min(charge_duration, self.departure_time -
                                   (self.t_start_charging - self.t_arriving_CS))
        lg.info(f'Vehicle {self.id} enters the station at {self.env.now}')

    def finish_charging(self, charging_station):
        self.mode = 'idle'
        for j in range(0, 24):
            if j * 60 <= self.env.now % 1440 <= (j + 1) * 60:
                h = j
        # self.costs['charging'] += (self.charging_threshold - self.charge_state) / 100 * 50 * charging_cost[h]/100
        self.charge_state += (charging_station.power * self.charge_duration) / (self.battery_capacity / 100)
        lg.info(f'Finished charging, Charging state of vehicle {self.id} is {self.charge_state} at {self.env.now}')

    '''def discharging(self, charging_station):
        self.mode = 'discharging'
        self.charge_state -= self.SOC_consumption(self.distance_to_CS)
        self.discharging_threshold = 50
        discharge_rate = charging_station.power
        self.discharge_duration = (((self.charge_state - self.discharging_threshold) * self.battery_capacity / 100)
                                / discharge_rate)
        self.location = charging_station.location
        lg.info(f'Vehicle {self.id} enters the station at {self.env.now}')

    def finish_discharging(self, charging_station):
        self.mode = 'idle'
        for j in range(0, 24):
            if j * 60 <= self.env.now % 1440 <= (j + 1) * 60:
                h = j
        self.reward['revenue'] += (self.charge_state - self.discharging_threshold) / 100 * 50 * charging_cost[h]/100
        if isinstance(self.reward['charging'], np.ndarray):
            self.reward['revenue'] = self.reward['revenue'][0]
        self.charge_state -= (charging_station.power * self.discharge_duration) / (self.battery_capacity / 100)
        lg.info(f'Finished discharging, Charging state of vehicle {self.id} is {self.charge_state} at {self.env.now}')'''
