from environment.env import Environment
from simulation.utils import setup_logger, create_directory_path, load_config

from setup import setup_simulation
from analisys import analyze_results

import random, os, json, shutil, sys

def main():
    # random seed
    seed = random.randint(0, 1000000)

    # path to the default directory where the results will be saved
    path = os.path.join(os.path.dirname(__file__), "../results")

    # command line arguments
    args = sys.argv[1:]
    
    for arg in args:
        if arg.startswith("-apath=") or arg.startswith("--absolute_path="):
            path = arg.split("=")[1]

        elif arg.startswith("-rpath=") or arg.startswith("--relative_path="):
            path = os.path.join(os.path.dirname(__file__), arg.split("=")[1])

    # crea cartella per i risultati della simulazione
    sim_path = create_directory_path(path)

    # command line options
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

    # seed for reproducibility
    print("Seed: {}".format(seed))

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

    # setup simulation
    print("Setting up simulation...", end="\n\t")
    
    setup_simulation(env, config_data, seed)

    # esecuzione simulazione
    print("Starting simulation...", end=" ")

    env.run()

    print("Simulation finished\n")

    # analisi risultati
    print("Analyzing results...", end="\n\t")

    analyze_results(sim_path, config_data)
    
    print("analyzed")

    print("\nYou can find all the files produced by the simulation in the directory {}".format(sim_path))

if __name__ == "__main__":
    main()