import simpy
from station import Station

class User:
    def __init__(self, env: simpy.Environment, id: int, from_station: Station, to_station: Station):
        self.env = env
        self.id = id
        self.from_station = from_station
        self.to_station = to_station
        self.vehicle = None

    def run(self):
        print("User {} from station {} to station {}".format(self.id, self.from_station.id, self.to_station.id))
        print("User {} requesting vehicle from station {} at {}".format(self.id, self.from_station.id, self.env.now))

        yield from self.from_station.request_unlock(self)
        battery = self.vehicle.battery*100
        print("User {} got vehicle {} with battery {}% from station {} at {}".format(self.id, self.vehicle.id, battery, self.from_station.id, self.env.now))
        
        distance = self.from_station.distance(self.to_station)
        time = self.vehicle.move(distance)
        yield self.env.timeout(time)

        print("User {} with vehicle {} arrived to station {} in {} using {}% battery".format(self.id, self.vehicle.id, self.to_station.id, time, battery-self.vehicle.battery*100))

        print("User {} requesting lock in station {} at {}".format(self.id, self.to_station.id, self.env.now))
        
        yield from self.to_station.request_lock(self.vehicle)
        
        print("User {} locked vehicle {} in station {} at {}".format(self.id, self.vehicle.id, self.to_station.id, self.env.now))
        print("User {} finished".format(self.id))
