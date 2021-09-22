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


