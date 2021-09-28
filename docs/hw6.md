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
    - If we are going to prioritize best, then we look for the bin with larger proportions of best
    - Likewise for worst
5. Then we pick the first bin and use its condition to slice the space, resulting in two sub-partition samples
6. The partition that maximizes our "goal" is the leaf of the current branch.
7. We repeat from step 1 with the other partition
    - But if we have reached max level, or we have too little samples we stop
    - If we stop, we convert the sample into a leaf

Because we only have one "goal" per level, which is maximize best (1) or worst (0), each FFT policy can be represented by a bit string. The only constraint is the last leaf is always the inverse goal of the second to level (it contains the remainder samples). For example, the tree 010:
- Paritions looking for the worst stuff at first level
- Partitions looking for the best stuff at second level
- The "third" level contains the remaining samples (possibly maximizing worst stuff)

Because the last bit is redundant, this FFT implementation takes only the first N-1 bits. So a 11110 tree is represented by the bit string 1111. Coincidentally, this generates a tree of height 4.

The following is the most important part of the FFT code, which contains the numbered steps from above:
```
def _build_level(self, level, sample, sequence):
        # First check if this level is the limit
        if level >= self["max_depth"] or sequence == "" or sample.n_rows < self["min_samples_split"]:
            return self._build_leaf(sample)
        
        # Target
        # 0 = focus on the rest
        # 1 = focus on the best
        target = sequence[0]

        # Build one level
        # First get partitions
        partitions = sample.discretize()
        bins = list(chain.from_iterable(partitions)) # Flatten the output

        # Now choose the best bin
        bins = self.score_bins(target, bins)
        chosen = bins[0]

        # Partition
        in_bin, out_bin = sample.slice(chosen)

        # Our chosen partition is the leaf of this branch
        # The other is the recursive case, down 1 level
        leaf = self._build_leaf(in_bin)
        down = self._build_level( level + 1, out_bin, sequence[1:] )

        # Lastly, construct the branch and return
        return FFTBranch( sample, target, chosen, leaf, down )
```

The tree is build based on hyper-parameter values. So for example, ``self["max_depth"]`` resolves to whatever max_depth value was assigned when creating an object. For example, to create a tree of with the sequence 111101 we do:
```
fft = FFT(samples, sequence = "11110", max_depth = 5)
```

### FFT Forest
Similarly, an [FFT Forest](https://github.com/lyonva/valkyrIA/blob/main/src/ml/fft.py) class was implemented to explore all possible trees of a certain max_depth. So for a depth of 5, there are ``2**5 = 32`` possible FFTs. To automate the search for a 'best' policy, this forest was implemented. The implementation simply tries every possible combination:
```
# Construct an FFT Forest
# i.e. all possible options
def fit(self):
    for bits in bit_strings(self["max_depth"]):
        args = self.hps()
        args["structure"] = bits
        self.fft += [FFT(self.sample, **args)]
```

So every sub-tree is built using the same hyper-parameters, except structure. ``bit_strings`` just returns every possible combination of bits at every level. So ``bit_strings(3)`` returns 000, 001, 010, 011, ...


