# From https://stackoverflow.com/questions/25827160/importing-correctly-with-pytest
import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))

from src.df import Sample
from src.ml import FFT
from src.hpt import RandomSearch, fft

import pytest


def random_search_dataset(file):
    path = os.path.join("data", file)
    df = Sample.read_csv(path)

    rs = RandomSearch(60)
    res = rs.fit( FFT, df, fft )
    for i in res:
        print(i)
    print(len(res))

def test_random_search_auto93():
    random_search_dataset("auto93.csv")
