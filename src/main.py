from user import User
from station import Station
from utils import setup_logger, find_index_nearest_point, create_directory_path, get_directory_path
import numpy as np

from simpy import Environment
from random import randint
import os, json

def main(env: Environment, config_data: dict):
    print("Setting up simulation...", end="\n\t")
    print("Loading configuration...", end=" ")
    # caricamento dinamico funzioni e moduli specificati nel file di configurazione
    try:
        # caricamento funzione di generazione posizioni stazioni
        generate_station_positions = getattr(__import__("station_deployment", 
                                                        fromlist=[config_data["station"]["deployment"]["type"]]
                                                        ),
                                            config_data["station"]["deployment"]["type"])

        # caricamento classe di storage per stazioni
        storage = getattr(__import__("station_storage", 
                                     fromlist=[config_data["station"]["storage"]["type"]]
                                     ),
                        config_data["station"]["storage"]["type"])

        # caricamento configurazione veicoli
        vehicle = __import__("vehicle", fromlist=config_data["vehicles"]["type"])
        
        vehicle_cls = []
        for v in config_data["vehicles"]["type"]:
            cls = getattr(vehicle, v)
            vehicle_cls.append(cls)
            cls.load_config(os.path.join(os.path.dirname(__file__),"../config/vehicle.json"))

        # caricamento funzione di deploy veicoli
        deploy_vehicles = getattr(__import__("vehicle_deployment", fromlist=[config_data["vehicles"]["deployment"]["type"]]),
                                  config_data["vehicles"]["deployment"]["type"])

    except AttributeError:
        raise Exception(f'Invalid configuration file')
    except Exception as e:
        raise e

    print("loaded", end="\n\t")


    print("Generating stations...", end=" ")
    # generazione posizioni stazioni
    positions = generate_station_positions(config_data["station"]["deployment"]["parameters"])

    # creazione stazioni
    stations = [
        Station(
            env = env,
            station_id = i,
            position = position, 
            capacity_per_time = config_data["station"]["charge_per_time"],
            max_concurrent_charging = config_data["station"]["max_concurrent_charging"],
            vehicles = storage(env, config_data["station"]["storage"]["parameters"])
            )
        for i, position in enumerate(positions)
        ]

    print("generated", end="\n\t")


    print("Deploying vehicles...", end=" ")
    # creazione e positionamento veicoli
    deploy_vehicles(stations, vehicle_cls, config_data["vehicles"]["deployment"]["parameters"])
    
    print("deployed", end="\n\t")


    print("Generating users...", end=" ")
    # inizializzazione utenti

    # fornisce accesso alla variabile env all'interno della classe User
    User.env = env

    """"users": {
        "generation": [
            [0, 1080, "uniform", 5786],
            [600, 840, "normal", 1714]
        ],
        "mean_distance": 3.02,
        "std_distance": 0.5,
        "std_velocity": 0.1
    },"""

    user_start_times = []
    for start, end, distribution, number in config_data["users"]["generation"]:
        if distribution == "uniform":
            user_start_times.extend(list(np.random.uniform(start, end, number)))
        elif distribution == "normal":
            mean = (start + end) / 2
            std = (end - start) / 6
            user_start_times.extend(list(np.around(np.random.normal(mean, std, number), decimals=5)))
        else:
            raise Exception(f'Invalid distribution {distribution}')

    distance = np.random.normal(config_data["users"]["mean_distance"], config_data["users"]["std_distance"], len(user_start_times))
    assert np.all(distance > 0), "Distance is negative"

    velocity = np.random.normal(config_data["users"]["mean_velocity"], config_data["users"]["std_velocity"], len(user_start_times))
    assert np.all(velocity > 0), "Velocity is negative"

    users = []
    for i in range(len(user_start_times)):
        p = randint(0,len(stations)-1)

        a = find_index_nearest_point(center = positions[p], radius = distance[i], points = positions)

        assert p != a, "User {} has same start and end station".format(i)

        users.append([User(i, stations[p], stations[a], velocity[i]), user_start_times[i]])
    
    ordered_users = sorted(users, key=lambda x: x[1])
    for i in range(len(ordered_users)-1, 0, -1):
        ordered_users[i][1] -= ordered_users[i-1][1]
        
    print("generated", end="\n\t")


    print("Starting simulation...", end=" ")
    # avvio simulazione
    for user, timeout in ordered_users:
        yield env.timeout(timeout)
        env.process(user.run())
    
def analyze_results(config):
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    print("Loading results...", end=" ")

    dir_path = get_directory_path()
    df = pd.read_csv(os.path.join(dir_path, "result.csv"))

    print("loaded", end="\n\t")

    number_of_users = sum([arr[3] for arr in config["users"]["generation"]])
    print("terminated the excution {}".format(df["User ID"].count(), number_of_users), end="\n\t")

    # Column names:
    # ["User ID", "From Station", "To Station", "Vehicle ID", "Unlock Time", "Lock Time", "Total Time", "Battery Used", "Distance"]
    
    print("Plotting results...", end=" ")
    # plot unlock time
    plt.figure()
    sns.histplot(data=df, x="Unlock Time", bins=100)
    plt.savefig(os.path.join(dir_path, "unlock_time.png"))

    # plot lock time
    plt.figure()
    sns.histplot(data=df, x="Lock Time", bins=100)
    plt.savefig(os.path.join(dir_path, "lock_time.png"))

    # plot From Station
    plt.figure()
    sns.histplot(data=df, x="From Station", bins=100)
    plt.savefig(os.path.join(dir_path, "from_station.png"))

    # plot To Station
    plt.figure()
    sns.histplot(data=df, x="To Station", bins=100)
    plt.savefig(os.path.join(dir_path, "to_station.png"))

    # Plot vehicle used
    plt.figure()
    sns.histplot(data=df, x="Vehicle ID", bins=100)
    plt.savefig(os.path.join(dir_path, "vehicle_used.png"))

    # plot distance
    plt.figure()
    sns.histplot(data=df, x="Distance", bins=100)
    plt.savefig(os.path.join(dir_path, "distance.png"))

    # plot battery used
    plt.figure()
    sns.histplot(data=df, x="Battery Used", bins=100)
    plt.savefig(os.path.join(dir_path, "battery_used.png"))

    # plot total time
    plt.figure()
    sns.histplot(data=df, x="Total Time", bins=100)
    plt.savefig(os.path.join(dir_path, "total_time.png"))

    print("plotted")

if __name__ == "__main__":
    # inizializzazione ambiente
    env = Environment()

    # caricamento file di configurazione
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

    # crea cartella per i risultati della simulazione
    sim_path = create_directory_path()

    # save configuration files
    with open(os.path.join(sim_path, "config.json"), "w") as f:
        json.dump(config_data, f)

    # setup logger
    root_logger = setup_logger(os.path.join(sim_path, "log.log"))

    # crea file per i risultati della simulazione
    result_path = os.path.join(sim_path, "result.csv")
    
    column_names = ["User ID", "From Station", "To Station", "Vehicle ID", "Unlock Time", "Lock Time", "Total Time", "Battery Used", "Distance"]
    with open(result_path, "w") as f:
        print(",".join(column_names), file=f)

    # avvio simulazione
    env.process(main(env, config_data))

    # esecuzione simulazione
    env.run(until=config_data["run_time"])

    print("Simulation finished")

    print("Analyzing results...", end="\n\t")
    # analisi risultati
    analyze_results(config_data)
    print("analyzed")