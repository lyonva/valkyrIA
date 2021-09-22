# Homework 5 Report
- CSC 791 Sinless Software Engineering
- By: Leonardo Villalobos Arias

## Description
The following improvements were done:
1. Add verbose mode to random projection. It shows a **dendogram** of the breaks and final groups.
2. Add method to **sort groups**, by their median y values.
3. Add method to suggest **discretization** (binning) of features by best and worst groups of a random projection.

### Dendogram
For the [Sample](https://github.com/lyonva/valkyrIA/blob/main/src/df/sample.py) class, the random projection method ```_divs``` now calls other methods that print a subgroup as a dendogram:

```
def _divs(self, rows, level, min_leaf_size, *, settings = {}):
        if len(rows) < 2*min_leaf_size:
            new = self.clone(rows, subsample=False)
            self._print_leaf(rows, level, settings=settings)
            return [new]
        self._print_node(rows, level, settings=settings)
        left, right = self.div1(rows, settings = settings)
        left = self._divs(left, level + 1, min_leaf_size, settings=settings)
        right = self._divs(right, level + 1, min_leaf_size, settings=settings)
        return left + right

    # Show a non-leaf node of the random projection
    def _print_node(self, rows, level, *, settings = {}):
        if settings.get("verbose") == True:
            text = "|.. " * level
            text += f"n={len(rows)} c={self.disonance(rows) : .2f}"
            print(text)
    
    # Print a subset as node of the random projection
    def _print_leaf(self, rows, level, *, settings = {}):
        if settings.get("verbose") == True:
            text = "|.. " * level
            text += f"n={len(rows)} c={self.disonance(rows) : .2f}"
            text += " " * 5
            text += "goals = ["
            if self.klass is not None:
                text += "-" # TODO
            elif len(self.y) > 0:
                data = self.sample_goals(rows)
                data = [ f"{d : .1f}" for d in data ]
                text += ",".join(data)
            else:
                text += "-"
            text += "]"
            print(text)
```

The result is that, if the verbose option is set, a call to divs will show the dendogram.

In addition, the groups are now returned as "sub-samples": copies of a sample that keep the columns but have different rows.


### Sort groups
We can sort a list of groups (sub-samples) by using the Zitler predicate. This was previously implemented for sorting the items *inside* a sample. To apply the same method to compare two samples, we generate a dummy median row. We sorted the samples by these values:

```
# Given a set of leaf clusters/groups
    # Sort them
    def sort_groups(self, groups, *, settings = {}):
        # First, create "median" representative rows for each cluster
        repr = [ [0 for c in self.cols] for g in groups ]
        # Set the correct median values for the column
        for i, g in enumerate(groups):
            for c in self.y:
                repr[i][c.at] = g.sample_median(c)
        
        # Second, use _zitler function to get sort order
        # Using argsort
        fun = lambda r1, r2: self._zitler(r1, r2)
        order = argsort(repr, key = cmp_to_key(fun), reverse = False)

        # Third, we re-sort the cluster with sortarg
        ordered_groups = sortarg(groups, order)

        # Fourth, if verbose, we show the results
        self._print_ordered_groups(ordered_groups, settings = settings)

        return ordered_groups
```

The sorted groups(median) are also printed if verbose is enabled.

### Discretization
The [sample](https://github.com/lyonva/valkyrIA/blob/main/src/df/sample.py) class can now make suggestions for discretization or binning of the samples for each *non-objective* feature. This is done by:
1. Using random projections to cluster the data
2. Sort the groups, pick best and worst ones
3. For each feature, find "cuts" that are interesting. Then show how they help divide best from worst.

Points 1 and 2 are covered on the previous two tasks. The discretization function in sample is the following:
```
def discretize(self, *, settings = {}):
        groups = self.divs(settings = settings)
        groups = self.sort_groups(groups, settings = settings)
        best, worst = groups[0], groups[-1]
        for good, bad in zip(best.x, worst.x):
            for res in good.discretize(bad):
                print(res)
        # Show some values from best and worst
        print("Best")
        print(best)
        print()
        print("Worst")
        print(worst)
```

Discretization is done in a per-[column](https://github.com/lyonva/valkyrIA/blob/main/src/df/column.py) basis, as this depends on the data type.

##### Sym
Discretization is basically built in. Every unique value is a bin.
```
def discretize(self, other):
        for val in set(self.count.keys() | other.count.keys()):
            yield bag( at = self.at, name = self.name,
                    lo = val, hi = val, best = self.get(val),
                    rest = other.get(val) )
```

##### Num
The following is the discretization code for Num:
```
def discretize(self, other):
        cohen = 0.3
        # Organize data
        X = [(good, 1) for good in self.val] + [(bad, 0) for bad in other.val]
        n1 = self.n
        n2 = other.n
        iota = cohen * (self.sd*n1 + other.sd*n2) / (n1 + n2)
        ranges = merge(unsuper(X, iota, sqrt(len(X))))
        
        if len(ranges) > 1:
            for r in ranges:
                counts = [x[1] for x in r]
                yield bag( at = self.at, name = self.name, lo = r[0][0],
                    hi = r[-1][0], best = counts.count(1), rest = counts.count(0))
```

Numerical features are divided in bands according to three rules:
1. Each group has at least sqrt(N) elements
2. Each group has variance of at least 30% of the variance of the total data (best and worst)
3. The last element of each group is *different* than the first element of the next group

The implementation is done on [auxiliary functions](https://github.com/lyonva/valkyrIA/blob/main/src/ml/group.py):

```
def unsuper(data, min_break, min_size):
    data.sort(key=lambda d: d[0])

    groups = []
    group = []
    nums = []

    while len(data) > 0:
        d = data.pop(0)
        x, _ = d

        group.append(d)
        nums.append(x)

        # Determine if break
        x1 = None if len(data) == 0 else data[0][0]

        if (x1 is None or (x != x1)) and (nums[-1] - nums[0] > min_break) and (len(nums) >= min_size):
            # New break
            groups.append(group)
            group = []
            nums = []
    
    # See if there is a remeinder
    if len(group) > 0:
        # It probably can not stand on its own, so add it to the last
        if len(groups) > 0:
            groups[-1] += group
        else:
            groups = [group]
    
    return groups
```

Lastly, we check if we can merge some of the grops. A merge is done if the result of merging 2 groups barely changes variance:
```
def merge(groups):
    proposal = []

    i = 0

    while i < len(groups) - 1:
        current = [g[0] for g in groups[i]]
        next = [g[0] for g in groups[i + 1]]
        both = current + next

        n1, n2 = len(current), len(next)
        var1, var2, var3 = var(current), var(next), var(both)

        # See if groups are dull
        # Dull = merge does not change variance
        if var3*0.95 <= (var1*n1 + var2*n2)/(n1+n2):
            proposal.append( groups[i] + groups[i+1] )
            i += 2
        else:
            proposal.append(groups[i])
            i += 1
    
    # Check if we need to add the last group
    # Note that if you merge the last 2 groups, then i = n
    if i == len(groups) - 1:
        proposal.append(groups[i])

    if len(proposal) < len(groups):
        return merge(proposal)
    else:
        return groups
```

The result of the discretization process is a set of possible partitions per feature and how well do they divide best from worst. See results for an example.

## Example
### Random-projection partition of data with dendogram
```
s = Sample(file)
groups = s.divs(settings = {"verbose":True})
```

### Sort those groups, from best to worst, using Zitler's function
```
sorted_groups = s.sort_groups(groups)
```

### Do discretization of features
```
s.discretize()
```

## Tests
As the name implies, random projections are _random_. As such, the test cases implemented for this homework mostly focus on capturing behavior and properties such as runtime instead of correctness.

The [test/test_random_projection.py](https://github.com/lyonva/valkyrIA/blob/main/test/test_random_projection.py) file from last homework is updated. It now shows the dendogram when doing random projections, and shows the sorted groups.

The file [test/test_discretize.py](https://github.com/lyonva/valkyrIA/blob/main/test/test_discretize.py) test the discretization method in the three datasets: weather, auto93, and pom3a. It relies on both projections and group sorting, but these are not shown in this test case.

## Results
The test were conducted by a github action for the commit [9c1f3c1](https://github.com/lyonva/valkyrIA/commit/9c1f3c173e4e8f94b332bfa4e743fb5a7897567b), and the corresponding [report](https://github.com/lyonva/valkyrIA/actions/runs/1260514926) shows that all test cases passed. The output generated by the program is included in each test case.

We show the results per dataset, at is easier to determine the effect.

### Weather

For weather, only 2 groups were generated. Thus, the dendogram is small:
```
|.. n=14 c= 1.00
|.. |.. n=7 c= 0.71     goals = [ 40.0, 40.0]
|.. |.. n=7 c= 0.88     goals = [ 30.0, 40.0]
```

Similarly, best and worst sorting only sort these two groups:
```
Wins+     Play-     
40.0      40.0       <== best
30.0      40.0       <== worst
```

A clear difference can be seen in Wins, but not really in play.

Not so surprisingly, the suggested bins are not so impactful:
```
{at:0, name:outlook, lo:sunny, hi:sunny, best:3, rest:2}
{at:0, name:outlook, lo:overcast, hi:overcast, best:2, rest:2}
{at:0, name:outlook, lo:rainy, hi:rainy, best:2, rest:3}
{at:1, name:Temp, lo:64, hi:72, best:3, rest:5}
{at:1, name:Temp, lo:75, hi:85, best:4, rest:2}
```

Only two features resulted in different bins: outlook and temp. From what we can see, outlook does not look all that influencial for victory. Sunny does have one more best, and rainy one more rest; so perhaps its a case of too little data. In the case of temp, the it seems higher the temp the better. The cut is still not as clear, however.

Lastly, we look at what the best and worst look like to confirm:
```
Best
outlook     Temp     ?Humidity     Windy     Wins+     Play-     
sunny       85       85            0         10        20        
sunny       72       95            0         7         20        
sunny       69       70            0         70        70              
rainy       75       80            0         80        40        
overcast    83       86            0         40        40        
overcast    81       75            0         30        60        
rainy       70       96            0         40        50        

Worst
outlook     Temp     ?Humidity     Windy     Wins+     Play-     
sunny       80       90            1         12        40        
rainy       68       80            0         50        30        
sunny       75       70            1         30        50        
rainy       71       91            1         50        40        
rainy       65       70            1         4         10        
overcast    72       90            1         60        50        
overcast    64       65            1         30        60        
```

Windy would have been an interesting suggestion, but our grouping method was not effective in this case. For the other two features, the results seem congruent.


### Auto93
Similar to last homework, 16 groups were generated. Each group contains 24-25 data points:

```
|.. n=392 c= 0.83
|.. |.. n=196 c= 0.64
|.. |.. |.. n=98 c= 0.59
|.. |.. |.. |.. n=49 c= 0.51
|.. |.. |.. |.. |.. n=24 c= 0.16     goals = [ 2332.5, 15.6, 30.0]
|.. |.. |.. |.. |.. n=25 c= 0.49     goals = [ 2205.0, 16.2, 30.0]
|.. |.. |.. |.. n=49 c= 0.32
|.. |.. |.. |.. |.. n=24 c= 0.27     goals = [ 2205.0, 16.4, 30.0]
|.. |.. |.. |.. |.. n=25 c= 0.32     goals = [ 2155.0, 16.5, 30.0]
|.. |.. |.. n=98 c= 0.64
|.. |.. |.. |.. n=49 c= 0.36
|.. |.. |.. |.. |.. n=24 c= 0.26     goals = [ 2137.0, 15.6, 30.0]
|.. |.. |.. |.. |.. n=25 c= 0.35     goals = [ 2464.0, 15.7, 30.0]
|.. |.. |.. |.. n=49 c= 0.55
|.. |.. |.. |.. |.. n=24 c= 0.51     goals = [ 2240.5, 16.8, 30.0]
|.. |.. |.. |.. |.. n=25 c= 0.46     goals = [ 2234.0, 15.5, 30.0]
|.. |.. n=196 c= 0.75
|.. |.. |.. n=98 c= 0.44
|.. |.. |.. |.. n=49 c= 0.41
|.. |.. |.. |.. |.. n=24 c= 0.29     goals = [ 4015.0, 14.0, 15.0]
|.. |.. |.. |.. |.. n=25 c= 0.18     goals = [ 4140.0, 13.2, 20.0]
|.. |.. |.. |.. n=49 c= 0.29
|.. |.. |.. |.. |.. n=24 c= 0.20     goals = [ 4112.5, 12.2, 10.0]
|.. |.. |.. |.. |.. n=25 c= 0.21     goals = [ 4425.0, 11.5, 10.0]
|.. |.. |.. n=98 c= 0.61
|.. |.. |.. |.. n=49 c= 0.61
|.. |.. |.. |.. |.. n=24 c= 0.59     goals = [ 2930.0, 16.4, 20.0]
|.. |.. |.. |.. |.. n=25 c= 0.29     goals = [ 3381.0, 16.6, 20.0]
|.. |.. |.. |.. n=49 c= 0.38
|.. |.. |.. |.. |.. n=24 c= 0.27     goals = [ 3061.5, 16.0, 20.0]
|.. |.. |.. |.. |.. n=25 c= 0.27     goals = [ 3158.0, 16.7, 20.0]
```

As for sorting these groups, the sorting algorithm seems to at least differentiate the very best from the worst. The top group does indeed have less weight, more acceleration, and more mpg. Going down the list does show some trade-offs, but defenitely at the bottom the worst groups are striclty worse to the best groups.

```
2155.0      16.5              30.0      <== best
2240.5      16.8              30.0     
2205.0      16.4              30.0     
2205.0      16.2              30.0     
2137.0      15.6              30.0     
2234.0      15.5              30.0     
2332.5      15.6              30.0     
2464.0      15.7              30.0     
2930.0      16.4              20.0     
3158.0      16.7              20.0     
3061.5      16.0              20.0     
3381.0      16.6              20.0     
4140.0      13.2              20.0     
4015.0      14.0              15.0     
4112.5      12.2              10.0     
4425.0      11.5              10.0      <== worst
```

The following are the suggested bins:
```
{at:1, name:Displacement, lo:70, hi:85, best:9, rest:0}
{at:1, name:Displacement, lo:91, hi:108, best:11, rest:0}
{at:1, name:Displacement, lo:113, hi:350, best:5, rest:4}
{at:1, name:Displacement, lo:360, hi:400, best:0, rest:12}
{at:1, name:Displacement, lo:429, hi:455, best:0, rest:9}
{at:2, name:Horsepower, lo:52, hi:68, best:8, rest:0}
{at:2, name:Horsepower, lo:70, hi:92, best:8, rest:0}
{at:2, name:Horsepower, lo:93, hi:100, best:8, rest:0}
{at:2, name:Horsepower, lo:110, hi:175, best:1, rest:8}
{at:2, name:Horsepower, lo:180, hi:208, best:0, rest:8}
{at:2, name:Horsepower, lo:210, hi:230, best:0, rest:9}
{at:6, name:origin, lo:3, hi:3, best:25, rest:0}
{at:6, name:origin, lo:1, hi:1, best:0, rest:25}
```

Three features were suggested. The first is Displacement, which appears to be a good separator. Displacement values above 350 are all rests, and below 108 are all bests. For horsepower we see a similar effect: bests are below 93 and rests are above 175. For origin we look at a similar cut: origin=3 is all bests and origin=1 is all rests.

The two groups:
```
Cylinders     Displacement     Horsepower     Weight-     Acceleration+     Model     origin     Mpg+     
4             98               68             2045        18.5              77        3          30       
4             97               67             1985        16.4              77        3          30       
4             85               70             1945        16.8              77        3          30       
4             97               75             2155        16.4              76        3          30       
4             134              96             2702        13.5              75        3          20       

4             120              97             2506        14.5              72        3          20       
4             113              95             2278        15.5              72        3          20       
4             97               92             2288        17                72        3          30       
4             97               88             2100        16.5              72        3          30       
3             70               90             2124        13.5              73        3          20       


Worst
Cylinders     Displacement     Horsepower     Weight-     Acceleration+     Model     origin     Mpg+     
8             400              170            4746        12                71        1          10       
8             360              170            4654        13                73        1          10       
8             350              175            4100        13                73        1          10       
8             318              210            4382        13.5              70        1          10       
8             383              180            4955        11.5              71        1          10       

8             455              225            4425        10                70        1          10       
8             455              225            3086        10                70        1          10       
8             440              215            4735        11                73        1          10       
8             400              230            4278        9.5               73        1          20       
8             455              225            4951        11                73        1          10       
```

You would think more horsepower is more acceleration, but apparently not. Two features that look meaningful were missed: Cylinders and Model. It appears newer cars with less cylinders are also a good signal of being best. These were possibly left out due to the magnitude of the features. The other features look correct, however.

### Pom3a

We have similarly around 64 groups like in last homework. Group sizes are around 50 to 60:
```
|.. n=9975 c= 0.75
|.. |.. n=4987 c= 0.61
|.. |.. |.. n=2493 c= 0.59
|.. |.. |.. |.. n=1246 c= 0.64
|.. |.. |.. |.. |.. n=623 c= 0.63
|.. |.. |.. |.. |.. |.. n=311 c= 0.61
|.. |.. |.. |.. |.. |.. |.. n=155 c= 0.56     goals = [ 825.6, 0.2, 0.3]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.58     goals = [ 800.8, 0.3, 0.3]
|.. |.. |.. |.. |.. |.. n=312 c= 0.52
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.51     goals = [ 1232.8, 0.5, 0.3]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.54     goals = [ 1306.0, 0.3, 0.3]
|.. |.. |.. |.. |.. n=623 c= 0.60
|.. |.. |.. |.. |.. |.. n=311 c= 0.59
|.. |.. |.. |.. |.. |.. |.. n=155 c= 0.55     goals = [ 559.0, 0.4, 0.3]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.50     goals = [ 562.0, 0.3, 0.3]
|.. |.. |.. |.. |.. |.. n=312 c= 0.51
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.57     goals = [ 1055.2, 0.3, 0.3]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.60     goals = [ 1048.4, 0.4, 0.2]
|.. |.. |.. |.. n=1247 c= 0.58
|.. |.. |.. |.. |.. n=623 c= 0.62
|.. |.. |.. |.. |.. |.. n=311 c= 0.56
|.. |.. |.. |.. |.. |.. |.. n=155 c= 0.58     goals = [ 402.5, 0.4, 0.3]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.56     goals = [ 538.3, 0.4, 0.3]
|.. |.. |.. |.. |.. |.. n=312 c= 0.57
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.57     goals = [ 295.3, 0.3, 0.3]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.52     goals = [ 357.0, 0.2, 0.3]
|.. |.. |.. |.. |.. n=624 c= 0.59
|.. |.. |.. |.. |.. |.. n=312 c= 0.57
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.57     goals = [ 714.9, 0.2, 0.4]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.56     goals = [ 974.1, 0.3, 0.3]
|.. |.. |.. |.. |.. |.. n=312 c= 0.52
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.53     goals = [ 851.8, 0.4, 0.2]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.60     goals = [ 499.8, 0.2, 0.3]
|.. |.. |.. n=2494 c= 0.73
|.. |.. |.. |.. n=1247 c= 0.61
|.. |.. |.. |.. |.. n=623 c= 0.61
|.. |.. |.. |.. |.. |.. n=311 c= 0.59
|.. |.. |.. |.. |.. |.. |.. n=155 c= 0.60     goals = [ 881.8, 0.3, 0.3]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.58     goals = [ 554.1, 0.3, 0.2]
|.. |.. |.. |.. |.. |.. n=312 c= 0.57
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.54     goals = [ 1001.6, 0.3, 0.2]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.52     goals = [ 971.9, 0.2, 0.3]
|.. |.. |.. |.. |.. n=624 c= 0.59
|.. |.. |.. |.. |.. |.. n=312 c= 0.58
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.55     goals = [ 314.4, 0.3, 0.3]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.55     goals = [ 412.0, 0.2, 0.3]
|.. |.. |.. |.. |.. |.. n=312 c= 0.57
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.57     goals = [ 506.6, 0.4, 0.3]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.52     goals = [ 351.5, 0.2, 0.3]
|.. |.. |.. |.. n=1247 c= 0.64
|.. |.. |.. |.. |.. n=623 c= 0.53
|.. |.. |.. |.. |.. |.. n=311 c= 0.65
|.. |.. |.. |.. |.. |.. |.. n=155 c= 0.57     goals = [ 407.3, 0.4, 0.3]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.52     goals = [ 402.7, 0.2, 0.3]
|.. |.. |.. |.. |.. |.. n=312 c= 0.58
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.56     goals = [ 367.2, 0.3, 0.2]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.56     goals = [ 577.9, 0.4, 0.2]
|.. |.. |.. |.. |.. n=624 c= 0.53
|.. |.. |.. |.. |.. |.. n=312 c= 0.56
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.56     goals = [ 801.1, 0.4, 0.1]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.58     goals = [ 401.2, 0.4, 0.2]
|.. |.. |.. |.. |.. |.. n=312 c= 0.55
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.54     goals = [ 386.0, 0.3, 0.3]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.52     goals = [ 473.3, 0.3, 0.2]
|.. |.. n=4988 c= 0.63
|.. |.. |.. n=2494 c= 0.64
|.. |.. |.. |.. n=1247 c= 0.61
|.. |.. |.. |.. |.. n=623 c= 0.71
|.. |.. |.. |.. |.. |.. n=311 c= 0.65
|.. |.. |.. |.. |.. |.. |.. n=155 c= 0.63     goals = [ 688.3, 0.5, 0.2]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.55     goals = [ 476.8, 0.4, 0.2]
|.. |.. |.. |.. |.. |.. n=312 c= 0.67
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.54     goals = [ 606.4, 0.5, 0.2]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.50     goals = [ 484.6, 0.5, 0.1]
|.. |.. |.. |.. |.. n=624 c= 0.58
|.. |.. |.. |.. |.. |.. n=312 c= 0.52
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.55     goals = [ 431.6, 0.3, 0.3]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.48     goals = [ 835.0, 0.3, 0.2]
|.. |.. |.. |.. |.. |.. n=312 c= 0.57
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.51     goals = [ 1000.2, 0.4, 0.2]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.61     goals = [ 949.4, 0.4, 0.2]
|.. |.. |.. |.. n=1247 c= 0.61
|.. |.. |.. |.. |.. n=623 c= 0.54
|.. |.. |.. |.. |.. |.. n=311 c= 0.56
|.. |.. |.. |.. |.. |.. |.. n=155 c= 0.58     goals = [ 545.2, 0.4, 0.2]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.48     goals = [ 461.9, 0.3, 0.3]
|.. |.. |.. |.. |.. |.. n=312 c= 0.55
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.59     goals = [ 661.4, 0.5, 0.2]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.49     goals = [ 319.4, 0.5, 0.2]
|.. |.. |.. |.. |.. n=624 c= 0.56
|.. |.. |.. |.. |.. |.. n=312 c= 0.53
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.54     goals = [ 407.1, 0.5, 0.1]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.54     goals = [ 428.8, 0.5, 0.1]
|.. |.. |.. |.. |.. |.. n=312 c= 0.60
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.55     goals = [ 572.9, 0.3, 0.2]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.53     goals = [ 775.5, 0.4, 0.1]
|.. |.. |.. n=2494 c= 0.59
|.. |.. |.. |.. n=1247 c= 0.62
|.. |.. |.. |.. |.. n=623 c= 0.57
|.. |.. |.. |.. |.. |.. n=311 c= 0.58
|.. |.. |.. |.. |.. |.. |.. n=155 c= 0.61     goals = [ 438.3, 0.4, 0.2]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.50     goals = [ 646.1, 0.4, 0.3]
|.. |.. |.. |.. |.. |.. n=312 c= 0.56
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.58     goals = [ 1157.9, 0.3, 0.2]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.56     goals = [ 736.3, 0.3, 0.2]
|.. |.. |.. |.. |.. n=624 c= 0.59
|.. |.. |.. |.. |.. |.. n=312 c= 0.56
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.60     goals = [ 716.2, 0.4, 0.2]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.53     goals = [ 515.6, 0.5, 0.2]
|.. |.. |.. |.. |.. |.. n=312 c= 0.54
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.47     goals = [ 786.8, 0.5, 0.2]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.60     goals = [ 1513.8, 0.5, 0.2]
|.. |.. |.. |.. n=1247 c= 0.58
|.. |.. |.. |.. |.. n=623 c= 0.60
|.. |.. |.. |.. |.. |.. n=311 c= 0.57
|.. |.. |.. |.. |.. |.. |.. n=155 c= 0.55     goals = [ 401.5, 0.5, 0.2]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.54     goals = [ 333.1, 0.4, 0.1]
|.. |.. |.. |.. |.. |.. n=312 c= 0.58
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.56     goals = [ 621.9, 0.5, 0.2]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.51     goals = [ 882.1, 0.4, 0.2]
|.. |.. |.. |.. |.. n=624 c= 0.57
|.. |.. |.. |.. |.. |.. n=312 c= 0.60
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.57     goals = [ 881.9, 0.5, 0.2]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.52     goals = [ 665.4, 0.4, 0.1]
|.. |.. |.. |.. |.. |.. n=312 c= 0.60
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.55     goals = [ 753.6, 0.5, 0.2]
|.. |.. |.. |.. |.. |.. |.. n=156 c= 0.60     goals = [ 1067.3, 0.4, 0.2]
```

For the groups sortings, we see larger differences on Cost and Scorei, and not so much on Idle:
```
Cost-     Scorei-     Idle-     
367.2     0.3         0.2        <== best
412.0     0.2         0.3       
333.1     0.4         0.1       
351.5     0.2         0.3       
572.9     0.3         0.2       
402.7     0.2         0.3       
357.0     0.2         0.3       
401.2     0.4         0.2       
461.9     0.3         0.3       
499.8     0.2         0.3       
407.1     0.5         0.1       
484.6     0.5         0.1       
314.4     0.3         0.3       
431.6     0.3         0.3       
473.3     0.3         0.2       
562.0     0.3         0.3       
428.8     0.5         0.1       
386.0     0.3         0.3       
476.8     0.4         0.2       
665.4     0.4         0.1       
295.3     0.3         0.3       
801.1     0.4         0.1       
554.1     0.3         0.2       
736.3     0.3         0.2       
438.3     0.4         0.2       
971.9     0.2         0.3       
775.5     0.4         0.1       
319.4     0.5         0.2       
825.6     0.2         0.3       
714.9     0.2         0.4       
835.0     0.3         0.2       
401.5     0.5         0.2       
402.5     0.4         0.3       
716.2     0.4         0.2       
1001.6    0.3         0.2       
545.2     0.4         0.2       
407.3     0.4         0.3       
1055.2    0.3         0.3       
800.8     0.3         0.3       
538.3     0.4         0.3       
506.6     0.4         0.3       
559.0     0.4         0.3       
974.1     0.3         0.3       
577.9     0.4         0.2       
882.1     0.4         0.2       
881.8     0.3         0.3       
661.4     0.5         0.2       
1048.4    0.4         0.2       
851.8     0.4         0.2       
1000.2    0.4         0.2       
606.4     0.5         0.2       
688.3     0.5         0.2       
515.6     0.5         0.2       
949.4     0.4         0.2       
646.1     0.4         0.3       
753.6     0.5         0.2       
621.9     0.5         0.2       
1157.9    0.3         0.2       
1067.3    0.4         0.2       
1306.0    0.3         0.3       
881.9     0.5         0.2       
786.8     0.5         0.2       
1232.8    0.5         0.3       
1513.8    0.5         0.2        <== worst
```

For the discretization, this time every feature did produce at least one split:
```
{at:0, name:Culture, lo:0.10258694771, hi:0.22540192391, best:34, rest:7}
{at:0, name:Culture, lo:0.227366446369, hi:0.344028534962, best:32, rest:17}
{at:0, name:Culture, lo:0.34438467357, hi:0.461778486092, best:46, rest:32}
{at:0, name:Culture, lo:0.462669517526, hi:0.583656818555, best:18, rest:30}
{at:0, name:Culture, lo:0.584681142002, hi:0.699347441003, best:18, rest:29}
{at:0, name:Culture, lo:0.702407386537, hi:0.891379333711, best:8, rest:41}
{at:1, name:Criticality, lo:0.820802845963, hi:1.02862094677, best:134, rest:33}
{at:1, name:Criticality, lo:1.02874602566, hi:1.19947113917, best:22, rest:123}
{at:2, name:CriticalityModifier, lo:2.05497089049, hi:3.17949779243, best:18, rest:0}
{at:2, name:CriticalityModifier, lo:3.20886970411, hi:3.7656471964, best:17, rest:1}
{at:2, name:CriticalityModifier, lo:3.78883319503, hi:4.94302894606, best:14, rest:4}
{at:2, name:CriticalityModifier, lo:4.96169676314, hi:6.37167886147, best:32, rest:16}
{at:2, name:CriticalityModifier, lo:6.38290409262, hi:7.54134198731, best:23, rest:40}
{at:2, name:CriticalityModifier, lo:7.55806621461, hi:9.9972818246, best:52, rest:95}
{at:3, name:InitialKnown, lo:0.405901380911, hi:0.53438076802, best:10, rest:67}
{at:3, name:InitialKnown, lo:0.534572912569, hi:0.699305451038, best:146, rest:89}
{at:4, name:InterDependency, lo:1.02876022048, hi:7.47604254943, best:31, rest:1}
{at:4, name:InterDependency, lo:7.5875125181, hi:13.8129382544, best:25, rest:3}
{at:4, name:InterDependency, lo:14.1491065286, hi:20.4022584779, best:23, rest:2}
{at:4, name:InterDependency, lo:20.5389508152, hi:26.7731967208, best:18, rest:4}
{at:4, name:InterDependency, lo:27.0612817706, hi:39.4865209271, best:36, rest:13}
{at:4, name:InterDependency, lo:39.7149929739, hi:46.9416452355, best:8, rest:15}
{at:4, name:InterDependency, lo:47.4168355004, hi:54.1265345609, best:4, rest:15}
{at:4, name:InterDependency, lo:54.3475459728, hi:78.6368740619, best:10, rest:48}
{at:4, name:InterDependency, lo:79.3817894865, hi:92.7069194678, best:1, rest:36}
{at:4, name:InterDependency, lo:93.250676621, hi:99.9810173884, best:0, rest:19}
{at:5, name:Dynamism, lo:1.20466831681, hi:7.44825255119, best:18, rest:0}
{at:5, name:Dynamism, lo:7.46577493319, hi:12.7646486587, best:17, rest:1}
{at:5, name:Dynamism, lo:12.8059704733, hi:16.2645918909, best:18, rest:1}
{at:5, name:Dynamism, lo:16.3676232105, hi:19.4049829772, best:18, rest:0}
{at:5, name:Dynamism, lo:19.423250472, hi:22.6521049344, best:21, rest:2}
{at:5, name:Dynamism, lo:23.1049993258, hi:25.9784334812, best:12, rest:6}
{at:5, name:Dynamism, lo:26.0186700219, hi:32.6025955303, best:30, rest:17}
{at:5, name:Dynamism, lo:32.9151362022, hi:38.7026470497, best:10, rest:38}
{at:5, name:Dynamism, lo:39.1491602529, hi:49.9765648015, best:12, rest:91}
{at:6, name:Size, lo:0.032862297841, hi:0.245275555665, best:19, rest:0}
{at:6, name:Size, lo:0.248366129538, hi:0.445766339688, best:23, rest:0}
{at:6, name:Size, lo:0.462484280702, hi:0.66715950954, best:23, rest:0}
{at:6, name:Size, lo:0.66721037836, hi:0.988841895952, best:18, rest:0}
{at:6, name:Size, lo:0.994565469302, hi:1.22372351464, best:19, rest:1}
{at:6, name:Size, lo:1.22424132671, hi:1.41852174406, best:20, rest:2}
{at:6, name:Size, lo:1.43441527546, hi:1.67740776481, best:16, rest:2}
{at:6, name:Size, lo:1.69821014717, hi:2.23048001473, best:10, rest:8}
{at:6, name:Size, lo:2.24989983272, hi:2.86533003125, best:5, rest:34}
{at:6, name:Size, lo:2.87017372328, hi:3.9954003641, best:3, rest:109}
{at:7, name:Plan, lo:0.00125948377998, hi:0.340536163472, best:27, rest:13}
{at:7, name:Plan, lo:0.355578349065, hi:0.683668474191, best:23, rest:13}
{at:7, name:Plan, lo:0.69175919591, hi:1.0328562418, best:22, rest:11}
{at:7, name:Plan, lo:1.03380299344, hi:1.36882244866, best:19, rest:18}
{at:7, name:Plan, lo:1.37677086254, hi:1.71121413811, best:15, rest:11}
{at:7, name:Plan, lo:1.73373794528, hi:2.06923286703, best:15, rest:19}
{at:7, name:Plan, lo:2.09421522283, hi:2.76442470126, best:22, rest:26}
{at:7, name:Plan, lo:2.76543457725, hi:4.97142899055, best:13, rest:45}
{at:8, name:TeamSize, lo:1.06408709123, hi:4.03962564951, best:28, rest:2}
{at:8, name:TeamSize, lo:4.04416062742, hi:6.98879268777, best:30, rest:2}
{at:8, name:TeamSize, lo:7.06554753523, hi:10.0258685148, best:26, rest:6}
{at:8, name:TeamSize, lo:10.1926817357, hi:13.092287433, best:13, rest:5}
{at:8, name:TeamSize, lo:13.1009556755, hi:19.2311211328, best:31, rest:18}
{at:8, name:TeamSize, lo:19.4153742371, hi:22.3192972086, best:9, rest:13}
{at:8, name:TeamSize, lo:22.4454628445, hi:25.6708545075, best:6, rest:12}
{at:8, name:TeamSize, lo:25.6850629326, hi:39.0242165634, best:12, rest:67}
{at:8, name:TeamSize, lo:39.4180953741, hi:43.8038020275, best:1, rest:31}
```

- Culture: Lower appears to correlate with best. The 3rd group does beg to differ.
- Criticality: Definitely a good feature to partition with, only two groups suggested as well. Low criticality = best.
- CriticalityModifier: Higher means more elements from rest, but not necesairly from best.
- InitialKnown: Not a good separator.
- InterDependency: Most bests seem to group in low values, and vice-versa.
- Dynamism: Higher means more elements from rest, but not necesairly from best.
- Size: A lot of groups, but we really need two: anything above from 2.87 is rest, and below that its best.
- Plan: Not a good separator.
- TeamSize: Lower seems to correlate with best. There is a middle group that contrains a lot from both.

These are the elements of best and rest:
```
Best
Culture     Criticality     CriticalityModifier     InitialKnown     InterDependency     Dynamism     Size     Plan     TeamSize     Cost-     Scorei-     Idle-     
0.1599954683710.871577406951  3.17949779243           0.698157249184   15.8820206777       1.204668316811.7804648320.075180428427515.1561980991243.4614638830.01434891805290.0740740740741
0.1524187373260.854141024614  3.03743940724           0.649671288879   38.1201461873       12.76464865871.174199570470.09030975146562.03346774909178.7181832870.1088727375350.107142857143
0.1108885243110.830063068405  6.14369542903           0.685309757603   56.3193055587       7.164142251621.574592341130.7611583774119.18306559928365.4388171250.07812387633510.21568627451
0.3322960291310.844623500115  3.04902220111           0.601262078686   16.6452951116       6.088841728442.230480014730.11031090318212.980563626 305.6214784890.1164557711770.131034482759
0.250317989280.933632717458  3.72055393144           0.67625414677    25.6318176307       12.16162030091.35996076181.426072930974.34295822177311.7100471320.1658454257020.298507462687

0.4089659964720.991251950421  8.91731047701           0.627009179952   9.058782632         21.31761027173.200849180420.044351532161725.50811318911349.693996940.2613407931690.0       
0.574205169040.951338148492  9.68772017238           0.694043004422   31.9428519049       15.19649526111.347246321563.221947567686.29018223573575.2239170220.2496187267490.0       
0.5846811420020.88392021796   6.62161149917           0.54066462404    44.4709262963       42.08950575960.6497759302410.5419871325024.94741441218344.7739399190.3462571671420.153846153846
0.7261866031430.930130431091  3.78883319503           0.585400354221   13.3490939237       48.41030723190.8460504013050.1488621336798.72608301156227.7838123330.762358841320.0       
0.4140663335060.882240905622  9.13725197051           0.602205821275   44.798917045        42.70291368980.2054306822241.044809183931.65416954237281.7680870.2933675840380.0       


Worst
Culture     Criticality     CriticalityModifier     InitialKnown     InterDependency     Dynamism     Size     Plan     TeamSize     Cost-     Scorei-     Idle-     
0.5466191082481.09182868579   6.82066641987           0.532490536651   84.7038400967       38.56235279433.004417699961.3688224486611.28668713631218.471713970.4897051703840.0262172284644
0.802084299041.13857899828   6.35837084779           0.567536267057   87.164689681        48.43640874873.990499780220.21253140938431.14139160851733.78345310.5458937768880.0350318471338
0.6930379703181.19380436622   4.94302894606           0.677300974832   73.8241310917       45.55637484093.51660080310.60640889208340.14027327661300.389641920.5512387012590.178053830228
0.4783797722741.1765727583    5.85157326484           0.698592661805   92.3170708          38.22144196042.727757488821.1767071136123.1621279902883.4745585530.3886051842170.0       
0.7511142681131.06959976912   8.19123442954           0.503161238206   97.7750870584       25.64837000573.679007806720.73925166734919.58182328261599.075371650.4862033494050.0756880733945

0.3251854474121.04160330918   9.78234796961           0.565333941109   64.9149935209       41.27448500733.346072645621.6685584831842.10970298642235.872490250.4270074499830.469387755102
0.3666970100780.940454445045  9.9151533446            0.583262169769   84.6935893439       36.04167194893.647440287682.6520528438837.74204710231730.012099350.4962128727460.424541607898
0.408854091881.0809751087    9.08841112101           0.572436187165   11.9029850527       41.35665570283.761260409573.301855124134.78845214292157.099564370.5170052899850.339285714286
0.1128079900941.11770343631   9.62243626605           0.541831470839   50.755641623        42.74201927033.789028765062.9140536667219.82311429282125.160731030.3093163502640.239543726236
0.2382333088961.06709768045   9.50062582914           0.610020985056   38.067201961        42.27322863873.965237656822.9300105227236.21319276642503.126275440.4235091906720.333898305085
```
