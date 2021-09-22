# From https://stackoverflow.com/questions/25827160/importing-correctly-with-pytest
import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))

import pytest
from src.df import Sample, Sym, Num
import time

def random_projection_dataset(file):
    path = os.path.join("data", file)
    df = Sample.read_csv(path)

    start_time = time.time()
    projections = df.divs(settings = {"verbose" : True})
    end_time = time.time()
    duration = end_time - start_time

    # Check minimum size of each group
    for group in projections:
        assert group.n_rows >= (df.n_rows)**(1/2)

    # Check that subgroups are complete
    n = sum([g.n_rows for g in projections])
    assert n == df.n_rows
    
    max_disonance = df.disonance()
    print(f"Dataset: {file}")
    print(f"{len(projections)} groups")
    print("Done in %.6f ms" % (duration*1000))
    # print(f"Initial maximum distance is {max_disonance : .3f}")

    # See distance between groups:
    # for i, g in enumerate(projections):
    #     print(f"Group {i+1} has {len(g)} items and a max distance of {df.disonance(g) : .3f}")
    #     assert df.disonance(g) - 0.05 <= max_disonance
    
    # Sort groups
    df.sort_groups(projections, settings={"verbose" : True})

def test_random_projections_weather():
    random_projection_dataset("weather.csv")

def test_random_projections_auto93():
    random_projection_dataset("auto93.csv")

def test_random_projections_pom3a():
    random_projection_dataset("pom3a.csv")