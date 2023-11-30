
def uniform(stations: list, vehicle_type: list, parameters: dict):
    # Deploy the same number of vehicles for each station
    if len(vehicle_type) == 1:
        vehicle = vehicle_type[0]
        vehicles = []
        for id in range(len(stations) * parameters["vehicles_per_station"]):
            vehicles.append(vehicle(id))
        
        for s in stations:
            vehicles, to_deploy = vehicles[parameters["vehicles_per_station"]:], vehicles[:parameters["vehicles_per_station"]]
            s.deploy(to_deploy)
    else:
        raise Exception(f'To Do')
    
def capacity_based(stations: list, vehicle_type: list, parameters: dict):
    # For each station, deploy a number of vehicles proportional to the station's capacity
    if len(vehicle_type) == 1:
        vehicle = vehicle_type[0]
        
        id = 0
        for s in stations:
            vehicles = [vehicle(i) for i in range(id, id + s.vehicles.capacity * parameters["multiplier"])]
            id += s.vehicles.capacity * parameters["multiplier"]
            s.deploy(vehicles)
            
    else:
        raise Exception(f'To Do')