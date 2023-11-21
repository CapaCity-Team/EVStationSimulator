from simpy import Environment
from user import User
from station import Station
from utils import setup_logger, create_directory_path, load_config, find_index_nearest_point
from random import randint
import os, json, shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def simulation(env: Environment, config_data: dict):
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
        
    print("generated")

    print("Finished setup\n")

    print("Starting simulation...", end=" ")
    # avvio simulazione
    for user, timeout in ordered_users:
        yield env.timeout(timeout)
        env.process(user.run())

def analyze_results(dir_path, config):
    print("Loading results...", end=" ")

    df = pd.read_csv(os.path.join(dir_path, "result.csv"))

    print("loaded", end="\n\t")

    # Column names:
    # ["User ID", "Start Time", "From Station", "To Station", "Vehicle ID", "Unlock Time", "Lock Time", "Total Time", "Battery Used", "Distance"]

    print("Calculating statistics...", end=" ")

    # calculate statistics
    number_of_users = sum([arr[3] for arr in config["users"]["generation"]])
    number_of_completed_trips = len(df)
    
    # about lock time
    avg_lock_time = df["Lock Time"].mean()
    max_lock_time = df["Lock Time"].max()
    min_lock_time = df["Lock Time"].min()
    median_lock_time = df["Lock Time"].median()
    mode_lock_time = df["Lock Time"].mode()[0]
    variance_lock_time = df["Lock Time"].var()

    # about unlock time
    avg_unlock_time = df["Unlock Time"].mean()
    max_unlock_time = df["Unlock Time"].max()
    min_unlock_time = df["Unlock Time"].min()
    median_unlock_time = df["Unlock Time"].median()
    mode_unlock_time = df["Unlock Time"].mode()[0]
    variance_unlock_time = df["Unlock Time"].var()

    # about distance
    avg_distance = df["Distance"].mean()
    max_distance = df["Distance"].max()
    min_distance = df["Distance"].min()
    median_distance = df["Distance"].median()
    mode_distance = df["Distance"].mode()[0]
    variance_distance = df["Distance"].var()

    # about departures per station
    group = df.groupby("From Station").count()["User ID"]
    avg_departures_per_station = group.mean()
    max_departures_per_station = group.max()
    min_departures_per_station = group.min()
    median_departures_per_station = group.median()
    mode_departures_per_station = group.mode()[0]
    variance_departures_per_station = group.var()
    
    # about arrivals per station
    group = df.groupby("To Station").count()["User ID"]
    avg_arrivals_per_station = group.mean()
    max_arrivals_per_station = group.max()
    min_arrivals_per_station = group.min()
    median_arrivals_per_station = group.median()
    mode_arrivals_per_station = group.mode()[0]
    variance_arrivals_per_station = group.var()

    # about use of vehicles
    group = df.groupby("Vehicle ID").count()["User ID"]
    avg_trips_per_vehicle = group.mean()
    max_trips_per_vehicle = group.max()
    min_trips_per_vehicle = group.min()
    median_trips_per_vehicle = group.median()
    mode_trips_per_vehicle = group.mode()[0]
    variance_trips_per_vehicle = group.var()

    # save this statistics in a file
    with open(os.path.join(dir_path, "statistics.txt"), "w") as f:
        print("Number of users: {}".format(number_of_users), file=f)
        print("Number of completed trips: {}".format(number_of_completed_trips), file=f)
        print("Average lock time: {}".format(avg_lock_time), file=f)
        print("Maximum lock time: {}".format(max_lock_time), file=f)
        print("Minimum lock time: {}".format(min_lock_time), file=f)
        print("Median lock time: {}".format(median_lock_time), file=f)
        print("Mode lock time: {}".format(mode_lock_time), file=f)
        print("Variance lock time: {}".format(variance_lock_time), file=f)
        print("Average unlock time: {}".format(avg_unlock_time), file=f)
        print("Maximum unlock time: {}".format(max_unlock_time), file=f)
        print("Minimum unlock time: {}".format(min_unlock_time), file=f)
        print("Median unlock time: {}".format(median_unlock_time), file=f)
        print("Mode unlock time: {}".format(mode_unlock_time), file=f)
        print("Variance unlock time: {}".format(variance_unlock_time), file=f)
        print("Average distance: {}".format(avg_distance), file=f)
        print("Maximum distance: {}".format(max_distance), file=f)
        print("Minimum distance: {}".format(min_distance), file=f)
        print("Median distance: {}".format(median_distance), file=f)
        print("Mode distance: {}".format(mode_distance), file=f)
        print("Variance distance: {}".format(variance_distance), file=f)
        print("Average departures per station: {}".format(avg_departures_per_station), file=f)
        print("Maximum departures per station: {}".format(max_departures_per_station), file=f)
        print("Minimum departures per station: {}".format(min_departures_per_station), file=f)
        print("Median departures per station: {}".format(median_departures_per_station), file=f)
        print("Mode departures per station: {}".format(mode_departures_per_station), file=f)
        print("Variance departures per station: {}".format(variance_departures_per_station), file=f)
        print("Average arrivals per station: {}".format(avg_arrivals_per_station), file=f)
        print("Maximum arrivals per station {}".format(max_arrivals_per_station), file=f)
        print("Minimum arrivals per station: {}".format(min_arrivals_per_station), file=f)
        print("Median arrivals per station: {}".format(median_arrivals_per_station), file=f)
        print("Mode arrivals per station: {}".format(mode_arrivals_per_station), file=f)
        print("Variance arrivals per station: {}".format(variance_arrivals_per_station), file=f)
        print("Average trips per vehicle: {}".format(avg_trips_per_vehicle), file=f)
        print("Maximum trips per vehicle: {}".format(max_trips_per_vehicle), file=f)
        print("Minimum trips per vehicle: {}".format(min_trips_per_vehicle), file=f)
        print("Median trips per vehicle: {}".format(median_trips_per_vehicle), file=f)
        print("Mode trips per vehicle: {}".format(mode_trips_per_vehicle), file=f)
        print("Variance trips per vehicle: {}".format(variance_trips_per_vehicle), file=f)

    print("calculated", end="\n\t")
    
    print("Plotting results...", end=" ")
    # plot a fig with time on the x from 0 to config["run_time"] and on the y the number of users
    plt.figure()
    sns.histplot(data=df, x="Start Time", bins=100)
    plt.savefig(os.path.join(dir_path, "start_time.png"))

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

def main():
    # inizializzazione ambiente
    env = Environment()

    # caricamento file di configurazione
    config_data = load_config(os.path.join(os.path.dirname(__file__),"../config/simulation.json"))

    # crea cartella per i risultati della simulazione
    sim_path = create_directory_path()

    # make a copy of the configuration files
    shutil.copyfile(os.path.join(os.path.dirname(__file__),"../config/simulation.json"), os.path.join(sim_path, "simulation.json"))
    shutil.copyfile(os.path.join(os.path.dirname(__file__),"../config/vehicle.json"), os.path.join(sim_path, "vehicle.json"))

    # setup logger
    setup_logger(os.path.join(sim_path, "log.log"))

    # crea file per i risultati della simulazione
    result_path = os.path.join(sim_path, "result.csv")
    
    column_names = ["User ID", "Start Time", "From Station", "To Station", "Vehicle ID", "Unlock Time", "Lock Time", "Total Time", "Battery Used", "Distance"]
    with open(result_path, "w") as f:
        print(",".join(column_names), file=f)

    # avvio simulazione
    env.process(simulation(env, config_data))
    
    # esecuzione simulazione
    env.run(until=config_data["run_time"])

    print("Simulation finished\n")

    print("Analyzing results...", end="\n\t")
    # analisi risultati
    analyze_results(sim_path, config_data)
    print("analyzed")


if __name__ == "__main__":
    main()