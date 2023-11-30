import random

def grid(params: dict, seed: int):
    # Generate the positions of the stations in a grid
    rows = params["rows"]
    columns = params["columns"]
    width = params["width"]

    positions = []
    for i in range(rows):
        for j in range(columns):
            positions.append((i*width, j*width))

    return positions

def square_random(params: dict, seed):
    random.seed(seed)
    
    size = params["size"]
    number = params["number"]
    
    # Generate the positions of the stations
    positions = []
    while len(positions) < number:
        position = (random.randint(0, size-1), random.randint(0, size-1))
        if position not in positions:
            positions.append(position)

    return positions

def circle_random(params: dict, seed: int):
    random.seed(seed)

    radius = params["radius"]
    number = params["number"]
    
    # Generate the positions of the stations
    positions = []
    while len(positions) < number:
        position = (random.randint(-radius,radius), random.randint(-radius,radius))
        if position not in positions and position[0]**2 + position[1]**2 <= radius**2:
            positions.append(position)

    return positions

def grid_cells(params: dict, seed: int):
    random.seed(seed)

    # Generate the positions of the stations in a grid
    rows = params["rows"] + 1 # +1 because the stations are in the middle of the cells so we need one more row and column
    columns = params["columns"] + 1
    width = params["width"]
    min_distance = params["min_distance"]

    positions = []
    for i in range(rows):
        for j in range(columns):
            # (i,j) is the lower left corner of the cell
            # (i+1,j+1) is the upper right corner of the cell
            
            # Generate the positions of the stations in a circle
            # radius = (width - min_distance) / 2

            center = (i*width + width/2, j*width + width/2)
            radius = (width - min_distance) / 2

            # Generate random positions in the circle
            while True:
                position = (random.randint(-radius,radius), random.randint(-radius,radius))
                if position[0]**2 + position[1]**2 <= radius**2:
                    break

            positions.append((center[0] + position[0], center[1] + position[1]))

    return positions