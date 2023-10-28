import simpy
from station import Station

class User:
    def __init__(self, env: simpy.Environment, id: int, from_station: Station, to_station: Station):
        self.env = env
        self.id = id
        self.from_station = from_station
        self.to_station = to_station
        self.action = env.process(self.run())

    def run(self):
        print("User {} created".format(self.id))
        print("User {} requesting vehicle from station {}".format(self.id, self.from_station.id))
        
        req_time = self.env.now
        vehicle = yield self.from_station.request_unlock(self)
        
        print("User {} got vehicle {} with battery {} from station {} in {} seconds".format(self.id, vehicle.id, vehicle.battery, self.from_station.id, self.env.now - req_time))
        
        distance = self.from_station.distance(self.to_station)
        time = vehicle.move(distance)
        yield self.env.timeout(time)

        print("User with vehicle {} arrived to station {} in {} seconds".format(vehicle.id, self.to_station.id, time))

        print("User {} requesting lock in station {}".format(self.id, self.to_station.id))
        
        req_time = self.env.now
        yield self.to_station.request_lock(vehicle, self)
        
        print("User {} locked vehicle {} in station {} in {} seconds".format(self.id, vehicle.id, self.to_station.id, self.env.now - req_time))
        print("User {} finished".format(self.id))
