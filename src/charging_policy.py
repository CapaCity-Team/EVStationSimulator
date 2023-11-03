from abc import ABC, abstractmethod

class ChargingPolicy(ABC):
    """
    Abstract base class for charging policies.
    """
    @abstractmethod
    def vehicles_to_charge(self, vehicles, number):
        """
        Selects a list of vehicles to charge.

        Args:
            vehicles (list): List of Vehicle objects.
            number (int): Number of vehicles to select.

        Returns:
            list: List of Vehicle objects to charge.
        """
        pass

    @abstractmethod
    def next_vehicle_to_charge(self, vehicles):
        """
        Selects the next vehicle to charge.

        Args:
            vehicles (list): List of Vehicle objects.

        Returns:
            Vehicle: Vehicle object to charge next.
        """
        pass

class LIFO(ChargingPolicy):
    """
    Last-In-First-Out charging policy.
    """
    def vehicles_to_charge(self, vehicles, number):
        """
        Selects a list of vehicles to charge using LIFO policy.

        Args:
            vehicles (list): List of Vehicle objects.
            number (int): Number of vehicles to select.

        Returns:
            list: List of Vehicle objects to charge.
        """
        to_charge = []
        for vehicle in vehicles[::-1]:
            if not vehicle.is_charged():
                to_charge.append(vehicle)
            if len(to_charge) == number:
                return to_charge
        return to_charge
    
    def next_vehicle_to_charge(self, vehicles):
        """
        Selects the next vehicle to charge using LIFO policy.

        Args:
            vehicles (list): List of Vehicle objects.

        Returns:
            Vehicle: Vehicle object to charge next.
        """
        for vehicle in vehicles[::-1]:
            if not vehicle.is_charged():
                return vehicle
        return None
    
class FIFO(ChargingPolicy):
    """
    First-In-First-Out charging policy.
    """
    def vehicles_to_charge(self, vehicles, number):
        """
        Selects a list of vehicles to charge using FIFO policy.

        Args:
            vehicles (list): List of Vehicle objects.
            number (int): Number of vehicles to select.

        Returns:
            list: List of Vehicle objects to charge.
        """
        to_charge = []
        for vehicle in vehicles:
            if not vehicle.is_charged():
                to_charge.append(vehicle)
            if len(to_charge) == number:
                return to_charge
        return to_charge
    
    def next_vehicle_to_charge(self, vehicles):
        """
        Selects the next vehicle to charge using FIFO policy.

        Args:
            vehicles (list): List of Vehicle objects.

        Returns:
            Vehicle: Vehicle object to charge next.
        """
        for vehicle in vehicles:
            if not vehicle.is_charged():
                return vehicle
        return None
