from simulation.env import Environment
from simulation.process import Process

from user import User
from station import Station
from utils import setup_logger, create_directory_path, load_config, find_index_nearest_k_points
import random
import os, json, shutil, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def simulation(env: Environment, config_data: dict, seed: int):
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
    positions = generate_station_positions(config_data["station"]["deployment"]["parameters"], seed)

    # plot station positions
    # plt.figure()
    # plt.scatter([p[0] for p in positions], [p[1] for p in positions])
    # plt.savefig(os.path.join(os.path.dirname(__file__), "../pitch_plot/stations.png"))

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

    user_start_times = []
    for start, end, number in config_data["users"]["linear"]:
        user_start_times.extend(list(np.random.uniform(start, end, int(number))))

    for start, end, number in config_data["users"]["normal"]:
        for sample in np.around(np.random.normal(0, 1, int(number)), decimals=5):
            user_start_times.append(start + ((sample + 3)/3)*(end-start))
    user_start_times.sort()

    # Generate an array of distances with a normal distribution
    distance = np.random.normal(0, 1, len(user_start_times))/3
    distance = np.where(distance < -3.3, -3.3, distance)
    distance = np.where(distance > 3.3, 3.3, distance)
    distance /= 3.3
    distance = np.where(distance < 0,
                        distance * (config_data["users"]["mean_distance"] - config_data["users"]["min_distance"]) + config_data["users"]["mean_distance"],
                        distance * (config_data["users"]["max_distance"] - config_data["users"]["mean_distance"]) + config_data["users"]["mean_distance"]) 

    # Generate an array of velocities with a normal distribution
    velocity = np.random.normal(0, 1, len(user_start_times))
    velocity = np.where(velocity < -3.3, -3.3, velocity)
    velocity = np.where(velocity > 3.3, 3.3, velocity)
    velocity /= 3.3
    velocity = np.where(velocity < 0,
                        velocity * (config_data["users"]["mean_velocity"] - config_data["users"]["min_velocity"]) + config_data["users"]["mean_velocity"],
                        velocity * (config_data["users"]["max_velocity"] - config_data["users"]["mean_velocity"]) + config_data["users"]["mean_velocity"])
    

    users = []
    max_distance = config_data["users"]["max_distance"]
    min_distance = config_data["users"]["min_distance"]
    
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
        user_to_redistribute = config_data["redistribution"] - 1 # -1 because the first user is redistributed before the redistribution loop
        
        v = np.full(len(stations), starting_v)
        redistribution = 0
        for i in range(len(user_start_times)):
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
                users.append([User(i, stations[p], stations[a], velocity[i]), user_start_times[i]])
                redistribution -= 1
            else:
                tries = 0
                while True:
                    if tries > max_tries:
                        print("######################")
                        print("######################")
                        print("###### WARNING #######")
                        print("######################")
                        print("######################")
                        # prossimi x utenti andranno da stazzioni piene a stazioni vuote
                        redistribution = user_to_redistribute

                        # Find the maximum value
                        max_value = np.max(v)

                        # Find the indices of all occurrences of the maximum value
                        max_indices = np.where(v == max_value)[0]
                        p = np.random.choice(max_indices)

                        # find the minimum value near tha station p
                        points = find_index_nearest_k_points(center = positions[p], radius = distance[i], points = positions, k = 20)
                        for point in points:
                            if p == point or v[point] >= v_max - 4 or stations[p].distance(stations[point]) > max_distance or stations[p].distance(stations[point]) < min_distance:
                                continue
                            else:
                                a = point
                                break
                        else:
                            raise Exception("No suitable point found")

                    else:
                        p = random.randint(0,len(stations)-1)
                        while v[p] <= 4:
                            p = random.randint(0,len(stations)-1)

                        points = find_index_nearest_k_points(center = positions[p], radius = distance[i], points = positions, k = 5)
                        
                        for point in points:
                            if p == point or v[point] >= v_max - 4 or stations[p].distance(stations[point]) > max_distance or stations[p].distance(stations[point]) < min_distance:
                                continue
                            else:
                                a = point
                                break
                        else:
                            tries += 1
                            continue

                    v[p] -= 1
                    v[a] += 1
                    users.append([User(i, stations[p], stations[a], velocity[i]), user_start_times[i]])
                    break
    else:
        for i in range(len(user_start_times)):
            p = random.randint(0,len(stations)-1)

            points = find_index_nearest_k_points(center = positions[p], radius = distance[i], points = positions, k = 5)

            for point in points:
                if p == point or stations[p].distance(stations[point]) > max_distance or stations[p].distance(stations[point]) < min_distance:
                    continue
                else:
                    a = point
                    break
            else:
                raise Exception("No suitable point found")

            users.append([User(i, stations[p], stations[a], velocity[i]), user_start_times[i]])
       
    print("generated")

    # avvio simulazione
    for user, start_time in users:
        p = Process(start_time, user.run())
        user.process = p
        env.add_process(p)

    print("Finished setup\n")

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

    # non completed trips id
    # non_completed_trips = set(range(number_of_users)) - set(df["User ID"])
    # print("Non completed trips: {}".format(non_completed_trips))
    # exit()

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
    
    # print("calculated")
    # return

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
    # seed per il generatore di numeri casuali
    seed = random.randint(0, 1000000)

    path = os.path.join(os.path.dirname(__file__), "../results")

    args = sys.argv[1:]
    
    for arg in args:
        if arg.startswith("-apath=") or arg.startswith("--absolute_path="):
            path = arg.split("=")[1]

        elif arg.startswith("-rpath=") or arg.startswith("--relative_path="):
            path = os.path.join(os.path.dirname(__file__), arg.split("=")[1])

    # crea cartella per i risultati della simulazione
    sim_path = create_directory_path(path)

    for arg in args:
        if arg == "-h" or arg == "--help":
            print("Usage: python3 {} [-s|--simplified] [--seed=SEED] [-log|--log]".format(sys.argv[0]))
            print("\t-s|--simplified\t\tRun the simulation with the simplified configuration")
            print("\t--seed=SEED\t\tSet the seed for the random number generator")
            print("\t-log|--log\t\tEnable logging")
            exit()
        
        elif arg == "-s" or arg == "--simplified":
            print("Running simplified simulation")
            # load simplified configuration
            simplified_config = load_config(os.path.join(os.path.dirname(__file__),"../config/simplified.json"))

            # use simplified configuration as description
            with open(os.path.join(sim_path, "description.txt"), "w") as f:
                shutil.copyfile(os.path.join(os.path.dirname(__file__),"../config/simplified.json"), os.path.join(sim_path, "description.txt"))

            # modify vehicle.json
            with open(os.path.join(os.path.dirname(__file__),"../config/vehicle.json"), "r") as f:
                vehicle_data = json.load(f)
                vehicle_data["Scooter"]["BATTERY_CAPACITY"] = 1000
                vehicle_data["Scooter"]["ENERGY_CONSUMPTION"] = 1000/simplified_config["vehicle"]["autonomy"]

            with open(os.path.join(os.path.dirname(__file__),"../config/vehicle.json"), "w") as f:
                json.dump(vehicle_data, f, indent=4)

            # create configuration files for the simplified configuration
            configuration = """{
    "station": {
        "charge_per_time": CHARGE_PER_TIME,
        "max_concurrent_charging": MAX_CONCURRENT_CHARGING,
        
        "storage":{
            "type": "TYPE",
            "parameters": PARAMETERS
        },

        "deployment": {
            "type": "grid_cells",
            "parameters": {
                "rows": ROWS,
                "columns": COLUMNS,
                "width": WIDTH,
                "min_distance": STAT_MIN_DISTANCE
            }
        }
    },

    "vehicles": {
        "type": ["Scooter"],
        
        "deployment": {
            "type": "uniform",
            "parameters": {
                "vehicles_per_station": VEHICLES_PER_STATION
            }
        }
    },

    "users": {
        "linear": LINEAR,
        "normal": NORMAL,
        "mean_distance": MEAN_DISTANCE,
        "max_distance": MAX_DISTANCE,
        "min_distance": MIN_DISTANCE,
        "mean_velocity": MEAN_VELOCITY,
        "max_velocity": MAX_VELOCITY,
        "min_velocity": MIN_VELOCITY
    },
    
    "no_degeneration": NO_DEGENERATION,
    "v_per_station": VEHICLES_PER_STATION,
    "station_capacity": STATION_CAPACITY,
    "tries": 5000,
    "redistribution": REDISTRIBUTION,

    "run_time": RUN_TIME
}"""

            radice = simplified_config["stations"]["number"]**0.5
            if radice - int(radice) < 0.5:
                radice = int(radice)
            else:
                radice = int(radice) + 1

            storage = {"capacity": simplified_config["stations"]["capacity"]} if simplified_config["stations"]["type"] == "LIFO" else {"stack1_size": simplified_config["stations"]["capacity"]//2,"stack2_size": simplified_config["stations"]["capacity"]//2}

            linear = [
                [0, 60, 245/10000*simplified_config["users"]["number"]],
                [60, 90, 139/10000*simplified_config["users"]["number"]],
                [90, 120, 155/10000*simplified_config["users"]["number"]],
                [120, 150, 171/10000*simplified_config["users"]["number"]],
                [150, 180, 188/10000*simplified_config["users"]["number"]],
                [180, 1080, 6122/10000*simplified_config["users"]["number"]]
            ]
            normal = [
                [60, 180, 857/10000*simplified_config["users"]["number"]],
                [420, 540, 286/10000*simplified_config["users"]["number"]],
                [720, 960, 1837/10000*simplified_config["users"]["number"]]
            ]

            placeholders = ["VEHICLES_PER_STATION", "CHARGE_PER_TIME", "MAX_CONCURRENT_CHARGING", "ROWS", "COLUMNS", "WIDTH", "STAT_MIN_DISTANCE", "TYPE", "PARAMETERS", "LINEAR", "NORMAL", "MEAN_DISTANCE", "MAX_DISTANCE", "MIN_DISTANCE", "MEAN_VELOCITY", "MAX_VELOCITY", "MIN_VELOCITY", "NO_DEGENERATION", "STATION_CAPACITY", "REDISTRIBUTION", "RUN_TIME"]
            substitutions= [simplified_config["stations"]["vehicles_per_station"],
                            1000/simplified_config["stations"]["recharge_time"],
                            simplified_config["stations"]["max_simultaneous_recharge"],
                            radice,
                            radice,
                            simplified_config["stations"]["distance"],
                            simplified_config["stations"]["min_distance"],
                            simplified_config["stations"]["type"],
                            str(storage).replace("'", '"'),
                            linear,
                            normal,
                            simplified_config["users"]["average_distance"],
                            simplified_config["users"]["max_distance"],
                            simplified_config["users"]["min_distance"],
                            simplified_config["vehicle"]["average_speed"],
                            simplified_config["vehicle"]["max_speed"],
                            simplified_config["vehicle"]["min_speed"],
                            str(simplified_config["no_degeneration"]).lower(),
                            simplified_config["stations"]["capacity"],
                            simplified_config["users"]["number"]//10,
                            simplified_config["run_time"]]
            
            # replace placeholders
            for i in range(len(placeholders)):
                configuration = configuration.replace(placeholders[i], str(substitutions[i]))

            # write configuration to file
            with open(os.path.join(os.path.dirname(__file__), "../config/simulation.json"), "w") as f:
                print(configuration, file=f)
        
        elif arg == "-log" or arg == "--log":
            setup_logger(os.path.join(sim_path, "log.log"))

        elif arg.startswith("--seed="):
            seed = int(arg.split("=")[1])

    
    # set seed
    print("Seed: {}".format(seed))
    random.seed(seed)
    np.random.seed(seed)

    #print(sim_path)
    # caricamento file di configurazione
    config_data = load_config(os.path.join(os.path.dirname(__file__),"../config/simulation.json"))

    # make a copy of the configuration files
    os.makedirs(os.path.join(sim_path, "conf"))
    shutil.copyfile(os.path.join(os.path.dirname(__file__),"../config/simulation.json"), os.path.join(sim_path, "conf/simulation.json"))
    shutil.copyfile(os.path.join(os.path.dirname(__file__),"../config/vehicle.json"), os.path.join(sim_path, "conf/vehicle.json"))

    # crea file per i risultati della simulazione
    result_path = os.path.join(sim_path, "result.csv")

    column_names = ["User ID", "Start Time", "From Station", "To Station", "Vehicle ID", "Unlock Time", "Lock Time", "Total Time", "Battery Used", "Distance", "Velocity"]
    with open(result_path, "w") as f:
        print(",".join(column_names), file=f)

    # inizializzazione ambiente
    env = Environment()

    # avvio simulazione
    simulation(env, config_data, seed)
    
    print("Starting simulation...", end=" ")

    # esecuzione simulazione
    env.run()

    print("Simulation finished\n")

    print("Analyzing results...", end="\n\t")
    # analisi risultati
    analyze_results(sim_path, config_data)
    print("analyzed")


if __name__ == "__main__":
    main()