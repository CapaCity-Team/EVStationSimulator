# Index

## Configuration Files
- [vehicle.json](#vehiclejson)
- [simulation.json](#simulationjson)

## Code
- [main.py](#mainpy)
- [map.py](#mappy)
- [station.py](#stationpy)
- [station_storage.py](#station_storagepy)
- [vehicle.py](#vehiclepy)
- [deployment.py](#deploymentpy)
- [user.py](#userpy)

# Configuration Files Details

## vehicle.json
The `vehicle.json` file serves as a dictionary with keys representing the names of vehicles and values specifying their parameters. Each vehicle has the following parameters:

- **BATTERY_CAPACITY**: Amount of energy the vehicle's battery can store.
- **ENERGY_CONSUMPTION**: Energy consumption per unit of distance traveled.
- **VELOCITY**: Distance the vehicle travel per unit of time.

## simulation.json

The `simulation.json` file is a dictionary with five keys:

### 1. Map
- **Type**: A string indicating the class name used for generating the map. Refer to the classes in the [map section](#mappy) section.
- **Parameters**: A dictionary containing parameters specific to the map class. Refer to the [map section](#mappy) section for details on each class.

### 2. Station
- **Capacity per Time**: Capacity charged by the station per unit of time.
- **Max Concurrent Charging**: Maximum number of vehicles that can be charged simultaneously.
- **Station Storage**: A string indicating the class name used for station storage. Refer to the classes in the [station storage section](#station_storagepy) section.
- **Storage Parameters**: A dictionary containing parameters specific to the station storage class. Refer to the [station storage section](#station_storagepy) section for details on each class.

### 3. Vehicle
- **Type**: A list containing the names of classes used for vehicles. Refer to the classes in the [vehicle section](#vehiclepy).
- **Deploy Vehicles**: A string indicating the name of the function used for deploying vehicles. Refer to the functions in the [deployment section](#deploymentpy).
- **Deploy Parameters**: A dictionary containing parameters specific to the deployment function. Refer to the [deployment section](#deploymentpy) for details on each function.

### 4. Users
- **Number**: The number of users generated in the simulation.
- **Interarrival Time**: The time between the generation of each user.

### 5. Run Time
- The time duration of the simulation.


# Customizing Simulation

To personalize the simulation, follow these steps:

## Configuration Files

1. **Adjusting Overall Simulation Settings:**
   - Modify parameters in `simulation.json` for global simulation configurations.

2. **Customizing Individual Vehicle Characteristics:**
   - Adjust parameters in `vehicle.json` for each vehicle's specific characteristics.

## Adding a New Vehicle

1. Create a New Vehicle Class:
   - In the `vehicle.py` file, create a new vehicle class by copying an existing one and changing the name.

2. Update `vehicle.json`:
   - Add a new key to the `vehicle.json` dictionary with the name of the new vehicle and its parameters.

## Adding a New Map

1. Create a New Map Class:
   - In the `map.py` file, create a new map class.

2. Update `simulation.json`:
   - Change the "Type" key to the name of the new map class in the `simulation.json` file.
   - Add the parameters of the new class to the "Parameters" dictionary in `simulation.json`.

## Adding a New Station Storage

1. Create a New Station Storage Class:
   - In the `station_storage.py` file, create a new station storage class.

2. Update `simulation.json`:
   - Change the "Station Storage" key to the name of the new station storage class in the `simulation.json` file.
   - Add the parameters of the new class to the "Storage Parameters" dictionary in `simulation.json`.

## Adding a New Deployment

1. Create a New Deployment Function:
   - In the `deployment.py` file, create a new deployment function.

2. Update `simulation.json`:
   - Change the "Deploy Vehicles" key to the name of the new deployment function in the `simulation.json` file.
   - Add the parameters of the new function to the "Deploy Parameters" dictionary in `simulation.json`.

---

# Code Files Details

## main.py

- **Functionality:**
  - Runs the entire simulation and performs data analysis.

- **Steps:**
  1. Reads the configuration files.
  2. Initializes the simulation, including:
     - Creating a map.
     - Generating station positions.
     - Generating stations.
     - Generating and deploying vehicles.
     - Generating users.
  3. Runs the simulation.
  4. Saves the results in a CSV file in the "data/simulation_results" folder.
  5. Conducts data analysis.
  6. Plots the results.

---

## map.py

- **Description:**
  - Contains map classes; all classes inherit from the map class and must implement the `generate` function.

- **Warning:**
  - The `__init__` method requires the following parameters:
    - `env`: simpy.Environment
    - `params`: dict
  - Will always be called with these parameters and only these parameters.
  - Additional parameters must be added to the `params` dict.

- **Generate Function:**
  - Takes no parameters.
  - Returns a list of tuples, where each tuple represents x and y coordinates of a station.

---

# station.py

This file contains the `Station` class.

## `Station` Class

### Parameters:

- `env`: simpy environment
- `station_id`: the id of the station
- `position`: the position of the station
- `capacity_per_time`: the capacity charged by the station per unit of time
- `max_concurrent_charging`: the maximum number of vehicles that can be charged simultaneously
- `vehicles`: the station storage object

### Methods:

#### `charge(self, vehicle: Vehicle, now: float):`

- Description: Performs the charging process for a vehicle.
- Returns: Does not return anything.

#### `charge_next_vehicle(self):`

- Description: Calls `charge` for the next vehicle in the queue.
- Returns: Does not return anything.

#### `stop_charging(self):`

- Description: Interrupts the charging process for all vehicles.
- Returns: Does not return anything.

#### `start_charging(self):`

- Description: Starts the charging process for however many vehicles can be charged simultaneously.
- Returns: Does not return anything.

#### `request_lock(self, vehicle: Vehicle):`

- Description: Requests a lock for a vehicle. It is a blocking function that waits until there is a slot available.
- Returns: Does not return anything.

#### `request_unlock(self, user):`

- Description: Requests an unlock for a vehicle and assigns it to a user. It is a blocking function that waits until there is a vehicle available.
- Returns: Does not return anything.

#### `distance(self, station) -> float:`

- Description: calc the distance between this station and the station passed as a parameter.
- Returns: float.

#### `deploy(self, vehicles: list):`

- Description: Deploys the vehicles to the station.
- Returns: Does not return anything.

---
        
# station_storage.py

This file contains the station storage classes. All station storage classes inherit from the station storage class.

## Station Storage Classes

### Description:

- Responsible for keeping track of vehicles available at a station.
- Responsible for selecting the next vehicle to charge.

**Note:** The station storage is not responsible for charging vehicles.

### Warning:

- The `__init__` method requires the following parameters:
  - `env`: simpy.Environment
  - `params`: dict
  - Will always be called with these parameters and only these parameters.
  - Additional parameters must be added to the `params` dict.

### Methods:

#### `charged(self, vehicle: Vehicle):`

- Description: Notifies the station storage that a vehicle has been fully charged so the available vehicles can be updated.
- Returns: Does not return anything.

#### `add_vehicle(self, vehicle: Vehicle):`

- Description: Adds a vehicle to the station storage.
- Returns: Does not return anything.

#### `pop_vehicle(self) -> Vehicle:`

- Description: Removes a vehicle from the station storage.
- Returns: The removed vehicle.

#### `next_vehicle_to_charge(self, charging_vehicles: list) -> Vehicle:`

- Description: Selects the next vehicle to charge from the station storage.
- Parameters:
  - `charging_vehicles`: List of vehicles currently charging (to avoid selecting them).
- Returns: The selected vehicle.

#### `need_reschedule(self) -> bool:`

- Description: Called when a vehicle is added to the station storage. Checks if the station storage needs to reschedule the charging of vehicles.
- Returns: `True` if the station storage needs to reschedule the charging of vehicles.

#### `lock(self, vehicle):`

- Description: Waits for a slot to be available and adds the vehicle to the station storage. Must be implemented as a generator and yield once.
- Returns: Does not return anything.

#### `unlock(self, user):`

- Description: Waits for a vehicle to be available, removes it from the station storage, and assigns it to the user. Must be implemented as a generator and yield once.
- Returns: Does not return anything.

#### `count(self) -> int:`

- Description: Returns the number of vehicles currently stored in the station storage.

#### `deploy(self, vehicles: list):`

- Description: Deploys a list of vehicles to the station storage. Used in the deployment phase to initialize the station storage. Must NOT be implemented as a generator.
- Returns: Does not return anything.

---

# vehicle.py

This file contains the vehicle classes. All vehicle classes inherit from the vehicle class and must implement the following three property functions.

### Initialization

#### `__init__(self, vehicle_id):`

- Description: Initializes the Vehicle with a unique ID and a default battery level of 1.

### Property Functions

#### `@property max_capacity(self):`

- Description: Returns the maximum capacity of the vehicle.

#### `@property energy_consumption(self):`

- Description: Returns the energy consumption of the vehicle.

#### `@property velocity(self):`

- Description: Returns the velocity of the vehicle.

### Movement

#### `move(self, distance: float) -> float:`

- Description: Moves the vehicle by a specified distance, updates the battery level, and returns the time taken.
- Returns: The time taken to move the vehicle by the specified distance.

### Battery and Charging

#### `capacity(self) -> float:`

- Description: Calculates the current capacity of the vehicle based on the battery level.
- Returns: The current capacity of the vehicle.

#### `capacity_left(self) -> float:`

- Description: Calculates the remaining capacity of the vehicle based on the battery level.
- Returns: The remaining capacity of the vehicle.

#### `is_charged(self) -> bool:`

- Description: Checks if the vehicle is fully charged (battery level is 1).
- Returns: `True` if the vehicle is fully charged, `False` otherwise.

#### `fully_charge(self):`

- Description: Fully charges the vehicle by setting the battery level to 1.
- Returns: Does not return anything.

#### `charge(self, percentage):`

- Description: Charges the vehicle by a specified percentage, ensuring the battery level does not exceed 1.

### Configuration Loading

#### `@classmethod load_config(cls, config_file):`

- Description: Loads configuration data from a JSON file and updates class attributes accordingly.
- Raises: ConfigFileNotFound exception if the configuration file is not found.
- Returns: Does not return anything.

---

# deployment.py

This file contains deployment functions.

All deployment functions must follow this format:

```python
def deploy_func_name(stations: list, vehicle_type: list, parameters: dict):
    # code
```

- **Description:**
  - The deploy function deploys vehicles to stations based on specified criteria.

- **Parameters:**
  - `stations`: List of `Station` objects.
  - `vehicle_type`: List of `Vehicle` classes used in the simulation.
  - `parameters`: Dictionary of parameters specified in the `simulation.json` file.

- **Returns:**
  - Does not return anything.

---

# user.py

This file contains the `User` class.

## `User` Class

### Parameters:

- `env`: simpy.Environment
- `id`: int
- `from_station`: Station
- `to_station`: Station

### Method:

#### `run(self):`

- **Description:**
  - When the user is generated, it requests a vehicle from the departure station.
  - When the user receives a vehicle, it moves the vehicle to the destination station.
  - When the user reaches the destination station, it releases the vehicle to the destination station.

- **Returns:**
  - Does not return anything.

---