# Developer Guide

Welcome to the Developer Guide for EVStationSimulator. This guide provides information on the code structure, development environment setup, and guidelines for contributing to the project.

## Code Structure

The codebase is organized into the following directories:

```
└── src/
    ├── main.py
    ├── station_deployment.py
    ├── station.py
    ├── station_storage.py
    ├── user.py
    ├── utils.py
    ├── vehicle_deployment.py
    └── vehicle.py
```

## Index

- [Developer Guide](#developer-guide)
  - [Code Structure](#code-structure)
  - [Index](#index)
  - [Code Documentation](#code-documentation)
    - [Main](#main)
    - [Station](#station)
    - [Station Storage](#station-storage)
    - [Station Deployment](#station-deployment)
    - [Vehicle](#vehicle)
    - [Vehicle Deployment](#vehicle-deployment)
    - [User](#user)
    - [Utils](#utils)

## Code Documentation

### Main
[Source Code](../src/main.py) contains the main function for the simulation. It is responsible for parsing the simulation configuration file, initializing the simulation, and running the simulation.

- **Functionality:**
  - Runs the entire simulation and performs data analysis.

- **Steps:**
  1. Reads the configuration files.
  2. Initializes the simulation, including:
     - Generating station positions.
     - Generating stations.
     - Generating and deploying vehicles.
     - Generating users.
  3. Runs the simulation.
  4. Saves the results in a CSV file in the "data/simulation_results" folder.
  5. Conducts data analysis.
  6. Plots the results.

---

### Station
[source](../src/station.py ':include :type=code python') contains the `Station` class.

- **Description**:
    The `Station` class acts as a wrapper for the station storage and is responsible for charging vehicles and interacting with the users.

- **Methods**:
    - `__init__(self, env: simpy.Environment, station_id: int, position: tuple, capacity_per_time: float, max_concurrent_charging: int, vehicles: StationStorage)`:
        - **Description**: Initializes the station with a unique ID, a position, a capacity per unit of time, a maximum number of vehicles that can be charged simultaneously, and a station storage.
        - **Parameters**:
            - `env`: The simpy environment.
            - `station_id`: The station ID.
            - `position`: The station position.
            - `capacity_per_time`: The capacity charged by the station per unit of time.
            - `max_concurrent_charging`: The maximum number of vehicles that can be charged simultaneously.
            - `vehicles`: The station storage.
        - **Returns**: Does not return anything.
    - `charge(self, vehicle: Vehicle, now: float)`:
        - **Description**: Performs the charging process for a vehicle.
        - **Parameters**:
            - `vehicle`: The vehicle to charge.
            - `now`: The current time.
        - **Returns**: Does not return anything.
    - `charge_next_vehicle(self)`:
        - **Description**: Calls `charge` for the next vehicle in the queue.
        - **Returns**: Does not return anything.
    - `stop_charging(self)`:
        - **Description**: Interrupts the charging process for all vehicles.
        - **Returns**: Does not return anything.
    - `start_charging(self)`:
        - **Description**: Starts the charging process for however many vehicles can be charged simultaneously.
        - **Returns**: Does not return anything.
    - `request_lock(self, vehicle: Vehicle)`:
        - **Description**: Requests a lock for a vehicle. It is a blocking function that waits until there is a slot available.
        - **Parameters**:
            - `vehicle`: The vehicle to lock.
        - **Returns**: Does not return anything.
    - `request_unlock(self, user)`:
        - **Description**: Requests an unlock for a vehicle and assigns it to a user. It is a blocking function that waits until there is a vehicle available.
        - **Parameters**:
            - `user`: The user to assign the vehicle to.
        - **Returns**: Does not return anything.
    - `distance(self, station) -> float`:
        - **Description**: calc the distance between this station and the station passed as a parameter.
        - **Parameters**:
            - `station`: The station to calculate the distance to.
        - **Returns**: The distance between this station and the station passed as a parameter.
    - `deploy(self, vehicles: list)`:
        - **Description**: Deploys the vehicles to the station.
        - **Parameters**:
            - `vehicles`: List of vehicles to deploy.
        - **Returns**: Does not return anything.

---

### Station Storage
[source](../src/station_storage.py ':include :type=code python') contains the `StationStorage` class and all its subclasses.

- **Description**:
    The class is responsible for keeping track of vehicles available at a station and selecting the next vehicle to charge. The class is also responsible for segbaling a need ro reschedule the charging of vehicles when a new vehicle is added to the station storage.
    
    **Note:** The station storage is not responsible for charging vehicles.

    **Warning**: The `__init__` method requires the following parameters:
    - `env`: simpy.Environment
    - `params`: dict
    - Will always be called with these parameters and only these parameters.
    - Additional parameters must be added to the `params` dict.

- **Methods**:
    - `__init__(self, env: simpy.Environment, params: dict)`:
        - **Description**: Initializes the station storage.
        - **Parameters**:
            - `env`: The simpy environment.
            - `params`: The station storage parameters defined in the configuration file.
        - **Returns**: Does not return anything.
    - `charged(self, vehicle: Vehicle)`:
        - **Description**: Notifies the station storage that a vehicle has been fully charged so the available vehicles can be updated.
        - **Parameters**:
            - `vehicle`: The vehicle that has been fully charged.
        - **Returns**: Does not return anything.
    - `add_vehicle(self, vehicle: Vehicle)`:
        - **Description**: Adds a vehicle to the station storage.
        - **Parameters**:
            - `vehicle`: The vehicle to add.
        - **Returns**: Does not return anything.
    - `pop_vehicle(self) -> Vehicle`:
        - **Description**: Removes a vehicle from the station storage.
        - **Returns**: The removed vehicle.
    - `next_vehicle_to_charge(self, charging_vehicles: list) -> Vehicle`:
        - **Description**: Selects the next vehicle to charge from the station storage.
        - **Parameters**:
            - `charging_vehicles`: List of vehicles currently charging (to avoid selecting them).
        - **Returns**: The selected vehicle.
    - `need_reschedule(self, charging_vehicles: list) -> bool`:
        - **Description**: Called when a vehicle is added to the station storage. Checks if the station storage needs to reschedule the charging of vehicles.
        - **Parameters**:
            - `charging_vehicles`: List of vehicles currently charging
        - **Returns**: `True` if the station storage needs to reschedule the charging of vehicles.
    - `lock(self, vehicle)`:
        - **Description**: Waits for a slot to be available and adds the vehicle to the station storage. 
        - **Parameters**:
            - `vehicle`: The vehicle to add.
        - **Returns**: Does not return anything.

        **Note**: Must be implemented as a generator and yield once.

    - `unlock(self, user)`:
        - **Description**: Waits for a vehicle to be available, removes it from the station storage, and assigns it to the user.
        - **Parameters**:
            - `user`: The user to assign the vehicle to.
        - **Returns**: Does not return anything.

        **Note**: Must be implemented as a generator and yield once.

    - `count(self) -> int`:
        - **Description**: Returns the number of vehicles currently stored in the station storage.
        - **Returns**: The number of vehicles currently stored in the station storage.
    - `max_capacity(self) -> int`:
        - **Description**: Returns the maximum capacity of the station storage.
        - **Returns**: The maximum capacity of the station storage.

    - `deploy(self, vehicles: list)`:
        - **Description**: Deploys a list of vehicles to the station storage. Used in the deployment phase to initialize the station storage.
        - **Parameters**:
            - `vehicles`: List of vehicles to deploy.
        - **Returns**: Does not return anything.

        **Note**: Must NOT be implemented as a generator.

---

### Station Deployment

[Souce Code](../src/station_deployment.py) contains deployment functions. All deployment functions take a dictionary of parameters as input and return a list of tuples containing the station x and y coordinates.

- `grid(params: dict) -> list`:
    - **Description:** Deploy a grid of stations with the specified number of rows and columns. The distance between each node is specified by the width parameter.
    - **parameters:**
        - rows: int
        - columns: int
        - width: float
    - **returns:** list of tuples containing the station x and y coordinates.

- `square_random(params: dict) -> list`:
    - **Description:** Deploy a specified number of stations randomly in a square of the specified size.
    - **parameters:**
        - size: float
        - number: int
    - **returns:** list of tuples containing the station x and y coordinates.

- `circle_random(params: dict) -> list`:
    - **Description:** Deploy a specified number of stations randomly in a circle of the specified radius.
    - **parameters:**
        - radius: float
        - number: int
    - **returns:** list of tuples containing the station x and y coordinates.

---

### Vehicle
[Souce Code](../src/vehicle.py) contains the vehicle classes. All vehicle classes inherit from the vehicle class.

- **Description:** The vehicle class is responsible for keeping track of the vehicle's battery level and moving the vehicle. The vehicle class is also responsible for calculating the energy consumption of the vehicle based on the distance traveled.

- **Properties:**
    - `@property max_capacity`: The maximum capacity of the vehicle.
    - `@property energy_consumption`: The energy consumption of the vehicle.

- **Methods:**
    - `__init__(self, vehicle_id: int)`:
        - **Description:** Initializes the vehicle with a unique ID and a default battery level of 1.
        - **Parameters:**
            - `vehicle_id`: The vehicle ID.
        - **Returns:** Does not return anything.
    - `move(self, distance: float) -> float`:
        - **Description:** Moves the vehicle by a specified distance, updates the battery level.
        - **Parameters:**
            - `distance`: The distance to move the vehicle.
        - **Returns:** Does not return anything.
        - **Raises:** NegativeBatteryLevel exception if the battery level becomes negative.
    - `capacity_left(self) -> float`:
        - **Description:** Calculates the capacity left in the vehicle based on the battery level.
        - **Returns:** The capacity left in the vehicle.
    - `capacity_used(self) -> float`:
        - **Description:** Calculates the capacity used by the vehicle based on the battery level.
        - **Returns:** The capacity used by the vehicle.
    - `is_charged(self) -> bool`:
        - **Description:** Checks if the vehicle is fully charged (battery level is 1).
        - **Returns:** `True` if the vehicle is fully charged, `False` otherwise.
    - `fully_charge(self)`:
        - **Description:** Fully charges the vehicle by setting the battery level to 1.
        - **Returns:** Does not return anything.
    - `charge(self, percentage)`:
        - **Description:** Charges the vehicle by a specified percentage, ensuring the battery level does not exceed 1.
        - **Parameters:**
            - `percentage`: The percentage to charge the vehicle by.
        - **Returns:** Does not return anything.

- **ClassMethods:**
    - `@classmethod load_config(cls, config_file)`:
        - **Description:** Loads configuration data from a JSON file and updates class attributes accordingly.
        - **Parameters:**
            - `config_file`: The path to the configuration file.
        - **Raises:** ConfigFileNotFound exception if the configuration file is not found.
        - **Returns:** Does not return anything.

---

### Vehicle Deployment
[Souce Code](../src/vehicle_deployment.py) contains deployment functions.

All deployment functions must follow this format:

The deploy function deploys vehicles to stations based on specified criteria.

**Parameters:**
- `stations`: List of `Station` objects.
- `vehicle_type`: List of `Vehicle` classes used in the simulation.
- `parameters`: Dictionary of parameters specified in the `simulation.json` file.

**Returns:**  Does not return anything.

Example:
```python
def deploy_func_name(stations: list, vehicle_type: list, parameters: dict):
    # code
```

**Distribution Functions:**

- `uniform(stations: list, vehicle_type: list, parameters: dict)`:
    - **Description:** Deploy a specified number of vehicles to each station.
    - **Parameters:**
        - `stations`: List of `Station` objects.
        - `vehicle_type`: List of `Vehicle` classes used in the simulation.
        - `parameters`:
            - `number`: The number of vehicles to deploy to each station.
    - **Returns:**  Does not return anything.

- `capacity_based(stations: list, vehicle_type: list, parameters: dict)`:
    - **Description:** Deploy vehicles to stations based on the station's capacity. The number of vehicles deployed to a station is equal to the station's capacity multiplied by the multiplier parameter.
    - **Parameters:**
        - `stations`: List of `Station` objects.
        - `vehicle_type`: List of `Vehicle` classes used in the simulation.
        - `parameters`:
            - `multiplier`: The multiplier used to calculate the number of vehicles to deploy to each station.
    - **Returns:**  Does not return anything.

---

### User
[Souce Code](../src/user.py) contains the `User` class. 

**Description**:
- The `User` class is responsible for requesting a vehicle from the departure station, moving the vehicle to the destination station, and releasing the vehicle to the destination station. The `User` class is also responsible for saving the relevant data for the simulation.

**Class Attributes:**
- env: simpy.Environment

**Methods:**
- `__init__(self, env: simpy.Environment, id: int, from_station: Station, to_station: Station, velocity: float)`:
    - **Description:**
        - Initializes the user with a unique ID, the departure station, the destination station, and the velocity of the user.
        - Initializes the user's data.
    - **Parameters:**
        - `id`: int
        - `from_station`: Station
        - `to_station`: Station
        - `velocity`: float
    - **Returns:** Does not return anything.
- `run(self):`:
    - **Description:**
        - When the user is generated, it requests a vehicle from the departure station.
        - When the user receives a vehicle, it moves the vehicle to the destination station.
        - When the user reaches the destination station, it releases the vehicle to the destination station.
    - **Returns:** Does not return anything.

---

### Utils
[Souce Code](../src/utils.py) contains utility functions.

**Variables:**
- `DEFAULT_DIRECTORY_PATH`: The default directory path for saving simulation results.

**Functions:**
- `create_directory_path() -> str`:
    - **Description:** Creates a directory path for saving simulation results.
    - **Returns:** The directory path.

- `get_directory_path() -> str`:
    - **Description:** Returns the directory path for saving simulation results.
    - **Returns:** The directory path.

- `load_config(config_path: str) -> dict`:
    - **Description:** Loads configuration data from a JSON file and returns it as a dictionary.
    - **Parameters:**
        - `config_path`: The path to the configuration file.
    - **Raises:** ConfigFileNotFound exception if the configuration file is not found.
    - **Returns:** The configuration data as a dictionary.

- `setup_logger(log_filename: str)`:
    - **Description:** Sets up the logger for the simulation.
    - **Parameters:**
        - `log_filename`: The name of the log file.
    - **Returns:** Does not return anything.

- `find_index_nearest_point(center: tuple, radius: float, points: list) -> int`:
    - **Description:** Finds the index of the point in the list of points that is closest to the circle defined by the center and the radius.
    - **Parameters:**
        - `center`: The center of the circle.
        - `radius`: The radius of the circle.
        - `points`: The list of points.
    - **Returns:** The index of the point in the list of points that is closest to the circle defined by the center and the radius.

---