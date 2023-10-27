from abc import ABC, abstractmethod
from src.charging_policy import ChargingPolicy

class VehicleArranger(ABC):
    def __init__(self, policy: ChargingPolicy):
        self.policy = policy

    @abstractmethod
    def lock(self, vehicle):
        pass

    @abstractmethod
    def unlock(self):
        pass

    @abstractmethod
    def next_vehicle_to_charge(self):
        pass

    @abstractmethod
    def need_reschedule(self):
        pass