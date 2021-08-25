# CompleX Number class
class cxn:
    
    def __init__(self, r = 0, i = 0):
        self.r = r
        self.i = i
    
    # Operations
    # Returns new coefficients
    def cxn_sum(self, other):
        return self.r + other.r, self.i + other.i
    
    def cxn_sub(self, other):
        return self.r - other.r, self.i - other.i
    
    def cxn_mul(self, other):
        new_r = self.r * other.r - self.i * other.i
        new_i = self.r * other.i + self.i * other.r
        return new_r, new_i
    
    def cxn_div(self, other):
        # TODO Decide if we want a special type of exception
        # For now, use unsafe division
        div = other.r*other.r + other.i*other.i
        new_r = self.r * other.r + self.i * other.i
        new_i = self.i * other.r - self.r * other.i
        return new_r/div, new_i/div
    
    # Unary operations
    def __neg__(self, other):
        return cxn(-self.r, -self.i)
    
    def __pos__(self, other):
        return cxn(self.r, self.i)
    
    # Binary operations
    def __add__(self, other):
        return cxn(self.cxn_sum(other))
    
    def __sub__(self, other):
        return cxn(self.cxn_sub(other))
    
    def __mul__(self, other):
        return cxn(self.cxn_mul(other))
    
    def __truediv__(self, other):
        return cxn(self.cxn_div(other))
    
    # Binary assignments
    def __iadd__(self, other):
        self.r, self.i = self.cxn_sum(other)
    
    def __isub__(self, other):
        self.r, self.i = self.cxn_sub(other)
    
    def __imul__(self, other):
        self.r, self.i = self.cxn_mul(other)
    
    def __itruediv__(self, other):
        self.r, self.i = self.cxn_div(other)
    
    # Comparison
    def __eq__(self, other):
        if type(other) != cxn:
            other = cxn(other, 0) # Enable comparison against int/float
        return self.r == other.r and self.i == other.i
    
    def __ne__(self, other):
        return not(self == other)
    
    # Format
    def __str__(self):
        return str(self.r) + "+" + str(self.i) + "i"
    