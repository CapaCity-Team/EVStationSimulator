import simpy
from vehicle import Vehicle
from station_storage import StationStorage

import logging

# Obtain a reference to the logger configured in the main script
logger = logging.getLogger(__name__)

class Station:
    """
    A class representing a charging station for electric vehicles.

    Attributes:
    - id (int): The unique identifier of the station.
    - charging_time (float): The time it takes to fully charge a vehicle.
    - max_concurrent_charging (int): The maximum number of vehicles that can be charged simultaneously.
    - vehicles (StationStorage): The storage object containing the vehicles currently at the station.
    - env (simpy.Environment): The simulation environment.
    - position (tuple): The (x, y) coordinates of the station.
    - charging_vehicles (dict): A dictionary containing the vehicles currently being charged and their corresponding charging processes.
    """

    def __init__(self, env: simpy.Environment, station_id: int, position: tuple, charging_time: float, max_concurrent_charging: int, vehicles: StationStorage):
        """
        Initializes a new instance of the Station class.

        Parameters:
        - env (simpy.Environment): The simulation environment.
        - station_id (int): The unique identifier of the station.
        - position (tuple): The (x, y) coordinates of the station.
        - charging_time (float): The time it takes to fully charge a vehicle.
        - max_concurrent_charging (int): The maximum number of vehicles that can be charged simultaneously.
        - vehicles (StationStorage): The storage object containing the vehicles currently at the station.
        """
        self.id = station_id
        
        self.charging_time = charging_time
        self.max_concurrent_charging = max_concurrent_charging
    
        self.vehicles = vehicles
        self.env = env

        self.position = position
        self.charging_vehicles = {}

    def charge(self, vehicle: Vehicle, now: float):
        """
        Charges a vehicle at the station.

        Parameters:
        - vehicle (Vehicle): The vehicle to be charged.
        - now (float): The current simulation time.

        Yields:
        - A timeout event representing the time it takes to charge the vehicle.
        """
        try:
            logger.info("Charging vehicle {} with battery {}% in station {}".format(vehicle.id, vehicle.battery*100, self.id))

            time = self.charging_time * vehicle.capacity_left()
            yield self.env.timeout(time)
            vehicle.fully_charge()

            logger.info("Charged vehicle {} in {} unit of time".format(vehicle.id, time))

            self.vehicles.charged(vehicle)
            
            self.charge_next_vehicle()
        
        except simpy.Interrupt:
            logger.info("Charging interrupted for vehicle {} at {}".format(vehicle.id, self.env.now))
            charged_time = self.env.now - now
            before = vehicle.battery
            vehicle.charge(charged_time / self.charging_time / vehicle.max_capacity)
            logger.info("Charged vehicle {} of {}% in station {}".format(vehicle.id, (vehicle.battery-before)*100, self.id))

        del self.charging_vehicles[vehicle]

    def charge_next_vehicle(self):
        """
        Starts charging the next vehicle in the queue, if any.
        """
        to_charge = self.vehicles.next_vehicle_to_charge(list(self.charging_vehicles.keys()))
        if to_charge is not None:
            charging_process = self.env.process(self.charge(to_charge, self.env.now))
            self.charging_vehicles[to_charge] = charging_process

    def stop_charging(self):
        """
        Stops charging all vehicles currently being charged.
        """
        for vehicle, process in self.charging_vehicles.items():
            process.interrupt()

    def start_charging(self):
        """
        Starts charging vehicles up to the maximum number of concurrent charging allowed.
        """
        for _ in range(self.max_concurrent_charging):
            self.charge_next_vehicle()

    def request_lock(self, vehicle: Vehicle):
        """
        Requests a lock for the given vehicle.

        Parameters:
        - vehicle (Vehicle): The vehicle to be locked.

        Yields:
        - A lock event for the vehicle.
        """
        yield from self.vehicles.lock(vehicle)
        if self.vehicles.need_reschedule():
            self.stop_charging()
            self.start_charging()
    
    def request_unlock(self, user):
        """
        Requests an unlock for the given user.

        Parameters:
        - user: The user to be unlocked.

        Yields:
        - An unlock event for the user.
        """
        yield from self.vehicles.unlock(user)
    
    def distance(self, station):
        """
        Calculates the Euclidean distance between this station and another station.

        Parameters:
        - station (Station): The other station.

        Returns:
        - The Euclidean distance between the two stations.
        """
        return ((self.position[0] - station.position[0])**2 + (self.position[1] - station.position[1])**2)**0.5
    
    def add_vehicle(self, vehicle: Vehicle):
        """
        Adds a vehicle to the station in the deployment phase.

        Parameters:
        - vehicle (Vehicle): The vehicle to add to the station.
        """
        self.vehicles.add_vehicle(vehicle)