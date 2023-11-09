from abc import ABC, abstractmethod

class ChargingPolicy(ABC):
    # Abstract base class representing a charging policy for vehicles

    @abstractmethod
    def vehicles_to_charge(self, vehicles, number):
        # Abstract method to select a list of vehicles to charge
        pass

    @abstractmethod
    def next_vehicle_to_charge(self, vehicles):
        # Abstract method to select the next vehicle to charge
        pass

class LIFO(ChargingPolicy):
    # Concrete class implementing a Last In, First Out (LIFO) charging policy

    def vehicles_to_charge(self, vehicles, number):
        # Select the last 'number' vehicles in the list that need charging
        to_charge = []
        for vehicle in vehicles[::-1]:
            if not vehicle.is_charged():
                to_charge.append(vehicle)
            if len(to_charge) == number:
                return to_charge
        return to_charge
    
    def next_vehicle_to_charge(self, vehicles):
        # Select the last vehicle in the list that needs charging
        for vehicle in vehicles[::-1]:
            if not vehicle.is_charged():
                return vehicle
        return None
    
class FIFO(ChargingPolicy):
    # Concrete class implementing a First In, First Out (FIFO) charging policy

    def vehicles_to_charge(self, vehicles, number):
        # Select the first 'number' vehicles in the list that need charging
        to_charge = []
        for vehicle in vehicles:
            if not vehicle.is_charged():
                to_charge.append(vehicle)
            if len(to_charge) == number:
                return to_charge
        return to_charge
    
    def next_vehicle_to_charge(self, vehicles):
        # Select the first vehicle in the list that needs charging
        for vehicle in vehicles:
            if not vehicle.is_charged():
                return vehicle
        return None

