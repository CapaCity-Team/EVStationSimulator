from random import randint

def grid(params: dict):
    # Generate the positions of the stations in a grid
    rows = params["rows"]
    columns = params["columns"]
    width = params["width"]

    positions = []
    for i in range(rows):
        for j in range(columns):
            positions.append((i*width, j*width))

    return positions

def square_random(params: dict):
    size = params["size"]
    number = params["number"]
    
    # Generate the positions of the stations
    positions = []
    while len(positions) < number:
        position = (randint(0, size-1), randint(0, size-1))
        if position not in positions:
            positions.append(position)

    return positions

def circle_random(params: dict):
    radius = params["radius"]
    number = params["number"]
    
    # Generate the positions of the stations
    positions = []
    while len(positions) < number:
        position = (randint(-radius,radius), randint(-radius,radius))
        if position not in positions and position[0]**2 + position[1]**2 <= radius**2:
            positions.append(position)

    return positions
    

