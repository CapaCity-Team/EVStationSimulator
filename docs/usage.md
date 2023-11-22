# Usage Guide

This guide provides detailed instructions on how to run and interact with EVStationSimulator.

## Running the Simulation

To run the simulation, follow these steps:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/CapaCity-Team/EVStationSimulator.git
   ```

2. **Navigate to the Project Directory:**

   ```bash
   cd EVStationSimulator
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Simulation:**

   ```bash
   python main.py
   ```

   This command initiates the simulation.
   The output in the console will look like this:

    ```
    Setting up simulation...
        Loading configuration... loaded
        Generating stations... generated
        Deploying vehicles... deployed
        Generating users... generated
    Finished setup

    Starting simulation... Simulation finished

    Analyzing results...
        Loading results... loaded
        Calculating statistics... calculated
        Plotting results... plotted
    analyzed
    ```

## Viewing Results

After the simulation is complete, the results and performance metrics are stored in the [results](../results) folder. Each simulation run is saved in a separate folder with an incremented count (e.g., `results/simulation_0`, `results/simulation_1`, etc.).

the directory structure looks like this:

```
data/
├── simulation_result/
    └── simulation_0/
        ├── battery_used.png
        ├── from_station.png
        ├── log.log
        ├── simulation.json
        ├── to_station.png
        ├── unlock_time.png
        ├── vehicle_used.png
        ├── distance.png
        ├── lock_time.png
        ├── result.csv
        ├── statistics.txt
        ├── total_time.png
        └── vehicle.json
    └── simulation_1/
        ...
```

- **`log.log`:** Contains the log of the simulation.

- **`simulation.json`:** Holds the configuration used for the simulation.

- **`vehicle.json`:** Stores the configuration used for the vehicles.

- **`result.csv`:** Contains the raw data for the simulation results.

- **`statistics.txt`:** Provides calculated performance metrics.

- **`.png` files:** Include plots representing the simulation results.

---

Congratulations! You have successfully run EVStationSimulator. Explore the [Documentation Structure](../README.md#documentation-structure) for more in-depth information on other aspects of the project like costumizing the simulation.