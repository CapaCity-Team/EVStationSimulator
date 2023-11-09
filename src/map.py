from abc import ABC, abstractmethod
from random import randint

class Shape:
    """
    Abstract base class for all shapes.
    """    
    @abstractmethod
    def generate(self, number: int):
        """
        Generates a list of positions for the stations.

        Parameters:
        - number (int): the number of stations to generate.

        Returns:
        - list: a list of positions for the stations.
        """
        pass

class Square(Shape):
    """
    Square shape.
    """
    def __init__(self, params: dict):
        """
        Initializes a new instance of the Square class.

        Parameters:
        - params (dict): the parameters for the shape.
        """
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
    
class Circle(Shape):
    """
    Circle shape.
    """
    def __init__(self, params: dict):
        """
        Initializes a new instance of the Circle class.

        Parameters:
        - params (dict): the parameters for the shape.
        """
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
    
class Grid(Shape):
    """
    Grid shape.
    """
    def __init__(self, params: dict):
        """
        Initializes a new instance of the Grid class.

        Parameters:
        - params (dict): the parameters for the shape.
        """
        self.rows = params["Rows"]
        self.columns = params["Columns"]
        self.width = params["Width"]
    
    def generate(self):
        positions = []
        for i in range(self.rows):
            for j in range(self.columns):
                positions.append((i*self.width, j*self.width))

        return positions