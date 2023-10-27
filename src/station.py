import simpy
from src.vehicle import Vehicle
from src.vehicle_arranger import VehicleArranger

class Station:
    def __init__(self, env: simpy.Environment, position: tuple, charging_time: float, max_concurrent_charging: int, vehicles: VehicleArranger):
        self.charging_time = charging_time
        self.max_concurrent_charging = max_concurrent_charging
    
        self.vehicles = vehicles
        self.env = env

        self.position = position
        self.charging_vehicles = []

    def charge(self, vehicle: Vehicle, now: float):
        try:
            time = self.charging_time * vehicle.capacity_left()
            yield self.env.timeout(time)
            vehicle.fully_charge()
            
            print("Charged vehicle {} in {} seconds".format(vehicle.id, time))
            self.charge_next_vehicle()
        
        except simpy.Interrupt:
            print("Charging interrupted for vehicle {}".format(vehicle.id))
            charged_time = self.env.now - now
            vehicle.charge(charged_time / self.charging_time / vehicle.max_capacity)

        for i in range(len(self.charging_vehicles)):
            if self.charging_vehicles[i][0] == vehicle:
                self.charging_vehicles.pop(i)
                break

    def charge_next_vehicle(self):
        to_charge = self.vehicles.next_vehicle_to_charge()
        if to_charge is not None:
            charging_process = self.charge(to_charge, self.env.now)
            self.charging_vehicles.append((to_charge, charging_process))

    def stop_charging(self):
        for vehicle, process in self.charging_vehicles:
            process.interrupt()

    def start_charging(self):
        for _ in range(self.max_concurrent_charging):
            self.charge_next_vehicle()

    def request_lock(self, vehicle: Vehicle):
        if self.vehicles.lock(vehicle):
            if self.vehicles.need_reschedule():
                self.stop_charging()
                self.start_charging()
            return True
        return False
    
    def request_unlock(self):
        self.stop_charging()
        v = self.vehicles.unlock()
        self.start_charging()
        return v