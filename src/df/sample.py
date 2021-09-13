from src.df import Skip, Num, Sym, Some
import string
from src.io import read_csv
from math import exp
from functools import cmp_to_key
import sys

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
