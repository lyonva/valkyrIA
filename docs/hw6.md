# Homework 6 Report
- CSC 791 Sinless Software Engineering
- By: Leonardo Villalobos Arias

## Description
The following features were added:
1. The ``discretization`` of ``samples`` returns more information about the state of the bins
2. Adds an FFT model that partitions a sample into a tree structure
3. Adds a FFT Forest model that builds all possible FFT of a certain depth.

### Better discretization
The ``discretization`` method of [sample](https://github.com/lyonva/valkyrIA/blob/main/src/df/sample.py) now shows more information, regarding the size of best and rest, as well as whether a certain bin is the first or last of a sequence. This facilitates the FFT and FFT Forest process. This is achieved this way:

##### For Num:
```
yield bag( at = self.at, name = self.name, lo = r[0][0], hi = r[-1][0],
                        best = counts.count(1), bests = n1,
                        rest = counts.count(0), rests = n2,
                        first = (n == 0), last = (n == len(ranges)))
```

##### For Sym:
```
yield bag( at = self.at, name = self.name, lo = val, hi = val,
                    best = self.get(val), bests = self.n,
                    rest = other.get(val), rests = other.n,
                    first = False, last = False )
```

A verbose mode was added to discretization. By default it just returns the partitions (one list per feature). Results are only shown if the verbose flag is True.
```
# Do random projections
    # Sort groups from best to worst
    # For each feature, determine better partitioning range
    def discretize(self, *, settings = {}):
        groups = self.divs(settings = settings)
        groups = self.sort_groups(groups, settings = settings)

        feature_ranges = []

        best, worst = groups[0], groups[-1]
        for good, bad in zip(best.x, worst.x):
            range = []
            for res in good.discretize(bad):
                range += [res]
            if len(range) > 0:
                feature_ranges += [range]
        
        self._show_discretized_ranges(feature_ranges, best, worst, settings = settings)
        # And this checks if settings has verbose == True

        return feature_ranges
```

### Fast Frugal Trees
A [FFT](https://github.com/lyonva/valkyrIA/blob/main/src/ml/fft.py) class was implemented. The FFT algorithm generates a tree structure in which each level is a branch that exits to a leaf, and the other exit is to a branch (or leaf). This way, a particular level only has at most one branch, and between one and two leaves. This means that the tree is "quick to judge".

As it currently stands, the quick tries to categories entries by proximity to the best and worst clusters of one random projections. So the FFT algorithm does:
1. Random projection on the current samples
2. Sort those random projections, pick best and worst ones (w.r.t. and objective)
3. For each feature, divide the feature in bins, determine the amount of best and worst samples (up to now, this is handled by ``discretize``
4. Sort the bins, choose the best according to our "goal"
    4.1. If we are going to prioritize best, then we look for the bin with larger proportions of best
    4.2. 
