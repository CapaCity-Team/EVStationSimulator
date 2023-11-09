import simpy
from vehicle import Vehicle
from station_storage import StationStorage

import logging

# Obtain a reference to the logger configured in the main script
logger = logging.getLogger(__name__)

class Station:
    def __init__(self, env: simpy.Environment, station_id: int, position: tuple, charging_time: float, max_concurrent_charging: int, vehicles: StationStorage):
        self.id = station_id
        
        self.charging_time = charging_time
        self.max_concurrent_charging = max_concurrent_charging
    
        self.vehicles = vehicles
        self.env = env

        self.position = position
        self.charging_vehicles = {}

    def charge(self, vehicle: Vehicle, now: float):
        # Process for charging a vehicle for a specified amount of time
        try:
            logger.info("Charging vehicle {} with battery {}% in station {}".format(vehicle.id, vehicle.battery*100, self.id))

            # Calculate the time needed to fully charge the vehicle
            time = self.charging_time * vehicle.capacity_left()
            
            yield self.env.timeout(time)
            
            vehicle.fully_charge()

            logger.info("Charged vehicle {} in {} unit of time".format(vehicle.id, time))

            # Notify the station storage that the vehicle is fully charged
            self.vehicles.charged(vehicle)
            
            # Charge the next vehicle in the queue
            self.charge_next_vehicle()
        
        except simpy.Interrupt:
            logger.info("Charging interrupted for vehicle {} at {}".format(vehicle.id, self.env.now))
            
            # Calculate the time the vehicle has been charging
            charged_time = self.env.now - now
            before = vehicle.battery
            vehicle.charge(charged_time / self.charging_time / vehicle.max_capacity)
            logger.info("Charged vehicle {} of {}% in station {}".format(vehicle.id, (vehicle.battery-before)*100, self.id))

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
        if self.vehicles.need_reschedule():
            self.stop_charging()
            self.start_charging()
    
    def request_unlock(self, user):
        # Request a vehicle from the station
        yield from self.vehicles.unlock(user)
    
    def distance(self, station):
        # Calculate the Euclidean distance between two stations
        return ((self.position[0] - station.position[0])**2 + (self.position[1] - station.position[1])**2)**0.5
    
    def add_vehicle(self, vehicle: Vehicle):
        # used in deployment phase
        self.vehicles.add_vehicle(vehicle)