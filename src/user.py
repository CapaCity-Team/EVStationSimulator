from simulation.constants import timeout

from station import Station
from utils import get_directory_path, log
import os

class User:
    env = None
    def __init__(self, id: int, from_station: Station, to_station: Station, velocity: float):
        self.id = id
        self.from_station = from_station
        self.to_station = to_station
        self.velocity = velocity
        self.process = None

    def run(self):
        if self.id == 2:
            pass

        start_time = self.env.now()

        log("User {} from station {} to station {}".format(self.id, self.from_station.id, self.to_station.id))
        log("User {} requesting vehicle from station {} at {}".format(self.id, self.from_station.id, self.env.now()))

        request_time = self.env.now()
        
        yield self.from_station.request_unlock(self.process)
        vehicle = self.from_station.unlock()
        
        unlock_time = self.env.now() - request_time

        battery = vehicle.battery*100
        assert battery == 100, "User {} got vehicle {} with battery {}% from station {} at {}".format(self.id, vehicle.id, battery, self.from_station.id, self.env.now)
        log("User {} got vehicle {} with battery {}% from station {} at {}".format(self.id, vehicle.id, battery, self.from_station.id, self.env.now()))

        distance = self.from_station.distance(self.to_station)
        vehicle.move(distance)
        
        time = distance / self.velocity
        
        yield timeout(time)

        battery_used = battery - vehicle.battery*100

        log("User {} with vehicle {} arrived to station {} in {} using {}% battery".format(self.id, vehicle.id, self.to_station.id, time, battery_used))

        log("User {} requesting lock in station {} at {}".format(self.id, self.to_station.id, self.env.now()))
 
        request_time = self.env.now()
        
        yield self.to_station.request_lock(self.process)

        self.to_station.lock(vehicle)
        
        lock_time = self.env.now() - request_time


        log("User {} locked vehicle {} in station {} at {}".format(self.id, vehicle.id, self.to_station.id, self.env.now()))
        log("User {} finished".format(self.id))

        total_time = self.env.now() - start_time
        if total_time <= 0:
            print("User {} total time is less or equal to 0".format(self.id))

        with open(os.path.join(get_directory_path(),"result.csv"), "a") as file:
            # ["User ID", "Start Time", "From Station", "To Station", "Vehicle ID", "Unlock Time", "Lock Time", "Total Time", "Battery Used", "Distance", "Velocity"]
            print("{},{},{},{},{},{},{},{},{},{},{}".format(self.id, start_time, self.from_station.id, self.to_station.id, vehicle.id, unlock_time, lock_time, total_time, battery_used, distance, self.velocity),
                file=file,
                flush=True)
