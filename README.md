# EVStationSimulator

## Overview

Welcome to EVStationSimulator, a simulation of a charging network for electric vehicles. This project aims to simulate the dynamics of electric vehicle charging stations, allowing users to explore and analyze the behavior of charging networks under various conditions. The simulation incorporates real data to generate authentic user travel requests, providing a realistic representation of electric vehicle charging scenarios.

### Simulation Outputs

At the conclusion of the simulation, various performance metrics are computed, including user wait times, station utilization rates, and overall system efficiency. These metrics offer valuable insights for assessing the effectiveness of charging station networks.

## Installation

To get started with EVStationSimulator, follow these steps:

1. Clone the repository to your local machine:

    ```bash
    git clone https://github.com/CapaCity-Team/EVStationSimulator.git
    ```

2. Navigate to the project directory:

    ```bash
    cd EVStationSimulator
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the simulation using the following command:

```bash
python main.py
```

This will initiate the simulation. After the simulation is complete, the results and analysis will be saved in the [results](data/simulation_result) folder. Each simulation run will be saved in a separate folder with an incremented count, for example:
- `data/simulation_result/simulation_0`
- `data/simulation_result/simulation_1`
- and so on.

## Configuration

Customize the simulation by adjusting parameters in the `simulation.json` and `vehicle.json` file. Refer to the [Configuration Guide](docs/configuration.md) for detailed information on available options.

You can also use the [Configuration Generator](conf_generator/generator.md) to generate a configuration file with your desired parameters.

If you need to modify the simulation code, refer to the [Developer Guide](docs/developer.md) for detailed information on the code structure and how to make changes.

## Documentation Structure

This documentation is organized into the following sections:

1. [Installation](docs/installation.md): Step-by-step instructions for installing EVStationSimulator.
2. [Usage](docs/usage.md): Details on how to run and interact with the simulation.
3. [Configuration Guide](docs/configuration.md): In-depth information on configuring simulation parameters.
4. [Developer Guide](docs/developer.md): Detailed insights into the code structure and how to make changes.

Feel free to navigate to specific sections based on your interests or needs.

## Contributing

If you'd like to contribute to this project, please fork the repository and create a pull request with your changes. We welcome contributions to improve the simulation and add new features.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

This project was inspired by the need to evaluate the performance of electric vehicle charging networks and contribute to the development of sustainable transportation solutions.

---

Feel free to explore the code, run the simulation, and use it for research or educational purposes. If you have any questions or encounter issues, please open an issue in this repository. We welcome your feedback and contributions to make this simulation even better!