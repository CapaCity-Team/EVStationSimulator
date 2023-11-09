import simpy
from abc import ABC, abstractmethod
from charging_policy import ChargingPolicy
from vehicle import Vehicle

class StationStorage(ABC):
    def __init__(self, env: simpy.Environment, policy: ChargingPolicy, params: dict):
        self.capacity = params["Capacity"]
        self.policy = policy
        
        # Create a store to keep track of the number of available slots
        self.slots = simpy.Store(env, self.capacity)
        # Create a store to keep track of the number of available vehicles
        self.available_vehicles = simpy.Store(env)

    @abstractmethod
    def charged(self, vehicle: Vehicle):
        # Notify the station storage that a vehicle has been fully charged
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
        # Check if the station storage needs to reschedule the charging of vehicles
        pass

    def lock(self, vehicle):
        # Wait for a slot to be available and add the vehicle to the station storage
        yield self.slots.put("vehicle")
        self.add_vehicle(vehicle)

    def unlock(self, user):
        # Wait for a vehicle to be available and remove it from the station storage
        yield self.available_vehicles.get()
        self.slots.get()
        v = self.pop_vehicle()
        user.vehicle = v

class StationStorageLIFO(StationStorage):
    def __init__(self, env: simpy.Environment, policy: ChargingPolicy, params: dict):
        super().__init__(env, policy, params)
        self.vehicles = []

    def charged(self, vehicle: Vehicle):
        # If the vehicle is the last one in the list then the last slot is charged so is available
        if self.vehicles and self.vehicles[-1] == vehicle:
            self.available_vehicles.put("vehicle")

    def add_vehicle(self, vehicle: Vehicle):
        self.vehicles.append(vehicle)

        if vehicle.is_charged():
            # If the vehicle is fully charged then the last slot is available
            if len(self.available_vehicles.items) == 0:
                self.available_vehicles.put("vehicle")
        else:
            # If the vehicle is not fully charged then the last slot is not available
            if len(self.available_vehicles.items) == 1:
                self.available_vehicles.get()        

    def pop_vehicle(self) -> Vehicle:
        v = self.vehicles.pop()
        # If the last slot is fully charged then there is an available vehicle
        if self.vehicles and self.vehicles[-1].is_charged():
            self.available_vehicles.put("vehicle")
        return v

    def next_vehicle_to_charge(self, charging_vehicles: list):
        # Select the next vehicle to charge according to the policy
        return self.policy.next_vehicle_to_charge([v for v in self.vehicles if v not in charging_vehicles])
    
    def need_reschedule(self):
        # Called when a vehicle is added to the station storage
        # Always return True because the LIFO policy should always reschedule charging
        return True
