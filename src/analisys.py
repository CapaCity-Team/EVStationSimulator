import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def analyze_results(dir_path: str, config: dict, seed: int):
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
    if number_of_users != number_of_completed_trips and config["no_degeneration"]:
        non_completed_trips = set(range(number_of_users)) - set(df["User ID"])
        assert len(non_completed_trips) == 0, "Non completed trips: {}".format(non_completed_trips)

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
"""Seed: {}
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
    seed,
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