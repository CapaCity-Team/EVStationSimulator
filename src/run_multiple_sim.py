import os

def main():
    model = """{
    "station": {
        "charge_per_time": CHARGE_PER_TIME,
        "max_concurrent_charging": MAX_CONCURRENT_CHARGING,
        
        "storage":{
            "type": "TYPE",
            "parameters": PARAMETERS
        },

        "deployment": {
            "type": "grid",
            "parameters": {
                "rows": 18,
                "columns": 18,
                "width": 1
            }
        }
    },

    "vehicles": {
        "type": ["Scooter"],
        
        "deployment": {
            "type": "uniform",
            "parameters": {
                "vehicles_per_station": 15
            }
        }
    },

    "users": {
        "linear": [
            [0, 60, 245],
            [60, 90, 139],
            [90, 120, 155],
            [120, 150, 171],
            [150, 180, 188],
            [180, 1080, 6122]
        ],
        "normal":[
            [60, 180, 857],
            [420, 540, 286],
            [720, 960, 1837]

        ],
        "mean_distance": 2.8,
        "std_distance": 0.5,
        "mean_velocity": 0.28,
        "std_velocity": 0.05
    },
    
    "no_degeneration": true,
    "v_per_station": 15,
    "station_capacity": 30,
    "tries": 5000,
    "redistribution": 1000,

    "run_time": 5000
}"""

    battery = 1000
    charging_times = [20, 10, 5]
    for i in range(len(charging_times)):
        charging_times[i] = 1000/charging_times[i]
    max_concurrent_charging = [1, 3, 10]
    storage_types = ["LIFO", "DualStack"]
    params = {
        "LIFO": """{
            "capacity": 30
        }""",
        "DualStack": """{
            "stack1_size": 15,
            "stack2_size": 15
        }"""
    }

    print("Running simulations...\n")
    for s in storage_types:
        for t in charging_times:
            for c in max_concurrent_charging:
                new_model = model.replace("CHARGE_PER_TIME", str(t))
                new_model = new_model.replace("MAX_CONCURRENT_CHARGING", str(c))
                new_model = new_model.replace("TYPE", s)
                new_model = new_model.replace("PARAMETERS", params[s])
                with open(os.path.join(os.path.dirname(__file__), "../config/simulation.json"), "w") as f:
                    f.write(new_model)
                
                print("Running simulation with {} storage, {} charging time and {} max concurrent charging\n".format(s, t, c))
                os.system("python3 {}".format(os.path.join(os.path.dirname(__file__), "main.py")))
                print()

    print("Done!")

if __name__ == "__main__":
    main()