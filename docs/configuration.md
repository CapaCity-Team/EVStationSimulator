# Configuration Guide

This guide provides detailed information on configuring EVStationSimulator to suit your specific requirements. Customize the simulation parameters to achieve the desired behavior for your electric vehicle charging station network simulation.

## Configuration Files

EVStationSimulator uses two main configuration files:

1. **simulation.json:**
   
   The [simulation configuration file](../config/simulation.json) acts as a central hub for orchestrating the simulation, housing parameters that influence the simulation duration, station characteristics, and user behavior.
   
   The file follows a dictionary structure with the following keys:
    ```json
   {
         "station": {
            ...
         },
         "vehicles": {
            ...
         },
         "users": {
            ...
         },
         "run_time": 1000
   }
   ```

     - **`station`**: This section allows fine-tuning of station configurations.

        ```json
        "station": {
            "charge_per_time": 50,
            "max_concurrent_charging": 5,
            "storage": {
                ...
            },
            "deployment": {
                ...
            }
        }
        ```
        - **`charge_per_time`**: The amount of energy charged per unit of time.
        - **`max_concurrent_charging`**: The maximum number of vehicles that can be charged simultaneously.


        - **`storage`**: dictionary with the following forms:
            ```json
            "storage": {
                "type": "LIFO",
                "parameters": {
                    "capacity": 20
                }
            }
            ```
            **`type`**: string indicating the name of the function used for generating stations. 
            
            **`parameters`**: dictionary containing parameters specific to the station storage class.

            Refer to the [station storage](#station-storage) section for details on each function.

        - **deployment**: dictionary with the following forms:
            ```json
            "deployment": {
                "type": "grid",
                "parameters": {
                    "rows": 18,
                    "columns": 18,
                    "width": 1
                }
            }
            ```

            **`type`**: string indicating the name of the function used for deploying stations.
            
            **`parameters`**: dictionary containing parameters specific to the deployment function.

            Refer to the functions in the [station deployment](#station-deployment) section for details on each function.

     
     - **`vehicles`**:This section allows fine-tuning of station configurations.
        
        ```json
        "vehicles": {
            "type": ["Scooter"],
            
            "deployment": {
                ...
            }
        }
        ```

        - **`type`**: list containing the names of classes used for vehicles.

        - **`deployment`**: dictionary with the following forms:
            ```json
            "deployment": {
                "type": "uniform",
                "parameters": {
                    "vehicles_per_station": 15
                }
            }
            ```

            **`type`**: string indicating the name of the function used for deploying vehicles.

            **`parameters`**: dictionary containing parameters specific to the deployment function.

            Refer to the functions in the [vehicle deployment](#vehicle-deployment) section for details on each function.
        

     - **`users`**: Tailor user behavior within the simulation through this key.

        Example:
        ```json
        "users": {
            "generation": [
                ...
            ],
            "mean_distance": 3.02,
            "std_distance": 0.5,
            "mean_velocity": 0.33,
            "std_velocity": 0.05
        }
        ```

        - **`generation`**: A list containing the generation details for new users across the simulation. Each element represents a period of time during which users are generated in the specified distribution and number.

            Each element in the list is a list of four elements:
            
            ```
            [
                [start_time, end_time, distribution, number]
            ]
            ```

            - **`start_time`**: start time of the period in units of simulation time.
            - **`end_time`**: end time of the period in units of simulation time.
            - **`distribution`**: type of distribution, either "uniform" or "normal."
            - **`number`**: number of users to be generated during the specified period.

            Example:
            ```json
            [
                [0, 100, "uniform", 10],
                [100, 200, "normal", 20]
            ]
            ```

            **NOTE**: Can be used overlapping time periods, as each element is evaluated separately and then summed together.

        - **`mean_distance`**: Mean distance traveled by users.
        - **`std_distance`**: Standard deviation of the distance traveled by users.
        - **`mean_velocity`**: Mean velocity of users.
        - **`std_velocity`**: Standard deviation of the velocity of users.

        Each user is generated with a random distance to travel and velocity based on the mean and standard deviation specified in the `users` dictionary.

     - **`run_time`**: Set the total duration of the simulation in the desired time unit (e.g., minutes, hours).

2. **vehicle.json**:

    The [vehicle configuration file](../config/simulation.json) contains the parameters for each vehicle class used in the simulation. The file follows a dictionary structure with the following keys:
    ```json
    {
        "Scooter": {
            "BATTERY_CAPACITY" : 1000,
            "ENERGY_CONSUMPTION" : 37.5
        },

        "Bike": {
            "BATTERY_CAPACITY" : 80,
            "ENERGY_CONSUMPTION" : 0.04
        }
    }
    ```

    - **`BATTERY_CAPACITY`**: The maximum amount of energy that can be stored in the vehicle's battery.

    - **`ENERGY_CONSUMPTION`**: The amount of energy consumed per unit of distance traveled.

## Station Storage

### LIFO
- Last In, First Out (LIFO) storage. The charging station will charge the vehicle that arrived last first.

    - `type`: "LIFO"

    - `parameters`:
        - "capacity": int

### DualStack:
- Utilizes two stacks to store vehicles—one for locked vehicles and one for unlocked vehicles. The stacks will swap for optimal availability of vehicles. The charging station will charge vehicles in the unlocked stack first, followed by vehicles in the locked stack.

    - `type`: "DualStack"
    - `parameters`:
        - "stack1_size": int
        - "stack2_size": int

## Station Deployment

### grid:
- Deploy a grid of stations with the specified number of rows and columns. The distance between each node is specified by the width parameter.
    - `type`: "grid"
    - `parameters`: 
        - "rows": int
        - "columns": int
        - "width": float

### square_random:
- Sample a specified number of points from a square of the specified size.
    - `type`: "square_random"
    - `parameters`: 
        - "size": float
        - "number": int

### circle_random:
- Sample a specified number of points from a circle of the specified radius.
    - `type`: "circle_random"
    - `parameters`:
        - radius: float
        - number: int

## Vehicle Deployment

### uniform:
- Deploy the same number of vehicles for each station
    - `type`: "uniform"
    - `parameters`:
        - "vehicles_per_station": int

### capacity_based:
- Deploy a number of vehicles proportional to the station's capacity
    - `type`: "capacity_based"
    - `parameters`:
        - "multiplier": float

## Customizing Configuration

To customize the simulation behavior, modify the values within the configuration files according to your requirements.

## Configuration Generator


For ease of use, you can use the [Configuration Generator](../conf_generator/generator.md) to generate configuration files with your desired parameters.

## Example Configuration

Here's an example configuration snippet for `simulation.json`:

```json
{
    "station": {
        "charge_per_time": 100,
        "max_concurrent_charging": 3,
        
        "storage":{
            "type": "DualStack",
            "parameters":{
                "stack1_size": 15,
                "stack2_size": 15
            }
        },

        "deployment": {
            "type": "grid",
            "parameters": {
                "rows": 18,
                "columns": 18,
                "width": 1
            }
        }
    },

    "vehicles": {
        "type": ["Scooter"],
        
        "deployment": {
            "type": "uniform",
            "parameters": {
                "vehicles_per_station": 15
            }
        }
    },

    "users": {
        "generation": [
            [0, 1080, "uniform", 5786],
            [600, 840, "normal", 1714]
        ],
        "mean_distance": 3.02,
        "std_distance": 0.5,
        "mean_velocity": 0.33,
        "std_velocity": 0.05
    },
    
    "run_time": 1500
}
```

And for `vehicle.json`:

```json
{
    "Scooter": {
        "BATTERY_CAPACITY" : 1000,
        "ENERGY_CONSUMPTION" : 37.5
    },

    "Bike": {
        "BATTERY_CAPACITY" : 80,
        "ENERGY_CONSUMPTION" : 0.04
    }
}
```

Adjust these examples based on your simulation requirements.

## Next Steps

After configuring EVStationSimulator, you can proceed to [running the simulation](usage.md) to observe the behavior of your charging network.

For more in-depth information on other aspects of the project, explore the [Documentation Structure](README.md#documentation-structure).