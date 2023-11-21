import os, json

def get_value(prompt: str, format: str, types: list):
    while True:
        print(prompt)
        print(format)

        try:
            values = input("> ").split(" ")
            for i in range(len(types)):
                values[i] = types[i](values[i])
            return values
        except:
            print("Invalid input")


vehicle_params = [(),
                  ("ENERGY_CONSUMPTION", "Autonomia veicolo (in spazio):", "<number> <unit>", [float, str])]

def main():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config")

    with open(os.path.join(config_path, "simulation.json"), "r") as file:
        config_sim = json.load(file)

    with open(os.path.join(config_path, "vehicle.json"), "r") as file:
        config_vehicle = json.load(file)

    config = {}
    
    print("Welcome to the configuration generator")
    print("This script will generate a configuration file for the simulation")
    print()
    print("Please enter the following information:")

    # vehicle
    vehicles = {}
    types = get_value("number of vehicle types:", "<number>", [int])[0]
    for i in range(types):
        print("type {}: ".format(i), end="")
        name = get_value("name of type (case insensitive):", "<name>", [str])[0]
        
        v = {}
        v["BATTERY_CAPACITY"] = get_value("Autonomia veicolo (space):", "<number> <unit>", [float, str])[0]
        # battery consumption dipende dalle unità di misura

        vehicles[name] = v
    

    # simulation
    n, unit = get_value("Unit of time:", "<number> <unit>", [int, str])
    config["time_unit"] = {"n": n, "unit": unit}

    n, unit = get_value("Unit of space:", "<number> <unit>", [int, str])
    config["space_unit"] = {"n": n, "unit": unit}

    print("Work in progress...")

    # station

"""sblocchi giornalieri pari a 7500
percorrenza media 2,3 km/noleggio
durata media 11,5 minuti/noleggio
velocità media 15 km/h

un numero di stazioni pari a 324(facile fare la griglia con 18x18)
distanza tra le stazioni 750 metri
griglia 18*18
ogni stazioni è separata da una unità di spazio
numero di bici per stazione 15
max capacità stazione 22


ore 16-20 sono le ore di punta
circa 4/18 = 0,22 % del tempo totale facciamo che il 40% dei noleggi avvengono in questo lasso di tempo
il restante 60% è distribuito uniformemente nelle restanti ore (6-16 e 20-24)
tra le 6-16 e 20-24 ci sono 7500*0,6 = 4500 noleggi -> 4500/14*4 = 1285 noleggi ogni 4 ore
tra le 16-20 ci sono 7500*0,4 = 3000 noleggi
ne sottraiamo 1285 -> 3000-1285 = 1715 noleggi in più tra le 16-20 distribuiti come una gaussiana"""


if __name__ == "__main__":
    main()
