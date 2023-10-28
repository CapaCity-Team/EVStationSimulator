import simpy
from abc import ABC, abstractmethod
from src.charging_policy import ChargingPolicy
from src.vehicle import Vehicle

class StationStorage(ABC):
    def __init__(self, capacity: int, policy: ChargingPolicy):
        self.capacity = capacity
        self.policy = policy
        
        self.slots = simpy.Resource(capacity, init=capacity)
        self.available_vehicles = simpy.Container(capacity, init=0)

    @abstractmethod
    def charged(self, vehicle: Vehicle):
        pass

    @abstractmethod
    def add_vehicle(self, vehicle: Vehicle):
        pass

    @abstractmethod
    def pop_vehicle(self) -> Vehicle:
        pass

    @abstractmethod
    def next_vehicle_to_charge(self, charging_vehicles: list):
        pass

    @abstractmethod
    def need_reschedule(self):
        pass

    def lock(self, vehicle):
        self.slots.request()
        self.add_vehicle(vehicle)

    def unlock(self):
        self.available_vehicles.get(1)
        v = self.pop_vehicle()
        self.slots.release()
        return v

    def zero_out_available(self):
        level = self.available_vehicles.level
        self.available_vehicles.get(level)

class StationStorageLIFO(StationStorage):
    def __init__(self, capacity: int, policy: ChargingPolicy):
        super().__init__(capacity, policy)
        self.vehicles = []

    def charged(self, vehicle: Vehicle):
        if self.vehicles and self.vehicles[-1] == vehicle:
            self.available_vehicles.put(1)

    def add_vehicle(self, vehicle: Vehicle):
        self.vehicles.append(vehicle)
        self.zero_out_available()
        if vehicle.is_charged():
            self.available_vehicles.put(1)

    def pop_vehicle(self) -> Vehicle:
        v = self.vehicles.pop()
        if self.vehicles and self.vehicles[-1].is_charged():
            self.available_vehicles.put(1)
        return v

    def next_vehicle_to_charge(self, charging_vehicles: list):
        return self.policy.next_vehicle_to_charge([v for v in self.vehicles if v not in charging_vehicles])
    
    def need_reschedule(self):
        return True
