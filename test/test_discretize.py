# From https://stackoverflow.com/questions/25827160/importing-correctly-with-pytest
import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))

import pytest
from src.df import Sample, Sym, Num
import time

def discretize_dataset(file):
    path = os.path.join("data", file)
    df = Sample.read_csv(path)

    print(f"Dataset: {file}")
    parts = df.discretize(settings = {"verbose" : True})
    
    for feature in parts:
        for interval in feature:
            in_sample, out_sample = df.slice(interval)
            rule = df.slice_str(interval)

            print("-"*50)
            print(rule)
            print()
            print("In the rule:")
            print(in_sample)
            print()
            print("Outside the rule:")
            print(out_sample)
            print("-"*50)


def test_discretize_weather():
    discretize_dataset("weather.csv")

def test_discretize_auto93():
    discretize_dataset("auto93.csv")

def test_discretize_pom3a():
    discretize_dataset("pom3a.csv")