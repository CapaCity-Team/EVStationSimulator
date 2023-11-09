from abc import ABC, abstractmethod
from random import randint

class Map(ABC):
    @abstractmethod
    def generate(self):
        pass

class Square(Map):
    def __init__(self, params: dict):
        self.size = params["Size"]
        self.distribution = params["Distribution"]
        self.number = params["Number of Stations"]
    
    def generate(self):

        if self.distribution == "random":
            positions = []
            while len(positions) < self.number:
                position = (randint(0,self.size-1), randint(0,self.size-1))
                if position not in positions:
                    positions.append(position)
        else:
            raise Exception(f'Invalid distribution {self.distribution}')

        return positions
    
class Circle(Map):
    def __init__(self, params: dict):
        self.radius = params["Radius"]
        self.distribution = params["Distribution"]
        self.number = params["Number of Stations"]
    
    def generate(self):

        if self.distribution == "random":
            positions = []
            while len(positions) < self.number:
                position = (randint(-self.radius,self.radius), randint(-self.radius,self.radius))
                if position not in positions and position[0]**2 + position[1]**2 <= self.radius**2:
                    positions.append(position)
        else:
            raise Exception(f'Invalid distribution {self.distribution}')

        return positions
    
class Grid(Map):
    def __init__(self, params: dict):
        self.rows = params["Rows"]
        self.columns = params["Columns"]
        self.width = params["Width"]
    
    def generate(self):
        positions = []
        for i in range(self.rows):
            for j in range(self.columns):
                positions.append((i*self.width, j*self.width))

        return positions