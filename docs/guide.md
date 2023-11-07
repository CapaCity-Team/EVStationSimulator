# Electric Station Simulation Documentation

This documentation outlines the structure and functionality of an electric station simulation program, including its primary components and configuration.

## Program Overview

The electric station simulation program simulates the operation of charging stations, vehicles, and user interactions within a defined environment.

### Components

1. **User**: Represents users of the charging stations.

2. **Station**: Represents charging stations where users can charge their vehicles.

3. **Scooter**: A specific type of vehicle used in the simulation.

4. **Charging Policies**: Charging policies define how vehicles are selected for charging.

5. **Station Storage**: Station storage determines the organization and management of charging stations.

6. **Map**: Defines the map or layout of the charging stations.

7. **Simulation Environment**: Utilizes SimPy for discrete-event simulation.

8. **Configuration**: Configuration data loaded from JSON files.

### Main Function

- `main(env, config_data)`: The primary function that sets up and runs the electric station simulation. It initializes various components based on configuration data and starts the simulation.

## Usage

1. Import the necessary modules and classes:

   ```python
   from user import User
   from station import Station
   from vehicle import Scooter
   import charging_policy
   import station_storage
   import map
   from simpy import Environment
   ```

2. Read the simulation configuration from JSON files.

3. Configure and initialize the simulation components, including users, stations, vehicles, charging policies, station storage, and the map.

4. Start and run the simulation environment using `env.run(until=config_data["Run Time"])`.

## Configuration

- Configuration data is loaded from JSON files, including vehicle configurations and simulation settings.

## Customization and Extension

- You can customize and extend the simulation by adding new vehicle types, charging policies, or station storage methods to suit your specific requirements.

---

# User Class Documentation

The `User` class represents a user of the electric station simulation, including their actions and interactions within the simulation environment.

## Class Overview

### `User`

- **Attributes:**
  - `env` (simpy.Environment): The simulation environment.
  - `id` (int): The user's ID.
  - `from_station` (Station): The station where the user starts.
  - `to_station` (Station): The station where the user wants to go.
  - `vehicle` (Vehicle): The vehicle the user is using.

- **Methods:**
  - `__init__(env, id, from_station, to_station)`: Initializes a new instance of the `User` class.
  - `run()`: The main method of the `User` class, representing the user's actions during the simulation.

---

# Station Class Documentation

The `Station` class represents a charging station for electric vehicles in a simulation environment.

## Class Overview

### `Station`

- **Attributes:**
  - `id` (int): The unique identifier of the station.
  - `charging_time` (float): The time it takes to fully charge a vehicle.
  - `max_concurrent_charging` (int): The maximum number of vehicles that can be charged simultaneously.
  - `vehicles` (StationStorage): The storage object containing the vehicles currently at the station.
  - `env` (simpy.Environment): The simulation environment.
  - `position` (tuple): The (x, y) coordinates of the station.
  - `charging_vehicles` (dict): A dictionary containing the vehicles currently being charged and their corresponding charging processes.

- **Methods:**
  - `__init__(env, station_id, position, charging_time, max_concurrent_charging, vehicles)`: Initializes a new instance of the `Station` class.
  - `charge(vehicle, now)`: Charges a vehicle at the station.
  - `charge_next_vehicle()`: Starts charging the next vehicle in the queue, if any.
  - `stop_charging()`: Stops charging all vehicles currently being charged.
  - `start_charging()`: Starts charging vehicles up to the maximum number of concurrent charging allowed.
  - `request_lock(vehicle)`: Requests a lock for the given vehicle.
  - `request_unlock(user)`: Requests an unlock for the given user.
  - `distance(station)`: Calculates the Euclidean distance between this station and another station.

---

# Vehicle Class and Subclasses Documentation

The `Vehicle` class and its subclasses, `Scooter` and `Bike`, represent different types of vehicles in the electric station simulation. These classes define the properties and behaviors of each vehicle.

## Class Overview

### `Vehicle` (Abstract Base Class)

- **Attributes:**
  - `id` (int): The ID of the vehicle.
  - `battery` (float): The current battery level of the vehicle.

- **Methods:**
  - `__init__(vehicle_id)`: Initializes a new instance of the `Vehicle` class.
  - `max_capacity`: Gets the maximum capacity of the vehicle (abstract property).
  - `energy_consumption`: Gets the energy consumption of the vehicle (abstract property).
  - `velocity`: Gets the velocity of the vehicle (abstract property).
  - `move(distance)`: Moves the vehicle a certain distance and updates its battery level.
  - `capacity`: Calculates the current capacity of the vehicle.
  - `capacity_left`: Calculates the remaining capacity of the vehicle.
  - `is_charged`: Determines if the vehicle is fully charged.
  - `fully_charge`: Fully charges the vehicle.
  - `charge(percentage)`: Charges the vehicle by a certain percentage.
  - `load_config(config_file)`: Loads the configuration for the vehicle from a JSON file.

### `Scooter` (Subclass of `Vehicle`)

- **Attributes:**
  - `BATTERY_CAPACITY` (float): The battery capacity of scooters.
  - `ENERGY_CONSUMPTION` (float): The energy consumption of scooters.
  - `VELOCITY` (float): The velocity of scooters.

- **Methods:**
  - `__init__(scooter_id)`: Initializes a new instance of the `Scooter` class.
  - `max_capacity`: Gets the maximum capacity of scooters.
  - `energy_consumption`: Gets the energy consumption of scooters.
  - `velocity`: Gets the velocity of scooters.

### `Bike` (Subclass of `Vehicle`)

- **Attributes:**
  - `BATTERY_CAPACITY` (float): The battery capacity of bikes.
  - `ENERGY_CONSUMPTION` (float): The energy consumption of bikes.
  - `VELOCITY` (float): The velocity of bikes.

- **Methods:**
  - `__init__(bike_id)`: Initializes a new instance of the `Bike` class.
  - `max_capacity`: Gets the maximum capacity of bikes.
  - `energy_consumption`: Gets the energy consumption of bikes.
  - `velocity`: Gets the velocity of bikes.

---

# StationStorage Documentation

The `StationStorage` class is an abstract base class for a station storage, providing a flexible framework for managing vehicle charging stations in a simulation environment.

## Class Overview

### `StationStorage` (Abstract Base Class)

- **Purpose:** An abstract base class for a station storage that supports various charging policies.
- **Attributes:**
  - `capacity` (int): the maximum number of vehicles that can be stored in the station.
  - `policy` (ChargingPolicy): the charging policy used by the station.
  - `slots` (simpy.Store): a store that represents the slots available for vehicles in the station.
  - `available_vehicles` (simpy.Store): a store that represents the vehicles available for charging in the station.

- **Methods:**
  - `__init__(env, capacity, policy)`: Initializes a new instance of the `StationStorage` class.
  - `charged(vehicle)`: Called when a vehicle has finished charging.
  - `add_vehicle(vehicle)`: Adds a vehicle to the station.
  - `pop_vehicle() -> Vehicle`: Removes and returns the next vehicle to charge.
  - `next_vehicle_to_charge(charging_vehicles)`: Returns the next vehicle to charge.
  - `need_reschedule()`: Returns whether the station needs to reschedule the charging of its vehicles.
  - `lock(vehicle)`: Locks a vehicle in the station.
  - `unlock(user)`: Unlocks a vehicle from the station.

### `StationStorageLIFO` (Concrete Class)

- **Purpose:** A station storage that uses a last-in, first-out (LIFO) policy for charging its vehicles.
- **Attributes:**
  - Inherits attributes and methods from `StationStorage`.
  - Additional attribute: `vehicles` (list) to track vehicles in the station.

- **Methods:**
  - Overrides `charged(vehicle)`: Handles vehicle charging completion using LIFO policy.
  - Overrides `add_vehicle(vehicle)`: Adds a vehicle to the station with LIFO policy considerations.
  - Overrides `pop_vehicle() -> Vehicle`: Removes and returns the next vehicle to charge with LIFO policy.
  - Overrides `next_vehicle_to_charge(charging_vehicles)`: Implements LIFO-based next vehicle selection.
  - Overrides `need_reschedule()`: Always returns `True` to indicate rescheduling is needed.

---

# Charging Policy Documentation

The `ChargingPolicy` class and its concrete subclasses, `LIFO` and `FIFO`, provide a framework for managing the charging order of vehicles in a charging station. These policies determine how vehicles are selected for charging and the order in which they are charged.

## Abstract Base Class

### `ChargingPolicy` (Abstract Base Class)

- **Purpose:** An abstract base class for charging policies.
- **Methods:**
  - `vehicles_to_charge(vehicles, number)`: Selects a list of vehicles to charge.
  - `next_vehicle_to_charge(vehicles)`: Selects the next vehicle to charge.

## Concrete Charging Policies

### `LIFO` (Last-In-First-Out Charging Policy)

- **Purpose:** Implements the Last-In-First-Out (LIFO) charging policy.
- **Methods:**
  - `vehicles_to_charge(vehicles, number)`: Selects a list of vehicles to charge using LIFO policy.
  - `next_vehicle_to_charge(vehicles)`: Selects the next vehicle to charge using LIFO policy.

### `FIFO` (First-In-First-Out Charging Policy)

- **Purpose:** Implements the First-In-First-Out (FIFO) charging policy.
- **Methods:**
  - `vehicles_to_charge(vehicles, number)`: Selects a list of vehicles to charge using FIFO policy.
  - `next_vehicle_to_charge(vehicles)`: Selects the next vehicle to charge using FIFO policy.
