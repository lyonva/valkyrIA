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

The discretization output now looks like this:
```
{at:1, name:Displacement, lo:70, hi:350, best:25, bests:25, rest:4, rests:25, first:True, last:False}
{at:1, name:Displacement, lo:360, hi:400, best:0, bests:25, rest:12, rests:25, first:False, last:False}
{at:1, name:Displacement, lo:429, hi:455, best:0, bests:25, rest:9, rests:25, first:False, last:False}

{at:2, name:Horsepower, lo:58, hi:65, best:8, bests:25, rest:0, rests:25, first:True, last:False}
{at:2, name:Horsepower, lo:67, hi:74, best:9, bests:25, rest:0, rests:25, first:False, last:False}
{at:2, name:Horsepower, lo:75, hi:110, best:8, bests:25, rest:0, rests:25, first:False, last:False}
{at:2, name:Horsepower, lo:167, hi:208, best:0, bests:25, rest:16, rests:25, first:False, last:False}
{at:2, name:Horsepower, lo:210, hi:230, best:0, bests:25, rest:9, rests:25, first:False, last:False}

{at:5, name:Model, lo:70, hi:73, best:0, bests:25, rest:25, rests:25, first:True, last:False}
{at:5, name:Model, lo:77, hi:82, best:25, bests:25, rest:0, rests:25, first:False, last:False}

{at:6, name:origin, lo:1, hi:1, best:0, bests:25, rest:25, rests:25, first:False, last:False}
{at:6, name:origin, lo:3, hi:3, best:25, bests:25, rest:0, rests:25, first:False, last:False}
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

The tree is build based on hyper-parameter values. So for example, ``self["max_depth"]`` resolves to whatever max_depth value was assigned when creating an object. For example, to create a tree of with the sequence 11110 we do:
```
fft = FFT(samples, sequence = "1111", max_depth = 5)
```

Do remember that we exclude the last bit, as it can be inferred. If we print the FFT, we get the structure and some results:

```
1 if   80 <= Model <= 82 then [2395, 16.4, 30] (85)
1 elif origin == 2 then [2246, 15.5, 30] (55)
1 elif 76 <= Model <= 79 then [3193, 15.4, 20] (105)
1 elif origin == 3 then [2228, 16, 30] (25)
0 else [3682.5, 14.0, 20.0] (122)
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

So every sub-tree is built using the same hyper-parameters, except structure. ``bit_strings`` just returns every possible combination of bits at every level. So ``bit_strings(3)`` returns 000, 001, 010, 011, ... Which result in something like this:

```
0
0 if   origin == 1 then [3381, 15, 20] (245)
0 elif 75 <= Horsepower <= 133 then [2449.0, 15.0, 30.0] (82)
0 elif origin == 2 then [1990, 18.6, 30] (27)
0 elif 68 <= Horsepower <= 74 then [2035.0, 17.3, 30.0] (12)
1 else [1971.5, 17.45, 30.0] (26)

1
1 if   Cylinders <= 5 then [2245.5, 16.15, 30.0] (206)
0 elif 190 <= Horsepower <= 230 then [4382, 11, 10] (17)
0 elif 158 <= Horsepower <= 180 then [4363, 12, 10] (23)
0 elif 148 <= Horsepower <= 155 then [4135, 13.2, 10] (29)
1 else [3365, 15.5, 20] (117)

2
0 if   Model <= 73 then [3280.0, 14.0, 20.0] (124)
1 elif origin == 3 then [2140.0, 16.4, 30.0] (64)
0 elif origin == 1 then [3193, 15.8, 20] (157)
0 elif 103 <= Horsepower <= 133 then [2830, 15.7, 20] (7)
1 else [2196.0, 15.5, 30.0] (40)

3
1 if   Displacement <= 108 then [2080.0, 16.45, 30.0] (114)
1 elif Horsepower <= 90 then [2678, 17, 30] (81)
0 elif origin == 1 then [3779.0, 14.0, 20.0] (162)
0 elif 116 <= Horsepower <= 133 then [2930, 13.6, 20] (7)
1 else [2607.5, 14.75, 20.0] (28)

4
0 if   origin == 1 then [3381, 15, 20] (245)
0 elif 75 <= Horsepower <= 133 then [2449.0, 15.0, 30.0] (82)
1 elif origin == 3 then [1985.0, 17.45, 30.0] (38)
0 elif 97 <= Displacement <= 146 then [2130, 20.5, 30] (11)
1 else [1987.5, 16.25, 30.0] (16)

5
1 if   origin == 3 then [2155, 16.4, 30] (79)
0 elif 180 <= Horsepower <= 230 then [4381.0, 11.05, 10.0] (22)
1 elif origin == 2 then [2240.0, 15.6, 30.0] (68)
0 elif 153 <= Horsepower <= 175 then [4317.0, 12.0, 10.0] (22)
1 else [3158, 15.5, 20] (201)

6
0 if   Model <= 73 then [3280.0, 14.0, 20.0] (124)
1 elif origin == 3 then [2140.0, 16.4, 30.0] (64)
1 elif origin == 2 then [2223, 15.5, 30] (47)
0 elif 304 <= Displacement <= 400 then [4152.5, 13.5, 20.0] (32)
1 else [2945, 16.4, 20] (125)

7
1 if   80 <= Model <= 82 then [2395, 16.4, 30] (85)
1 elif origin == 2 then [2246, 15.5, 30] (55)
1 elif origin == 3 then [2155, 16.4, 30] (45)
0 elif 193 <= Horsepower <= 230 then [4403.5, 11.0, 10.0] (14)
1 else [3439, 14.9, 20] (193)

8
0 if   origin == 1 then [3381, 15, 20] (245)
0 elif 131 <= Displacement <= 183 then [2920.0, 15.15, 25.0] (20)
0 elif origin == 2 then [2202, 15.5, 30] (59)
1 elif Horsepower <= 70 then [1980.0, 17.45, 30.0] (36)
0 else [2295.0, 15.0, 30.0] (32)

9
1 if   origin == 3 then [2155, 16.4, 30] (79)
0 elif 390 <= Displacement <= 455 then [4425, 11.1, 10] (23)
0 elif origin == 1 then [3271.5, 15.45, 20.0] (222)
1 elif origin == 2 then [2240.0, 15.6, 30.0] (68)
0 else [] (0)

10
0 if   Model <= 73 then [3280.0, 14.0, 20.0] (124)
1 elif origin == 3 then [2140.0, 16.4, 30.0] (64)
0 elif 120 <= Horsepower <= 190 then [4054, 13.6, 20] (45)
1 elif Displacement <= 173 then [2451, 15.7, 30] (105)
0 else [3372.5, 17.05, 20.0] (54)

11
1 if   80 <= Model <= 82 then [2395, 16.4, 30] (85)
1 elif origin == 2 then [2246, 15.5, 30] (55)
0 elif origin == 1 then [3525, 14.5, 20] (207)
1 elif Horsepower <= 65 then [1818.0, 18.25, 30.0] (10)
0 else [2279, 15.5, 30] (35)

12
0 if   Model <= 73 then [3280.0, 14.0, 20.0] (124)
0 elif origin == 1 then [3193, 15.8, 20] (157)
1 elif Displacement <= 119 then [2065, 16.4, 30] (79)
1 elif origin == 2 then [3145.0, 16.3, 20.0] (18)
0 else [2683.5, 14.5, 30.0] (14)

13
1 if   origin == 3 then [2155, 16.4, 30] (79)
0 elif origin == 1 then [3381, 15, 20] (245)
1 elif Displacement <= 97 then [1995.0, 15.9, 30.0] (28)
1 elif 77 <= Model <= 82 then [2950, 15.8, 30] (15)
0 else [2582, 15.5, 20] (25)

14
0 if   origin == 1 then [3381, 15, 20] (245)
1 elif 62 <= Horsepower <= 75 then [2050, 16.6, 30] (57)
1 elif Horsepower <= 60 then [1851.0, 19.2, 35.0] (18)
1 elif Cylinders <= 4 then [2425.0, 14.95, 30.0] (60)
0 else [2930.0, 15.0, 20.0] (12)

15
1 if   Displacement <= 107 then [2070, 16.4, 30] (109)
1 elif Displacement <= 151 then [2582, 15.7, 30] (95)
1 elif Displacement <= 231 then [3102, 16, 20] (51)
1 elif Displacement <= 360 then [3801.0, 14.0, 20.0] (112)
0 else [4425, 11.1, 10] (25)
```

## Tests
The test cases implemented for this homework mostly focus on capturing behavior and properties such as runtime instead of correctness. This is because a large part of the output depends on randomness (random projections).

The file [test/test_discretize.py](https://github.com/lyonva/valkyrIA/blob/main/test/test_discretize.py) test the discretization method in the three datasets: weather, auto93, and pom3a. This was previously implemented and discusses in homework 5, but its output should now show the novel discretization outputs.

The file [test/test_fft.py](https://github.com/lyonva/valkyrIA/blob/main/test/test_fft.py) tests the creation of the FFT model in the three datasets. Again, we mostly focus on correctness and showing the output. We generate a 11110 tree (default) in this test cases.

The file [test/test_fft_forest.py](https://github.com/lyonva/valkyrIA/blob/main/test/test_fft_forest.py) tests the creation of the FFT model in the three datasets. We vary the max_depth per dataset: 1 for weather, 4 for auto93, and 2 for pom3a (due to runtime).


## Results
The test were conducted by a github action for the commit [127a47f](https://github.com/lyonva/valkyrIA/commit/127a47f6b19c2c63075b148c03163f4f9ce315e9), and the corresponding [report](https://github.com/lyonva/valkyrIA/actions/runs/1283748927) shows that all test cases passed. The output generated by the program is included in each test case.

### FFT
Output for the FFT is as expected. For weather dataset, the amount of levels is cut short due to missingness of data. Our implementation requires at least 10 samples by default to perform a split.

###### weather.csv
```
1 if   75 <= Temp <= 85 then [30.0, 40.0] (6)
0 else [45.0, 45.0] (8)
```

##### auto93.csv
```
1 if   Displacement <= 108 then [2080.0, 16.45, 30.0] (114)
1 elif 79 <= Model <= 82 then [2867.5, 16.0, 30.0] (68)
1 elif Displacement <= 225 then [2694, 15.7, 20] (81)
1 elif Displacement <= 250 then [3315.5, 16.299999999999997, 20.0] (32)
0 else [4154, 13, 10] (97)
```

##### pom3a.csv
```
1 if   0.579434883526 <= InitialKnown <= 0.698515072498 then [620.987597988, 0.37724682641, 0.166666666667] (3899)
1 elif Criticality <= 1.06321768247 then [547.427353199, 0.38240493792950003, 0.258680974198] (3874)
1 elif 2.69523097448 <= CriticalityModifier <= 4.68398682936 then [479.076661612, 0.394771820957, 0.260869565217] (553)
1 elif CriticalityModifier <= 4.96338513413 then [354.3944567855, 0.38370213014800003, 0.266352694924] (246)
0 else [1059.31895265, 0.384022213802, 0.271428571429] (1403)
```

Results are highly volatile due to randomness. However, in my short experience, the same rules get usually picked. It may be worth exploring the stability of this algorithm. The algorithm runs and partitions the data according to the rules. No rows are lost in the process, and the tree is a *partition* of the original samples.


### FFT Forest
Output for the FFT Forest is as expected. Note that in some scenarios, the last group is empty, as some partitions contain the entirety of the data. The actual result should be a tree of lesser height, and this has to be corrected.

###### weather.csv
```
0
0 if   Temp <= 72 then [45.0, 45.0] (8)
1 else [30.0, 40.0] (6)

1
1 if   75 <= Temp <= 85 then [30.0, 40.0] (6)
0 else [45.0, 45.0] (8)
```

##### auto93.csv
```
0
0 if   origin == 1 then [3381, 15, 20] (245)
0 elif 75 <= Horsepower <= 133 then [2449.0, 15.0, 30.0] (82)
0 elif origin == 2 then [1990, 18.6, 30] (27)
0 elif 68 <= Horsepower <= 74 then [2035.0, 17.3, 30.0] (12)
1 else [1971.5, 17.45, 30.0] (26)

1
1 if   Cylinders <= 5 then [2245.5, 16.15, 30.0] (206)
0 elif 190 <= Horsepower <= 230 then [4382, 11, 10] (17)
0 elif 158 <= Horsepower <= 180 then [4363, 12, 10] (23)
0 elif 148 <= Horsepower <= 155 then [4135, 13.2, 10] (29)
1 else [3365, 15.5, 20] (117)

2
0 if   Model <= 73 then [3280.0, 14.0, 20.0] (124)
1 elif origin == 3 then [2140.0, 16.4, 30.0] (64)
0 elif origin == 1 then [3193, 15.8, 20] (157)
0 elif 103 <= Horsepower <= 133 then [2830, 15.7, 20] (7)
1 else [2196.0, 15.5, 30.0] (40)

3
1 if   Displacement <= 108 then [2080.0, 16.45, 30.0] (114)
1 elif Horsepower <= 90 then [2678, 17, 30] (81)
0 elif origin == 1 then [3779.0, 14.0, 20.0] (162)
0 elif 116 <= Horsepower <= 133 then [2930, 13.6, 20] (7)
1 else [2607.5, 14.75, 20.0] (28)

4
0 if   origin == 1 then [3381, 15, 20] (245)
0 elif 75 <= Horsepower <= 133 then [2449.0, 15.0, 30.0] (82)
1 elif origin == 3 then [1985.0, 17.45, 30.0] (38)
0 elif 97 <= Displacement <= 146 then [2130, 20.5, 30] (11)
1 else [1987.5, 16.25, 30.0] (16)

5
1 if   origin == 3 then [2155, 16.4, 30] (79)
0 elif 180 <= Horsepower <= 230 then [4381.0, 11.05, 10.0] (22)
1 elif origin == 2 then [2240.0, 15.6, 30.0] (68)
0 elif 153 <= Horsepower <= 175 then [4317.0, 12.0, 10.0] (22)
1 else [3158, 15.5, 20] (201)

6
0 if   Model <= 73 then [3280.0, 14.0, 20.0] (124)
1 elif origin == 3 then [2140.0, 16.4, 30.0] (64)
1 elif origin == 2 then [2223, 15.5, 30] (47)
0 elif 304 <= Displacement <= 400 then [4152.5, 13.5, 20.0] (32)
1 else [2945, 16.4, 20] (125)

7
1 if   80 <= Model <= 82 then [2395, 16.4, 30] (85)
1 elif origin == 2 then [2246, 15.5, 30] (55)
1 elif origin == 3 then [2155, 16.4, 30] (45)
0 elif 193 <= Horsepower <= 230 then [4403.5, 11.0, 10.0] (14)
1 else [3439, 14.9, 20] (193)

8
0 if   origin == 1 then [3381, 15, 20] (245)
0 elif 131 <= Displacement <= 183 then [2920.0, 15.15, 25.0] (20)
0 elif origin == 2 then [2202, 15.5, 30] (59)
1 elif Horsepower <= 70 then [1980.0, 17.45, 30.0] (36)
0 else [2295.0, 15.0, 30.0] (32)

9
1 if   origin == 3 then [2155, 16.4, 30] (79)
0 elif 390 <= Displacement <= 455 then [4425, 11.1, 10] (23)
0 elif origin == 1 then [3271.5, 15.45, 20.0] (222)
1 elif origin == 2 then [2240.0, 15.6, 30.0] (68)
0 else [] (0)

10
0 if   Model <= 73 then [3280.0, 14.0, 20.0] (124)
1 elif origin == 3 then [2140.0, 16.4, 30.0] (64)
0 elif 120 <= Horsepower <= 190 then [4054, 13.6, 20] (45)
1 elif Displacement <= 173 then [2451, 15.7, 30] (105)
0 else [3372.5, 17.05, 20.0] (54)

11
1 if   80 <= Model <= 82 then [2395, 16.4, 30] (85)
1 elif origin == 2 then [2246, 15.5, 30] (55)
0 elif origin == 1 then [3525, 14.5, 20] (207)
1 elif Horsepower <= 65 then [1818.0, 18.25, 30.0] (10)
0 else [2279, 15.5, 30] (35)

12
0 if   Model <= 73 then [3280.0, 14.0, 20.0] (124)
0 elif origin == 1 then [3193, 15.8, 20] (157)
1 elif Displacement <= 119 then [2065, 16.4, 30] (79)
1 elif origin == 2 then [3145.0, 16.3, 20.0] (18)
0 else [2683.5, 14.5, 30.0] (14)

13
1 if   origin == 3 then [2155, 16.4, 30] (79)
0 elif origin == 1 then [3381, 15, 20] (245)
1 elif Displacement <= 97 then [1995.0, 15.9, 30.0] (28)
1 elif 77 <= Model <= 82 then [2950, 15.8, 30] (15)
0 else [2582, 15.5, 20] (25)

14
0 if   origin == 1 then [3381, 15, 20] (245)
1 elif 62 <= Horsepower <= 75 then [2050, 16.6, 30] (57)
1 elif Horsepower <= 60 then [1851.0, 19.2, 35.0] (18)
1 elif Cylinders <= 4 then [2425.0, 14.95, 30.0] (60)
0 else [2930.0, 15.0, 20.0] (12)

15
1 if   Displacement <= 107 then [2070, 16.4, 30] (109)
1 elif Displacement <= 151 then [2582, 15.7, 30] (95)
1 elif Displacement <= 231 then [3102, 16, 20] (51)
1 elif Displacement <= 360 then [3801.0, 14.0, 20.0] (112)
0 else [4425, 11.1, 10] (25)

```

##### pom3a.csv
```
0
0 if   InitialKnown <= 0.535446107118 then [617.650545645, 0.3833877283025, 0.2743308167465] (4562)
0 elif 3.38773586343 <= Size <= 3.9955647093 then [961.474232696, 0.38595174255, 0.191199483746] (806)
1 else [567.209562095, 0.377538368156, 0.181818181818] (4607)

1
1 if   0.512033468642 <= InitialKnown <= 0.698017028435 then [618.113452456, 0.380071809258, 0.193548387097] (6147)
0 elif 0.918194310746 <= Criticality <= 1.19866725627 then [676.953188741, 0.384135514868, 0.278195488722] (2867)
1 else [493.730711182, 0.374600189456, 0.271186440678] (961)

2
0 if   33.7175877554 <= TeamSize <= 43.8778799814 then [725.689164608, 0.396687058757, 0.2] (2299)
1 elif 0.601872055649 <= InitialKnown <= 0.699305451038 then [591.8118423245, 0.3700329767365, 0.176224120933] (2428)
0 else [588.419799697, 0.3793193668825, 0.2584381352335] (5248)

3
1 if   Criticality <= 0.908023820855 then [476.69847933799997, 0.3767293882035, 0.222222222222] (2330)
1 elif 84.260032764 <= InterDependency <= 99.9382131444 then [661.301819798, 0.38070605794650003, 0.230375912598] (1206)
0 else [675.347139432, 0.382808967396, 0.225806451613] (6439)
```

An interesting result: even though it is cut short, the FFTrees on pom3a manage to capture a lot of data on the first two levels. In the 101 tree, the last leaf contains only 961 rows!

As a final note: we currently have no way of automatically picking which is the best tree (if there is one, that is). We lack a metric for choosing what better models the feature space.
