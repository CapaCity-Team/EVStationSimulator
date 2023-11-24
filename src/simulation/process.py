from simulation.constants import *

class Interrupt(Exception):
    pass

class Process:
    def __init__(self, time, generator):
        self.time = time
        self.generator = generator
    
    def next(self):
        try:
            return next(self.generator)
        except StopIteration:
            return END
        except Exception as e:
            if str(e) == "generator raised StopIteration":
                return END
            else:
                raise e
        
    def interrupt(self):
        self.generator.throw(Interrupt())

    def __eq__(self, other):
        return self.time == other.time
    
    def __lt__(self, other):
        return self.time < other.time
    
    def __gt__(self, other):
        return self.time > other.time