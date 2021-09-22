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
The test were conducted by a github action for the commit [86c16c8](https://github.com/lyonva/valkyrIA/commit/86c16c85e18705a682da8e80bc3fb391183619e0), and the corresponding [report](https://github.com/lyonva/valkyrIA/actions/runs/1231332402) shows that all test cases passed. The output generated by the program is included in each test case. The relevant raw output of each test case is at the end of this document.

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

### Output

#### Random projection on weather
```
2 groups
Done in 0.922680 ms
Initial maximum distance is  1.000
Group 1 has 7 items and a max distance of  0.881
Group 2 has 7 items and a max distance of  0.694
```

#### Random projection on auto93
```
16 groups
Done in 105.824471 ms
Initial maximum distance is  0.936
Group 1 has 24 items and a max distance of  0.538
Group 2 has 25 items and a max distance of  0.183
Group 3 has 24 items and a max distance of  0.353
Group 4 has 25 items and a max distance of  0.248
Group 5 has 24 items and a max distance of  0.261
Group 6 has 25 items and a max distance of  0.199
Group 7 has 24 items and a max distance of  0.206
Group 8 has 25 items and a max distance of  0.187
Group 9 has 24 items and a max distance of  0.187
Group 10 has 25 items and a max distance of  0.314
Group 11 has 24 items and a max distance of  0.521
Group 12 has 25 items and a max distance of  0.479
Group 13 has 24 items and a max distance of  0.368
Group 14 has 25 items and a max distance of  0.188
Group 15 has 24 items and a max distance of  0.121
Group 16 has 25 items and a max distance of  0.457
```

#### Random projection on pom3a
```
64 groups
Done in 4344.971180 ms
Initial maximum distance is  0.736
Group 1 has 155 items and a max distance of  0.579
Group 2 has 156 items and a max distance of  0.538
Group 3 has 156 items and a max distance of  0.605
Group 4 has 156 items and a max distance of  0.527
Group 5 has 155 items and a max distance of  0.624
Group 6 has 156 items and a max distance of  0.535
Group 7 has 156 items and a max distance of  0.560
Group 8 has 156 items and a max distance of  0.519
Group 9 has 155 items and a max distance of  0.538
Group 10 has 156 items and a max distance of  0.539
Group 11 has 156 items and a max distance of  0.604
Group 12 has 156 items and a max distance of  0.565
Group 13 has 156 items and a max distance of  0.521
Group 14 has 156 items and a max distance of  0.597
Group 15 has 156 items and a max distance of  0.551
Group 16 has 156 items and a max distance of  0.495
Group 17 has 155 items and a max distance of  0.568
Group 18 has 156 items and a max distance of  0.531
Group 19 has 156 items and a max distance of  0.490
Group 20 has 156 items and a max distance of  0.551
Group 21 has 156 items and a max distance of  0.527
Group 22 has 156 items and a max distance of  0.550
Group 23 has 156 items and a max distance of  0.514
Group 24 has 156 items and a max distance of  0.512
Group 25 has 155 items and a max distance of  0.482
Group 26 has 156 items and a max distance of  0.569
Group 27 has 156 items and a max distance of  0.645
Group 28 has 156 items and a max distance of  0.526
Group 29 has 156 items and a max distance of  0.462
Group 30 has 156 items and a max distance of  0.567
Group 31 has 156 items and a max distance of  0.537
Group 32 has 156 items and a max distance of  0.602
Group 33 has 155 items and a max distance of  0.623
Group 34 has 156 items and a max distance of  0.554
Group 35 has 156 items and a max distance of  0.475
Group 36 has 156 items and a max distance of  0.560
Group 37 has 156 items and a max distance of  0.519
Group 38 has 156 items and a max distance of  0.578
Group 39 has 156 items and a max distance of  0.577
Group 40 has 156 items and a max distance of  0.569
Group 41 has 155 items and a max distance of  0.526
Group 42 has 156 items and a max distance of  0.594
Group 43 has 156 items and a max distance of  0.503
Group 44 has 156 items and a max distance of  0.477
Group 45 has 156 items and a max distance of  0.584
Group 46 has 156 items and a max distance of  0.589
Group 47 has 156 items and a max distance of  0.538
Group 48 has 156 items and a max distance of  0.510
Group 49 has 155 items and a max distance of  0.549
Group 50 has 156 items and a max distance of  0.479
Group 51 has 156 items and a max distance of  0.577
Group 52 has 156 items and a max distance of  0.587
Group 53 has 156 items and a max distance of  0.619
Group 54 has 156 items and a max distance of  0.549
Group 55 has 156 items and a max distance of  0.528
Group 56 has 156 items and a max distance of  0.600
Group 57 has 155 items and a max distance of  0.508
Group 58 has 156 items and a max distance of  0.514
Group 59 has 156 items and a max distance of  0.568
Group 60 has 156 items and a max distance of  0.587
Group 61 has 156 items and a max distance of  0.502
Group 62 has 156 items and a max distance of  0.531
Group 63 has 156 items and a max distance of  0.550
Group 64 has 156 items and a max distance of  0.578
```

#### Neighbors auto93
```
Row:  [8, 304, 193, 4732, 18.5, 70, '1', 10]
Nearest: d = 0.01736317241002193 [8, 307, 200, 4376, 15, 70, '1', 10]
Farthest: d = 0.8382509109345883 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 360, 215, 4615, 14, 70, '1', 10]
Nearest: d = 0.05003310880432553 [8, 318, 210, 4382, 13.5, 70, '1', 10]
Farthest: d = 0.8816578456075281 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 307, 200, 4376, 15, 70, '1', 10]
Nearest: d = 0.01736317241002193 [8, 304, 193, 4732, 18.5, 70, '1', 10]
Farthest: d = 0.8463366804832029 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 318, 210, 4382, 13.5, 70, '1', 10]
Nearest: d = 0.027428441624535522 [8, 307, 200, 4376, 15, 70, '1', 10]
Farthest: d = 0.8606354742160611 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 429, 208, 4633, 11, 72, '1', 10]
Nearest: d = 0.04289443211421362 [8, 440, 215, 4735, 11, 73, '1', 10]
Farthest: d = 0.8705416202921752 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 400, 150, 4997, 14, 73, '1', 10]
Nearest: d = 0.0 [8, 400, 150, 4464, 12, 73, '1', 10]
Farthest: d = 0.7926209304862524 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 350, 180, 3664, 11, 73, '1', 10]
Nearest: d = 0.0 [8, 350, 180, 4499, 12.5, 73, '1', 10]
Farthest: d = 0.7891535701483156 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 383, 180, 4955, 11.5, 71, '1', 10]
Nearest: d = 0.02310004268289592 [8, 400, 175, 5140, 12, 71, '1', 10]
Farthest: d = 0.8378970651607536 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 350, 160, 4456, 13.5, 72, '1', 10]
Nearest: d = 0.012152543355977123 [8, 350, 165, 4274, 12, 72, '1', 10]
Farthest: d = 0.7882064757632686 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 429, 198, 4952, 11.5, 73, '1', 10]
Nearest: d = 0.04322976744898665 [8, 440, 215, 4735, 11, 73, '1', 10]
Farthest: d = 0.8447565087773833 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 455, 225, 4951, 11, 73, '1', 10]
Nearest: d = 0.02985297225826908 [8, 440, 215, 4735, 11, 73, '1', 10]
Farthest: d = 0.8879474371975149 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 400, 167, 4906, 12.5, 73, '1', 10]
Nearest: d = 0.041318647410322235 [8, 400, 150, 4997, 14, 73, '1', 10]
Farthest: d = 0.8007657617806032 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 350, 180, 4499, 12.5, 73, '1', 10]
Nearest: d = 0.0 [8, 350, 180, 3664, 11, 73, '1', 10]
Farthest: d = 0.7891535701483156 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 400, 170, 4746, 12, 71, '1', 10]
Nearest: d = 0.012152543355977123 [8, 400, 175, 5140, 12, 71, '1', 10]
Farthest: d = 0.8372040456804744 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 400, 175, 5140, 12, 71, '1', 10]
Nearest: d = 0.0 [8, 400, 175, 4464, 11.5, 71, '1', 10]
Farthest: d = 0.841444589884958 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 350, 165, 4274, 12, 72, '1', 10]
Nearest: d = 0.012152543355977123 [8, 350, 160, 4456, 13.5, 72, '1', 10]
Farthest: d = 0.7923364783587764 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 350, 155, 4502, 13.5, 72, '1', 10]
Nearest: d = 0.004996486709349038 [8, 351, 153, 4129, 13, 72, '1', 10]
Farthest: d = 0.7842430557884171 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 400, 190, 4422, 12.5, 72, '1', 10]
Nearest: d = 0.03645763006793137 [8, 400, 175, 4385, 12, 72, '1', 10]
Farthest: d = 0.8378482524472787 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 307, 130, 4098, 14, 72, '1', 10]
Nearest: d = 0.024982433546745324 [8, 302, 140, 4294, 16, 72, '1', 10]
Farthest: d = 0.7544620836181126 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 302, 140, 4294, 16, 72, '1', 10]
Nearest: d = 0.024414725052933142 [8, 304, 150, 3892, 12.5, 72, '1', 20]
Farthest: d = 0.7551269476968361 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 350, 175, 4100, 13, 73, '1', 10]
Nearest: d = 0.011555906860464033 [8, 360, 175, 3821, 11, 73, '1', 10]
Farthest: d = 0.7844422253517994 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 350, 145, 3988, 13, 73, '1', 10]
Nearest: d = 0.0 [8, 350, 145, 4082, 13, 73, '1', 20]
Farthest: d = 0.7646649904548912 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 400, 150, 4464, 12, 73, '1', 10]
Nearest: d = 0.0 [8, 400, 150, 4997, 14, 73, '1', 10]
Farthest: d = 0.7926209304862524 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 351, 158, 4363, 13, 73, '1', 10]
Nearest: d = 0.030964951190608 [8, 360, 170, 4654, 13, 73, '1', 10]
Farthest: d = 0.7703062202583362 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 440, 215, 4735, 11, 73, '1', 10]
Nearest: d = 0.02985297225826908 [8, 455, 225, 4951, 11, 73, '1', 10]
Farthest: d = 0.868654278673615 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 360, 175, 3821, 11, 73, '1', 10]
Nearest: d = 0.011555906860464033 [8, 350, 175, 4100, 13, 73, '1', 10]
Farthest: d = 0.7888220435919991 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 360, 170, 4654, 13, 73, '1', 10]
Nearest: d = 0.012152543355977123 [8, 360, 175, 3821, 11, 73, '1', 10]
Farthest: d = 0.7842970309224347 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 350, 150, 4699, 14.5, 74, '1', 10]
Nearest: d = 0.036978901953484876 [8, 318, 150, 4457, 13.5, 74, '1', 10]
Farthest: d = 0.7546277187873385 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 302, 129, 3169, 12, 75, '1', 10]
Nearest: d = 0.03734697124653677 [8, 302, 130, 3870, 15, 76, '1', 10]
Farthest: d = 0.7152386628385657 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 318, 150, 3940, 13.2, 76, '1', 10]
Nearest: d = 0.0 [8, 318, 150, 3755, 14, 76, '1', 10]
Farthest: d = 0.7217671699560936 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [8, 350, 145, 4055, 12, 76, '1', 10]
Nearest: d = 0.017052760406184368 [8, 351, 152, 4215, 12.8, 76, '1', 10]
Farthest: d = 0.7352056659152298 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [8, 302, 130, 3870, 15, 76, '1', 10]
Nearest: d = 0.024414725052933166 [8, 304, 120, 3962, 13.9, 76, '1', 20]
Farthest: d = 0.7074824189861448 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [8, 318, 150, 3755, 14, 76, '1', 10]
Nearest: d = 0.0 [8, 318, 150, 3940, 13.2, 76, '1', 10]
Farthest: d = 0.7217671699560936 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [8, 454, 220, 4354, 9, 70, '1', 10]
Nearest: d = 0.012207362526466594 [8, 455, 225, 4425, 10, 70, '1', 10]
Farthest: d = 0.9300127835418535 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 440, 215, 4312, 8.5, 70, '1', 10]
Nearest: d = 0.020234147311404896 [8, 454, 220, 4354, 9, 70, '1', 10]
Farthest: d = 0.917638412370569 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 455, 225, 4425, 10, 70, '1', 10]
Nearest: d = 0.0 [8, 455, 225, 3086, 10, 70, '1', 10]
Farthest: d = 0.9359223532033172 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 340, 160, 3609, 8, 70, '1', 10]
Nearest: d = 0.016769713574972693 [8, 350, 165, 3693, 11.5, 70, '1', 20]
Farthest: d = 0.8220444184904028 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 455, 225, 3086, 10, 70, '1', 10]
Nearest: d = 0.0 [8, 455, 225, 4425, 10, 70, '1', 10]
Farthest: d = 0.9359223532033172 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 350, 165, 4209, 12, 71, '1', 10]
Nearest: d = 0.02918898791569452 [8, 351, 153, 4154, 13.5, 71, '1', 10]
Farthest: d = 0.8105330108050223 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 400, 175, 4464, 11.5, 71, '1', 10]
Nearest: d = 0.0 [8, 400, 175, 5140, 12, 71, '1', 10]
Farthest: d = 0.841444589884958 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 351, 153, 4154, 13.5, 71, '1', 10]
Nearest: d = 0.02918898791569452 [8, 350, 165, 4209, 12, 71, '1', 10]
Farthest: d = 0.8015426825348647 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 318, 150, 4096, 13, 71, '1', 10]
Nearest: d = 0.03726779962499649 [8, 318, 150, 4077, 14, 72, '1', 10]
Farthest: d = 0.7861372240003939 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 400, 175, 4385, 12, 72, '1', 10]
Nearest: d = 0.03645763006793137 [8, 400, 190, 4422, 12.5, 72, '1', 10]
Farthest: d = 0.823931023314451 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 351, 153, 4129, 13, 72, '1', 10]
Nearest: d = 0.004996486709349038 [8, 350, 155, 4502, 13.5, 72, '1', 10]
Farthest: d = 0.7831372837877918 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 318, 150, 4077, 14, 72, '1', 10]
Nearest: d = 0.0 [8, 318, 150, 4135, 13.5, 72, '1', 20]
Farthest: d = 0.767362410007409 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 304, 150, 3672, 11.5, 73, '1', 10]
Nearest: d = 0.016178269604649638 [8, 318, 150, 4237, 14.5, 73, '1', 10]
Farthest: d = 0.7456169206035191 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 302, 137, 4042, 14.5, 73, '1', 10]
Nearest: d = 0.03168102736753492 [8, 304, 150, 3672, 11.5, 73, '1', 10]
Farthest: d = 0.7402828991541222 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 318, 150, 4237, 14.5, 73, '1', 10]
Nearest: d = 0.0 [8, 318, 150, 3777, 12.5, 73, '1', 20]
Farthest: d = 0.7516354188620492 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 318, 150, 4457, 13.5, 74, '1', 10]
Nearest: d = 0.016178269604649638 [8, 304, 150, 4257, 15.5, 74, '1', 10]
Farthest: d = 0.7395270430027374 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 302, 140, 4638, 16, 74, '1', 10]
Nearest: d = 0.0 [8, 302, 140, 4141, 14, 74, '1', 20]
Farthest: d = 0.728922367779348 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 304, 150, 4257, 15.5, 74, '1', 10]
Nearest: d = 0.016178269604649638 [8, 318, 150, 4457, 13.5, 74, '1', 10]
Farthest: d = 0.7334091877899532 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 351, 148, 4657, 13.5, 75, '1', 10]
Nearest: d = 0.007382529474406659 [8, 350, 145, 4440, 14, 75, '1', 20]
Farthest: d = 0.7441616255159558 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 351, 152, 4215, 12.8, 76, '1', 10]
Nearest: d = 0.017052760406184368 [8, 350, 145, 4055, 12, 76, '1', 10]
Farthest: d = 0.7386039130626744 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [8, 350, 165, 3693, 11.5, 70, '1', 20]
Nearest: d = 0.016769713574972693 [8, 340, 160, 3609, 8, 70, '1', 10]
Farthest: d = 0.8300049433883505 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 429, 198, 4341, 10, 70, '1', 20]
Nearest: d = 0.04322976744898665 [8, 440, 215, 4312, 8.5, 70, '1', 10]
Farthest: d = 0.8950494730023325 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 390, 190, 3850, 8.5, 70, '1', 20]
Nearest: d = 0.04522234216418568 [8, 383, 180, 4955, 11.5, 71, '1', 10]
Farthest: d = 0.8689889998333429 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 383, 170, 3563, 10, 70, '1', 20]
Nearest: d = 0.04002404076168936 [8, 350, 165, 3693, 11.5, 70, '1', 20]
Farthest: d = 0.8482239092029819 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 400, 150, 3761, 9.5, 70, '1', 20]
Nearest: d = 0.05242973032769832 [8, 383, 170, 3563, 10, 70, '1', 20]
Farthest: d = 0.8410322287385494 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 318, 150, 4135, 13.5, 72, '1', 20]
Nearest: d = 0.0 [8, 318, 150, 4077, 14, 72, '1', 10]
Farthest: d = 0.767362410007409 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 304, 150, 3892, 12.5, 72, '1', 20]
Nearest: d = 0.0 [8, 304, 150, 3672, 11.5, 72, '1', 20]
Farthest: d = 0.7621308368049315 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 318, 150, 3777, 12.5, 73, '1', 20]
Nearest: d = 0.0 [8, 318, 150, 4237, 14.5, 73, '1', 10]
Farthest: d = 0.7516354188620492 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 350, 145, 4082, 13, 73, '1', 20]
Nearest: d = 0.0 [8, 350, 145, 3988, 13, 73, '1', 10]
Farthest: d = 0.7646649904548912 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 318, 150, 3399, 11, 73, '1', 20]
Nearest: d = 0.0 [8, 318, 150, 4237, 14.5, 73, '1', 10]
Farthest: d = 0.7516354188620492 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [6, 250, 100, 3336, 17, 74, '1', 20]
Nearest: d = 0.0 [6, 250, 100, 3781, 17, 74, '1', 20]
Farthest: d = 0.6047806342111002 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 250, 72, 3432, 21, 75, '1', 20]
Nearest: d = 0.0 [6, 250, 72, 3158, 19.5, 75, '1', 20]
Farthest: d = 0.595499985554623 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [6, 250, 72, 3158, 19.5, 75, '1', 20]
Nearest: d = 0.0 [6, 250, 72, 3432, 21, 75, '1', 20]
Farthest: d = 0.595499985554623 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 350, 145, 4440, 14, 75, '1', 20]
Nearest: d = 0.007382529474406659 [8, 351, 148, 4657, 13.5, 75, '1', 10]
Farthest: d = 0.7425491325791483 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [6, 258, 110, 3730, 19, 75, '1', 20]
Nearest: d = 0.015269225893091124 [6, 250, 105, 3897, 18.5, 75, '1', 20]
Farthest: d = 0.5954347959184497 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 302, 130, 4295, 14.9, 77, '1', 20]
Nearest: d = 0.03662208757939976 [8, 305, 145, 3880, 12.5, 77, '1', 20]
Farthest: d = 0.7162620841385414 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [8, 304, 120, 3962, 13.9, 76, '1', 20]
Nearest: d = 0.024414725052933166 [8, 302, 130, 3870, 15, 76, '1', 10]
Farthest: d = 0.7060225406848217 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [8, 318, 145, 4140, 13.7, 77, '1', 20]
Nearest: d = 0.015022678918603248 [8, 305, 145, 3880, 12.5, 77, '1', 20]
Farthest: d = 0.7283300244834389 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [8, 350, 170, 4165, 11.4, 77, '1', 20]
Nearest: d = 0.04449298966089495 [8, 350, 180, 4380, 12.1, 76, '1', 20]
Farthest: d = 0.7565476068651765 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [8, 400, 190, 4325, 12.2, 77, '1', 20]
Nearest: d = 0.024305086711954246 [8, 400, 180, 4220, 11.1, 77, '1', 20]
Farthest: d = 0.8007194483073985 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [8, 351, 142, 4054, 14.3, 79, '1', 20]
Nearest: d = 0.009722034684781687 [8, 351, 138, 3955, 13.2, 79, '1', 20]
Farthest: d = 0.7651546911076686 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [8, 304, 150, 3433, 12, 70, '1', 20]
Nearest: d = 0.016178269604649638 [8, 318, 150, 3436, 11, 70, '1', 20]
Farthest: d = 0.8012206459647031 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 225, 105, 3439, 15.5, 71, '1', 20]
Nearest: d = 0.01459857567946564 [6, 232, 100, 3288, 15.5, 71, '1', 20]
Farthest: d = 0.6622147624934427 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 250, 100, 3278, 18, 73, '1', 20]
Nearest: d = 0.02080063234883524 [6, 232, 100, 2945, 16, 73, '1', 20]
Farthest: d = 0.6239957745272733 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 400, 230, 4278, 9.5, 73, '1', 20]
Nearest: d = 0.058870897088915235 [8, 440, 215, 4735, 11, 73, '1', 10]
Farthest: d = 0.866181269934664 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 250, 100, 3781, 17, 74, '1', 20]
Nearest: d = 0.0 [6, 250, 100, 3336, 17, 74, '1', 20]
Farthest: d = 0.6047806342111002 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 258, 110, 3632, 18, 74, '1', 20]
Nearest: d = 0.02600388796758966 [6, 250, 100, 3336, 17, 74, '1', 20]
Farthest: d = 0.6126793039786632 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 302, 140, 4141, 14, 74, '1', 20]
Nearest: d = 0.0 [8, 302, 140, 4638, 16, 74, '1', 10]
Farthest: d = 0.728922367779348 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 400, 170, 4668, 11.5, 75, '1', 20]
Nearest: d = 0.07292530913995152 [8, 350, 180, 4380, 12.1, 76, '1', 20]
Farthest: d = 0.7804436557967358 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 318, 150, 4498, 14.5, 75, '1', 20]
Nearest: d = 0.03726779962499649 [8, 318, 150, 3940, 13.2, 76, '1', 10]
Farthest: d = 0.7291244540917516 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [6, 250, 105, 3897, 18.5, 75, '1', 20]
Nearest: d = 0.0 [6, 250, 105, 3459, 16, 75, '1', 20]
Farthest: d = 0.5917233620057454 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 318, 150, 4190, 13, 76, '1', 20]
Nearest: d = 0.0 [8, 318, 150, 3940, 13.2, 76, '1', 10]
Farthest: d = 0.7217671699560936 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [8, 400, 180, 4220, 11.1, 77, '1', 20]
Nearest: d = 0.024305086711954246 [8, 400, 190, 4325, 12.2, 77, '1', 20]
Farthest: d = 0.7903980893344837 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [8, 351, 149, 4335, 14.5, 77, '1', 20]
Nearest: d = 0.03797440243763811 [8, 351, 152, 4215, 12.8, 76, '1', 10]
Farthest: d = 0.7457475939289727 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [6, 163, 133, 3410, 15.8, 78, '2', 20]
Nearest: d = 0.019444069369563374 [6, 163, 125, 3140, 13.6, 78, '2', 20]
Farthest: d = 0.6962395907067777 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 168, 120, 3820, 16.7, 76, '2', 20]
Nearest: d = 0.07574050839158915 [6, 163, 125, 3140, 13.6, 78, '2', 20]
Farthest: d = 0.6761090932153578 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [8, 350, 180, 4380, 12.1, 76, '1', 20]
Nearest: d = 0.04449298966089495 [8, 350, 170, 4165, 11.4, 77, '1', 20]
Farthest: d = 0.7546851970800944 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [8, 351, 138, 3955, 13.2, 79, '1', 20]
Nearest: d = 0.009722034684781687 [8, 351, 142, 4054, 14.3, 79, '1', 20]
Farthest: d = 0.763825611784661 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [8, 350, 155, 4360, 14.9, 79, '1', 20]
Nearest: d = 0.016769713574972693 [8, 360, 150, 3940, 13, 79, '1', 20]
Farthest: d = 0.7721155738341426 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [8, 302, 140, 3449, 10.5, 70, '1', 20]
Nearest: d = 0.024414725052933142 [8, 304, 150, 3433, 12, 70, '1', 20]
Farthest: d = 0.7936412600361323 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 250, 100, 3329, 15.5, 71, '1', 20]
Nearest: d = 0.0 [6, 250, 100, 3282, 15, 71, '1', 20]
Farthest: d = 0.6670279470782668 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 304, 150, 3672, 11.5, 72, '1', 20]
Nearest: d = 0.0 [8, 304, 150, 3892, 12.5, 72, '1', 20]
Farthest: d = 0.7621308368049315 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 231, 110, 3907, 21, 75, '1', 20]
Nearest: d = 0.0 [6, 231, 110, 3039, 15, 75, '1', 20]
Farthest: d = 0.5864351764391414 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 260, 110, 4060, 19, 77, '1', 20]
Nearest: d = 0.03726779962499646 [8, 260, 110, 3365, 15.5, 78, '1', 20]
Farthest: d = 0.6956494384053629 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [6, 163, 125, 3140, 13.6, 78, '2', 20]
Nearest: d = 0.019444069369563374 [6, 163, 133, 3410, 15.8, 78, '2', 20]
Farthest: d = 0.7027256162081348 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [8, 305, 130, 3840, 15.4, 79, '1', 20]
Nearest: d = 0.004233896657200183 [8, 302, 129, 3725, 13.4, 79, '1', 20]
Farthest: d = 0.7404293265834371 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [8, 305, 140, 4215, 13, 76, '1', 20]
Nearest: d = 0.02455108446848552 [8, 302, 130, 3870, 15, 76, '1', 10]
Farthest: d = 0.7119633820331236 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [6, 258, 95, 3193, 17.8, 76, '1', 20]
Nearest: d = 0.02600388796758966 [6, 250, 105, 3353, 14.5, 76, '1', 20]
Farthest: d = 0.5844381274469762 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [8, 305, 145, 3880, 12.5, 77, '1', 20]
Nearest: d = 0.015022678918603248 [8, 318, 145, 4140, 13.7, 77, '1', 20]
Farthest: d = 0.7225508368263007 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [6, 250, 110, 3520, 16.4, 77, '1', 20]
Nearest: d = 0.02509502022267309 [6, 231, 105, 3425, 16.9, 77, '1', 20]
Farthest: d = 0.5962485165814689 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [8, 318, 140, 4080, 13.7, 78, '1', 20]
Nearest: d = 0.0 [8, 318, 140, 3735, 13.2, 78, '1', 20]
Farthest: d = 0.7369223486226214 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [8, 302, 129, 3725, 13.4, 79, '1', 20]
Nearest: d = 0.004233896657200183 [8, 305, 130, 3840, 15.4, 79, '1', 20]
Farthest: d = 0.7389050868019325 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [6, 225, 85, 3465, 16.6, 81, '1', 20]
Nearest: d = 0.02979572112997189 [6, 200, 88, 3060, 17.1, 81, '1', 20]
Farthest: d = 0.6564447394960773 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [6, 231, 165, 3445, 13.4, 78, '1', 20]
Nearest: d = 0.11373622246356639 [6, 258, 120, 3410, 15.1, 78, '1', 20]
Farthest: d = 0.6546154973031912 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [8, 307, 130, 3504, 12, 70, '1', 20]
Nearest: d = 0.024982433546745324 [8, 302, 140, 3449, 10.5, 70, '1', 20]
Farthest: d = 0.7891965188413876 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 318, 150, 3436, 11, 70, '1', 20]
Nearest: d = 0.016178269604649638 [8, 304, 150, 3433, 12, 70, '1', 20]
Farthest: d = 0.8061985979915185 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 199, 97, 2774, 15.5, 70, '1', 20]
Nearest: d = 0.0049964867093490566 [6, 198, 95, 2833, 15.5, 70, '1', 20]
Farthest: d = 0.6766504451643468 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 232, 100, 3288, 15.5, 71, '1', 20]
Nearest: d = 0.0 [6, 232, 100, 2634, 13, 71, '1', 20]
Farthest: d = 0.6618184201770638 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 258, 110, 2962, 13.5, 71, '1', 20]
Nearest: d = 0.02600388796758966 [6, 250, 100, 3329, 15.5, 71, '1', 20]
Farthest: d = 0.6741977426471004 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 250, 88, 3139, 14.5, 71, '1', 20]
Nearest: d = 0.0 [6, 250, 88, 3302, 15.5, 71, '1', 20]
Farthest: d = 0.6625493572583744 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [4, 121, 112, 2933, 14.5, 72, '2', 20]
Nearest: d = 0.037267799624996496 [4, 121, 112, 2868, 15.5, 73, '2', 20]
Farthest: d = 0.746965556117887 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 225, 105, 3121, 16.5, 73, '1', 20]
Nearest: d = 0.01459857567946564 [6, 232, 100, 2945, 16, 73, '1', 20]
Farthest: d = 0.618847991116309 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 232, 100, 2945, 16, 73, '1', 20]
Nearest: d = 0.0 [6, 232, 100, 2789, 15, 73, '1', 20]
Farthest: d = 0.6184238560486724 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 250, 88, 3021, 16.5, 73, '1', 20]
Nearest: d = 0.0291661040543451 [6, 250, 100, 3278, 18, 73, '1', 20]
Farthest: d = 0.6198167856652526 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [6, 232, 100, 2789, 15, 73, '1', 20]
Nearest: d = 0.0 [6, 232, 100, 2945, 16, 73, '1', 20]
Farthest: d = 0.6184238560486724 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [3, 70, 90, 2124, 13.5, 73, '3', 20]
Nearest: d = 0.04096767184654188 [3, 70, 97, 2330, 13.5, 72, '3', 20]
Farthest: d = 0.8474078239552566 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 225, 105, 3613, 16.5, 74, '1', 20]
Nearest: d = 0.01459857567946564 [6, 232, 100, 2901, 16, 74, '1', 20]
Farthest: d = 0.5994678681944346 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 250, 105, 3459, 16, 75, '1', 20]
Nearest: d = 0.0 [6, 250, 105, 3897, 18.5, 75, '1', 20]
Farthest: d = 0.5917233620057454 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [6, 225, 95, 3785, 19, 75, '1', 20]
Nearest: d = 0.0 [6, 225, 95, 3264, 16, 75, '1', 20]
Farthest: d = 0.5821963992385523 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [6, 171, 97, 2984, 14.5, 75, '1', 20]
Nearest: d = 0.048846878787109735 [6, 198, 95, 3102, 16.5, 74, '1', 20]
Farthest: d = 0.5660368364931474 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [6, 250, 78, 3574, 21, 76, '1', 20]
Nearest: d = 0.0358235667099229 [6, 232, 90, 3085, 17.6, 76, '1', 20]
Farthest: d = 0.583393538767211 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [6, 258, 120, 3410, 15.1, 78, '1', 20]
Nearest: d = 0.04522141936018905 [6, 225, 110, 3620, 18.7, 78, '1', 20]
Farthest: d = 0.6227778898083779 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [8, 302, 139, 3205, 11.2, 78, '1', 20]
Nearest: d = 0.0 [8, 302, 139, 3570, 12.8, 78, '1', 20]
Farthest: d = 0.7295866139964297 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [8, 318, 135, 3830, 15.2, 79, '1', 20]
Nearest: d = 0.01932266006300246 [8, 305, 130, 3840, 15.4, 79, '1', 20]
Farthest: d = 0.7474741585049812 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [6, 250, 110, 3645, 16.2, 76, '1', 20]
Nearest: d = 0.012152543355977123 [6, 250, 105, 3353, 14.5, 76, '1', 20]
Farthest: d = 0.581796526948289 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [6, 250, 98, 3525, 19, 77, '1', 20]
Nearest: d = 0.02777655445865305 [6, 231, 105, 3425, 16.9, 77, '1', 20]
Farthest: d = 0.5916035498589948 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [8, 360, 150, 3940, 13, 79, '1', 20]
Nearest: d = 0.016769713574972693 [8, 350, 155, 4360, 14.9, 79, '1', 20]
Farthest: d = 0.7726290504773502 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [6, 225, 110, 3620, 18.7, 78, '1', 20]
Nearest: d = 0.013991366767806589 [6, 231, 105, 3535, 19.2, 78, '1', 20]
Farthest: d = 0.6057759596396619 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [6, 232, 100, 2634, 13, 71, '1', 20]
Nearest: d = 0.0 [6, 232, 100, 3288, 15.5, 71, '1', 20]
Farthest: d = 0.6618184201770638 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 250, 88, 3302, 15.5, 71, '1', 20]
Nearest: d = 0.0 [6, 250, 88, 3139, 14.5, 71, '1', 20]
Farthest: d = 0.6625493572583744 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 250, 100, 3282, 15, 71, '1', 20]
Nearest: d = 0.0 [6, 250, 100, 3329, 15.5, 71, '1', 20]
Farthest: d = 0.6670279470782668 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [3, 70, 97, 2330, 13.5, 72, '3', 20]
Nearest: d = 0.04096767184654188 [3, 70, 90, 2124, 13.5, 73, '3', 20]
Farthest: d = 0.8368274033911334 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 122, 85, 2310, 18.5, 73, '1', 20]
Nearest: d = 0.037346971246536784 [4, 122, 86, 2226, 16.5, 72, '1', 20]
Farthest: d = 0.635896644370334 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 121, 112, 2868, 15.5, 73, '2', 20]
Nearest: d = 0.004861017342390844 [4, 121, 110, 2660, 14, 73, '2', 20]
Farthest: d = 0.7515996184611515 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 232, 100, 2901, 16, 74, '1', 20]
Nearest: d = 0.01459857567946564 [6, 225, 105, 3613, 16.5, 74, '1', 20]
Farthest: d = 0.5990300114510106 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 225, 95, 3264, 16, 75, '1', 20]
Nearest: d = 0.0 [6, 225, 95, 3785, 19, 75, '1', 20]
Farthest: d = 0.5821963992385523 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [6, 232, 90, 3211, 17, 75, '1', 20]
Nearest: d = 0.014598575679465662 [6, 225, 95, 3785, 19, 75, '1', 20]
Farthest: d = 0.5851144591080639 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [4, 120, 88, 3270, 21.9, 76, '2', 20]
Nearest: d = 0.015789565272497873 [4, 107, 86, 2464, 15.5, 76, '2', 30]
Farthest: d = 0.7992118596931701 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 156, 108, 2930, 15.5, 76, '3', 20]
Nearest: d = 0.04729925932557616 [6, 146, 97, 2815, 14.5, 77, '3', 20]
Farthest: d = 0.6944430914873629 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 225, 100, 3630, 17.7, 77, '1', 20]
Nearest: d = 0.013991366767806566 [6, 231, 105, 3425, 16.9, 77, '1', 20]
Farthest: d = 0.5823748625336843 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [6, 225, 90, 3381, 18.7, 80, '1', 20]
Nearest: d = 0.03813558693319238 [6, 232, 90, 3265, 18.2, 79, '1', 20]
Farthest: d = 0.6357708619398343 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [6, 231, 105, 3535, 19.2, 78, '1', 20]
Nearest: d = 0.0 [6, 231, 105, 3380, 15.8, 78, '1', 20]
Farthest: d = 0.6045086534280786 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [8, 305, 145, 3425, 13.2, 78, '1', 20]
Nearest: d = 0.01498946012804714 [8, 302, 139, 3205, 11.2, 78, '1', 20]
Farthest: d = 0.7330467171853137 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [8, 267, 125, 3605, 15, 79, '1', 20]
Nearest: d = 0.041597722349506865 [8, 302, 129, 3725, 13.4, 79, '1', 20]
Farthest: d = 0.7242320619614453 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [8, 318, 140, 3735, 13.2, 78, '1', 20]
Nearest: d = 0.0 [8, 318, 140, 4080, 13.7, 78, '1', 20]
Farthest: d = 0.7369223486226214 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [6, 232, 90, 3210, 17.2, 78, '1', 20]
Nearest: d = 0.025615841620485504 [6, 225, 100, 3430, 17.2, 78, '1', 20]
Farthest: d = 0.5977754026745007 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [6, 200, 85, 2990, 18.2, 79, '1', 20]
Nearest: d = 0.03726779962499651 [6, 200, 85, 2965, 15.8, 78, '1', 20]
Farthest: d = 0.6063433550118542 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [8, 260, 110, 3365, 15.5, 78, '1', 20]
Nearest: d = 0.03726779962499646 [8, 260, 110, 4060, 19, 77, '1', 20]
Farthest: d = 0.7065450579626714 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [4, 140, 90, 2408, 19.5, 72, '1', 20]
Nearest: d = 0.022960493560102536 [4, 122, 86, 2226, 16.5, 72, '1', 20]
Farthest: d = 0.6113276321302319 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 97, 88, 2279, 19, 73, '3', 20]
Nearest: d = 0.01934547947976896 [4, 108, 94, 2379, 16.5, 73, '3', 20]
Farthest: d = 0.7890021389281503 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 114, 91, 2582, 14, 73, '2', 20]
Nearest: d = 0.01864851655821766 [4, 98, 90, 2265, 15.5, 73, '2', 30]
Farthest: d = 0.7757920108365356 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 156, 122, 2807, 13.5, 73, '3', 20]
Nearest: d = 0.11686678309317924 [6, 156, 108, 2930, 15.5, 76, '3', 20]
Farthest: d = 0.6531129307556213 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 198, 95, 3102, 16.5, 74, '1', 20]
Nearest: d = 0.03726779962499649 [6, 198, 95, 2904, 16, 73, '1', 20]
Farthest: d = 0.5877362777226093 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [8, 262, 110, 3221, 13.5, 75, '1', 20]
Nearest: d = 0.06533900190970535 [8, 302, 129, 3169, 12, 75, '1', 10]
Farthest: d = 0.6960896280587536 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [6, 232, 100, 2914, 16, 75, '1', 20]
Nearest: d = 0.014598575679465662 [6, 225, 95, 3785, 19, 75, '1', 20]
Farthest: d = 0.5846094363053393 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [6, 225, 100, 3651, 17.7, 76, '1', 20]
Nearest: d = 0.0 [6, 225, 100, 3233, 15.4, 76, '1', 20]
Farthest: d = 0.5712776289405386 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [4, 130, 102, 3150, 15.7, 76, '2', 20]
Nearest: d = 0.0359358313374816 [4, 120, 88, 3270, 21.9, 76, '2', 20]
Farthest: d = 0.7800148641104179 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [8, 302, 139, 3570, 12.8, 78, '1', 20]
Nearest: d = 0.0 [8, 302, 139, 3205, 11.2, 78, '1', 20]
Farthest: d = 0.7295866139964297 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [6, 200, 85, 2965, 15.8, 78, '1', 20]
Nearest: d = 0.0 [6, 200, 85, 3070, 16.7, 78, '1', 20]
Farthest: d = 0.5877233616378147 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [6, 232, 90, 3265, 18.2, 79, '1', 20]
Nearest: d = 0.03726779962499651 [6, 232, 90, 3210, 17.2, 78, '1', 20]
Farthest: d = 0.6166637273965697 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [6, 200, 88, 3060, 17.1, 81, '1', 20]
Nearest: d = 0.02979572112997189 [6, 225, 85, 3465, 16.6, 81, '1', 20]
Farthest: d = 0.6516466152877423 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [5, 131, 103, 2830, 15.9, 78, '2', 20]
Nearest: d = 0.09478502312642334 [4, 121, 115, 2795, 15.7, 78, '2', 20]
Farthest: d = 0.7674621182063912 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 231, 105, 3425, 16.9, 77, '1', 20]
Nearest: d = 0.013991366767806566 [6, 225, 100, 3630, 17.7, 77, '1', 20]
Farthest: d = 0.5870241721906309 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [6, 200, 95, 3155, 18.2, 78, '1', 20]
Nearest: d = 0.024305086711954246 [6, 200, 85, 2965, 15.8, 78, '1', 20]
Farthest: d = 0.5909650080745777 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [6, 225, 100, 3430, 17.2, 78, '1', 20]
Nearest: d = 0.013991366767806566 [6, 231, 105, 3535, 19.2, 78, '1', 20]
Farthest: d = 0.5999948448482378 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [6, 231, 105, 3380, 15.8, 78, '1', 20]
Nearest: d = 0.0 [6, 231, 105, 3535, 19.2, 78, '1', 20]
Farthest: d = 0.6045086534280786 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [6, 225, 110, 3360, 16.6, 79, '1', 20]
Nearest: d = 0.013991366767806589 [6, 231, 115, 3245, 15.4, 79, '1', 20]
Farthest: d = 0.6249604982624617 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [6, 200, 85, 3070, 16.7, 78, '1', 20]
Nearest: d = 0.0 [6, 200, 85, 2965, 15.8, 78, '1', 20]
Farthest: d = 0.5877233616378147 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [6, 200, 85, 2587, 16, 70, '1', 20]
Nearest: d = 0.012207362526466594 [6, 199, 90, 2648, 15, 70, '1', 20]
Farthest: d = 0.6727557352337509 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 199, 90, 2648, 15, 70, '1', 20]
Nearest: d = 0.012207362526466594 [6, 200, 85, 2587, 16, 70, '1', 20]
Farthest: d = 0.6741095174942047 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [4, 122, 86, 2226, 16.5, 72, '1', 20]
Nearest: d = 0.0 [4, 122, 86, 2395, 16, 72, '1', 20]
Farthest: d = 0.629104078016663 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 120, 87, 2979, 19.5, 72, '2', 20]
Nearest: d = 0.026760557735689482 [4, 121, 76, 2511, 18, 72, '2', 20]
Farthest: d = 0.7719583406117062 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 140, 72, 2401, 19.5, 73, '1', 20]
Nearest: d = 0.03782872244524258 [4, 122, 85, 2310, 18.5, 73, '1', 20]
Farthest: d = 0.6413187481868282 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 155, 107, 2472, 14, 73, '1', 20]
Nearest: d = 0.057617683294089665 [6, 198, 95, 2904, 16, 73, '1', 20]
Farthest: d = 0.6056913842154084 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [6, 231, 110, 3039, 15, 75, '1', 20]
Nearest: d = 0.0 [6, 231, 110, 3907, 21, 75, '1', 20]
Farthest: d = 0.5864351764391414 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [4, 134, 95, 2515, 14.8, 78, '3', 20]
Nearest: d = 0.0 [4, 134, 95, 2560, 14.2, 78, '3', 30]
Farthest: d = 0.8089025814729484 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 121, 110, 2600, 12.8, 77, '2', 20]
Nearest: d = 0.03919914793599205 [4, 121, 115, 2795, 15.7, 78, '2', 20]
Farthest: d = 0.7893993310367377 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [3, 80, 110, 2720, 13.5, 77, '3', 20]
Nearest: d = 0.11143770798809392 [4, 119, 97, 2405, 14.9, 78, '3', 20]
Farthest: d = 0.8567203458051007 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 231, 115, 3245, 15.4, 79, '1', 20]
Nearest: d = 0.013991366767806589 [6, 225, 110, 3360, 16.6, 79, '1', 20]
Farthest: d = 0.6297644479116837 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [4, 121, 115, 2795, 15.7, 78, '2', 20]
Nearest: d = 0.03919914793599205 [4, 121, 110, 2600, 12.8, 77, '2', 20]
Farthest: d = 0.7983350444667524 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 198, 95, 2833, 15.5, 70, '1', 20]
Nearest: d = 0.0049964867093490566 [6, 199, 97, 2774, 15.5, 70, '1', 20]
Farthest: d = 0.6756811698296313 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [4, 140, 72, 2408, 19, 71, '1', 20]
Nearest: d = 0.039881214834300314 [4, 122, 86, 2220, 14, 71, '1', 20]
Farthest: d = 0.6358815080905215 [8, 455, 225, 4951, 11, 73, '1', 10]

Row:  [4, 121, 76, 2511, 18, 72, '2', 20]
Nearest: d = 0.026760557735689482 [4, 120, 87, 2979, 19.5, 72, '2', 20]
Farthest: d = 0.7833746731356817 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 122, 86, 2395, 16, 72, '1', 20]
Nearest: d = 0.0 [4, 122, 86, 2226, 16.5, 72, '1', 20]
Farthest: d = 0.629104078016663 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 108, 94, 2379, 16.5, 73, '3', 20]
Nearest: d = 0.01934547947976896 [4, 97, 88, 2279, 19, 73, '3', 20]
Farthest: d = 0.7763178294053368 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 121, 98, 2945, 14.5, 75, '2', 20]
Nearest: d = 0.0100618281449836 [4, 115, 95, 2694, 15, 75, '2', 20]
Farthest: d = 0.7790847065369153 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 225, 100, 3233, 15.4, 76, '1', 20]
Nearest: d = 0.0 [6, 225, 100, 3651, 17.7, 76, '1', 20]
Farthest: d = 0.5712776289405386 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [6, 250, 105, 3353, 14.5, 76, '1', 20]
Nearest: d = 0.012152543355977123 [6, 250, 110, 3645, 16.2, 76, '1', 20]
Farthest: d = 0.581263214617106 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [6, 146, 97, 2815, 14.5, 77, '3', 20]
Nearest: d = 0.04729925932557616 [6, 156, 108, 2930, 15.5, 76, '3', 20]
Farthest: d = 0.7241176021054015 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 232, 112, 2835, 14.7, 82, '1', 20]
Nearest: d = 0.03760124689854835 [6, 231, 110, 3415, 15.8, 81, '1', 20]
Farthest: d = 0.6943126053129531 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [4, 140, 88, 2890, 17.3, 79, '1', 20]
Nearest: d = 0.013609249041661537 [4, 151, 90, 2670, 16, 79, '1', 30]
Farthest: d = 0.6956144972874069 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 231, 110, 3415, 15.8, 81, '1', 20]
Nearest: d = 0.03760124689854835 [6, 232, 112, 2835, 14.7, 82, '1', 20]
Farthest: d = 0.6695001215552993 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [6, 232, 90, 3085, 17.6, 76, '1', 20]
Nearest: d = 0.025615841620485504 [6, 225, 100, 3651, 17.7, 76, '1', 20]
Farthest: d = 0.5743334660781332 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [4, 122, 86, 2220, 14, 71, '1', 20]
Nearest: d = 0.022960493560102536 [4, 140, 90, 2264, 15.5, 71, '1', 30]
Farthest: d = 0.629104078016663 [8, 455, 225, 4951, 11, 73, '1', 10]

Row:  [4, 97, 54, 2254, 23.5, 72, '2', 20]
Nearest: d = 0.03647593974120214 [4, 96, 69, 2189, 18, 72, '2', 30]
Farthest: d = 0.8230686086648367 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 120, 97, 2506, 14.5, 72, '3', 20]
Nearest: d = 0.009437350870514841 [4, 113, 95, 2278, 15.5, 72, '3', 20]
Farthest: d = 0.7617125895335902 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 198, 95, 2904, 16, 73, '1', 20]
Nearest: d = 0.03726779962499649 [6, 198, 95, 3102, 16.5, 74, '1', 20]
Farthest: d = 0.6074907762775821 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [4, 140, 83, 2639, 17, 75, '1', 20]
Nearest: d = 0.012152543355977123 [4, 140, 78, 2592, 18.5, 75, '1', 20]
Farthest: d = 0.6436944426959805 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 140, 78, 2592, 18.5, 75, '1', 20]
Nearest: d = 0.012152543355977123 [4, 140, 83, 2639, 17, 75, '1', 20]
Farthest: d = 0.6502912337382241 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 115, 95, 2694, 15, 75, '2', 20]
Nearest: d = 0.0100618281449836 [4, 121, 98, 2945, 14.5, 75, '2', 20]
Farthest: d = 0.7854475670393822 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 120, 88, 2957, 17, 75, '2', 20]
Nearest: d = 0.01796791566874081 [4, 115, 95, 2694, 15, 75, '2', 20]
Farthest: d = 0.7895959845999964 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [8, 350, 125, 3900, 17.4, 79, '1', 20]
Nearest: d = 0.031617737514905535 [8, 351, 138, 3955, 13.2, 79, '1', 20]
Farthest: d = 0.7598562354011715 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [4, 156, 105, 2745, 16.7, 78, '1', 20]
Nearest: d = 0.04526687995919188 [4, 140, 88, 2720, 15.4, 78, '1', 30]
Farthest: d = 0.6491072623075114 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 173, 110, 2725, 12.6, 81, '1', 20]
Nearest: d = 0.038397315508303845 [6, 181, 110, 2945, 16.4, 82, '1', 30]
Farthest: d = 0.6572407204277381 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [3, 70, 100, 2420, 12.5, 80, '3', 20]
Nearest: d = 0.10763058498543686 [4, 119, 92, 2434, 15, 80, '3', 40]
Farthest: d = 0.9105656158385874 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 151, 85, 2855, 17.6, 78, '1', 20]
Nearest: d = 0.014654300443274187 [4, 140, 88, 2720, 15.4, 78, '1', 30]
Farthest: d = 0.6753404880597794 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 119, 97, 2405, 14.9, 78, '3', 20]
Nearest: d = 0.0 [4, 119, 97, 2300, 14.7, 78, '3', 30]
Farthest: d = 0.8151290995699383 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [8, 260, 90, 3420, 22.2, 79, '1', 20]
Nearest: d = 0.06125224770725845 [8, 260, 110, 3365, 15.5, 78, '1', 20]
Farthest: d = 0.7187159312266143 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [4, 113, 95, 2372, 15, 70, '3', 20]
Nearest: d = 0.02512610286252951 [4, 97, 88, 2130, 14.5, 70, '3', 30]
Farthest: d = 0.7723516880793351 [8, 455, 225, 4951, 11, 73, '1', 10]

Row:  [4, 107, 90, 2430, 14.5, 70, '2', 20]
Nearest: d = 0.008073714145912039 [4, 110, 87, 2672, 17.5, 70, '2', 30]
Farthest: d = 0.7809500063521505 [8, 455, 225, 4951, 11, 73, '1', 10]

Row:  [4, 113, 95, 2278, 15.5, 72, '3', 20]
Nearest: d = 0.009437350870514841 [4, 120, 97, 2506, 14.5, 72, '3', 20]
Farthest: d = 0.7678428782208988 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 116, 75, 2158, 15.5, 73, '2', 20]
Nearest: d = 0.03726779962499649 [4, 116, 75, 2246, 14, 74, '2', 30]
Farthest: d = 0.7917576738453693 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 121, 110, 2660, 14, 73, '2', 20]
Nearest: d = 0.004861017342390844 [4, 121, 112, 2868, 15.5, 73, '2', 20]
Farthest: d = 0.753389506354909 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 90, 75, 2108, 15.5, 74, '2', 20]
Nearest: d = 0.01089038353121633 [4, 97, 78, 2300, 14.5, 74, '2', 30]
Farthest: d = 0.8130469923878201 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 120, 97, 2489, 15, 74, '3', 20]
Nearest: d = 0.016935586628800747 [4, 108, 93, 2391, 15.5, 74, '3', 30]
Farthest: d = 0.7725753916095401 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 134, 96, 2702, 13.5, 75, '3', 20]
Nearest: d = 0.017503430663105023 [4, 119, 97, 2545, 17, 75, '3', 20]
Farthest: d = 0.7737097066698447 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 119, 97, 2545, 17, 75, '3', 20]
Nearest: d = 0.017503430663105023 [4, 134, 96, 2702, 13.5, 75, '3', 20]
Farthest: d = 0.7811970188749005 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 200, 81, 3012, 17.6, 76, '1', 20]
Nearest: d = 0.04296436144232446 [6, 232, 90, 3085, 17.6, 76, '1', 20]
Farthest: d = 0.5647325666614595 [3, 70, 100, 2420, 12.5, 80, '3', 20]

Row:  [4, 140, 92, 2865, 16.4, 82, '1', 20]
Nearest: d = 0.013609249041661532 [4, 151, 90, 2735, 18, 82, '1', 30]
Farthest: d = 0.7516645306541976 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 146, 120, 2930, 13.8, 81, '3', 20]
Nearest: d = 0.027218498083323054 [6, 168, 116, 2900, 12.6, 81, '3', 30]
Farthest: d = 0.7698627754237922 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 151, 90, 3003, 20.1, 80, '1', 20]
Nearest: d = 0.0 [4, 151, 90, 2678, 16.5, 80, '1', 30]
Farthest: d = 0.705664323713323 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 98, 60, 2164, 22.1, 76, '1', 20]
Nearest: d = 0.024571380008860704 [4, 85, 52, 2035, 22.2, 76, '1', 30]
Farthest: d = 0.7134579963269814 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 151, 88, 2740, 16, 77, '1', 20]
Nearest: d = 0.012941775082101257 [4, 140, 89, 2755, 15.8, 77, '1', 30]
Farthest: d = 0.6560048894745064 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 110, 87, 2672, 17.5, 70, '2', 30]
Nearest: d = 0.008073714145912039 [4, 107, 90, 2430, 14.5, 70, '2', 20]
Farthest: d = 0.7822689914303316 [8, 455, 225, 4951, 11, 73, '1', 10]

Row:  [4, 104, 95, 2375, 17.5, 70, '2', 30]
Nearest: d = 0.012637358051507381 [4, 107, 90, 2430, 14.5, 70, '2', 20]
Farthest: d = 0.7777248591061258 [8, 455, 225, 4951, 11, 73, '1', 10]

Row:  [4, 113, 95, 2228, 14, 71, '3', 30]
Nearest: d = 0.02512610286252951 [4, 97, 88, 2130, 14.5, 71, '3', 30]
Farthest: d = 0.7678428782208988 [8, 455, 225, 4951, 11, 73, '1', 10]

Row:  [4, 97.5, 80, 2126, 17, 72, '1', 30]
Nearest: d = 0.0005777953430232004 [4, 98, 80, 2164, 15, 72, '1', 30]
Farthest: d = 0.6545450536149973 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 140, 75, 2542, 17, 74, '1', 30]
Nearest: d = 0.024090467329014497 [4, 122, 80, 2451, 16.5, 74, '1', 30]
Farthest: d = 0.6447031545493285 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 90, 71, 2223, 16.5, 75, '2', 30]
Nearest: d = 0.002430508671195422 [4, 90, 70, 1937, 14, 75, '2', 30]
Farthest: d = 0.8250628925543794 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 121, 115, 2671, 13.5, 75, '2', 30]
Nearest: d = 0.04131864741032221 [4, 121, 98, 2945, 14.5, 75, '2', 20]
Farthest: d = 0.7636571066631049 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 116, 81, 2220, 16.9, 76, '2', 30]
Nearest: d = 0.015995339525835525 [4, 107, 86, 2464, 15.5, 76, '2', 30]
Farthest: d = 0.8086776917771977 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 140, 92, 2572, 14.9, 76, '1', 30]
Nearest: d = 0.03797440243763811 [4, 140, 89, 2755, 15.8, 77, '1', 30]
Farthest: d = 0.644204599986367 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 181, 110, 2945, 16.4, 82, '1', 30]
Nearest: d = 0.038397315508303845 [6, 173, 110, 2725, 12.6, 81, '1', 20]
Farthest: d = 0.6823628858751943 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [4, 140, 88, 2720, 15.4, 78, '1', 30]
Nearest: d = 0.014654300443274187 [4, 151, 85, 2855, 17.6, 78, '1', 20]
Farthest: d = 0.6784308496267698 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [5, 183, 77, 3530, 20.1, 79, '2', 30]
Nearest: d = 0.08433780083461773 [5, 121, 67, 2950, 19.9, 80, '2', 40]
Farthest: d = 0.7827468086941883 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 168, 116, 2900, 12.6, 81, '3', 30]
Nearest: d = 0.027218498083323054 [6, 146, 120, 2930, 13.8, 81, '3', 20]
Farthest: d = 0.7617320869302384 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 122, 96, 2300, 15.5, 77, '1', 30]
Nearest: d = 0.026872431109753767 [4, 140, 89, 2755, 15.8, 77, '1', 30]
Farthest: d = 0.6651617720097639 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 140, 89, 2755, 15.8, 77, '1', 30]
Nearest: d = 0.012941775082101257 [4, 151, 88, 2740, 16, 77, '1', 20]
Farthest: d = 0.6616814730114188 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 156, 92, 2620, 14.4, 81, '1', 30]
Nearest: d = 0.020284392509767775 [4, 151, 84, 2635, 16.4, 81, '1', 30]
Farthest: d = 0.7210660527809544 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 97, 46, 1835, 20.5, 70, '2', 30]
Nearest: d = 0.050465174917333766 [4, 97, 60, 1834, 19, 71, '2', 30]
Farthest: d = 0.8372138446872649 [8, 455, 225, 4951, 11, 73, '1', 10]

Row:  [4, 121, 113, 2234, 12.5, 70, '2', 30]
Nearest: d = 0.04795744279856569 [4, 104, 95, 2375, 17.5, 70, '2', 30]
Farthest: d = 0.7526372337700745 [8, 350, 105, 3725, 19, 81, '1', 30]

Row:  [4, 91, 70, 1955, 20.5, 71, '1', 30]
Nearest: d = 0.04512257028846389 [4, 97.5, 80, 2126, 17, 72, '1', 30]
Farthest: d = 0.6726172677582815 [8, 455, 225, 4951, 11, 73, '1', 10]

Row:  [4, 96, 69, 2189, 18, 72, '2', 30]
Nearest: d = 0.033527300721729734 [4, 121, 76, 2511, 18, 72, '2', 20]
Farthest: d = 0.8058683189296548 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 97, 46, 1950, 21, 73, '2', 30]
Nearest: d = 0.034296198065227684 [4, 68, 49, 1867, 19.5, 73, '2', 30]
Farthest: d = 0.8372138446872649 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 98, 90, 2265, 15.5, 73, '2', 30]
Nearest: d = 0.01864851655821766 [4, 114, 91, 2582, 14, 73, '2', 20]
Farthest: d = 0.7863561285550624 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 122, 80, 2451, 16.5, 74, '1', 30]
Nearest: d = 0.024090467329014497 [4, 140, 75, 2542, 17, 74, '1', 30]
Farthest: d = 0.6500036693856049 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 79, 67, 1963, 15.5, 74, '2', 30]
Nearest: d = 0.0 [4, 79, 67, 2000, 16, 74, '2', 30]
Farthest: d = 0.8285444707199764 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 97, 78, 2300, 14.5, 74, '2', 30]
Nearest: d = 0.01089038353121633 [4, 90, 75, 2108, 15.5, 74, '2', 20]
Farthest: d = 0.8056199693860412 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 116, 75, 2246, 14, 74, '2', 30]
Nearest: d = 0.02313529946995009 [4, 97, 78, 2300, 14.5, 74, '2', 30]
Farthest: d = 0.797873696969171 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 108, 93, 2391, 15.5, 74, '3', 30]
Nearest: d = 0.016935586628800747 [4, 120, 97, 2489, 15, 74, '3', 20]
Farthest: d = 0.7835465738654179 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 98, 79, 2255, 17.7, 76, '1', 30]
Nearest: d = 0.03851502106063281 [4, 98, 83, 2075, 15.9, 77, '1', 30]
Farthest: d = 0.6885605630638767 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 97, 75, 2265, 18.2, 77, '3', 30]
Nearest: d = 0.01705276040618434 [4, 98, 68, 2045, 18.5, 77, '3', 30]
Farthest: d = 0.8367319386852475 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 156, 92, 2585, 14.5, 82, '1', 30]
Nearest: d = 0.0075507771417884185 [4, 151, 90, 2735, 18, 82, '1', 30]
Farthest: d = 0.7428867322260847 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 140, 88, 2870, 18.1, 80, '1', 30]
Nearest: d = 0.013609249041661537 [4, 151, 90, 3003, 20.1, 80, '1', 20]
Farthest: d = 0.7143307481309346 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 140, 72, 2565, 13.6, 76, '1', 30]
Nearest: d = 0.04001942397531615 [4, 140, 78, 2592, 18.5, 75, '1', 20]
Farthest: d = 0.6699177089582872 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 151, 84, 2635, 16.4, 81, '1', 30]
Nearest: d = 0.018489450976742452 [4, 135, 84, 2490, 15.7, 81, '1', 30]
Farthest: d = 0.7327423920615623 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [8, 350, 105, 3725, 19, 81, '1', 30]
Nearest: d = 0.08898597932178987 [8, 350, 125, 3900, 17.4, 79, '1', 20]
Farthest: d = 0.785857897328735 [3, 70, 97, 2330, 13.5, 72, '3', 20]

Row:  [6, 173, 115, 2700, 12.9, 79, '1', 30]
Nearest: d = 0.0 [6, 173, 115, 2595, 11.3, 79, '1', 30]
Farthest: d = 0.6167156651807375 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [4, 97, 88, 2130, 14.5, 70, '3', 30]
Nearest: d = 0.02512610286252951 [4, 113, 95, 2372, 15, 70, '3', 20]
Farthest: d = 0.7890021389281503 [8, 455, 225, 4951, 11, 73, '1', 10]

Row:  [4, 97, 88, 2130, 14.5, 71, '3', 30]
Nearest: d = 0.02512610286252951 [4, 113, 95, 2228, 14, 71, '3', 30]
Farthest: d = 0.7845890203085637 [8, 455, 225, 4951, 11, 73, '1', 10]

Row:  [4, 97, 60, 1834, 19, 71, '2', 30]
Nearest: d = 0.031990679051671064 [4, 79, 70, 2074, 19.5, 71, '2', 30]
Farthest: d = 0.8158018581797579 [8, 455, 225, 4951, 11, 73, '1', 10]

Row:  [4, 97, 88, 2100, 16.5, 72, '3', 30]
Nearest: d = 0.009722034684781701 [4, 97, 92, 2288, 17, 72, '3', 30]
Farthest: d = 0.7845890203085637 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 101, 83, 2202, 15.3, 76, '2', 30]
Nearest: d = 0.010061828144983609 [4, 107, 86, 2464, 15.5, 76, '2', 30]
Farthest: d = 0.8151453670885571 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 112, 88, 2640, 18.6, 82, '1', 30]
Nearest: d = 0.0 [4, 112, 88, 2605, 19.6, 82, '1', 30]
Farthest: d = 0.7719991911472969 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 151, 90, 2735, 18, 82, '1', 30]
Nearest: d = 0.0 [4, 151, 90, 2950, 17.3, 82, '1', 30]
Farthest: d = 0.7477120093143432 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 151, 90, 2950, 17.3, 82, '1', 30]
Nearest: d = 0.0 [4, 151, 90, 2735, 18, 82, '1', 30]
Farthest: d = 0.7477120093143432 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 140, 86, 2790, 15.6, 82, '1', 30]
Nearest: d = 0.0075507771417884185 [4, 135, 84, 2525, 16, 82, '1', 30]
Farthest: d = 0.7580503930489247 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 119, 97, 2300, 14.7, 78, '3', 30]
Nearest: d = 0.0 [4, 119, 97, 2405, 14.9, 78, '3', 20]
Farthest: d = 0.8151290995699383 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 141, 71, 3190, 24.8, 79, '2', 30]
Nearest: d = 0.038946008693355454 [4, 146, 67, 3250, 21.8, 80, '2', 30]
Farthest: d = 0.8439569538178885 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 135, 84, 2490, 15.7, 81, '1', 30]
Nearest: d = 0.0 [4, 135, 84, 2385, 12.9, 81, '1', 30]
Farthest: d = 0.7417842983128811 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 121, 80, 2670, 15, 79, '1', 30]
Nearest: d = 0.026578585779067267 [4, 98, 80, 1915, 14.4, 79, '1', 40]
Farthest: d = 0.7167100201696578 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 134, 95, 2560, 14.2, 78, '3', 30]
Nearest: d = 0.0 [4, 134, 95, 2515, 14.8, 78, '3', 20]
Farthest: d = 0.8089025814729484 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 156, 105, 2800, 14.4, 80, '1', 30]
Nearest: d = 0.03691264737203309 [4, 151, 90, 3003, 20.1, 80, '1', 20]
Farthest: d = 0.6865422332095473 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 140, 90, 2264, 15.5, 71, '1', 30]
Nearest: d = 0.022960493560102536 [4, 122, 86, 2220, 14, 71, '1', 20]
Farthest: d = 0.6156743758714639 [4, 97, 52, 2130, 24.6, 82, '2', 40]

Row:  [4, 116, 90, 2123, 14, 71, '2', 30]
Nearest: d = 0.038254692232908234 [4, 120, 87, 2979, 19.5, 72, '2', 20]
Farthest: d = 0.77115611430848 [8, 455, 225, 4951, 11, 73, '1', 10]

Row:  [4, 97, 92, 2288, 17, 72, '3', 30]
Nearest: d = 0.009722034684781701 [4, 97, 88, 2100, 16.5, 72, '3', 30]
Farthest: d = 0.7805126319259253 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 98, 80, 2164, 15, 72, '1', 30]
Nearest: d = 0.0005777953430232004 [4, 97.5, 80, 2126, 17, 72, '1', 30]
Farthest: d = 0.6541805249270101 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 90, 75, 2125, 14.5, 74, '1', 30]
Nearest: d = 0.03892458734147804 [4, 122, 80, 2451, 16.5, 74, '1', 30]
Farthest: d = 0.6790032487631263 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 107, 86, 2464, 15.5, 76, '2', 30]
Nearest: d = 0.010061828144983609 [4, 101, 83, 2202, 15.3, 76, '2', 30]
Farthest: d = 0.8086144894649444 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 97, 75, 2155, 16.4, 76, '3', 30]
Nearest: d = 0.018438558676545737 [4, 85, 70, 1990, 17, 76, '3', 30]
Farthest: d = 0.8258721339653115 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 151, 90, 2678, 16.5, 80, '1', 30]
Nearest: d = 0.0 [4, 151, 90, 3003, 20.1, 80, '1', 20]
Farthest: d = 0.705664323713323 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 112, 88, 2605, 19.6, 82, '1', 30]
Nearest: d = 0.0 [4, 112, 88, 2640, 18.6, 82, '1', 30]
Farthest: d = 0.7719991911472969 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 120, 79, 2625, 18.6, 82, '1', 30]
Nearest: d = 0.007382529474406627 [4, 119, 82, 2720, 19.4, 82, '1', 30]
Farthest: d = 0.7770364690147699 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 141, 80, 3230, 20.4, 81, '2', 30]
Nearest: d = 0.04408322391650668 [4, 105, 74, 2190, 14.2, 81, '2', 30]
Farthest: d = 0.867134451122022 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 151, 90, 2670, 16, 79, '1', 30]
Nearest: d = 0.0 [4, 151, 90, 2556, 13.2, 79, '1', 30]
Farthest: d = 0.6867119111191334 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 173, 115, 2595, 11.3, 79, '1', 30]
Nearest: d = 0.0 [6, 173, 115, 2700, 12.9, 79, '1', 30]
Farthest: d = 0.6167156651807375 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [4, 68, 49, 1867, 19.5, 73, '2', 30]
Nearest: d = 0.034296198065227684 [4, 97, 46, 1950, 21, 73, '2', 30]
Farthest: d = 0.8505802534069448 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 98, 83, 2219, 16.5, 74, '2', 30]
Nearest: d = 0.012207362526466595 [4, 97, 78, 2300, 14.5, 74, '2', 30]
Farthest: d = 0.799707808029529 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 97, 75, 2171, 16, 75, '3', 30]
Nearest: d = 0.03726779962499649 [4, 97, 75, 2155, 16.4, 76, '3', 30]
Farthest: d = 0.8165702687966538 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 90, 70, 1937, 14, 75, '2', 30]
Nearest: d = 0.002430508671195422 [4, 90, 71, 2223, 16.5, 75, '2', 30]
Farthest: d = 0.826168357383671 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 85, 52, 2035, 22.2, 76, '1', 30]
Nearest: d = 0.024571380008860704 [4, 98, 60, 2164, 22.1, 76, '1', 20]
Farthest: d = 0.7332234426234876 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 90, 70, 1937, 14.2, 76, '2', 30]
Nearest: d = 0.00844638823704776 [4, 97, 71, 1825, 12.2, 76, '2', 30]
Farthest: d = 0.8353633535892095 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 97, 78, 1940, 14.5, 77, '2', 30]
Nearest: d = 0.0 [4, 97, 78, 2190, 14.1, 77, '2', 30]
Farthest: d = 0.8335807509815106 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 135, 84, 2525, 16, 82, '1', 30]
Nearest: d = 0.0 [4, 135, 84, 2295, 11.6, 82, '1', 30]
Farthest: d = 0.7630127060986454 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 97, 71, 1825, 12.2, 76, '2', 30]
Nearest: d = 0.00844638823704776 [4, 90, 70, 1937, 14.2, 76, '2', 30]
Farthest: d = 0.8302097003165747 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 98, 68, 2135, 16.6, 78, '3', 30]
Nearest: d = 0.01578956527249787 [4, 85, 70, 2070, 18.6, 78, '3', 40]
Farthest: d = 0.8559753560164288 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 134, 90, 2711, 15.5, 80, '3', 30]
Nearest: d = 0.0180025609894924 [4, 119, 92, 2434, 15, 80, '3', 40]
Farthest: d = 0.8438901911650601 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 89, 62, 1845, 15.3, 80, '2', 30]
Nearest: d = 0.03404673817536537 [4, 90, 48, 2335, 23.7, 80, '2', 40]
Farthest: d = 0.8959494108288935 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 98, 65, 2380, 20.7, 81, '1', 30]
Nearest: d = 0.0 [4, 98, 65, 2045, 16.2, 81, '1', 30]
Farthest: d = 0.7857979307221659 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 79, 70, 2074, 19.5, 71, '2', 30]
Nearest: d = 0.01791178335496145 [4, 88, 76, 2065, 14.5, 71, '2', 30]
Farthest: d = 0.8150289875885821 [8, 455, 225, 4951, 11, 73, '1', 10]

Row:  [4, 88, 76, 2065, 14.5, 71, '2', 30]
Nearest: d = 0.01791178335496145 [4, 79, 70, 2074, 19.5, 71, '2', 30]
Farthest: d = 0.8028495821340947 [8, 455, 225, 4951, 11, 73, '1', 10]

Row:  [4, 111, 80, 2155, 14.8, 77, '1', 30]
Nearest: d = 0.016698719516724973 [4, 98, 83, 2075, 15.9, 77, '1', 30]
Farthest: d = 0.6915798953407178 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 97, 67, 1985, 16.4, 77, '3', 30]
Nearest: d = 0.0026912380486373475 [4, 98, 68, 2045, 18.5, 77, '3', 30]
Farthest: d = 0.8453851801465626 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 98, 68, 2155, 16.5, 78, '1', 30]
Nearest: d = 0.0048610173423908505 [4, 98, 66, 1800, 14.4, 78, '1', 40]
Farthest: d = 0.7298587603827552 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 146, 67, 3250, 21.8, 80, '2', 30]
Nearest: d = 0.038946008693355454 [4, 141, 71, 3190, 24.8, 79, '2', 30]
Farthest: d = 0.8613157900623312 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 135, 84, 2385, 12.9, 81, '1', 30]
Nearest: d = 0.0 [4, 135, 84, 2490, 15.7, 81, '1', 30]
Farthest: d = 0.7417842983128811 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 98, 63, 2051, 17, 77, '1', 30]
Nearest: d = 0.03797440243763806 [4, 98, 66, 1800, 14.4, 78, '1', 40]
Farthest: d = 0.721999124482381 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 97, 78, 2190, 14.1, 77, '2', 30]
Nearest: d = 0.0 [4, 97, 78, 1940, 14.5, 77, '2', 30]
Farthest: d = 0.8335807509815106 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 145, 76, 3160, 19.6, 81, '2', 30]
Nearest: d = 0.10313375101075396 [5, 121, 67, 2950, 19.9, 80, '2', 40]
Farthest: d = 0.812118275401509 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 105, 75, 2230, 14.5, 78, '1', 30]
Nearest: d = 0.01883866634046141 [4, 98, 68, 2155, 16.5, 78, '1', 30]
Farthest: d = 0.7165124022174066 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 71, 65, 1773, 19, 71, '3', 30]
Nearest: d = 0.00979047231985135 [4, 72, 69, 1613, 18, 71, '3', 40]
Farthest: d = 0.825648552551034 [8, 455, 225, 4951, 11, 73, '1', 10]

Row:  [4, 79, 67, 1950, 19, 74, '3', 30]
Nearest: d = 0.010444828335514428 [4, 71, 65, 1836, 21, 74, '3', 30]
Farthest: d = 0.8285444707199764 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 76, 52, 1649, 16.5, 74, '3', 30]
Nearest: d = 0.02332233406654296 [4, 83, 61, 2003, 19, 74, '3', 30]
Farthest: d = 0.8478447392675613 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 79, 67, 2000, 16, 74, '2', 30]
Nearest: d = 0.0 [4, 79, 67, 1963, 15.5, 74, '2', 30]
Farthest: d = 0.8285444707199764 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 112, 85, 2575, 16.2, 82, '1', 30]
Nearest: d = 0.007291526013586266 [4, 112, 88, 2640, 18.6, 82, '1', 30]
Farthest: d = 0.775172095471134 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 91, 68, 1970, 17.6, 82, '3', 30]
Nearest: d = 0.0 [4, 91, 68, 2025, 18.2, 82, '3', 40]
Farthest: d = 0.9222497675299961 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 119, 82, 2720, 19.4, 82, '1', 30]
Nearest: d = 0.007382529474406627 [4, 120, 79, 2625, 18.6, 82, '1', 30]
Farthest: d = 0.7743126170261486 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 120, 75, 2542, 17.5, 80, '3', 30]
Nearest: d = 0.013867088232556841 [4, 108, 75, 2265, 15.2, 80, '3', 30]
Farthest: d = 0.8658342173824766 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 98, 68, 2045, 18.5, 77, '3', 30]
Nearest: d = 0.0026912380486373475 [4, 97, 67, 1985, 16.4, 77, '3', 30]
Farthest: d = 0.8437182448982117 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 89, 71, 1990, 14.9, 78, '2', 30]
Nearest: d = 0.03726779962499651 [4, 89, 71, 1925, 14, 79, '2', 30]
Farthest: d = 0.8578295945613464 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 120, 74, 2635, 18.3, 81, '3', 30]
Nearest: d = 0.014078476780187286 [4, 108, 75, 2350, 16.8, 81, '3', 30]
Farthest: d = 0.8835234449348923 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 85, 65, 2020, 19.2, 79, '3', 30]
Nearest: d = 0.0011555906860464039 [4, 86, 65, 1975, 15.2, 79, '3', 30]
Farthest: d = 0.8800815880870168 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 89, 71, 1925, 14, 79, '2', 30]
Nearest: d = 0.0053824760972746855 [4, 91, 69, 2130, 14.7, 79, '2', 40]
Farthest: d = 0.8714830603152279 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 71, 65, 1836, 21, 74, '3', 30]
Nearest: d = 0.010444828335514428 [4, 79, 67, 1950, 19, 74, '3', 30]
Farthest: d = 0.8356806800424934 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 83, 61, 2003, 19, 74, '3', 30]
Nearest: d = 0.015298092814663409 [4, 79, 67, 1950, 19, 74, '3', 30]
Farthest: d = 0.833008701669163 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 85, 70, 1990, 17, 76, '3', 30]
Nearest: d = 0.018438558676545737 [4, 97, 75, 2155, 16.4, 76, '3', 30]
Farthest: d = 0.8382955863885808 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 91, 67, 1965, 15.7, 82, '3', 30]
Nearest: d = 0.0 [4, 91, 67, 1965, 15, 82, '3', 40]
Farthest: d = 0.923258065773254 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 144, 96, 2665, 13.9, 82, '3', 30]
Nearest: d = 0.033871173257601486 [4, 120, 88, 2160, 14.5, 82, '3', 40]
Farthest: d = 0.8691747949774401 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 135, 84, 2295, 11.6, 82, '1', 30]
Nearest: d = 0.0 [4, 135, 84, 2525, 16, 82, '1', 30]
Farthest: d = 0.7630127060986454 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 98, 70, 2120, 15.5, 80, '1', 30]
Nearest: d = 0.03813558693319238 [4, 105, 70, 2200, 13.2, 79, '1', 30]
Farthest: d = 0.7609254955180437 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 108, 75, 2265, 15.2, 80, '3', 30]
Nearest: d = 0.007382529474406627 [4, 107, 72, 2290, 17, 80, '3', 30]
Farthest: d = 0.8721225386315502 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 97, 67, 2065, 17.8, 81, '3', 30]
Nearest: d = 0.007347203986084452 [4, 91, 68, 1985, 16, 81, '3', 30]
Farthest: d = 0.9025940963752401 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 107, 72, 2290, 17, 80, '3', 30]
Nearest: d = 0.007382529474406627 [4, 108, 75, 2265, 15.2, 80, '3', 30]
Farthest: d = 0.8757257674842237 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 108, 75, 2350, 16.8, 81, '3', 30]
Nearest: d = 0.0011555906860464009 [4, 107, 75, 2210, 14.4, 81, '3', 30]
Farthest: d = 0.8886868903364145 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 168, 132, 2910, 11.4, 80, '3', 30]
Nearest: d = 0.053720379690556305 [6, 146, 120, 2930, 13.8, 81, '3', 20]
Farthest: d = 0.7293671763886731 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 78, 52, 1985, 19.4, 78, '3', 30]
Nearest: d = 0.0245713800088607 [4, 91, 60, 1800, 16.4, 78, '3', 40]
Farthest: d = 0.8851487214823426 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 119, 100, 2615, 14.8, 81, '3', 30]
Nearest: d = 0.04203523191963237 [4, 119, 92, 2434, 15, 80, '3', 40]
Farthest: d = 0.8597199660239322 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 91, 53, 1795, 17.5, 75, '3', 30]
Nearest: d = 0.03726779962499649 [4, 91, 53, 1795, 17.4, 76, '3', 30]
Farthest: d = 0.8452335409394766 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 91, 53, 1795, 17.4, 76, '3', 30]
Nearest: d = 0.03726779962499649 [4, 91, 53, 1795, 17.5, 75, '3', 30]
Farthest: d = 0.8542233411156964 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 105, 74, 2190, 14.2, 81, '2', 30]
Nearest: d = 0.03726779962499651 [4, 105, 74, 1980, 15.3, 82, '2', 40]
Farthest: d = 0.8912546259575055 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 85, 70, 1945, 16.8, 77, '3', 30]
Nearest: d = 0.015667242503271648 [4, 97, 67, 1985, 16.4, 77, '3', 30]
Farthest: d = 0.8489964933461916 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 98, 83, 2075, 15.9, 77, '1', 30]
Nearest: d = 0.016698719516724973 [4, 111, 80, 2155, 14.8, 77, '1', 30]
Farthest: d = 0.6966820735146896 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 151, 90, 2556, 13.2, 79, '1', 30]
Nearest: d = 0.0 [4, 151, 90, 2670, 16, 79, '1', 30]
Farthest: d = 0.6867119111191334 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 107, 75, 2210, 14.4, 81, '3', 30]
Nearest: d = 0.0011555906860464009 [4, 108, 75, 2350, 16.8, 81, '3', 30]
Farthest: d = 0.8892089096439666 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 97, 67, 2145, 18, 80, '3', 30]
Nearest: d = 0.006933544116278421 [4, 91, 67, 1850, 13.8, 80, '3', 40]
Farthest: d = 0.8862897021543066 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 112, 88, 2395, 18, 82, '1', 30]
Nearest: d = 0.0 [4, 112, 88, 2640, 18.6, 82, '1', 30]
Farthest: d = 0.7719991911472969 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 108, 70, 2245, 16.9, 82, '3', 30]
Nearest: d = 0.012207362526466595 [4, 107, 75, 2205, 14.5, 82, '3', 40]
Farthest: d = 0.9114370940506009 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 86, 65, 1975, 15.2, 79, '3', 30]
Nearest: d = 0.0011555906860464039 [4, 85, 65, 2020, 19.2, 79, '3', 30]
Farthest: d = 0.8795207493872319 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 91, 68, 1985, 16, 81, '3', 30]
Nearest: d = 0.007347203986084452 [4, 97, 67, 2065, 17.8, 81, '3', 30]
Farthest: d = 0.9047652674946621 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 105, 70, 2200, 13.2, 79, '1', 30]
Nearest: d = 0.0 [4, 105, 70, 2150, 14.9, 79, '1', 30]
Farthest: d = 0.738924811163912 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 97, 78, 2188, 15.8, 80, '2', 30]
Nearest: d = 0.004996486709349054 [4, 98, 76, 2144, 14.7, 80, '2', 40]
Farthest: d = 0.8750372573440702 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 98, 65, 2045, 16.2, 81, '1', 30]
Nearest: d = 0.0 [4, 98, 65, 2380, 20.7, 81, '1', 30]
Farthest: d = 0.7857979307221659 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 105, 70, 2150, 14.9, 79, '1', 30]
Nearest: d = 0.0 [4, 105, 70, 2200, 13.2, 79, '1', 30]
Farthest: d = 0.738924811163912 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 105, 63, 2215, 14.9, 81, '1', 30]
Nearest: d = 0.00943735087051484 [4, 98, 65, 2380, 20.7, 81, '1', 30]
Farthest: d = 0.7840114102909831 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 72, 69, 1613, 18, 71, '3', 40]
Nearest: d = 0.00979047231985135 [4, 71, 65, 1773, 19, 71, '3', 30]
Farthest: d = 0.8204903226806708 [8, 455, 225, 4951, 11, 73, '1', 10]

Row:  [4, 122, 88, 2500, 15.1, 80, '2', 40]
Nearest: d = 0.03775388570894209 [4, 97, 78, 2188, 15.8, 80, '2', 30]
Farthest: d = 0.8519650255411378 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 81, 60, 1760, 16.1, 81, '3', 40]
Nearest: d = 0.0053824760972746915 [4, 79, 58, 1755, 16.9, 81, '3', 40]
Farthest: d = 0.9185166071125622 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 98, 80, 1915, 14.4, 79, '1', 40]
Nearest: d = 0.025615841620485493 [4, 105, 70, 2200, 13.2, 79, '1', 30]
Farthest: d = 0.7313662582032501 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 79, 58, 1825, 18.6, 77, '2', 40]
Nearest: d = 0.04627319201048747 [4, 90, 48, 1985, 21.5, 78, '2', 40]
Farthest: d = 0.8657934728133442 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 105, 74, 1980, 15.3, 82, '2', 40]
Nearest: d = 0.03726779962499651 [4, 105, 74, 2190, 14.2, 81, '2', 30]
Farthest: d = 0.9089990389076864 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 98, 70, 2125, 17.3, 82, '1', 40]
Nearest: d = 0.01883866634046141 [4, 105, 63, 2125, 14.7, 82, '1', 40]
Farthest: d = 0.8000741970845524 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 120, 88, 2160, 14.5, 82, '3', 40]
Nearest: d = 0.033871173257601486 [4, 144, 96, 2665, 13.9, 82, '3', 30]
Farthest: d = 0.8881101264337747 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 107, 75, 2205, 14.5, 82, '3', 40]
Nearest: d = 0.012207362526466595 [4, 108, 70, 2245, 16.9, 82, '3', 30]
Farthest: d = 0.9069933458601869 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 135, 84, 2370, 13, 82, '1', 40]
Nearest: d = 0.0 [4, 135, 84, 2525, 16, 82, '1', 30]
Farthest: d = 0.7630127060986454 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 98, 66, 1800, 14.4, 78, '1', 40]
Nearest: d = 0.0048610173423908505 [4, 98, 68, 2155, 16.5, 78, '1', 30]
Farthest: d = 0.7324119533873884 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 91, 60, 1800, 16.4, 78, '3', 40]
Nearest: d = 0.021059580610700103 [4, 98, 68, 2135, 16.6, 78, '3', 30]
Farthest: d = 0.8687064601477122 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [5, 121, 67, 2950, 19.9, 80, '2', 40]
Nearest: d = 0.08433780083461773 [5, 183, 77, 3530, 20.1, 79, '2', 30]
Farthest: d = 0.8410298935157172 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 119, 92, 2434, 15, 80, '3', 40]
Nearest: d = 0.0180025609894924 [4, 134, 90, 2711, 15.5, 80, '3', 30]
Farthest: d = 0.8497908977793803 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 85, 65, 1975, 19.4, 81, '3', 40]
Nearest: d = 0.008633225871343832 [4, 89, 62, 2050, 17.3, 81, '3', 40]
Farthest: d = 0.9110977758974725 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 91, 68, 2025, 18.2, 82, '3', 40]
Nearest: d = 0.0 [4, 91, 68, 1970, 17.6, 82, '3', 30]
Farthest: d = 0.9222497675299961 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 86, 65, 2019, 16.4, 80, '3', 40]
Nearest: d = 0.0 [4, 86, 65, 2110, 17.9, 80, '3', 50]
Farthest: d = 0.8943968009175609 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 91, 69, 2130, 14.7, 79, '2', 40]
Nearest: d = 0.0053824760972746855 [4, 89, 71, 1925, 14, 79, '2', 30]
Farthest: d = 0.8724652578456608 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 89, 62, 2050, 17.3, 81, '3', 40]
Nearest: d = 0.008633225871343832 [4, 85, 65, 1975, 19.4, 81, '3', 40]
Farthest: d = 0.9120811441046833 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 105, 63, 2125, 14.7, 82, '1', 40]
Nearest: d = 0.01883866634046141 [4, 98, 70, 2125, 17.3, 82, '1', 40]
Farthest: d = 0.8041258209452677 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 91, 67, 1965, 15, 82, '3', 40]
Nearest: d = 0.0 [4, 91, 67, 1965, 15.7, 82, '3', 30]
Farthest: d = 0.923258065773254 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 91, 67, 1995, 16.2, 82, '3', 40]
Nearest: d = 0.0 [4, 91, 67, 1965, 15.7, 82, '3', 30]
Farthest: d = 0.923258065773254 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [6, 262, 85, 3015, 17, 82, '1', 40]
Nearest: d = 0.056718934855945355 [6, 225, 85, 3465, 16.6, 81, '1', 20]
Farthest: d = 0.6908987636719375 [4, 97, 46, 1835, 20.5, 70, '2', 30]

Row:  [4, 89, 60, 1968, 18.8, 80, '3', 40]
Nearest: d = 0.012637358051507376 [4, 86, 65, 2019, 16.4, 80, '3', 40]
Farthest: d = 0.8981094493765988 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 86, 64, 1875, 16.4, 81, '1', 40]
Nearest: d = 0.014078476780187279 [4, 98, 65, 2380, 20.7, 81, '1', 30]
Farthest: d = 0.7943604790640558 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 79, 58, 1755, 16.9, 81, '3', 40]
Nearest: d = 0.0053824760972746915 [4, 81, 60, 1760, 16.1, 81, '3', 40]
Farthest: d = 0.9217365879502619 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 85, 70, 2070, 18.6, 78, '3', 40]
Nearest: d = 0.01578956527249787 [4, 98, 68, 2135, 16.6, 78, '3', 30]
Farthest: d = 0.8611784826895429 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 85, 65, 2110, 19.2, 80, '3', 40]
Nearest: d = 0.0011555906860464039 [4, 86, 65, 2019, 16.4, 80, '3', 40]
Farthest: d = 0.8949483172667874 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 98, 76, 2144, 14.7, 80, '2', 40]
Nearest: d = 0.004996486709349054 [4, 97, 78, 2188, 15.8, 80, '2', 30]
Farthest: d = 0.876488769163873 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 90, 48, 1985, 21.5, 78, '2', 40]
Nearest: d = 0.04627319201048747 [4, 79, 58, 1825, 18.6, 77, '2', 40]
Farthest: d = 0.883101505730696 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 90, 48, 2335, 23.7, 80, '2', 40]
Nearest: d = 0.0 [4, 90, 48, 2085, 21.7, 80, '2', 40]
Farthest: d = 0.9109710584995677 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 97, 52, 2130, 24.6, 82, '2', 40]
Nearest: d = 0.05426447448673316 [4, 105, 74, 1980, 15.3, 82, '2', 40]
Farthest: d = 0.9359223532033172 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 90, 48, 2085, 21.7, 80, '2', 40]
Nearest: d = 0.0 [4, 90, 48, 2335, 23.7, 80, '2', 40]
Farthest: d = 0.9109710584995677 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 91, 67, 1850, 13.8, 80, '3', 40]
Nearest: d = 0.006933544116278421 [4, 97, 67, 2145, 18, 80, '3', 30]
Farthest: d = 0.8895472696289158 [8, 455, 225, 3086, 10, 70, '1', 10]

Row:  [4, 86, 65, 2110, 17.9, 80, '3', 50]
Nearest: d = 0.0 [4, 86, 65, 2019, 16.4, 80, '3', 40]
Farthest: d = 0.8943968009175609 [8, 455, 225, 3086, 10, 70, '1', 10]
```
