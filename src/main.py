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

    """"
    "users": {
        "linear": [
            [0, 60, 245],
            [60, 90, 340],
            [90, 120, 380],
            [120, 150, 420],
            [150, 180, 460],
            [180, 1080, 15000]
        ],
        "normal":[
            [60, 180, 8, 2.66, 857],
            [420, 540, 14, 4.33, 286],
            [720, 960, 18, 6, 1837]

        ],
        "mean_distance": 3.3,
        "std_distance": 0.6,
        "mean_velocity": 0.28,
        "std_velocity": 0.05
    }
    """

    user_start_times = []
    for start, end, number in config_data["users"]["linear"]:
        user_start_times.extend(list(np.random.uniform(start, end, int(number))))

    for start, end, number in config_data["users"]["normal"]:
        for sample in np.around(np.random.normal(0, 1, int(number)), decimals=5):
            user_start_times.append(start + ((sample + 3)/3)*(end-start))

    distance = np.random.normal(config_data["users"]["mean_distance"], config_data["users"]["std_distance"], len(user_start_times))
    assert np.all(distance > 0), "Distance is negative"

    velocity = np.random.normal(config_data["users"]["mean_velocity"], config_data["users"]["std_velocity"], len(user_start_times))
    assert np.all(velocity > 0), "Velocity is negative"
    
    ordered_times = sorted(user_start_times)

    for i in range(len(ordered_times)-1, 0, -1):
        ordered_times[i] -= ordered_times[i-1]

    users = []

    if(config_data["no_degeneration"]):
        """
        "no_degeneration": true,
        "v_per_station": 15,
        "station_capacity": 30,
        "tries": 5000,
        "redistribution": 1000,
        """
        v_max = config_data["station_capacity"]
        starting_v = config_data["v_per_station"]
        max_tries = config_data["tries"]
        user_to_redistribute = config_data["redistribution"] - 1
        
        v = np.full( len(stations), starting_v)
        redistribution = 0
        for i in range(len(ordered_times)):
            if redistribution > 0:
                # Find the maximum value
                max_value = np.max(v)

                # Find the indices of all occurrences of the maximum value
                max_indices = np.where(v == max_value)[0]
                p = np.random.choice(max_indices)

                # Find the minimum value
                min_value = np.min(v)

                # Find the indices of all occurrences of the minimum value
                min_indices = np.where(v == min_value)[0]
                a = np.random.choice(min_indices)

                v[p] -= 1
                v[a] += 1
                users.append([User(i, stations[p], stations[a], velocity[i]), ordered_times[i]])
                redistribution -= 1
            else:
                tries = 0
                while True:
                    if tries > 5000:
                        # prossimi x utenti andranno da stazzioni piene a stazioni vuote
                        redistribution = user_to_redistribute

                        # Find the maximum value
                        max_value = np.max(v)

                        # Find the indices of all occurrences of the maximum value
                        max_indices = np.where(v == max_value)[0]
                        p = np.random.choice(max_indices)

                        # Find the minimum value
                        min_value = np.min(v)

                        # Find the indices of all occurrences of the minimum value
                        min_indices = np.where(v == min_value)[0]
                        a = np.random.choice(min_indices)

                    else:
                        p = randint(0,len(stations)-1)
                        while v[p] <= 4:
                            p = randint(0,len(stations)-1)

                        a = find_index_nearest_point(center = positions[p], radius = distance[i], points = positions)
                        
                        if p == a or v[a] >= v_max - 4:
                            tries += 1
                            continue
                    
                    v[p] -= 1
                    v[a] += 1
                    users.append([User(i, stations[p], stations[a], velocity[i]), ordered_times[i]])
                    break
    else:
        for i in range(len(ordered_times)):
            p = randint(0,len(stations)-1)

            a = find_index_nearest_point(center = positions[p], radius = distance[i], points = positions)

            assert p != a, "User {} has same start and end station".format(i)

            users.append([User(i, stations[p], stations[a], velocity[i]), ordered_times[i]])
       
    print("generated")

    print("Finished setup\n")

    print("Starting simulation...", end=" ")
    # avvio simulazione
    for user, timeout in users:
        yield env.timeout(timeout)
        env.process(user.run())

def analyze_results(dir_path, config):
    print("Loading results...", end=" ")

    df = pd.read_csv(os.path.join(dir_path, "result.csv"))

    print("loaded", end="\n\t")

    # Column names:
    # ["User ID", "Start Time", "From Station", "To Station", "Vehicle ID", "Unlock Time", "Lock Time", "Total Time", "Battery Used", "Distance", "Velocity"]
            
    print("Calculating statistics...", end=" ")

    # calculate statistics
    number_of_users = sum([int(arr[2]) for arr in config["users"]["linear"]]) + sum([int(arr[2]) for arr in config["users"]["normal"]])
    number_of_completed_trips = len(df)

    # about distance
    avg_distance = df["Distance"].mean()
    max_distance = df["Distance"].max()
    min_distance = df["Distance"].min()
    median_distance = df["Distance"].median()
    mode_distance = df["Distance"].mode()[0]
    variance_distance = df["Distance"].var()

    # about velocity
    avg_velocity = df["Velocity"].mean()
    max_velocity = df["Velocity"].max()
    min_velocity = df["Velocity"].min()
    median_velocity = df["Velocity"].median()
    mode_velocity = df["Velocity"].mode()[0]
    variance_velocity = df["Velocity"].var()

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

    # about trip time (total time - lock time - unlock time)
    avg_trip_time = (df["Total Time"] - df["Lock Time"] - df["Unlock Time"]).mean()
    max_trip_time = (df["Total Time"] - df["Lock Time"] - df["Unlock Time"]).max()
    min_trip_time = (df["Total Time"] - df["Lock Time"] - df["Unlock Time"]).min()
    median_trip_time = (df["Total Time"] - df["Lock Time"] - df["Unlock Time"]).median()
    mode_trip_time = (df["Total Time"] - df["Lock Time"] - df["Unlock Time"]).mode()[0]
    variance_trip_time = (df["Total Time"] - df["Lock Time"] - df["Unlock Time"]).var()

    # about total time
    avg_total_time = df["Total Time"].mean()
    max_total_time = df["Total Time"].max()
    min_total_time = df["Total Time"].min()
    median_total_time = df["Total Time"].median()
    mode_total_time = df["Total Time"].mode()[0]
    variance_total_time = df["Total Time"].var()

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
        print(
"""
Number of users: {}
Number of completed trips: {}

Average distance: {}
Maximum distance: {}
Minimum distance: {}
Median distance: {}
Mode distance: {}
Variance distance: {}

Average velocity: {}
Maximum velocity: {}
Minimum velocity: {}
Median velocity: {}
Mode velocity: {}
Variance velocity: {}

Average lock time: {}
Maximum lock time: {}
Minimum lock time: {}
Median lock time: {}
Mode lock time: {}
Variance lock time: {}

Average unlock time: {}
Maximum unlock time: {}
Minimum unlock time: {}
Median unlock time: {}
Mode unlock time: {}
Variance unlock time: {}

Average trip time: {}
Maximum trip time: {}
Minimum trip time: {}
Median trip time: {}
Mode trip time: {}
Variance trip time: {}

Average total time (unlock + trip + lock): {}
Maximum total time: {}
Minimum total time: {}
Median total time: {}
Mode total time: {}
Variance total time: {}

Average departures per station: {}
Maximum departures per station: {}
Minimum departures per station: {}
Median departures per station: {}
Mode departures per station: {}
Variance departures per station: {}

Average arrivals per station: {}
Maximum arrivals per station {}
Minimum arrivals per station: {}
Median arrivals per station: {}
Mode arrivals per station: {}
Variance arrivals per station: {}

Average trips per vehicle: {}
Maximum trips per vehicle: {}
Minimum trips per vehicle: {}
Median trips per vehicle: {}
Mode trips per vehicle: {}
Variance trips per vehicle: {}
""".format(
    number_of_users, number_of_completed_trips,
    avg_distance, max_distance, min_distance, median_distance, mode_distance, variance_distance,
    avg_velocity, max_velocity, min_velocity, median_velocity, mode_velocity, variance_velocity,
    avg_lock_time, max_lock_time, min_lock_time, median_lock_time, mode_lock_time, variance_lock_time,
    avg_unlock_time, max_unlock_time, min_unlock_time, median_unlock_time, mode_unlock_time, variance_unlock_time,
    avg_trip_time, max_trip_time, min_trip_time, median_trip_time, mode_trip_time, variance_trip_time,
    avg_total_time, max_total_time, min_total_time, median_total_time, mode_total_time, variance_total_time,
    avg_departures_per_station, max_departures_per_station, min_departures_per_station, median_departures_per_station, mode_departures_per_station, variance_departures_per_station,
    avg_arrivals_per_station, max_arrivals_per_station, min_arrivals_per_station, median_arrivals_per_station, mode_arrivals_per_station, variance_arrivals_per_station,
    avg_trips_per_vehicle, max_trips_per_vehicle, min_trips_per_vehicle, median_trips_per_vehicle, mode_trips_per_vehicle, variance_trips_per_vehicle
), file=f)
        
    print("calculated", end="\n\t")
    
    print("Plotting results...", end=" ")
    
    # create a directory for the plots
    os.makedirs(os.path.join(dir_path, "plots"))
    
    # plot a fig with time on the x from 0 to config["run_time"] and on the y the number of users
    plt.figure()
    sns.histplot(data=df, x="Start Time", bins=100)
    plt.savefig(os.path.join(dir_path, "plots/start_time.png"))

    # plot unlock time
    plt.figure()
    sns.histplot(data=df, x="Unlock Time", bins=100)
    plt.savefig(os.path.join(dir_path, "plots/unlock_time.png"))

    # plot lock time
    plt.figure()
    sns.histplot(data=df, x="Lock Time", bins=100)
    plt.savefig(os.path.join(dir_path, "plots/lock_time.png"))

    # plot From Station
    plt.figure()
    sns.histplot(data=df, x="From Station", bins=100)
    plt.savefig(os.path.join(dir_path, "plots/from_station.png"))

    # plot To Station
    plt.figure()
    sns.histplot(data=df, x="To Station", bins=100)
    plt.savefig(os.path.join(dir_path, "plots/to_station.png"))

    # Plot vehicle used
    plt.figure()
    sns.histplot(data=df, x="Vehicle ID", bins=100)
    plt.savefig(os.path.join(dir_path, "plots/vehicle_used.png"))

    # plot distance
    plt.figure()
    sns.histplot(data=df, x="Distance", bins=100)
    plt.savefig(os.path.join(dir_path, "plots/distance.png"))

    # plot battery used
    plt.figure()
    sns.histplot(data=df, x="Battery Used", bins=100)
    plt.savefig(os.path.join(dir_path, "plots/battery_used.png"))

    # plot total time
    plt.figure()
    sns.histplot(data=df, x="Total Time", bins=100)
    plt.savefig(os.path.join(dir_path, "plots/total_time.png"))

    # plot velocity
    plt.figure()
    sns.histplot(data=df, x="Velocity", bins=100)
    plt.savefig(os.path.join(dir_path, "plots/velocity.png"))

    # plot trip time
    plt.figure()
    sns.histplot(data=df, x=df["Total Time"] - df["Lock Time"] - df["Unlock Time"], bins=100)
    plt.savefig(os.path.join(dir_path, "plots/trip_time.png"))

    print("plotted")

def main():
    # inizializzazione ambiente
    env = Environment()

    # caricamento file di configurazione
    config_data = load_config(os.path.join(os.path.dirname(__file__),"../config/simulation.json"))

    # crea cartella per i risultati della simulazione
    sim_path = create_directory_path()

    # write brief description of the simulation and the configuration used
    ## WARNING: assumptions are made on the structure of the configuration file
    # TODO: make this more general
    with open(os.path.join(sim_path, "description.txt"), "w") as f:
        print(
"""
Description:
Grid 18x18, each point is 700 meters away from the others
- Number of stations: 324
- Vehicle per station: {}
- Station Storage: {}
- Number of users: {}
- Vehicle autonomy: {} meters
- Charging time: {} minutes
- Simultanous charging: {}
- No Degeneration flag: {}
""".format(
    config_data["v_per_station"],
    config_data["station"]["storage"],
    sum([int(arr[2]) for arr in config_data["users"]["linear"]]) + sum([int(arr[2]) for arr in config_data["users"]["normal"]]),
    1000/41.5*700,
    1000/config_data["station"]["charge_per_time"],
    config_data["station"]["max_concurrent_charging"],
    config_data["no_degeneration"]
), file=f)

    # make a copy of the configuration files
    os.makedirs(os.path.join(sim_path, "conf"))
    shutil.copyfile(os.path.join(os.path.dirname(__file__),"../config/simulation.json"), os.path.join(sim_path, "conf/simulation.json"))
    shutil.copyfile(os.path.join(os.path.dirname(__file__),"../config/vehicle.json"), os.path.join(sim_path, "conf/vehicle.json"))

    # setup logger
    setup_logger(os.path.join(sim_path, "log.log"))

    # crea file per i risultati della simulazione
    result_path = os.path.join(sim_path, "result.csv")

    column_names = ["User ID", "Start Time", "From Station", "To Station", "Vehicle ID", "Unlock Time", "Lock Time", "Total Time", "Battery Used", "Distance", "Velocity"]
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