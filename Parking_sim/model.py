import pandas as pd
import numpy as np
import simpy
import random
from Parking_sim.log import lg
from Parking_sim.read import charging_cost
from Parking_sim.vehicle import Vehicle


class Model:

    def __init__(self, env, charging_station, simulation_time):
        self.t = []
        self.charging_station = charging_station
        self.trip_list = []
        self.waiting_list = []
        self.simulation_time = simulation_time
        self.env = env
        self.request_start = env.event()
        self.demand_generated = []
        self.utilization = []
        self.vehicle_id = None

    def charge_task(self, vehicle):
        prio = int((vehicle.charge_state - vehicle.charge_state % 10) / 10)
        if isinstance(prio, np.ndarray):
            prio = prio[0]
        req = self.charging_station.plugs.request(priority=prio)
        vehicle.mode = 'queue'
        # the vehicle either starts charging after the queue or interrupt the queue if the departure time is over
        events = yield req | self.env.timeout(vehicle.departure_time)
        if req in events:
            lg.info(f'Vehicle {vehicle.id} starts charging at {self.env.now}')
            vehicle.t_start_charging = self.env.now
            vehicle.mode = 'charging'
            charging = self.env.process(self.charge(self.charging_station, vehicle))
            # charging process can be interrupted
            yield charging | vehicle.charging_interruption
            self.charging_station.plugs.release(req)
            req.cancel()

            # if it interrupts before finishing the charging event, we need to update everything
            if not charging.triggered:
                charging.interrupt()
                lg.info(f'Vehicle {vehicle.id} stops charging at {self.env.now}')
                return

        # if it interrupts the queue before the charging is triggered, we need to update everything
        else:
            lg.info(f'vehicle {vehicle.id} interrupts the queue')
            req.cancel()
            self.charging_station.plugs.release(req)
            return

    def charge(self, charging_station, vehicle):
        vehicle.charging(self.charging_station)
        vehicle.t_arriving_CS = self.env.now
        # the vehicle either finishes the charging process or interrupts it
        try:
            yield self.env.timeout(vehicle.charge_duration)
            vehicle.finish_charging(charging_station)
            vehicle.charging_end.succeed()
            vehicle.charging_end = self.env.event()
        except simpy.Interrupt:
            old_SOC = vehicle.charge_state
            vehicle.charge_state += float((charging_station.power * (float(self.env.now) - vehicle.t_start_charging)) \
                                          / (vehicle.battery_capacity / 100))

            for j in range(0, 24):
                if j * 60 <= self.env.now % 1440 <= (j + 1) * 60:
                    h = j
            vehicle.reward['charging'] += (vehicle.charge_state - old_SOC) / 100 * 50 * charging_cost[h] / 100
            if isinstance(vehicle.reward['charging'], np.ndarray):
                vehicle.reward['charging'] = vehicle.reward['charging'][0]
            vehicle.costs['charging'] += (vehicle.charging_threshold - vehicle.charge_state) * \
                                         charging_cost[h] / 100
            lg.info(f'Warning!!!Charging state of vehicle {vehicle.id} is {vehicle.charge_state} at {self.env.now} ')

    def request_generation(self):
        j = 0
        while True:
            j += 1
            time = self.env.now
            demand_list = np.random.rand(24) * 1000
            for i in range(0, 24):
                if i * 60 <= time % 1440 <= (i + 1) * 60:
                    demand = demand_list[i]
            vehicle = Vehicle(id=j, env=self.env, capacity=50, charge_state=random.randint(15, 90),
                              mode='idle', departure_time=random.randint(60, 500))
            vehicle.SOC_preference = random.randint(vehicle.charge_state, 100)
            interarrival = random.expovariate(demand/60)
            yield self.env.timeout(interarrival)
            self.request_start.succeed(value=vehicle)
            self.vehicle = vehicle
            self.request_start = self.env.event()
            lg.info(f'Request {vehicle.id} is received at {self.env.now}')
            vehicle.t_arriving_CS = self.env.now

    def run(self):
        while True:
            yield self.request_start
            self.env.process(self.charge_task(self.vehicle))

    def obs_CS(self, charging_station):
        while True:
            charging_station.queue.append([charging_station.plugs.count, len(charging_station.plugs.queue)])
            yield self.env.timeout(1)

    def save_results(self):

        '''pd_cs = pd.DataFrame()
        for c in self.charging_station:
            pd_cs = pd_cs.append([c.queue])
        pd_cs.to_csv(f'results/CSs{episode}.csv')'''
        pass

