from environment.env import Environment
from environment.process import Process

from simulation.user import User
from simulation.station import Station
from simulation.utils import find_index_nearest_k_points, find_index_at_distance

import numpy as np
import os, random

def setup_simulation(env: Environment, config_data: dict, seed: int):
    # set seed
    random.seed(seed)
    np.random.seed(seed)

    print("Loading configuration...", end=" ")
    # caricamento dinamico funzioni e moduli specificati nel file di configurazione
    try:
        # caricamento funzione di generazione posizioni stazioni
        generate_station_positions = getattr(__import__("simulation.station_deployment", 
                                                        fromlist=[config_data["station"]["deployment"]["type"]]
                                                        ),
                                            config_data["station"]["deployment"]["type"])

        # caricamento classe di storage per stazioni
        storage = getattr(__import__("simulation.station_storage", 
                                     fromlist=[config_data["station"]["storage"]["type"]]
                                     ),
                        config_data["station"]["storage"]["type"])

        # caricamento configurazione veicoli
        vehicle = __import__("simulation.vehicle", fromlist=config_data["vehicles"]["type"])
        
        vehicle_cls = []
        for v in config_data["vehicles"]["type"]:
            cls = getattr(vehicle, v)
            vehicle_cls.append(cls)
            cls.load_config(os.path.join(os.path.dirname(__file__),"../config/vehicle.json"))

        # caricamento funzione di deploy veicoli
        deploy_vehicles = getattr(__import__("simulation.vehicle_deployment", fromlist=[config_data["vehicles"]["deployment"]["type"]]),
                                  config_data["vehicles"]["deployment"]["type"])

    except AttributeError:
        raise Exception(f'Invalid configuration file')
    except Exception as e:
        raise e

    print("loaded", end="\n\t")


    print("Generating stations...", end=" ")
    # generazione posizioni stazioni
    positions = generate_station_positions(config_data["station"]["deployment"]["parameters"], seed)

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
    
    # Generate starting and ending stations for each user
    if(config_data["no_degeneration"]):
        max_tries = config_data["tries"]
        user_to_redistribute = config_data["redistribution"] - 1 # -1 because the first user is redistributed before the redistribution loop
        
        v = np.array([station.vehicles.count() for station in stations])
        v_max = np.array([station.vehicles.max_capacity() for station in stations])
        
        redistribution = 0
        for i in range(len(user_start_times)):
            if redistribution > 0:
                # Find the maximum relative value
                v_perc = v/v_max
                max_value = np.max(v_perc)

                # Find the indices of all occurrences of the maximum value
                max_indices = np.where(v == max_value)[0]
                p = np.random.choice(max_indices)

                # find the point between min_distance and max_distance from the station p
                indexes = find_index_at_distance(center = positions[p], min_radius = distance[i], max_radius = distance[i], points = positions)
                sorted_indexes = sorted(indexes, key=lambda k: v[k])

                for index in sorted_indexes:
                    if p == index:
                        continue
                    else:
                        a = index
                        break
                else:
                    raise Exception("No suitable point found")

                v[p] -= 1
                v[a] += 1
                users.append([User(i, stations[p], stations[a], velocity[i]), user_start_times[i]])
                redistribution -= 1
            else:
                tries = 0
                while True:
                    if tries > max_tries:
                        print("#############################################")
                        print("#############################################")
                        print("###### WARNING STARTING REDISTRIBUTION ######")
                        print("#############################################")
                        print("#############################################")

                        # prossimi x utenti andranno da stazzioni piene a stazioni vuote
                        redistribution = user_to_redistribute

                        # Find the maximum relative value
                        v_perc = v/v_max
                        max_value = np.max(v_perc)

                        # Find the indices of all occurrences of the maximum value
                        max_indices = np.where(v == max_value)[0]
                        p = np.random.choice(max_indices)

                        # find the point between min_distance and max_distance from the station p
                        indexes = find_index_at_distance(center = positions[p], min_radius = distance[i], max_radius = distance[i], points = positions)
                        sorted_indexes = sorted(indexes, key=lambda k: v[k])

                        for index in sorted_indexes:
                            if p == index:
                                continue
                            else:
                                a = index
                                break
                        else:
                            raise Exception("No suitable point found")

                    else:
                        p = random.randint(0,len(stations)-1)
                        while v[p] <= 0:
                            p = random.randint(0,len(stations)-1)

                        indexes = find_index_nearest_k_points(center = positions[p], radius = distance[i], points = positions, k = 5)
                        
                        for index in indexes:
                            if p == index or v[index] == v_max[index] or stations[p].distance(stations[index]) > max_distance or stations[p].distance(stations[index]) < min_distance:
                                continue
                            else:
                                a = index
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

            indexes = find_index_nearest_k_points(center = positions[p], radius = distance[i], points = positions, k = 5)

            for index in indexes:
                if p == index or stations[p].distance(stations[index]) > max_distance or stations[p].distance(stations[index]) < min_distance:
                    continue
                else:
                    a = index
                    break
            else:
                raise Exception("No suitable point found")

            users.append([User(i, stations[p], stations[a], velocity[i]), user_start_times[i]])
       
    print("generated")
    
    # creazione processi
    for user, start_time in users:
        p = Process(start_time, user.run())
        user.process = p
        env.add_process(p)