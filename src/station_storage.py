import simpy
from abc import ABC, abstractmethod
from charging_policy import ChargingPolicy
from vehicle import Vehicle

class StationStorage(ABC):
    def __init__(self, env: simpy.Environment, capacity: int, policy: ChargingPolicy):
        self.capacity = capacity
        self.policy = policy
        
        self.slots = simpy.Store(env, capacity)
        self.available_vehicles = simpy.Store(env)

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
        yield self.slots.put("vehicle")
        self.add_vehicle(vehicle)

    def unlock(self, user):
        yield self.available_vehicles.get()
        self.slots.get()
        v = self.pop_vehicle()
        user.vehicle = v

class StationStorageLIFO(StationStorage):
    def __init__(self, env: simpy.Environment, capacity: int, policy: ChargingPolicy):
        super().__init__(env, capacity, policy)
        self.vehicles = []

    def charged(self, vehicle: Vehicle):
        if self.vehicles and self.vehicles[-1] == vehicle:
            self.available_vehicles.put("vehicle")

    def add_vehicle(self, vehicle: Vehicle):
        self.vehicles.append(vehicle)
        if vehicle.is_charged():
            if len(self.available_vehicles.items) == 0:
                self.available_vehicles.put("vehicle")
        else:
            if len(self.available_vehicles.items) == 1:
                self.available_vehicles.get()        

    def pop_vehicle(self) -> Vehicle:
        v = self.vehicles.pop()
        if self.vehicles and self.vehicles[-1].is_charged():
            self.available_vehicles.put("vehicle")
        return v

    def next_vehicle_to_charge(self, charging_vehicles: list):
        return self.policy.next_vehicle_to_charge([v for v in self.vehicles if v not in charging_vehicles])
    
    def need_reschedule(self):
        return True
