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
    
    def clone(self):
        new_sample = Sample()
        new_sample.add(self.names)
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
        return self._divs( self.rows, 1, ceil( self.n_rows**(1/2) ), settings=settings )
    
    def _divs(self, rows, level, min_leaf_size, *, settings = {}):
        if len(rows) < 2*min_leaf_size:
            self._print_leaf(rows, level, settings=settings)
            return [rows]
        self._print_node(rows, level, settings=settings)
        left, right = self.div1(rows, settings = settings)
        left = self._divs(left, level + 1, min_leaf_size, settings=settings)
        right = self._divs(right, level + 1, min_leaf_size, settings=settings)
        left.extend(right)
        return left

    # Show a non-leaf node of the random projection
    def _print_node(self, rows, level, *, settings = {}):
        if settings.get("verbose") == True:
            text = "|.. " * level
            text += f"n={len(rows)} c={self.disonance(rows) : .2f}"
            print(text)
    
    # Show a leaf node of the random projection
    def _print_leaf(self, rows, level, *, settings = {}):
        if settings.get("verbose") == True:
            text = "|.. " * level
            text += f"n={len(rows)} c={self.disonance(rows) : .2f}"
            text += " " * 5
            text += "goals = ["
            if self.klass is not None:
                text += "-" # TODO
            elif len(self.y) > 0:
                data = [ self.sample_median(rows, c) for c in self.y ]
                data = [ f"{d : .1f}" for d in data ]
                text += ",".join(data)
            else:
                text += "-"
            text += "]"
            print(text)
    
    # Get the median of a sub-sample
    # On a particular column
    def sample_median(self, rows, col):
        data = [ r[col.at] for r in rows ]
        return median(data)
    
    # Multi-objective order function for rows
    # Equivalent of askink r1 < r2
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
