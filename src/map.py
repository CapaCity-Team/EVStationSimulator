from abc import ABC, abstractmethod
from random import randint

class Shape:
    """
    Abstract base class for all shapes.
    """
    def __init__(self, size: int, distribution: str):
        """
        Initializes a new instance of the Shape class.

        Parameters:
        - size (int): the size of the map.
        - distribution (str): the distribution of the stations.
        """
        self.size = size
        self.distribution = distribution

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
