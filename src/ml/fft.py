from src.etc import argsort, sortarg
from itertools import chain
from math import exp

def bit_strings(level):
    if level <= 1:
        return ["0", "1"]
    next = bit_strings(level - 1)
    return [ x + "0" for x in next ] + [ x + "1" for x in next ]

def dec_2_bin(num):
    s = ""
    while num > 0:
        num, res = num // 2, num % 2
        s = str(res) + s
    return s

# Generates all possible trees in a depth
class FFTForest():
    default_parameters = {
        "max_depth" : 4, # Maximum depth for the trees
            # FFTF will generate 2**max_depth trees
        "score_support" : 2, # Support parameter for scoring function
            # Scoring determines which bin is the best for dividing data
        "min_samples_split" : 10, # Minimum number of samples per split
            # Leaves will be then at least min_samples_split / 2
        "min_bin_exp" : 0.5, # For generating bins, the min amount of samples is n**min_bin_exp
        "d" : 2, # Exponent for distance metrics
        "cohen" : 0.35, # For binning, ignore diferences less than cohen*sd
        "random_proj_exp" : 0.5, # For random project, the min amount of samples is n**random_proj_exp
        "random_proj_depth" : 5, # For random project, the max dendogram level
        "target" : "1", # 1 for optimizing best, 0 for optimizing rest
    }

    # Get value of a particular hyper-parameter
    def hp(self, name):
        if name in self.hyper_parameters.keys(): 
            return self.hyper_parameters[name]
        else:
            return self.default_parameters[name]
    
    # Get all hps
    def hps(self):
        return { name : self.hp(name) for name in self.default_parameters.keys() }
    
    # Overload get to fetch hyper-params
    def __getitem__(self, name):
        return self.hp(name)

    def __init__(self, sample, **hyper_parameters):
        self.sample = sample
        self.hyper_parameters = hyper_parameters
        self.fft = []
        self.fit()

    # Construct an FFT Forest
    # i.e. all possible options
    def fit(self):
        for bits in bit_strings(self["max_depth"]):
            args = self.hps()
            args["structure"] = bits
            self.fft += [FFT(self.sample, **args)]
    
    # Show all FFTrees
    def __str__(self):
        s = ""
        for i, fft in enumerate(self.fft):
            s += f"{i}\n{fft}\n"
        return s
    
    def best_tree(self):
        # The best FFTree is the one with the best leaf
        best = None
        for fft in self.fft:
            if best is None:
                best = fft
            else:
                best_leaf = best.best_leaf()
                next_leaf = fft.best_leaf()
                if best_leaf.zitler(next_leaf) == 1:
                    best = fft
        return fft


        

class FFT():

    default_parameters = {
        "structure" : "1111", # Default tree structure
            # Indicates type of exit node
            # Last node is always opposite of second-to-last
            # So it is omitted
            # i.e. default value is actually 11110
        "max_depth" : 4, # Maximum depth for the tree
            # Stop condition for building is either max_depth or structure
        "score_support" : 2, # Support parameter for scoring function
            # Scoring determines which bin is the best for dividing data
        "min_samples_split" : 10, # Minimum number of samples per split
            # Leaves will be then at least min_samples_split / 2
        "min_bin_exp" : 0.5, # For generating bins, the min amount of samples is n**min_bin_exp
        "d" : 2, # Exponent for distance metrics
        "cohen" : 0.35, # For binning, ignore diferences less than cohen*sd
        "random_proj_exp" : 0.5, # For random project, the min amount of samples is n**random_proj_exp
        "random_proj_depth" : 5, # For random project, the max dendogram level
        "target" : "1", # 1 for optimizing best, 0 for optimizing rest
    }

    # Get value of a particular hyper-parameter
    def hp(self, name):
        if name in self.hyper_parameters.keys(): 
            return self.hyper_parameters[name]
        else:
            return self.default_parameters[name]
    
    # Get all hps
    def hps(self):
        return { name : self.hp(name) for name in self.default_parameters.keys() }
    
    # Overload get to fetch hyper-params
    def __getitem__(self, name):
        return self.hp(name)

    def __init__(self, sample, **hyper_parameters):
        self.sample = sample
        self.hyper_parameters = hyper_parameters
        self.root = None
        self.fit()
    
    # Construct an FFT
    def fit(self):
        structure = self["structure"]
        if type(structure) == int:
            structure = dec_2_bin(self["structure"])
        self.root = self._build_level(0, self.sample, sequence = structure)

    # Builds a level of the FFTree
    # Returns the resulting leaf
    # Recursive: builds the entire tree
    def _build_level(self, level, sample, sequence):
        # First check if this level is the limit
        if level >= self["max_depth"] or sequence == "" or sample.n_rows < self["min_samples_split"]:
            return self._build_leaf(sample)
        
        # Target
        # 0 = focus on the rest
        # 1 = focus on the best
        target = sequence[0]

        # Build one level
        # First get partitions
        partitions = sample.discretize(settings = self.hps())
        bins = list(chain.from_iterable(partitions)) # Flatten the output

        # Now choose the best bin
        bins = self.score_bins(target, bins)
        chosen = bins[0]

        # Partition
        in_bin, out_bin = sample.slice(chosen)

        # Our chosen partition is the leaf of this branch
        # The other is the recursive case, down 1 level
        leaf = self._build_leaf(in_bin)
        down = self._build_level( level + 1, out_bin, sequence[1:] )

        # Lastly, construct the branch and return
        return FFTBranch( sample, target, chosen, leaf, down )


    # Builds and returns a leaf
    def _build_leaf(self, sample):
        return FFTLeaf(sample)
    
    # Score one bin
    # More score = better
    def score_bin(self, rule, bin):
        s = self["score_support"]
        b = bin["best"]/bin["bests"]
        r = bin["rest"]/bin["rests"]
        if rule == "0": # Prioritize rests
            score = 0 if b > r else r**s/(b+r)
        elif rule == "1": # Prioritize bests
            score = 0 if r > b else b**s/(b+r)
        else: # Prioritize novel stuff
            score = 1 / (b+r)
        return score
    
    # Score all bins in a list
    # Sort in descending score
    def score_bins(self, rule, bins):
        scores = [ self.score_bin(rule, bin) for bin in bins ]
        order = argsort( scores, reverse = True )
        return sortarg(bins, order)
    
    def best_leaf(self):
        if type(self.root) == FFTLeaf:
            return self.root
        best = self.root.leaf
        current = self.root.down
        while type(current) == FFTBranch:
            leaf = current.leaf
            if leaf.sample.n_rows > 0 and best.zitler(leaf) == 1:
                best = leaf
            current = current.down
        
        # Check last leaf
        leaf = current
        if leaf.sample.n_rows > 0 and best.zitler(leaf) == 1:
            best = leaf
        
        return best
        


    # Return FFT as a string
    def __str__(self):
        prev = None
        curr = self.root
        s = ""
        
        # Print each level
        while type(curr) is FFTBranch:
            cond = "if  " if (prev is None) else "elif"
            bit = curr.bit
            s += f"{bit} {cond} {str(curr)}" + "\n"
            prev = curr
            curr = curr.down
        
        # Print leave
        last_bit = "0" if prev.bit == "1" else "1"
        s += f"{last_bit} else {str(curr)}\n"

        return s

    
class FFTLeaf():
    def __init__(self, sample):
        self.sample = sample

    def __str__(self):
        return f"{self.sample.sample_goals()} ({self.sample.n_rows})"
    
    def zitler(self, other):
        r1 = self.sample.sample_goals()
        r2 = other.sample.sample_goals()
        goals = self.sample.y
        s1, s2 = 0, 0
        n = len(goals)
        for i, goal in enumerate(goals):
            w = goal.weight() # Ask if min or max column

            # Get normalized values for each row
            x = goal.norm_score(r1[i])
            y = goal.norm_score(r2[i])

            # Scores
            s1 -= exp( w * (x-y)/n )
            s2 -= exp( w * (y-x)/n )
        
        # Now account for n
        x = self.sample.n_rows
        y = other.sample.n_rows
        x = x / max(x, y)
        y = y / max(x, y)
        s1 -= exp( 1 * (x-y)/n )
        s2 -= exp( 1 * (y-x)/n )
        
        # Return in format of python sort
        if s1/n < s2/n:
            return -1
        elif s1/n > s2/n:
            return 1
        else:
            return 0

# Class that represents a branch or decision of an FFTree
# bit is whether the branch is a 0 or 1 decision
# bin is the rule used for partition
# leaf branches are always terminal
# down branches may be another branch or a terminal
class FFTBranch():
    def __init__(self, sample, bit, bin, leaf = None, down = None):
        self.sample = sample
        self.bit = bit
        self.bin = bin
        self.leaf = leaf
        self.down = down
    
    def __str__(self):
        return f"{self.sample.slice_str(self.bin)} then {str(self.leaf)}"