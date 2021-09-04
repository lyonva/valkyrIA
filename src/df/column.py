from abc import ABC, abstractmethod
from math import inf, sqrt
from random import random

# Base class for data columns
class Column(ABC):

    def __init__(self, name):
        self.name = name
        self.n = 0

    @abstractmethod
    def add(self, x):
        pass

# Skip column class
# Ignores data
class Skip(Column):
    def add(self, x):
        pass

# Number column class
# Stores numerical values
class Num(Column):
    def __init__(self, name):
        super(Num, self).__init__(name)
        self.lo = inf
        self.hi = -inf
        self.mu = 0
        self.mu2 = 0
        self.sd = 0
    
    def add(self, x):
        self.n += 1

        # Update hi and low
        self.hi = max(self.hi, x)
        self.lo = min(self.lo, x)

        # Update momentums and sd
        delta = x - self.mu
        self.mu += delta / self.n
        self.mu2 += delta * (x - self.mu)
        if self.n > 1:
            self.sd = sqrt((self.mu2 / (self.n - 1)))

# Symbol column class
# Stores categorical values
class Sym(Column):
    def __init__(self, name):
        super(Sym, self).__init__(name)
        self.count = {}
        self.mode = []
        self.n_mode = 0
    
    def add(self, x):
        self.n += 1

        # Add to count and/or increment count
        if x not in self.count.keys():
            self.count[x] = 0
        self.count[x] += 1

        # Update mode
        if self.count[x] > self.n_mode:
            self.n_mode = self.count[x]
            self.mode = [x]
        elif self.count[x] == self.n_mode:
            self.mode.append(x)

# Sample column class
# Stores a random subset of the added values
class Some(Column):
    def __init__(self, name):
        super(Some, self).__init__(name)
        self.samples = []
        self.cap = 256
        self.sorted = False
    
    def add(self, x):
        self.n += 1

        # If list is not full, add to list
        if len(self.samples) < self.cap:
            self.samples.append(x)
            self.sorted = False
        # If it is full, choose anything to replace
        else:
            if random() < self.cap / self.n:
                pos = int(random() * self.cap())
                self.samples[pos] = x
                self.sorted = False