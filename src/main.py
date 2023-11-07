from user import User
from station import Station
from vehicle import Scooter

import charging_policy
import station_storage
import map

from simpy import Environment
from random import randint
import os, json

def main(env: Environment, config_data: dict):
    try:
        Scooter.load_config(os.path.join(os.path.dirname(__file__),"../config/vehicle.json"))

        # to do the multivehicle case
        # vehicles_type = []
        # for type in config_data["Vehicles"]["Type"]:
        #     v = getattr(vehicle, type)
        #     v.load_config(config_data["Vehicles"]["Config File"])
        #     vehicles_type.append(vehicle)

        policy = getattr(charging_policy, config_data["Station"]["Charging Policy"])

        storage = getattr(station_storage, config_data["Station"]["Station Storage"])

        shape = getattr(map, config_data["Map"]["Shape"])
    except AttributeError:
        raise Exception(f'Invalid configuration file')
    except Exception as e:
        raise e

    positions = shape(config_data["Map"]["Size"], config_data["Map"]["Distribution"]).generate(config_data["Map"]["Number of Stations"])

    stations = [Station(env, i, position, config_data["Station"]["Charging Time"], config_data["Station"]["Max Concurrent Charging"], storage(env, config_data["Station"]["Capacity"], policy())) for i, position in enumerate(positions)]

    for i, station in enumerate(stations):
        for j in range(config_data["Station"]["Number of Vehicles"]):
            station.vehicles.add_vehicle(Scooter(i*config_data["Station"]["Number of Vehicles"] + j))
    
    # inizializzazione utenti
    users = []
    for i in range(config_data["Number of Users"]):
        p = randint(0,len(stations)-1)
        a = randint(0,len(stations)-1)
        while a == p:
            a = randint(0,len(stations)-1)
        users.append(User(env, i, stations[p], stations[a]))
    
    # avvio simulazione
    for user in users:
        yield env.timeout(0.5)
        env.process(user.run())

if __name__ == "__main__":
    env = Environment()

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

    env.process(main(env, config_data))
    
    env.run(until=config_data["Run Time"])