from user import User
from station import Station

from simpy import Environment
from random import randint
import os, json

import logging
from logging.handlers import RotatingFileHandler

# Configure the root logger to write to a rotating log file
log_filename = os.path.join(os.path.dirname(__file__), "../data/logs/log.log")
max_log_size = 1 * 1024 * 1024  # 1 MB

# Set the log level for the root logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a RotatingFileHandler and set the log file name and max size
file_handler = RotatingFileHandler(log_filename, maxBytes=max_log_size, backupCount=5)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Get the root logger and add the file handler
root_logger = logging.getLogger()
root_logger.addHandler(file_handler)

# Remove the console handler to disable console output
for handler in root_logger.handlers:
    if isinstance(handler, logging.StreamHandler):
        root_logger.removeHandler(handler)

path_result = os.path.join(os.path.dirname(__file__), "../data/simulation_result/result.csv")
column_names = ["User ID", "From Station", "To Station", "Vehicle ID", "Unlock Time", "Lock Time", "Total Time", "Battery Used", "Distance"]
with open(path_result, "w") as f:
    print(",".join(column_names), file=f)

def main(env: Environment, config_data: dict):
    # caricamento classi
    try:
        import vehicle
        import station_storage
        import map
        import deployment

        # caricamento classe di mappa
        map_type = getattr(map, config_data["Map"]["Type"])

        # caricamento classe di storage
        storage = getattr(station_storage, config_data["Station"]["Station Storage"])

        # caricamento configurazione veicoli
        vehicle_cls = []
        for v in config_data["Vehicles"]["Type"]:
            cls = getattr(vehicle, v)
            vehicle_cls.append(cls)
            cls.load_config(os.path.join(os.path.dirname(__file__),"../config/vehicle.json"))

        # caricamento funzione di deploy veicoli
        deploy_vehicles = getattr(deployment, config_data["Vehicles"]["Deploy Vehicles"])

    except AttributeError:
        raise Exception(f'Invalid configuration file')
    except Exception as e:
        raise e

    # generazione posizioni stazioni
    positions = map_type(config_data["Map"]["Parameters"]).generate()

    # creazione stazioni
    stations = [
        Station(
            env = env,
            station_id = i,
            position = position, 
            capacity_per_time = config_data["Station"]["Capacity per Time"],
            max_concurrent_charging = config_data["Station"]["Max Concurrent Charging"],
            vehicles = storage(env, config_data["Station"]["Storage Parameters"])
            )
        for i, position in enumerate(positions)
        ]

    # creazione e positionamento veicoli
    deploy_vehicles(stations, vehicle_cls, config_data["Vehicles"]["Deploy Parameters"])
    
    # inizializzazione utenti
    users = []
    for i in range(config_data["Users"]["Number"]):
        p = randint(0,len(stations)-1)
        a = randint(0,len(stations)-1)
        while a == p:
            a = randint(0,len(stations)-1)
        users.append(User(env, i, stations[p], stations[a]))
    
    # avvio simulazione
    for user in users:
        yield env.timeout(config_data["Users"]["Interarrival Time"])
        env.process(user.run())
    
def analyze_results():
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np

    path_result = os.path.join(os.path.dirname(__file__), "../data/simulation_result/result.csv")
    df = pd.read_csv(path_result)

    # Column names:
    # ["User ID", "From Station", "To Station", "Vehicle ID", "Unlock Time", "Lock Time", "Total Time", "Battery Used", "Distance"]
    
    # plot unlock time
    plt.figure()
    sns.histplot(data=df, x="Unlock Time", bins=100)
    plt.savefig(os.path.join(os.path.dirname(__file__), "../data/simulation_result/unlock_time.png"))

    # plot lock time
    plt.figure()
    sns.histplot(data=df, x="Lock Time", bins=100)
    plt.savefig(os.path.join(os.path.dirname(__file__), "../data/simulation_result/lock_time.png"))

    # plot From Station
    plt.figure()
    sns.histplot(data=df, x="From Station", bins=100)
    plt.savefig(os.path.join(os.path.dirname(__file__), "../data/simulation_result/from_station.png"))

    # plot To Station
    plt.figure()
    sns.histplot(data=df, x="To Station", bins=100)
    plt.savefig(os.path.join(os.path.dirname(__file__), "../data/simulation_result/to_station.png"))

    # Plot vehicle used
    plt.figure()
    sns.histplot(data=df, x="Vehicle ID", bins=100)
    plt.savefig(os.path.join(os.path.dirname(__file__), "../data/simulation_result/vehicle_used.png"))

    # plot distance
    plt.figure()
    sns.histplot(data=df, x="Distance", bins=100)
    plt.savefig(os.path.join(os.path.dirname(__file__), "../data/simulation_result/distance.png"))

    # plot battery used
    plt.figure()
    sns.histplot(data=df, x="Battery Used", bins=100)
    plt.savefig(os.path.join(os.path.dirname(__file__), "../data/simulation_result/battery_used.png"))

    # plot total time
    plt.figure()
    sns.histplot(data=df, x="Total Time", bins=100)
    plt.savefig(os.path.join(os.path.dirname(__file__), "../data/simulation_result/total_time.png"))

if __name__ == "__main__":
    # inizializzazione ambiente
    env = Environment()

    # caricamento configurazione
    try:
        config_file = os.path.join(os.path.dirname(__file__),"../config/simulation.json")
        with open(config_file, 'r') as file:
            config_data = json.load(file)
    except FileNotFoundError:
        raise Exception(f'File {config_file} not found')
    except json.decoder.JSONDecodeError:
        raise Exception(f'File {config_file} is not a valid JSON file')
    except Exception as e:
        raise e

    # avvio simulazione
    env.process(main(env, config_data))
    
    # esecuzione simulazione
    env.run(until=config_data["Run Time"])

    # analisi risultati
    analyze_results()