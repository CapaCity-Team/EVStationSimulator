from simulation.utils import sortedlist
from simulation.process import Process
from simulation.constants import *

class Environment:
    def __init__(self):
        self.time = 0
        self.processes = sortedlist()

    def now(self):
        return self.time

    def add_process(self, process: Process):
        self.processes.insert(process)

    def run(self, until=None):
        while self.processes and (until is None or self.time < until):
            process = self.processes.pop(0)
            self.time = process.time
            
            signal = process.next()

            if signal == END or signal == WAIT:
                continue
            elif signal == GETTED:
                self.processes.insert(process)
            elif signal[1] == TIMEOUT:
                process.time = self.time + signal[0]
                self.processes.insert(process)
            
    def awake(self, process: Process):
        process.time = self.time
        self.processes.insert(process)
