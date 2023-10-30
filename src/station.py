import simpy
from vehicle import Vehicle
from station_storage import StationStorage

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
        try:
            print("Charging vehicle {} with battery {} in station {}".format(vehicle.id, vehicle.battery, self.id))

            time = self.charging_time * vehicle.capacity_left()
            yield self.env.timeout(time)
            vehicle.fully_charge()

            print("Charged vehicle {} in {} seconds".format(vehicle.id, time))

            self.vehicles.charged(vehicle)
            
            self.charge_next_vehicle()
        
        except simpy.Interrupt:
            print("Charging interrupted for vehicle {} at {}".format(vehicle.id, self.env.now))
            charged_time = self.env.now - now
            before = vehicle.battery
            vehicle.charge(charged_time / self.charging_time / vehicle.max_capacity)
            print("Charged vehicle {} of {}% in station {}".format(vehicle.id, (vehicle.battery-before)*100, self.id))

        del self.charging_vehicles[vehicle]

    def charge_next_vehicle(self):
        to_charge = self.vehicles.next_vehicle_to_charge(self.charging_vehicles.keys())
        if to_charge is not None:
            charging_process = self.env.process(self.charge(to_charge, self.env.now))
            self.charging_vehicles[to_charge] = charging_process

    def stop_charging(self):
        for vehicle, process in self.charging_vehicles.items():
            process.interrupt()

    def start_charging(self):
        for _ in range(self.max_concurrent_charging):
            self.charge_next_vehicle()

    def request_lock(self, vehicle: Vehicle):
        self.vehicles.lock(vehicle)
        if self.vehicles.need_reschedule():
            self.stop_charging()
            self.start_charging()
    
    def request_unlock(self) -> Vehicle:
        return self.vehicles.unlock()
    
    def distance(self, station):
        return ((self.position[0] - station.position[0])**2 + (self.position[1] - station.position[1])**2)**0.5