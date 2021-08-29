# From https://stackoverflow.com/questions/25827160/importing-correctly-with-pytest
import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))
import pytest

from src.etc import atom
import random
import string

# Test conversion from int to int
# On 1000 random integers
# On the arbitrary range -10**100 and 10**100
def test_int_to_int():
    for i in range(1000):
        num = random.randint(-10**100, 10**100)
        res = atom( num )
        assert num == res

# Test conversion from str to int
# On 1000 random integers
# On the arbitrary range -10**100 and 10**100
def test_str_to_int():
    for i in range(1000):
        num = random.randint(-10**100, 10**100)
        res = atom( str(num) )
        assert num == res

# Test conversion from float to float
# On 1000 random floats
# On the arbitrary range -10**100 and 10**100
def test_float_to_float():
    for i in range(1000):
        num = random.random() * 2*10**100 - 10**100
        res = atom( str(num) )
        assert num == res

# Test conversion from str to float
# On 1000 random floats
# On the arbitrary range -10**100 and 10**100
def test_str_to_float():
    for i in range(1000):
        num = random.random() * 2*10**100 - 10**100
        res = atom( str(num) )
        assert num == res

# Test conversion from bool to bool
def test_bool_to_bool():
    assert atom(True) == True
    assert atom(False) == False

# Test conversion from str to bool
def test_str_to_bool():
    assert atom("TRUE") == True
    assert atom("FALSE") == False


# Test conversion from str to str
# On 1000 random 
# Random text generation from https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
def test_str_to_str():
    for i in range(1000):
        text = ''.join(random.choices(string.ascii_uppercase, k=random.randint(0, 31)))
        assert atom(text) == text

# Test conversion from object to object
# Should return the same thing
def test_obj_to_obj():
    # List
    subjects = [ [],
                [1,2,3],
                type,
                type(type),
                str,
                {},
                {"a":1, "b":2},
                ("tu","ple")
        ]
    
    for subject in subjects:
        assert atom(subject) == subject
    
