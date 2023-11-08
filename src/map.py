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
    
    def generate(self, number: int):
        """
        Generates a list of positions for the stations.

        Parameters:
        - number (int): the number of stations to generate.

        Returns:
        - list: a list of positions for the stations.
        """

        if self.distribution == "random":
            positions = []
            while len(positions) < number:
                position = (randint(0,self.size-1), randint(0,self.size-1))
                if position not in positions:
                    positions.append(position)
        else:
            raise Exception(f'Invalid distribution {self.distribution}')

        return positions
