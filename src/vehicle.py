import json
from abc import ABC, abstractmethod

class ConfigFileNotFound(Exception):
    pass

class Vehicle(ABC):
    def __init__(self, vehicle_id):
        self.id = vehicle_id
        self.battery = 1

    @property
    @abstractmethod
    def max_capacity(self):
        pass

    @property
    @abstractmethod
    def energy_consumption(self):
        pass
    
    @property
    @abstractmethod
    def velocity(self):
        pass

    def move(self, distance: float):
        self.battery -= distance * self.energy_consumption
        return distance / self.velocity

    def capacity(self):
        return self.max_capacity*self.battery
    
    def capacity_left(self):
        return (1-self.battery)*self.max_capacity

    def is_charged(self):
        return self.battery == 1

    def fully_charge(self):
        self.battery = 1

    def charge(self, percentage):
        self.battery += percentage
        if self.battery > 1:
            self.battery = 1

    @classmethod
    def load_config(cls, config_file):
        try:
            with open(config_file, 'r') as file:
                config_data = json.load(file)[cls.__name__]
                for key, value in config_data.items():
                    setattr(cls, key, value)
        except FileNotFoundError:
            raise ConfigFileNotFound(f'File {config_file} not found')

class Scooter(Vehicle):
    BATTERY_CAPACITY = None
    ENERGY_CONSUMPTION = None
    VELOCITY = None
    def __init__(self, scooter_id):
        super().__init__(scooter_id)

    @property
    def max_capacity(self):
        return self.BATTERY_CAPACITY
    
    @property
    def energy_consumption(self):
        return self.ENERGY_CONSUMPTION
    
    @property
    def velocity(self):
        return self.VELOCITY

    
class Bike(Vehicle):
    BATTERY_CAPACITY = None
    ENERGY_CONSUMPTION = None
    VELOCITY = None
    def __init__(self, bike_id):
        super().__init__(bike_id)

    @property
    def max_capacity(self):
        return self.BATTERY_CAPACITY
    
    @property
    def energy_consumption(self):
        return self.ENERGY_CONSUMPTION
    
    @property
    def velocity(self):
        return self.VELOCITY