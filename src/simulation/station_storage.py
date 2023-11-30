from environment.env import Environment
from environment.resources import Lock, Slots
from environment.process import Process

from abc import ABC, abstractmethod
from simulation.vehicle import Vehicle

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
    def next_vehicle_to_charge(self, charging_vehicles: list):
        pass

    @abstractmethod
    def need_reschedule(self):
        # Check if the station storage needs to reschedule the charging of vehicles
        pass
    
    @abstractmethod
    def request_lock(self, process: Process):
        # Wait for a slot to be available
        pass
    
    @abstractmethod
    def lock(self, vehicle: Vehicle):
        # add the vehicle to the station storage
        pass
    
    @abstractmethod
    def request_unlock(self, process: Process):
        # Wait for a vehicle to be available
        pass
    
    @abstractmethod
    def unlock(self) -> Vehicle:
        # return the available vehicle
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
    
    def __init__(self, env: Environment, params: dict):
        # params: {
        #     "Capacity": int
        # }
        
        self.capacity = params["capacity"]

        self.slots = Slots(env, capacity=self.capacity)
        
        self.available_vehicles = Lock(env)
        
        self.vehicles = []

    def charged(self, vehicle: Vehicle):
        # If the vehicle is the last one in the list then the last slot is charged so is available
        if self.vehicles and self.vehicles[-1] == vehicle:
            self.available_vehicles.release()    

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
    
    def request_lock(self, process):
        # Wait for a slot to be available
        return self.slots.request(process)

    def lock(self, vehicle: Vehicle):
        self.vehicles.append(vehicle)

        if vehicle.is_charged():
            # If the vehicle is fully charged then the last slot is available
            self.available_vehicles.release()
        else:
            # If the vehicle is not fully charged then the last slot is not available
            self.available_vehicles.block() 

    def request_unlock(self, process):
        # Wait for a vehicle to be available
        return self.available_vehicles.request(process)
    
    def unlock(self) -> Vehicle:
        v = self.vehicles.pop()
        # return true if some process is waiting for a slot
        if not self.slots.release():
            # if some process is waiting for a slot then the last slot is not available
            # If the last slot is fully charged then there is an available vehicle
            if self.vehicles and self.vehicles[-1].is_charged():
                self.available_vehicles.release()
        return v

    def count(self):
        # Return the number of vehicles currently stored in the station storage
        return len(self.vehicles)

    def deploy(self, vehicles: list):
        # Deploy a list of vehicles to the station storage
        # Used in the deployment phase to initialize the station storage
        
        # Add the vehicles to the station storage and use a slot for each vehicle
        for v in vehicles:
            self.vehicles.append(v)

        if self.vehicles and self.vehicles[-1].is_charged():
            # If the last vehicle is fully charged then there is an available vehicle
            self.available_vehicles.release()

        self.slots.initial(self.capacity - len(vehicles))

    def max_capacity(self):
        # Return the maximum number of vehicles that can be stored in the station storage
        return self.capacity

class DualStack(StationStorage):
    # Concrete class implementing a Dual Stack station storage
    # Vehicles are stored in two lists, one is used to insert vehicles and the other is used to remove vehicles
    # The lists are swapped when the first list is empty or the second list is full

    def __init__(self, env: Environment, params: dict):
        # params: {
        #     "stack1_size": int,
        #     "stack2_size": int
        # }

        self.stack1_size = params["stack1_size"]
        self.stack2_size = params["stack2_size"]

        # The number of items corresponds to the number of occupied slots
        # for example, if there are 2 items in the store then there are 2 occupied slots and capacity - 2 available slots
        self.slots = Slots(env, capacity=self.stack1_size + self.stack2_size)

        # locked when the last slot is not available
        self.available_vehicles = Lock(env)

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
            self.available_vehicles.release()
        else:
            self.available_vehicles.block()

    def charged(self, vehicle: Vehicle):
        # If the vehicle is the last one in the remove stack then the last slot is charged so is available
        if self.remove_stack and self.remove_stack[-1] == vehicle:
            self.available_vehicles.release()

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
    
    def request_lock(self, process: Process):
        # Wait for a slot to be available
        return self.slots.request(process)

    def lock(self, vehicle: Vehicle):
        # add the vehicle to the station storage
        self.insert_stack.append(vehicle)

        # If the insert stack is full then swap the stacks
        size = self.stack1_size if self.insert_stack == self.stack1 else self.stack2_size
        if (len(self.insert_stack) == size and len(self.stack1) + len(self.stack2) < self.max_capacity()) or len(self.remove_stack) == 0:
            self.swap_stacks()

    def request_unlock(self, process: Process):
        # Wait for a vehicle to be available
        return self.available_vehicles.request(process)

    def unlock(self) -> Vehicle:
        # return the available vehicle
        v = self.remove_stack.pop()
        
        self.slots.release()
        
        if len(self.remove_stack) == 0:
            if len(self.insert_stack) == 0:
                # If both stacks are empty then there are no available vehicles
                self.available_vehicles.block()
            else:
                # If the remove stack is empty then swap the stacks
                self.swap_stacks()
        elif self.remove_stack[-1].is_charged():
            # If the last vehicle in the remove stack is fully charged then there is an available vehicle
            self.available_vehicles.release()

        return v

    def deploy(self, vehicles: list):
        # Deploy a list of vehicles to the station storage
        # Used in the deployment phase to initialize the station storage
        # divide the vehicles in the two stacks
        # the most full stack is the remove stack
        # the other stack is the insert stack

        if len(vehicles) > self.stack1_size + self.stack2_size:
            raise ValueError("The number of vehicles to deploy must be less than the capacity of the station storage")

        self.stack1 = vehicles[:self.stack1_size]
        self.stack2 = vehicles[self.stack1_size:]

        self.remove_stack = self.stack1
        self.insert_stack = self.stack2

        self.slots.initial(self.stack1_size + self.stack2_size - len(vehicles))

        if self.remove_stack and self.remove_stack[-1].is_charged():
            # If the last vehicle in the remove stack is fully charged then there is an available vehicle
            self.available_vehicles.release()

    def max_capacity(self):
        # Return the maximum number of vehicles that can be stored in the station storage
        return self.stack1_size + self.stack2_size

