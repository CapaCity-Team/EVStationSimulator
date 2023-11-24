import os, json

def main():
    """{
        "stations": {
            "number": 324,
            "recharge_time": 10,
            "max_simultaneous_recharge": 3,
            "capacity": 30,
            "type": "LIFO",
            "distance": 1,
            "vehicles_per_station": 15
        },
        "vehicle": {
            "autonomy": 7,
            "average_speed": 0.3,
            "min_speed": 0.1,
            "max_speed": 0.5
        },
        "users": {
            "number": 10000,
            "average_distance": 3.5,
            "min_distance": 1,
            "max_distance": 6.0
        },

        "no_degeneration": true,

        "run_time": 2000
    }"""

    with open(os.path.join(os.path.dirname(__file__), "../config/simplified.json"), "r") as f:
        simplified_config = json.load(f)

    storage_types = ["DualStack"]
    charging_times = [20, 10, 5]
    max_concurrent_charging = [1, 3, 6]

    for s in storage_types:
        for t in charging_times:
            for c in max_concurrent_charging:
                simplified_config["stations"]["type"] = s
                simplified_config["stations"]["recharge_time"] = t
                simplified_config["stations"]["max_simultaneous_recharge"] = c

                with open(os.path.join(os.path.dirname(__file__), "../config/simplified.json"), "w") as f:
                    json.dump(simplified_config, f, indent=4)
                
                print("Running simulation with {} storage, {} charging time and {} max concurrent charging\n".format(s, t, c))
                os.system("python3 {} -s".format(os.path.join(os.path.dirname(__file__), "main.py")))
                print()

    print("Done!")

if __name__ == "__main__":
    main()