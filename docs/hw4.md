# Homework 3 Report
- CSC 791 Sinless Software Engineering
- By: Leonardo Villalobos Arias

## Description
#### Column
Random projections were implemented for the [Sample](https://github.com/lyonva/valkyrIA/blob/main/src/df/sample.py) class. These random projections are a method to partition data into groups depending on a measure of distance (Euclidean).

To do this, a measure of distance was added for each type of data, implemented on the subclasses of [column](https://github.com/lyonva/valkyrIA/blob/main/src/df/column.py). For numerical columns (Num class), distance is calculated as the difference of the normalized ([0,1] range) numbers. For categorical columns (Sym class), distance is calculated as 0 if the text values are the same, and 1 otherwise. Missing values are handled assumed the worst case scenario. This is implemented as the ``distance`` method in these classes.

Back in the ``Sample`` class, a generalized metric of distance between 2 rows was implemented, under the function ``distance``. The current implementation calculates the Euclidean distance between the two rows using all the Num and Sym columns. Other measures of distance (Manhattan) can be easily implemented in the future. The following auxiliary methods were implemented as well:
-``neighbors`` takes one row ``r`` and a list of rows (all data if none is specified) and returns the list sorted from nearest to farthest to ``r``.
-``faraway`` takes one row ``r`` and a list of rows (all data if none is specified) and returns a randomly sampled element that is the farthest away.
-``shuffle`` takes a list of rows (all data if none is specified) and randomly selects a subsample. The amount of samples can be specified, and otherwise the method just randomizes the order of the rows.
-``disonance`` takes a list of rows (all data if none is specified) and calculates the maximum distance between the two elements that are farthest away.
-``norm_disonance`` works like ``disonance`` but divides the score by the disonance of the entire data.

With these methods, the random projection algorithm was implemented. The algorithm works as follows:

```
do_1_random_projection(data):
  zero = one random sample of data
  A = the point farthest from zero
  B = the point farthest from A
  Our new dimension is the line(hyperplane) that goes through A and B
  for each point C in data
    calculate the projection of C in the AB line: point D
    calculate the distance from A to D: x
    x is the new "feature" value
  Sort all points according to their x score
  Partition these sorted points. This results on a group closer to A and a group closer to B.
  
do_random_projections(data):
  if data is not too small:
    A, B = do_1_random_projection(data)
    do_random_projections(A)
    do_random_projections(B)
```

These functions were implemented in the ``Sample`` class as ``div1`` and ``divs``, respectively. ``div1`` does a random projection and partition in one dimension, and ``divs`` does this process recursively until a stop condition is achieved. In this implementation, the data is divided until no more divisions of size at least sqrt(n) are possible. Finally, ``divs`` returns a list of partitions. Each partition is a list of rows that can be joined to form the complete ``Sample``.

## Example

### Calculate the distance between two rows
```
s = Sample(file)
d = s.distance(row1, row2)
```
d is a measure of distance between the rows, in the range [0,1]. A distance of 0 means the points are in the same space, and a distance of 1 means they are complete opposites.

### Get data by proximity of a certain row
```
neigh = s.neighbors(row1)
```
This returns a list of all the rows in the sample (_sans_ row), ordered from nearest to row to farthest from row.

Neighbors can also be calculated from a subset:
```
neigh = s.neighbors(row1, rows = subsample)
```
Where subsample is a list of rows that are a subset of the complete data space in ``s``.

### Randomly sample rows
```
subsample = s.shuffle(samples = 128)
```
This returns a random selection of 128 rows, as a list of lists.

Similarly, a subsample can be further sampled:
```
subsubsample = s.shuffle(rows = subsample, samples = 128)
```

### Get a point that is faraway
```
far = s.farthest(row1)
```
Randomly samples all data (to speed up process) and returns the row that is farthest away from ``row1``.

Similarly, we can get this row from only a subset of the data:
```
far = s.farthest(row1, rows = subsample)
```

### Determine how closely grouped is the data
```
d = s.disonance()
```
Returns the distance between the points that are the most far away. This measure is not sampled, so it is resource intensive.

Disonance can be also determined for a subset. Useful for knowing when a partition can succesfully make data closer:
```
d = s.disonance(rows = subsample)
```

### Divide all data using random projections
```
groups = s.divs()
```
The result, ``groups`` is a partition of the data. Each item of ``groups`` is a **subset**, represented as a list of lists.


## Tests
As the name implies, random projections are _random_. As such, the test cases implemented for this homework mostly focus on capturing behavior and properties such as runtime instead of correctness.
