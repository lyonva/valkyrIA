from src.df import Skip, Num, Sym, Some
from src.etc import argsort, sortarg
import string
from src.io import read_csv
from math import exp, ceil
from statistics import median
from functools import cmp_to_key
import sys
from random import sample

SKIP_TYPE = 0
NUM_TYPE = 1
SYM_TYPE = 2
GOAL_TYPE = 3
KLASS_TYPE = 4

def col_type(name):
    if name[0] == "!":
        return KLASS_TYPE
    elif name[-1] in ["+", "-"]:
        return GOAL_TYPE
    elif name[0] == "?":
        return SKIP_TYPE
    elif name[0] in string.ascii_uppercase:
        return NUM_TYPE
    elif name[0] in string.ascii_lowercase:
        return SYM_TYPE
    else:
        return SKIP_TYPE

class Sample:
    def __init__(self):
        self.cols = []
        self.x = []
        self.y = []
        self.klass = None
        self.names = []
        self.rows = []
        self.keep = True
        self.n_rows = 0
        self.subsample = False
    
    @staticmethod
    def read_csv(path):
        df = Sample()
        df.read( read_csv(path) )
        return df

    def _make_header(self, names):
        self.names = names
        for i, name in enumerate(names):
            # Generate new column
            new_type = col_type(name)
            if new_type in [SKIP_TYPE]:
                col = Skip(i, name)
            elif new_type in [NUM_TYPE, GOAL_TYPE]:
                col = Num(i, name)
            elif new_type in [SYM_TYPE, KLASS_TYPE]:
                col = Sym(i, name)
            
            # Append in cols and in x or y
            self.cols.append(col)
            if new_type in [GOAL_TYPE]:
                self.y.append(col)
            elif new_type in [KLASS_TYPE]:
                self.klass = KLASS_TYPE
            else:
                self.x.append(col)

    def _add_data(self, row):
        if len(row) == len(self.cols):
            if not(self.subsample):
                for item, col in zip(row, self.cols):
                    col.add(item)
            if self.keep:
                self.rows.append(row)
                self.n_rows += 1

    def add(self, row):
        if len(self.names) == 0:
            self._make_header(row)
        else:
            self._add_data(row)
    
    def read(self, matrix):
        for row in matrix:
            self.add(row)
    
    # Creates a Sample with the same row structure
    # Can create subsamples: share clones of columns, but can not update them
    def clone(self, data = None, *, subsample = False):
        new_sample = Sample()
        if subsample:
            # Copy exact column structure
            # Make so clone does not add anything
            new_sample.cols = self.cols
            new_sample.x = self.x
            new_sample.y = self.y
            new_sample.klass = self.klass
            new_sample.names = self.names
            new_sample.keep = self.keep
            new_sample.subsample = True
        else:
            new_sample.add(self.names)
        if data is not None:
            new_sample.read(data)
        return new_sample
    
    def sort(self, asc=True):
        fun = lambda r1, r2: self._zitler(r1, r2)
        self.rows.sort(key = cmp_to_key(fun), reverse = not(asc))
    
    def distance(self, r1, r2, *, settings = {}):
        d = 0
        n = sys.float_info.epsilon
        p = settings["p"] if "p" in settings.keys() else 2
        cols = settings["cols"] if "cols" in settings.keys() else self.x
        for col in cols:
            if type(col) in [Num, Sym]:
                n += 1
                a = r1[col.at]
                b = r2[col.at]
                d += col.distance(a, b)**p
        return (d/n)**(1/p)

    def neighbors(self, r1, *, settings = {}, rows = None):
        a = []
        rows = rows if rows is not None else self.rows
        for r2 in rows:
            if r1 != r2:
                a.append( (self.distance(r1, r2, settings=settings), r2) )
        
        def sort_fun(x, y):
            if x[0] == y[0]: return 0
            elif x[0] < y[0]: return -1
            else: return 1

        a.sort(key = cmp_to_key(sort_fun), reverse = False)
        return a
    
    def shuffle(self, rows = None, samples = None):
        rows = self.rows if rows is None else rows
        samples = self.n_rows if samples is None else samples
        samples = min(len(rows), samples)
        idx = sample( [i for i in range(len(rows))], k = samples )
        return [ rows[i] for i in idx ]
    
    def faraway(self, row, rows = None, *, settings = {}):
        rows = self.rows if rows is None else rows
        samples = settings["samples"] if "samples" in settings else 128
        all = self.neighbors(row, settings=settings, rows = self.shuffle( rows, samples = samples ))
        return all[-1][1]
    
    # Get maximum distance of a sub-group
    def disonance(self, rows = None):
        rows = self.rows if rows is None else rows
        n = len(rows)
        zero = self.shuffle(rows, 1)[0]
        one = self.faraway(zero, rows)
        two = self.faraway(one, rows)
        return self.distance(one, two)

    # Get maximum distance of sub-group
    # Normalized by distance of the all
    def norm_disonance(self, rows):
        return self.disonance(rows) / self.disonance(self.rows)

    def div1(self, rows = None, cols = None, *, settings = {}):
        rows = self.rows if rows is None else rows
        cols = self.x if cols is None else cols

        # Select random row, then the farthest away, and so on
        zero = self.shuffle(rows, samples = 1)[0]
        A = self.faraway(zero, rows, settings=settings)
        B = self.faraway(A, rows, settings=settings)
        c = self.distance(A, B, settings = settings) # Distance between A and B

        projection = []
        for C in rows:
            a = self.distance(C, B, settings=settings) # D between B and C
            b = self.distance(A, C, settings=settings) # D between A and C
            
            # Calculate this C's projection
            # This is the "shadow" of C
            # In the line that crosses A and B
            # Assume A, B, and C form a triangle
            # Calculate the angle of A as:
            # cos(A) = (b^2 + c^2 - a^2) / (2bc)
            # Then we find the shadow point D: C's projection in the A-B line
            # We find the distance x between A and D as:
            # x = cos(a) * b
            # To simplify: x = (b^2 + c^2 - a^2) / (2c)
            proj = (b**2 + c**2 - a**2) / (2*c)
            projection.append(proj)
        order = argsort(projection)
        sorted = sortarg(rows, order)
        mid = len(sorted) // 2
        return sorted[:mid], sorted[mid:]
    
    def divs(self, *, settings = {}):
        random_proj_exp = 0.5 if "random_proj_exp" not in settings.keys() else settings["random_proj_exp"]
        min_leaf_size = int(self.n_rows**(random_proj_exp))
        return self._divs( self.rows, 1, min_leaf_size, settings=settings )
    
    def _divs(self, rows, level, min_leaf_size, *, settings = {}):
        random_proj_depth = 5 if "random_proj_depth" not in settings.keys() else settings["random_proj_depth"]
        if len(rows) < 2*min_leaf_size or level > random_proj_depth:
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
    
    # Get the medians of all the goals
    def sample_goals(self, rows = None):
        if rows is None:
            rows = self.rows
        if len(self.y) == 0:
            return []
        if len(rows) == 0:
            return []
        return [ self.sample_median(c, rows) for c in self.y ]

    # Get the median of a particular column
    def sample_median(self, col, rows = None):
        if rows is None:
            rows = self.rows
        data = [ r[col.at] for r in rows ]
        return median(data)
    
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
    
    def _print_ordered_groups(self, groups, *, settings = {}):
        if (settings.get("verbose") == True) and (len(groups) > 1):
            names = [ y.name for y in self.y ]
            space = [len(n) + 5 for n in names]
            s = ""

            # Header
            for n, sp in zip(names, space):
                s += f"{n : <{sp}}"
            s += "\n"

            # Each group
            # Assume its sorted
            for i, g in enumerate(groups):
                median = g.sample_goals()
                for m, sp in zip(median, space):
                    s += f"{m : <{sp}.1f}"
                if i == 0:
                    s += " <== best"
                if i == len(groups) - 1:
                    s += " <== worst"
                s += "\n"
            
            print(s)

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
            for res in good.discretize(bad, settings = settings):
                range += [res]
            if len(range) > 0:
                feature_ranges += [range]
        
        self._show_discretized_ranges(feature_ranges, best, worst, settings = settings)

        return feature_ranges

        
    def _show_discretized_ranges(self, feature_ranges, best, worst, *, settings = {}):
        if (settings.get("verbose") == True):
            for range in feature_ranges:
                for r in range:
                    print(r)
                print("")

            # Show some values from best and worst
            print("Best")
            print(best)
            print()
            print("Worst")
            print(worst)
    
    # Determine if a row is in or out a slice
    # row is the row
    # bin is a bag with range info
    def match(self, row, bin):
        lo = bin["lo"]
        hi = bin["hi"]
        v = row[ bin["at"] ]
        if bin["first"]:
            return v <= hi
        elif bin["last"]:
            return lo <= v
        else:
            return lo <= v <= hi
    
    # Cut the sample in half
    # According to a range (bin)
    def slice(self, bin):
        # Sort whether each row is in or out the bin
        in_bin = []
        out_bin = []
        for row in self.rows:
            verdict = self.match(row, bin)
            to_app = in_bin if verdict else out_bin
            to_app += [row]
        
        # Make sub-clones
        in_sample = self.clone(in_bin)
        out_sample = self.clone(out_bin)

        return in_sample, out_sample
    
    # Return slicing rule as str notation
    # For debugging
    def slice_str(self, bin):
        lo = bin["lo"]
        hi = bin["hi"]
        name = bin["name"]
        if lo == hi:
            return f"{name} == {lo}"
        elif bin["first"]:
            return f"{name} <= {hi}"
        elif bin["laste"]:
            return f"{lo} <= {name}"
        else:
            return f"{bin.lo} <= {bin.name} <= {bin.hi}"

    # Multi-objective order function for rows
    # Equivalent of asking r1 < r2
    def _zitler(self, r1, r2):
        goals = self.y
        s1, s2 = 0, 0
        n = len(goals)
        for goal in goals:
            w = goal.weight() # Ask if min or max column

            # Get normalized values for each row
            x = goal.norm_score(r1[goal.at])
            y = goal.norm_score(r2[goal.at])

            # Scores
            s1 -= exp( w * (x-y)/n )
            s2 -= exp( w * (y-x)/n )
        
        # Return in format of python sort
        if s1/n < s2/n:
            return -1
        elif s1/n > s2/n:
            return 1
        else:
            return 0

    # Convert to string
    # Show header, first 5 and last 5 rows
    def __str__(self):
        space = [len(n) + 5 for n in self.names]
        s = ""

        # Header
        for n, sp in zip(self.names, space):
            s += f"{n : <{sp}}"
        s += "\n"

        # First 5
        rows = self.rows[0:5]
        for row in rows:
            for r, sp in zip(row, space):
                s += f"{r : <{sp}}"
            s += "\n"
        
        # Padding
        s+= "\n"

        # Last 5
        rows = self.rows[::-1][0:5][::-1]
        for row in rows:
            for r, sp in zip(row, space):
                s += f"{r : <{sp}}"
            s += "\n"

        return s
