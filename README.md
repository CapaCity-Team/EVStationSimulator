# Electric Vehicle Charging Station Simulation

![Demo](demo.gif)

This GitHub repository contains a simulation of an electric vehicle charging station network in a 2D grid. In this simulation, electric vehicles move between stations to get charged. Each vehicle consumes energy while moving, and each station has a maximum number of vehicles it can accommodate and a certain power to divide among the vehicles.

## Overview

The main goal of this project is to simulate the operation of an electric vehicle charging network and measure various performance metrics, including user wait times, station utilization, and overall system efficiency.

## Features

- **2D Grid Simulation:** The simulation takes place in a 2D grid where electric vehicle stations are distributed.

- **Real Data Integration:** The simulation uses real data to generate user requests for traveling from one station to another. This data is based on historical usage patterns.

- **Vehicle Movement:** Vehicles move within the grid, consuming energy in the process.

- **Charging:** Vehicles visit stations to recharge their batteries. Each station has a limited power supply, and the power is divided among the connected vehicles.

- **Performance Metrics:** At the end of the simulation, various performance metrics are measured, including user wait times, station utilization, and overall system efficiency.

## Getting Started

To run the simulation, follow these steps:

1. Clone the repository to your local machine:
   ```shell
   git clone https://github.com/yourusername/electric-vehicle-simulation.git
   ```
2. Navigate to the project directory:
   ```shell
   cd electric-vehicle-simulation
   ```
3. Install the required dependencies:
   ```shell
   pip install -r requirements.txt
   ```
4. Run the simulation:
   ```shell
    python main.py
   ```
## Configuration

You can configure various aspects of the simulation in the `config.json` file. Here, you can set parameters such as the grid size, the number of stations, the maximum number of vehicles per station, and the power available at each station.

## Results and Analysis

After running the simulation, the results and performance metrics will be displayed in the console. You can analyze these metrics to evaluate the efficiency of the electric vehicle charging network.

## Contributing

If you'd like to contribute to this project, please fork the repository and create a pull request with your changes. We welcome contributions to improve the simulation and add new features.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project was inspired by the need to evaluate the performance of electric vehicle charging networks and contribute to the development of sustainable transportation solutions.

---

Feel free to explore the code, run the simulation, and use it for research or educational purposes. If you have any questions or encounter issues, please open an issue in this repository. We welcome your feedback and contributions to make this simulation even better!
