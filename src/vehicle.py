import json
from abc import ABC, abstractmethod

class ConfigFileNotFound(Exception):
    pass

class NegativeBatteryLevel(Exception):
    pass

class Vehicle(ABC):
    def __init__(self, vehicle_id):
        # Initialize the Vehicle with a unique ID and a default battery level of 1
        self.id = vehicle_id
        self.battery = 1

    @property
    @abstractmethod
    def max_capacity(self):
        # Abstract property representing the maximum capacity of the vehicle
        pass

    @property
    @abstractmethod
    def energy_consumption(self):
        # Abstract property representing the energy consumption of the vehicle
        pass

    def move(self, distance: float):
        # Move the vehicle by a specified distance, update battery level
        self.battery -= distance * self.energy_consumption / self.max_capacity

        if self.battery < 0:
            # Raise a custom exception if the battery level becomes negative
            raise NegativeBatteryLevel(f'Vehicle {self.id} battery level is negative')

    def capacity_left(self):
        # Calculate the current capacity of the vehicle based on battery level
        return self.max_capacity * self.battery
    
    def capacity_used(self):
        # Calculate the remaining capacity of the vehicle based on battery level
        return (1 - self.battery) * self.max_capacity

    def is_charged(self):
        # Check if the vehicle is fully charged (battery level is 1)
        return self.battery == 1

    def fully_charge(self):
        # Fully charge the vehicle by setting the battery level to 1
        self.battery = 1

    def charge(self, percentage):
        # Charge the vehicle by a specified percentage, ensuring the battery level does not exceed 1
        self.battery += percentage
        if self.battery > 1:
            self.battery = 1

    @classmethod
    def load_config(cls, config_file):
        # Load configuration data from a JSON file and update class attributes accordingly
        try:
            with open(config_file, 'r') as file:
                config_data = json.load(file)[cls.__name__]
                for key, value in config_data.items():
                    setattr(cls, key, value)
        except FileNotFoundError:
            # Raise a custom exception if the configuration file is not found
            raise ConfigFileNotFound(f'File {config_file} not found')

class Scooter(Vehicle):
    # Subclass of Vehicle representing a Scooter

    # Class-level attributes for configuring the Scooter's behavior
    BATTERY_CAPACITY = None
    ENERGY_CONSUMPTION = None

    def __init__(self, scooter_id):
        # Initialize Scooter using the base class constructor
        super().__init__(scooter_id)

    @property
    def max_capacity(self):
        # Override the abstract property to provide Scooter-specific max capacity
        return self.BATTERY_CAPACITY
    
    @property
    def energy_consumption(self):
        # Override the abstract property to provide Scooter-specific energy consumption
        return self.ENERGY_CONSUMPTION

    
class Bike(Vehicle):
    # Subclass of Vehicle representing a Bike

    # Class-level attributes for configuring the Bike's behavior
    BATTERY_CAPACITY = None
    ENERGY_CONSUMPTION = None

    def __init__(self, bike_id):
        # Initialize Bike using the base class constructor
        super().__init__(bike_id)

    @property
    def max_capacity(self):
        # Override the abstract property to provide Bike-specific max capacity
        return self.BATTERY_CAPACITY
    
    @property
    def energy_consumption(self):
        # Override the abstract property to provide Bike-specific energy consumption
        return self.ENERGY_CONSUMPTION