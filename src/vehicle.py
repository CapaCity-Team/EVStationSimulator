import json
from abc import ABC, abstractmethod

class ConfigFileNotFound(Exception):
    pass

class Vehicle(ABC):
    """
    Abstract base class for all vehicles.
    """
    def __init__(self, vehicle_id):
        """
        Initializes a new instance of the Vehicle class.

        Args:
            vehicle_id (int): The ID of the vehicle.
        """
        self.id = vehicle_id
        self.battery = 1

    @property
    @abstractmethod
    def max_capacity(self):
        """
        Gets the maximum capacity of the vehicle.

        Returns:
            float: The maximum capacity of the vehicle.
        """
        pass

    @property
    @abstractmethod
    def energy_consumption(self):
        """
        Gets the energy consumption of the vehicle.

        Returns:
            float: The energy consumption of the vehicle.
        """
        pass
    
    @property
    @abstractmethod
    def velocity(self):
        """
        Gets the velocity of the vehicle.

        Returns:
            float: The velocity of the vehicle.
        """
        pass

    def move(self, distance: float):
        """
        Moves the vehicle a certain distance.

        Args:
            distance (float): The distance to move the vehicle.

        Returns:
            float: The time it takes to move the vehicle the specified distance.
        """
        self.battery -= distance * self.energy_consumption
        return distance / self.velocity

    def capacity(self):
        """
        Calculates the current capacity of the vehicle.

        Returns:
            float: The current capacity of the vehicle.
        """
        return self.max_capacity*self.battery
    
    def capacity_left(self):
        """
        Calculates the remaining capacity of the vehicle.

        Returns:
            float: The remaining capacity of the vehicle.
        """
        return (1-self.battery)*self.max_capacity

    def is_charged(self):
        """
        Determines if the vehicle is fully charged.

        Returns:
            bool: True if the vehicle is fully charged, False otherwise.
        """
        return self.battery == 1

    def fully_charge(self):
        """
        Fully charges the vehicle.
        """
        self.battery = 1

    def charge(self, percentage):
        """
        Charges the vehicle by a certain percentage.

        Args:
            percentage (float): The percentage to charge the vehicle by.
        """
        self.battery += percentage
        if self.battery > 1:
            self.battery = 1

    @classmethod
    def load_config(cls, config_file):
        """
        Loads the configuration for the vehicle from a JSON file.

        Args:
            config_file (str): The path to the configuration file.

        Raises:
            ConfigFileNotFound: If the configuration file is not found.

        """
        try:
            with open(config_file, 'r') as file:
                config_data = json.load(file)[cls.__name__]
                for key, value in config_data.items():
                    setattr(cls, key, value)
        except FileNotFoundError:
            raise ConfigFileNotFound(f'File {config_file} not found')

class Scooter(Vehicle):
    """
    Represents a scooter vehicle.
    """
    BATTERY_CAPACITY = None
    ENERGY_CONSUMPTION = None
    VELOCITY = None
    def __init__(self, scooter_id):
        """
        Initializes a new instance of the Scooter class.

        Args:
            scooter_id (int): The ID of the scooter.
        """
        super().__init__(scooter_id)

    @property
    def max_capacity(self):
        """
        Gets the maximum capacity of the scooter.

        Returns:
            float: The maximum capacity of the scooter.
        """
        return self.BATTERY_CAPACITY
    
    @property
    def energy_consumption(self):
        """
        Gets the energy consumption of the scooter.

        Returns:
            float: The energy consumption of the scooter.
        """
        return self.ENERGY_CONSUMPTION
    
    @property
    def velocity(self):
        """
        Gets the velocity of the scooter.

        Returns:
            float: The velocity of the scooter.
        """
        return self.VELOCITY

    
class Bike(Vehicle):
    """
    Represents a bike vehicle.
    """
    BATTERY_CAPACITY = None
    ENERGY_CONSUMPTION = None
    VELOCITY = None
    def __init__(self, bike_id):
        """
        Initializes a new instance of the Bike class.

        Args:
            bike_id (int): The ID of the bike.
        """
        super().__init__(bike_id)

    @property
    def max_capacity(self):
        """
        Gets the maximum capacity of the bike.

        Returns:
            float: The maximum capacity of the bike.
        """
        return self.BATTERY_CAPACITY
    
    @property
    def energy_consumption(self):
        """
        Gets the energy consumption of the bike.

        Returns:
            float: The energy consumption of the bike.
        """
        return self.ENERGY_CONSUMPTION
    
    @property
    def velocity(self):
        """
        Gets the velocity of the bike.

        Returns:
            float: The velocity of the bike.
        """
        return self.VELOCITY