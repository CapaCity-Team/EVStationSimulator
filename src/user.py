import simpy
from station import Station

import logging, os

# Obtain a reference to the loggers configured in the main script
logger = logging.getLogger(__name__)
path_result = os.path.join(os.path.dirname(__file__), "../data/simulation_result/result.csv")

class User:
    """
    A class representing a user of the electric station simulation.

    Attributes:
    - env (simpy.Environment): the simulation environment
    - id (int): the user's ID
    - from_station (Station): the station where the user starts
    - to_station (Station): the station where the user wants to go
    - vehicle (Vehicle): the vehicle the user is using
    """

    def __init__(self, env: simpy.Environment, id: int, from_station: Station, to_station: Station):
        self.env = env
        self.id = id
        self.from_station = from_station
        self.to_station = to_station
        self.vehicle = None

    def run(self):
        """
        The main method of the User class, representing the user's actions during the simulation.
        """
        start_time = self.env.now

        logger.info("User {} from station {} to station {}".format(self.id, self.from_station.id, self.to_station.id))
        logger.info("User {} requesting vehicle from station {} at {}".format(self.id, self.from_station.id, self.env.now))

        request_time = self.env.now
        yield from self.from_station.request_unlock(self)
        unlock_time = self.env.now - request_time

        battery = self.vehicle.battery*100
        logger.info("User {} got vehicle {} with battery {}% from station {} at {}".format(self.id, self.vehicle.id, battery, self.from_station.id, self.env.now))

        distance = self.from_station.distance(self.to_station)
        time = self.vehicle.move(distance)
        yield self.env.timeout(time)

        battery_used = battery - self.vehicle.battery*100

        logger.info("User {} with vehicle {} arrived to station {} in {} using {}% battery".format(self.id, self.vehicle.id, self.to_station.id, time, battery_used))

        logger.info("User {} requesting lock in station {} at {}".format(self.id, self.to_station.id, self.env.now))
 
        request_time = self.env.now
        yield from self.to_station.request_lock(self.vehicle)
        lock_time = self.env.now - request_time
        
        logger.info("User {} locked vehicle {} in station {} at {}".format(self.id, self.vehicle.id, self.to_station.id, self.env.now))
        logger.info("User {} finished".format(self.id))

        end_time = self.env.now
        
        # ["User ID", "From Station", "To Station", "Vehicle ID", "Start Time", "End Time", "Unlock Time", "Lock Time", "Distance", "Time Traveling", "Battery Used"]
        print("{},{},{},{},{},{},{},{},{},{},{}".format(self.id, self.from_station.id, self.to_station.id, self.vehicle.id, start_time, end_time, unlock_time, lock_time, distance, time, battery_used),
              file=open(path_result, "a"),
                flush=True)
