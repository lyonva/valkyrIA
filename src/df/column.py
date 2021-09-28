from abc import ABC, abstractmethod
from math import inf, sqrt
from random import random
from src.etc import bag
from src.ml import unsuper, merge

def is_na(x):
    return x == "?"

# Base class for data columns
class Column(ABC):

    def __init__(self, at, name):
        self.at = at
        self.name = name
        self.n = 0

    @abstractmethod
    def add(self, x):
        pass

    @abstractmethod
    def distance(self, x1, x2, settings = {}):
        pass

    def discretize(self, other):
        yield from []

# Skip column class
# Ignores data
class Skip(Column):
    def add(self, x):
        pass
    
    def distance(self, x1, x2, settings = {}):
        return 1

# Number column class
# Stores numerical values
class Num(Column):
    def __init__(self, at, name):
        super(Num, self).__init__(at, name)
        self.lo = inf
        self.hi = -inf
        self.mu = 0
        self.mu2 = 0
        self.sd = 0
        self.val = []
    
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
        
        self.val.append(x)
    
    def weight(self):
        if self.name[-1] == "+":
            return 1
        if self.name[-1] == "-":
            return -1
        return 0
    
    def norm_score(self, x):
        return (x - self.lo) / (self.hi - self.lo)
    
    def distance(self, x1, x2, settings = {}):
        if is_na(x1) and is_na(x2):
            return 1
        if is_na(x1) or is_na(x2):
            x = x1 if is_na(x2) else x2
            x = self.norm_score(x)
            y = 0 if x > 0.5 else 1
            return y - x
        return self.norm_score(x1) - self.norm_score(x2)
    
    def discretize(self, other):
        cohen = 0.3
        # Organize data
        X = [(good, 1) for good in self.val] + [(bad, 0) for bad in other.val]
        n1 = self.n
        n2 = other.n
        iota = cohen * (self.sd*n1 + other.sd*n2) / (n1 + n2)
        ranges = merge(unsuper(X, iota, sqrt(len(X))))
        
        if len(ranges) > 1:
            for n, r in enumerate(ranges):
                counts = [x[1] for x in r]
                yield bag( at = self.at, name = self.name, lo = r[0][0], hi = r[-1][0],
                        best = counts.count(1), bests = n1,
                        rest = counts.count(0), rests = n2,
                        first = (n == 0), last = (n == len(ranges)))

# Symbol column class
# Stores categorical values
class Sym(Column):
    def __init__(self, at, name):
        super(Sym, self).__init__(at, name)
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
    
    def distance(self, x1, x2, settings = {}):
        if is_na(x1) or is_na(x2):
            return 1
        return 0 if x1.upper() == x2.upper() else 1
    
    def get(self, key):
        x = self.count.get(key)
        if x is None:
            x = 0
        return x

    def discretize(self, other):
        for val in set(self.count.keys() | other.count.keys()):
            yield bag( at = self.at, name = self.name, lo = val, hi = val,
                    best = self.get(val), bests = self.n,
                    rest = other.get(val), rests = other.n,
                    first = False, last = False )


# Sample column class
# Stores a random subset of the added values
class Some(Column):
    def __init__(self, at, name):
        super(Some, self).__init__(at, name)
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
                pos = int(random() * self.cap)
                self.samples[pos] = x
                self.sorted = False
    
    def distance(self, x1, x2, settings = {}):
        return 1