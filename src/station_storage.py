import simpy
from abc import ABC, abstractmethod
from charging_policy import ChargingPolicy
from vehicle import Vehicle

class StationStorage(ABC):
    """
    Abstract base class for a station storage.

    Attributes:
    - capacity (int): the maximum number of vehicles that can be stored in the station.
    - policy (ChargingPolicy): the charging policy used by the station.
    - slots (simpy.Store): a store that represents the slots available for vehicles in the station.
    - available_vehicles (simpy.Store): a store that represents the vehicles available for charging in the station.
    """

    def __init__(self, env: simpy.Environment, capacity: int, policy: ChargingPolicy):
        """
        Initializes a new instance of the StationStorage class.

        Parameters:
        - env (simpy.Environment): the simulation environment.
        - capacity (int): the maximum number of vehicles that can be stored in the station.
        - policy (ChargingPolicy): the charging policy used by the station.
        """
        self.capacity = capacity
        self.policy = policy
        
        self.slots = simpy.Store(env, capacity)
        self.available_vehicles = simpy.Store(env)

    @abstractmethod
    def charged(self, vehicle: Vehicle):
        """
        Called when a vehicle has finished charging.

        Parameters:
        - vehicle (Vehicle): the vehicle that has finished charging.
        """
        pass

    @abstractmethod
    def add_vehicle(self, vehicle: Vehicle):
        """
        Adds a vehicle to the station.

        Parameters:
        - vehicle (Vehicle): the vehicle to add to the station.
        """
        pass

    @abstractmethod
    def pop_vehicle(self) -> Vehicle:
        """
        Removes and returns the next vehicle to charge.

        Returns:
        - Vehicle: the next vehicle to charge.
        """
        pass

    @abstractmethod
    def next_vehicle_to_charge(self, charging_vehicles: list):
        """
        Returns the next vehicle to charge.

        Parameters:
        - charging_vehicles (list): a list of vehicles that are currently charging.

        Returns:
        - Vehicle: the next vehicle to charge.
        """
        pass

    @abstractmethod
    def need_reschedule(self):
        """
        Returns whether the station needs to reschedule the charging of its vehicles.

        Returns:
        - bool: True if the station needs to reschedule the charging of its vehicles, False otherwise.
        """
        pass

    def lock(self, vehicle):
        """
        Locks a vehicle in the station.

        Parameters:
        - vehicle (Vehicle): the vehicle to lock in the station.
        """
        yield self.slots.put("vehicle")
        self.add_vehicle(vehicle)

    def unlock(self, user):
        """
        Unlocks a vehicle from the station.

        Parameters:
        - user (User): the user that unlocks the vehicle.
        """
        yield self.available_vehicles.get()
        self.slots.get()
        v = self.pop_vehicle()
        user.vehicle = v

class StationStorageLIFO(StationStorage):
    """
    A station storage that uses a last-in, first-out (LIFO) policy for charging its vehicles.
    """

    def __init__(self, env: simpy.Environment, capacity: int, policy: ChargingPolicy):
        """
        Initializes a new instance of the StationStorageLIFO class.

        Parameters:
        - env (simpy.Environment): the simulation environment.
        - capacity (int): the maximum number of vehicles that can be stored in the station.
        - policy (ChargingPolicy): the charging policy used by the station.
        """
        super().__init__(env, capacity, policy)
        self.vehicles = []

    def charged(self, vehicle: Vehicle):
        """
        Called when a vehicle has finished charging.

        Parameters:
        - vehicle (Vehicle): the vehicle that has finished charging.
        """
        if self.vehicles and self.vehicles[-1] == vehicle:
            self.available_vehicles.put("vehicle")

    def add_vehicle(self, vehicle: Vehicle):
        """
        Adds a vehicle to the station.

        Parameters:
        - vehicle (Vehicle): the vehicle to add to the station.
        """
        self.vehicles.append(vehicle)
        if vehicle.is_charged():
            if len(self.available_vehicles.items) == 0:
                self.available_vehicles.put("vehicle")
        else:
            if len(self.available_vehicles.items) == 1:
                self.available_vehicles.get()        

    def pop_vehicle(self) -> Vehicle:
        """
        Removes and returns the next vehicle to charge.

        Returns:
        - Vehicle: the next vehicle to charge.
        """
        v = self.vehicles.pop()
        if self.vehicles and self.vehicles[-1].is_charged():
            self.available_vehicles.put("vehicle")
        return v

    def next_vehicle_to_charge(self, charging_vehicles: list):
        """
        Returns the next vehicle to charge.

        Parameters:
        - charging_vehicles (list): a list of vehicles that are currently charging.

        Returns:
        - Vehicle: the next vehicle to charge.
        """
        return self.policy.next_vehicle_to_charge([v for v in self.vehicles if v not in charging_vehicles])
    
    def need_reschedule(self):
        """
        Returns whether the station needs to reschedule the charging of its vehicles.

        Returns:
        - bool: True if the station needs to reschedule the charging of its vehicles, False otherwise.
        """
        return True
