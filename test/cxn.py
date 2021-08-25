# From https://stackoverflow.com/questions/25827160/importing-correctly-with-pytest
import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))

import pytest
from random import randint
from src.etc.cxn import cxn

def random_cxn():
    a, b = randint(-20, 20), randint(-20, 20)
    return cxn(a, b)

def test_init():
    a, b = randint(-20, 20), randint(-20, 20)
    n1 = cxn(a, b)
    assert n1.r == a
    assert n1.i == b

def test_str():
    a, b = 0, 0
    n1 = cxn(a, b)
    assert str(n1) == "0+0i"

def test_eqT():
    n1 = random_cxn()
    n2 = cxn(n1.r, n1.i)
    assert n1 == n2

def test_eqF():
    n1 = random_cxn()
    n2 = cxn(n1.r+1, n1.i+1)
    assert not(n1 == n2)

def test_eqCT():
    num = randint(-20, 20)
    n1 = cxn(num, 0)
    assert n1 == num

def test_eqCF():
    num = randint(-20, 20)
    n1 = cxn(num, 1)
    assert not(n1 == num)

def test_neqT():
    n1 = random_cxn()
    n2 = cxn(n1.r+1, n1.i+1)
    assert n1 != n2

def test_neqF():
    n1 = random_cxn()
    n2 = cxn(n1.r, n1.i)
    assert not(n1 != n2)

def test_neqCT():
    num = randint(-20, 20)
    n1 = cxn(num, 1)
    assert n1 != num

def test_neqCF():
    num = randint(-20, 20)
    n1 = cxn(num, 0)
    assert not(n1 != num)



def test_add():
    n1 = random_cxn()
    n2 = random_cxn()
    n3 = n1 + n2
    assert n3.r == n1.r + n2.r
    assert n3.i == n1.i + n2.i

def test_sub():
    n1 = random_cxn()
    n2 = random_cxn()
    n3 = n1 - n2
    assert n3.r == n1.r - n2.r
    assert n3.i == n1.i - n2.i

def test_mul():
    n1 = random_cxn()
    n2 = random_cxn()
    n3 = n1 * n2
    assert n3.r == n1.r * n2.r - n1.i * n2.i
    assert n3.i == n1.i * n2.r + n1.r * n2.i
    
def test_div():
    n1 = random_cxn()
    n2 = 0
    while n2 == 0:
        n2 = random_cxn()
    n3 = n1 / n2
    div = n2.r**2 + n2.i**2
    assert n3.r == (n1.r * n2.r + n1.i * n2.i) / (div)
    assert n3.i == (n1.i * n2.r - n1.r * n2.i) / (div)

def test_div0():
    n1 = random_cxn()
    n2 = cxn(0,0)
    try:
        n3 = n1 / n2
        assert False
    except ZeroDivisionError:
        assert True
    except:
        assert False

def test_neg():
    n1 = random_cxn()
    n2 = -n1
    assert n2.r == -n1.r
    assert n2.i == -n1.i

def test_pos():
    n1 = random_cxn()
    n2 = +n1
    assert n2.r == n1.r
    assert n2.i == n1.i
