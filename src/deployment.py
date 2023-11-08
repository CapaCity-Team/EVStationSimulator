
def uniform_distribution(stations: list, vehicle_type: list, parameters: dict):
    if len(vehicle_type) == 1:
        vehicle = vehicle_type[0]
        vehicles = []
        for id in range(len(stations) * parameters["Vehicles per Station"]):
            vehicles.append(vehicle(id))
        
        for s in stations:
            for _ in range(parameters["Vehicles per Station"]):
                s.add_vehicle(vehicles.pop(0))
    else:
        raise Exception(f'To Do')