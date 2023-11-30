from environment.env import Environment
from environment.constants import *

class Lock:
    def __init__(self, env: Environment):
        self.env = env
        self.locked = True
        self.waiting = []

    def request(self, process) -> tuple:
        if self.locked:
            self.waiting.append(process)
            return WAIT
        else:
            self.locked = True
            return GETTED

    def release(self):
        if self.waiting:
            process = self.waiting.pop(0)
            self.env.awake(process)
        else:
            self.locked = False

    def block(self):
        self.locked = True

class CapacityOutOfBound(Exception):
    pass

class Slots:
    def __init__(self, env: Environment, capacity: int):
        self.env = env
        self.capacity = capacity
        self.available = capacity
        self.waiting = []

    def request(self, process) -> tuple:
        if self.available > 0:
            self.available -= 1
            return GETTED
        else:
            self.waiting.append(process)
            return WAIT

    def release(self):
        if self.waiting:
            process = self.waiting.pop(0)
            self.env.awake(process)
            return True
        else:
            self.available += 1
            if self.available > self.capacity:
                raise CapacityOutOfBound()
            return False

    def initial(self, n: int):
        self.available = n