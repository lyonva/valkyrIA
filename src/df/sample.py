from src.df import Skip, Num, Sym, Some
import string
from src.io import read_csv

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
        for name in names:
            # Generate new column
            new_type = col_type(name)
            if new_type in [SKIP_TYPE]:
                col = Skip(name)
            elif new_type in [NUM_TYPE, GOAL_TYPE]:
                col = Num(name)
            elif new_type in [SYM_TYPE, KLASS_TYPE]:
                col = Sym(name)
            
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
