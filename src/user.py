import simpy
from station import Station
from utils import get_directory_path

import logging, os

# Obtain a reference to the loggers configured in the main script
logger = logging.getLogger(__name__)

class User:
    env = None
    def __init__(self, id: int, from_station: Station, to_station: Station, velocity: float):
        self.id = id
        self.from_station = from_station
        self.to_station = to_station
        self.velocity = velocity
        self.vehicle = None

    def run(self):
        start_time = self.env.now

        logger.info("User {} from station {} to station {}".format(self.id, self.from_station.id, self.to_station.id))
        logger.info("User {} requesting vehicle from station {} at {}".format(self.id, self.from_station.id, self.env.now))

        request_time = self.env.now
        yield from self.from_station.request_unlock(self)
        unlock_time = self.env.now - request_time

        battery = self.vehicle.battery*100
        logger.info("User {} got vehicle {} with battery {}% from station {} at {}".format(self.id, self.vehicle.id, battery, self.from_station.id, self.env.now))

        distance = self.from_station.distance(self.to_station)
        self.vehicle.move(distance)
        
        time = distance / self.velocity
        
        yield self.env.timeout(time)

        battery_used = battery - self.vehicle.battery*100

        logger.info("User {} with vehicle {} arrived to station {} in {} using {}% battery".format(self.id, self.vehicle.id, self.to_station.id, time, battery_used))

        logger.info("User {} requesting lock in station {} at {}".format(self.id, self.to_station.id, self.env.now))
 
        request_time = self.env.now
        yield from self.to_station.request_lock(self.vehicle)
        lock_time = self.env.now - request_time
        
        logger.info("User {} locked vehicle {} in station {} at {}".format(self.id, self.vehicle.id, self.to_station.id, self.env.now))
        logger.info("User {} finished".format(self.id))

        total_time = self.env.now - start_time
        if total_time <= 0:
            print("User {} total time is 0".format(self.id))


        with open(os.path.join(get_directory_path(),"result.csv"), "a") as file:
            # ["User ID", "Start Time", "From Station", "To Station", "Vehicle ID", "Unlock Time", "Lock Time", "Total Time", "Battery Used", "Distance", "Velocity"]
            print("{},{},{},{},{},{},{},{},{},{},{}".format(self.id, start_time, self.from_station.id, self.to_station.id, self.vehicle.id, unlock_time, lock_time, total_time, battery_used, distance, self.velocity),
                file=file,
                flush=True)
