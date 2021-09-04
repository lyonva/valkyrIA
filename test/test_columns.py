# From https://stackoverflow.com/questions/25827160/importing-correctly-with-pytest
import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))

import pytest
from random import randint, random, choices
from src.df import Skip, Num, Sym, Some
from statistics import mean, stdev

# Test skip type column
def test_columns_skip():
    # Generate 100000 random numbers between +-100
    data = [randint(-100,100) for i in range(100000)]

    col = Skip("test")
    for d in data:
        col.add(d)
    
    assert col.n == 0

# Test numerical type column
def test_columns_num():
    # Generate 100000 random numbers between +-100
    data = [randint(-100,100) for i in range(100000)]

    col = Num("test")
    for d in data:
        col.add(d)
    
    assert col.n == 100000
    assert pytest.approx(col.hi, 0.00001) == max(data)
    assert pytest.approx(col.lo, 0.00001) == min(data)
    assert pytest.approx(col.mu, 0.00001) == mean(data)
    assert pytest.approx(col.sd, 0.00001) == stdev(data)

# Test categorical type column
# Use uneven distribution to force mode
def test_columns_sym_unbalanced():
    # Generate 100000 random words
    words = ["Wands", "Cups", "Swords", "Coins"]
    p = [0.25, 0.1, 0.5, 0.15]

    data = choices(words, p, k = 100000)

    col = Sym("test")
    for d in data:
        col.add(d)
    
    assert col.n == 100000
    for w in words:
        assert col.count[w] == data.count(w)
    counts = [data.count(w) for w in words]
    mode = []
    for w, c in zip(words, counts):
        if c == max(counts):
            mode.append(w)
    assert col.mode == mode
    assert col.n_mode == max(counts)

# Test categorical type column
# Use even distribution so mode can be more than one element
def test_columns_sym_balanced():
    # Generate 100000 random words
    words = ["Wands", "Cups", "Swords", "Coins"]
    p = [0.25, 0.25, 0.25, 0.25]

    data = choices(words, p, k = 100000)

    col = Sym("test")
    for d in data:
        col.add(d)
    
    assert col.n == 100000
    for w in words:
        assert col.count[w] == data.count(w)
    counts = [data.count(w) for w in words]
    mode = []
    for w, c in zip(words, counts):
        if c == max(counts):
            mode.append(w)
    assert col.mode == mode
    assert col.n_mode == max(counts)

# Test categorical type column
# Use fixed repetitions so mode is all elements
def test_columns_sym_even():
    # Generate 100000 fixed words
    words = ["Wands", "Cups", "Swords", "Coins"]

    data = words * 25000

    col = Sym("test")
    for d in data:
        col.add(d)
    
    assert col.n == 100000
    for w in words:
        assert col.count[w] == data.count(w)
    mode = words
    assert col.mode == mode
    assert col.n_mode == 25000

# Test sample type column
def test_columns_some():
    # Generate 100000 random numbers between +-100
    data = [randint(-100,100) for i in range(100000)]

    col = Some("test")
    for d in data:
        col.add(d)
    
    assert col.n == 100000
    assert len(col.samples) == col.cap
    for i in col.samples:
        assert i in data