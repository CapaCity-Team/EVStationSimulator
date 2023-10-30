from station import Station
from vehicle import Scooter
from user import User
from charging_policy import LIFO
from station_storage import StationStorageLIFO
from simpy import Environment
from random import randint

def main(env: Environment):
    Scooter.load_config("../config/vehicle.json")

    # inizializzazione stazioni
    stations = [Station(env, i, (randint(0,20), randint(0,20)), 1, 2, StationStorageLIFO(env, 10, LIFO())) for i in range(5)]

    # inizializzazione veicoli
    vehicles = [Scooter(i) for i in range(6*len(stations))]

    # riempimento stazioni
    for i, station in enumerate(stations):
        for j in range(6):
            station.vehicles.add_vehicle(vehicles[i*6 + j])
    
    # inizializzazione utenti
    users = []
    for i in range(10):
        p = randint(0,4)
        a = randint(0,4)
        users.append(User(env, i, stations[p], stations[a]))
    
    # avvio simulazione
    for user in users:
        yield env.timeout(0.5)
        env.process(user.run())

if __name__ == "__main__":
    env = Environment()
    env.process(main(env))
    env.run(until=20)