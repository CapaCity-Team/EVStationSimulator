import simpy
from abc import ABC, abstractmethod
from vehicle import Vehicle

class StationStorage(ABC):
    # Abstract base class representing a station storage for vehicles
    # The station storage is responsible for keeping track of the vehicles available at a station
    # The station storage is also responsible for selecting the next vehicle to charge

    # Note: the station storage is not responsible for charging vehicles
    
    # Warning: the __init__ method requires the following parameters:
    # - env: simpy.Environment
    # - params: dict
    # will always be called with these parameters and only these parameters
    # additional parameters must be added to the params dict

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

    @abstractmethod
    def lock(self, vehicle):
        # Wait for a slot to be available and add the vehicle to the station storage
        # Must be implemented as a generator and yield once
        pass

    @abstractmethod
    def unlock(self, user):
        # Wait for a vehicle to be available and remove it from the station storage
        # Must be implemented as a generator and yield once
        pass

    @abstractmethod
    def count(self):
        # Return the number of vehicles currently stored in the station storage
        pass

    @abstractmethod
    def deploy(self, vehicles: list):
        # Deploy a list of vehicles to the station storage
        # Used in the deployment phase to initialize the station storage
        # Must NOT be implemented as a generator
        pass

    @abstractmethod
    def max_capacity(self):
        # Return the maximum number of vehicles that can be stored in the station storage
        pass

class LIFO(StationStorage):
    # Concrete class implementing a Last In, First Out (LIFO) station storage
    # Vehicles are stored in a list and the last vehicle added is the first to be removed
    # Charging is rescheduled every time a vehicle is added to the station storage
    # The next vehicle to charge is the last vehicle in the list that needs charging
    
    def __init__(self, env: simpy.Environment, params: dict):
        # params: {
        #     "Capacity": int
        # }
        
        self.capacity = params["capacity"]
        
        # Create a store to keep track of the number of available slots
        # The number of items corresponds to the number of occupied slots
        # for example, if there are 2 items in the store then there are 2 occupied slots and capacity - 2 available slots
        self.slots = simpy.Store(env, capacity=self.capacity)
        
        # Create a store to keep track of the number of available vehicles
        # The number of items corresponds to the number of available vehicles
        # for example, if there are 2 items in the store then there are 2 available vehicles
        self.available_vehicles = simpy.Store(env)
        
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
        # Select the last vehicle in the list that needs charging
        for vehicle in [v for v in self.vehicles if v not in charging_vehicles][::-1]:
            if not vehicle.is_charged():
                return vehicle
        return None
    
    def need_reschedule(self, charging_vehicles: list):
        # Called when a vehicle is added to the station storage
        # The battery of the new vehicle isn't full (just used for moving to the station)
        # means that the last vehicle in the list needs to be charged
        # so the charging needs to be rescheduled
        return True
    
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

    def count(self):
        # Return the number of vehicles currently stored in the station storage
        return len(self.vehicles)

    def deploy(self, vehicles: list):
        # Deploy a list of vehicles to the station storage
        # Used in the deployment phase to initialize the station storage
        
        # Add the vehicles to the station storage and use a slot for each vehicle
        for v in vehicles:
            self.vehicles.append(v)
            self.slots.put("vehicle")

        if self.vehicles and self.vehicles[-1].is_charged():
            # If the last vehicle is fully charged then there is an available vehicle
            self.available_vehicles.put("vehicle")

    def max_capacity(self):
        # Return the maximum number of vehicles that can be stored in the station storage
        return self.capacity


class DualStack(StationStorage):
    # Concrete class implementing a Dual Stack station storage
    # Vehicles are stored in two lists, one is used to insert vehicles and the other is used to remove vehicles
    # The lists are swapped when the first list is empty or the second list is full

    def __init__(self, env: simpy.Environment, params: dict):
        # params: {
        #     "stack1_size": int,
        #     "stack2_size": int
        # }

        self.stack1_size = params["stack1_size"]
        self.stack2_size = params["stack2_size"]

        # Create a store to keep track of the number of available slots
        # The number of items corresponds to the number of occupied slots
        # for example, if there are 2 items in the store then there are 2 occupied slots and capacity - 2 available slots
        self.slots = simpy.Store(env, capacity=self.stack1_size + self.stack2_size)

        # Create a store to keep track of the number of available vehicles
        # The number of items corresponds to the number of available vehicles
        # for example, if there are 2 items in the store then there are 2 available vehicles
        self.available_vehicles = simpy.Store(env)

        self.stack1 = []
        self.stack2 = []

        self.insert_stack = self.stack1
        self.remove_stack = self.stack2

    def swap_stacks(self):
        # Swap the insert and remove stacks
        self.insert_stack, self.remove_stack = self.remove_stack, self.insert_stack

        # If the last vehicle in the remove stack is fully charged then there is an available vehicle
        # Otherwise the last vehicle is not available
        if self.remove_stack and self.remove_stack[-1].is_charged():
            if len(self.available_vehicles.items) == 0:
                self.available_vehicles.put("vehicle")
        else:
            if len(self.available_vehicles.items) == 1:
                self.available_vehicles.get()

    def charged(self, vehicle: Vehicle):
        # If the vehicle is the last one in the remove stack then the last slot is charged so is available
        if self.remove_stack and self.remove_stack[-1] == vehicle:
            self.available_vehicles.put("vehicle")

    def next_vehicle_to_charge(self, charging_vehicles: list):
        # first check in the remove stack
        for vehicle in [v for v in self.remove_stack if v not in charging_vehicles][::-1]:
            if not vehicle.is_charged():
                return vehicle
        
        # then check in the insert stack
        for vehicle in [v for v in self.insert_stack if v not in charging_vehicles][::-1]:
            if not vehicle.is_charged():
                return vehicle
            
        return None
    
    def need_reschedule(self, charging_vehicles: list):
        # Called when a vehicle is added to the insert stack
        # The battery of the new vehicle isn't full (just used for moving to the station)
        # means that the last vehicle in the insert stack isn't fully charged
        # so the charging needs to be rescheduled only if there are charging vehicles in the insert stack
        return any([v in charging_vehicles for v in self.insert_stack])

    def count(self):
        # Return the number of vehicles currently stored in the station storage
        return len(self.stack1) + len(self.stack2)
    
    def add_vehicle(self, vehicle: Vehicle):
        # Add the vehicle to the insert stack
        self.insert_stack.append(vehicle)

        # If the insert stack is full then swap the stacks
        size = self.stack1_size if self.insert_stack == self.stack1 else self.stack2_size
        if len(self.insert_stack) == size:
            self.swap_stacks()

    def pop_vehicle(self) -> Vehicle:
        v = self.remove_stack.pop()
        
        if len(self.remove_stack) == 0:
            # If the remove stack is empty then swap the stacks
            self.swap_stacks()
        elif self.remove_stack[-1].is_charged():
            # If the last vehicle in the remove stack is fully charged then there is an available vehicle
            self.available_vehicles.put("vehicle")

        return v
    
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

    def deploy(self, vehicles: list):
        # Deploy a list of vehicles to the station storage
        # Used in the deployment phase to initialize the station storage

        if len(vehicles) > self.stack1_size + self.stack2_size:
            raise ValueError("The number of vehicles to deploy must be less than the capacity of the station storage")
        
        # Add the vehicles to the insert stack and use a slot for each vehicle
        for v in vehicles:
            self.add_vehicle(v)
            self.slots.put("vehicle")

        if self.insert_stack and self.insert_stack[-1].is_charged() and len(self.available_vehicles.items) == 0:
            # If the last vehicle in the insert stack is fully charged then there is an available vehicle
            self.available_vehicles.put("vehicle")

    def max_capacity(self):
        # Return the maximum number of vehicles that can be stored in the station storage
        return self.stack1_size + self.stack2_size