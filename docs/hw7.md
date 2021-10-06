# Homework 7 Report
- CSC 791 Sinless Software Engineering
- By: Leonardo Villalobos Arias

## Description
The following features were added:
1. ``FFT`` and ``FFTForest`` have configurable hyper-parameters.
2. Implemented a ``RandomSearch`` class that generates and evaluates random hyper parameter models
3. Recorded model performance for ``RandomSearch`` on ``FFT`` using 30, 60, 125, 250, 500, and 1000 random hyper parameters.
4. Generate ``FFT`` models that lern the best hyper parameter rules for ``FFT``.

All the points specified in the homework were implemented.

## Code
The available hyper parameters for ``FFT`` and ``FFTForest`` in their [source file](https://github.com/lyonva/valkyrIA/blob/main/src/ml/fft.py). A configuration of the valid ranges for each hyper-parameter can be found on [this file](https://github.com/lyonva/valkyrIA/blob/main/src/hpt/search_space.py).

The ``RandomSearch`` class is implemented in [this file](https://github.com/lyonva/valkyrIA/blob/main/src/hpt/rs.py). I also implemented [test cases](https://github.com/lyonva/valkyrIA/blob/main/test/test_rs.py) for this and for generating the result datasets on auto93.csv.

Lastly, a [test case](https://github.com/lyonva/valkyrIA/blob/main/test/test_fft_forest_onrs.py) also manages the learning of the best hyper parameter rules using ``FFTForest``.

## Results
The results of the ``FFTForest`` learning the best hyper-parameter rules can be found [here](https://github.com/lyonva/valkyrIA/runs/3817515815?check_suite_focus=true). For each size, the best tree is shown:

```
rs-auto93-30.csv
Done in 384.476900 ms
1 if   D <= 2 then [2217, 16.2, 30, 188] (11)
1 elif 3 <= Score_support <= 4 then [2155.0, 16.4, 30.0, 79.0] (10)
0 else [2234, 16.1, 30, 203] (9)

Dataset: rs-auto93-60.csv
Done in 802.234411 ms
1 if   0.447599229660031 <= Random_proj_exp <= 0.677168912903968 then [2234.0, 16.1, 30.0, 203.0] (34)
1 elif structure == 8 then [2234, 16.1, 30, 203] (5)
1 elif 4 <= Max_depth <= 5 then [2155.0, 16.4, 30.0, 79.0] (12)
0 else [2155, 16.4, 30, 79] (9)

Dataset: rs-auto93-125.csv
Done in 1778.838873 ms
1 if   4 <= Max_depth <= 5 then [2234.0, 16.1, 30.0, 203.0] (60)
1 elif 0.701409131359357 <= Cohen <= 1.09703030279161 then [2234.0, 16.1, 30.0, 191.0] (26)
1 elif 0.699821257294446 <= Min_bin_exp <= 0.858839722961367 then [2195, 16.1, 30, 94] (9)
1 elif Min_samples_split <= 21 then [2234.0, 16.1, 30.0, 203.0] (14)
0 else [2234.0, 16.1, 30.0, 196.5] (16)

Dataset: rs-auto93-250.csv
Done in 3909.083366 ms
1 if   Random_proj_depth <= 3 then [2234.0, 16.1, 30.0, 203.0] (120)
1 elif Score_support <= 2 then [2155, 16.4, 30, 87] (69)
1 elif D <= 2 then [2155, 16.4, 30, 79] (29)
1 elif Min_bin_exp <= 0.620554238489775 then [2172.0, 16.4, 30.0, 106.5] (18)
0 else [2155.0, 16.4, 30.0, 79.0] (14)

Dataset: rs-auto93-500.csv
Done in 7639.793158 ms
1 if   3 <= D <= 4 then [2234.0, 16.1, 30.0, 191.5] (240)
1 elif Max_depth <= 3 then [2234, 16.1, 30, 203] (139)
1 elif 0.503873734714912 <= Random_proj_exp <= 0.692639768954122 then [2234, 16.1, 30, 203] (49)
1 elif 27 <= Min_samples_split <= 44 then [2155, 16.4, 30, 144] (33)
0 else [2155, 16.1, 30, 144] (39)

Dataset: rs-auto93-1000.csv
Done in 16312.348127 ms
1 if   Score_support <= 2 then [2234, 16.1, 30, 203] (517)
1 elif D <= 2 then [2234, 16.1, 30, 167] (239)
1 elif Max_depth <= 3 then [2234, 16.1, 30, 195] (121)
1 elif Random_proj_depth <= 3 then [2234, 16.1, 30, 203] (65)
0 else [2155.0, 16.4, 30.0, 79.0] (58)
```

## Report

### What were the run times of your optimizer as you increased r?
Execution time was kept linear, with some wriggle. In that sense, we can empirically state that Random State is ``O(n)`` in terms of complexity.

### Does Hyperparameter optimization change a learner's behavior?
Definitely. If all of the generated trees (which are 11110), the last leaf usually contains less 'bests' than the other, middle values. Moreover, looking at the ``FFTForest`` results from [hw6](https://github.com/lyonva/valkyrIA/blob/main/docs/hw6.md), we can get FFTrees that are better leaves than using no tuning.

### Does Hyperparameter optimization improve a learner's behavior?
That is more difficult to assert. We would first need a way to compare these two learners. One possibility would be to use Zitler predicates, but so far the predictive capacity of these learners has not been assessed.

### Does the Villalobos hypothesis hold for car design? 
At least in this scenario, the FFT for r = 30 appears to be a little worse than r = 60. However, from r = 60 onwards the leafs appear to "stabilize", getting similar metrics. However, these trees have radically different rules. So perhaps, tuning is effective, but multiple solutions are equally viable.

So for now it appears to hold. I'd like to first revise more my code and these results before asserting this statement.
