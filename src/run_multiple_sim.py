import os, json

def main():
    with open(os.path.join(os.path.dirname(__file__), "../config/simplified.json"), "r") as f:
        simplified_config = json.load(f)

    charging_times = [i for i in range(1, 100)]
    user_number = [25000, 30000, 35000]
    seeds = [11297, 8850, 22096, 31782, 55605]

    # save seeds to file
    with open(os.path.join(os.path.dirname(__file__), "../../simulations/seeds.txt"), "w") as f:
        for seed in seeds:
            f.write(str(seed) + "\n")

    print(f"running {len(user_number)*len(charging_times)*len(seeds)} simulations")

    base_path = os.path.join(os.path.dirname(__file__), "../../simulations")

    for n in user_number:
        simplified_config["users"]["number"] = n
        os.makedirs(os.path.join(base_path, f"user_{n}"))
        
        for t in charging_times:
            simplified_config["stations"]["recharge_time"] = t
            path = os.path.join(base_path, f"user_{n}", f"time_{t}")
            os.makedirs(path)

            print("Running simulations with charging time {}\n".format(t))

            with open(os.path.join(os.path.dirname(__file__), "../config/simplified.json"), "w") as f:
                    json.dump(simplified_config, f, indent=4)            

            for i, seed in enumerate(seeds):
                print("Running simulation {}\n".format(i))
                os.system("python3 {} -s --seed={} -rpath={}".format(os.path.join(os.path.dirname(__file__), "main.py"), seed, path))
                print()

    print("Done!")

if __name__ == "__main__":
    main()