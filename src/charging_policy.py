from abc import ABC, abstractmethod

class ChargingPolicy(ABC):
    @abstractmethod
    def vehicles_to_charge(self, vehicles, number):
        pass

    @abstractmethod
    def next_vehicle_to_charge(self, vehicles):
        pass

class LIFO(ChargingPolicy):
    def vehicles_to_charge(self, vehicles, number):
        to_charge = []
        for vehicle in vehicles[::-1]:
            if not vehicle.is_charged():
                to_charge.append(vehicle)
            if len(to_charge) == number:
                return to_charge
        return to_charge
    
    def next_vehicle_to_charge(self, vehicles):
        for vehicle in vehicles[::-1]:
            if not vehicle.is_charged():
                return vehicle
        return None
    
class FIFO(ChargingPolicy):
    def vehicles_to_charge(self, vehicles, number):
        to_charge = []
        for vehicle in vehicles:
            if not vehicle.is_charged():
                to_charge.append(vehicle)
            if len(to_charge) == number:
                return to_charge
        return to_charge
    
    def next_vehicle_to_charge(self, vehicles):
        for vehicle in vehicles:
            if not vehicle.is_charged():
                return vehicle
        return None
