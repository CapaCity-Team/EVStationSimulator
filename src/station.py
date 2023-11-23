import simpy
from vehicle import Vehicle
from station_storage import StationStorage
from utils import log

class Station:
    def __init__(self, env: simpy.Environment, station_id: int, position: tuple, capacity_per_time: float, max_concurrent_charging: int, vehicles: StationStorage):
        self.id = station_id
        
        self.capacity_per_time = capacity_per_time
        self.max_concurrent_charging = max_concurrent_charging
    
        self.vehicles = vehicles
        self.env = env

        self.position = position
        self.charging_vehicles = {}

    def charge(self, vehicle: Vehicle, now: float):
        # Process for charging a vehicle for a specified amount of time
        try:
            log("Charging vehicle {} with battery {}% in station {}".format(vehicle.id, vehicle.battery*100, self.id))

            # Calculate the time needed to fully charge the vehicle
            time = vehicle.capacity_used() / self.capacity_per_time
            
            yield self.env.timeout(time)
            
            vehicle.fully_charge()

            log("Charged vehicle {} in {} unit of time".format(vehicle.id, time))

            # Notify the station storage that the vehicle is fully charged
            self.vehicles.charged(vehicle)
            
            # Charge the next vehicle in the queue
            self.charge_next_vehicle()
        
        except simpy.Interrupt:
            log("Charging interrupted for vehicle {} at {}".format(vehicle.id, self.env.now))
            
            # Calculate the time the vehicle has been charging
            charged_time = self.env.now - now
            before = vehicle.battery
            vehicle.charge(charged_time * self.capacity_per_time / vehicle.max_capacity)
            log("Charged vehicle {} of {}% in station {}".format(vehicle.id, (vehicle.battery-before)*100, self.id))

        # Remove the vehicle from the list of charging vehicles
        del self.charging_vehicles[vehicle]

    def charge_next_vehicle(self):
        # Charge the next vehicle in the queue if there is one
        to_charge = self.vehicles.next_vehicle_to_charge(list(self.charging_vehicles.keys()))
        if to_charge is not None:
            charging_process = self.env.process(self.charge(to_charge, self.env.now))
            self.charging_vehicles[to_charge] = charging_process

    def stop_charging(self):
        # Interrupt the charging process for all vehicles
        for vehicle, process in self.charging_vehicles.items():
            process.interrupt()

    def start_charging(self):
        # Start charging the next vehicles up to the maximum number of concurrent charging
        for _ in range(self.max_concurrent_charging):
            self.charge_next_vehicle()

    def request_lock(self, vehicle: Vehicle):
        # Request a vehicle to the station
        yield from self.vehicles.lock(vehicle)
        # Check if the station needs to reschedule charging 
        
        log("Station {} has {} vehicles at {}".format(self.id, self.vehicles.count(), self.env.now))
        assert self.vehicles.count() <= self.vehicles.max_capacity(), "Station {} has {} vehicles".format(self.id, self.vehicles.count())
        
        if len(self.charging_vehicles) < self.max_concurrent_charging or self.vehicles.need_reschedule(self.charging_vehicles):
            self.stop_charging()
            self.start_charging()
    
    def request_unlock(self, user):
        # Request a vehicle from the station
        yield from self.vehicles.unlock(user)

        log("Station {} has {} vehicles at {}".format(self.id, self.vehicles.count(), self.env.now))
        assert self.vehicles.count() <= self.vehicles.max_capacity(), "Station {} has {} vehicles".format(self.id, self.vehicles.count())
    
    def distance(self, station):
        # Calculate the Euclidean distance between two stations
        return ((self.position[0] - station.position[0])**2 + (self.position[1] - station.position[1])**2)**0.5
    
    def deploy(self, vehicles: list):
        # used in deployment phase
        self.vehicles.deploy(vehicles)