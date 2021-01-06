from Parking_sim.charging_station import ChargingStation
from Parking_sim.model import Model, lg
import simpy

from datetime import datetime

start_time = datetime.now()
env = simpy.Environment()
charging_station = ChargingStation(id=1, env=env, power=10/60, Number_of_chargers=10)

# Run simulation
sim = Model(env, charging_station=charging_station, simulation_time=1440 * 0.5)
env.process(sim.request_generation())
env.process(sim.run())
env.process(sim.obs_CS(charging_station=charging_station))
env.run(until=sim.simulation_time)

#sim.save_results()
end_time = datetime.now()
print('Duration: {}'.format(end_time - start_time))
'''except:
episode = episode'''

