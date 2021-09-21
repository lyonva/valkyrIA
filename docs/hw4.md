# Homework 4 Report
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
As the name implies, random projections are _random_. As such, the test cases implemented for this homework mostly focus on capturing behavior and properties such as runtime instead of correctness. Two tests were implemented:
- [test/test_distance_neighbors.py](https://github.com/lyonva/valkyrIA/blob/main/test/test_distance_neighbors.py): Tests the distance function of ``Num``, ``Sym``, and ``Sample``; and tests the neighbor function of ``Sample``. The test case shows, for each row, the row that is the closest and the one that is the farthest. Tests were implemented only for the auto93.csv file, but others can easily be added.
- [test/test_random_projection.py](https://github.com/lyonva/valkyrIA/blob/main/test/test_random_projection.py): Tests the random projection partition function of ``Sample``, verifying that the partitions are of the right size and that no partition has more disonance than the complete set. The test cases were implemented for the weather, auto93, and pom3a sets. Times and the partitions generated were recorded.

## Results
The test were conducted by a github action for the commit [86c16c8](https://github.com/lyonva/valkyrIA/commit/86c16c85e18705a682da8e80bc3fb391183619e0), and the corresponding [report](https://github.com/lyonva/valkyrIA/actions/runs/1231332402) shows that all test cases passed. The output generated by the program is included in each test case.

### Neighbors
The following is an example of the output produced by the test case:
```
Row:  [8, 383, 180, 4955, 11.5, 71, '1', 10]
Nearest: d = 0.02310004268289592 [8, 400, 175, 5140, 12, 71, '1', 10]
Farthest: d = 0.8378970651607536 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 350, 160, 4456, 13.5, 72, '1', 10]
Nearest: d = 0.012152543355977123 [8, 350, 165, 4274, 12, 72, '1', 10]
Farthest: d = 0.7882064757632686 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 429, 198, 4952, 11.5, 73, '1', 10]
Nearest: d = 0.04322976744898665 [8, 440, 215, 4735, 11, 73, '1', 10]
Farthest: d = 0.8447565087773833 [4, 97, 52, 2130, 24.6, 82, '2', 40]
```
In some cases, mainly due to the features that are ignored, the closest datapoint has a distance of 0.

### Random Projections
The following table summarizes the times and partitions produced for the teste datasets:

Dataset | Time (ms) | # Partitions
---- | ----: | ----:
weather | 1 | 2
auto93 | 106 | 16
pom3a | 4345 | 64


Execution time appears to grow cuadratically with the size of the dataset.

One interesting observation is that disonance (i.e. distance between the farthest away points) gets _smaller_ as the dataset is larger. Dissonance for the complete weather, auto93, and pom3a sets is 1, 0.936, and 0.736. This only means that, as more data is added, the less "corners" the dataset has. This may imply that random projections get worse as more data is added.

The dissonance of all generated samples ranged from as low as 0.12 to as high as 0.88. However, in all cases the generated partitions had less disonance than the original set. The partitioning was most effective at reducing dissonance to the auto93 set.
