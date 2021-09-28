# From https://stackoverflow.com/questions/25827160/importing-correctly-with-pytest
import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))

import pytest
from src.df import Sample
import time
from src.ml import FFTForest

def fftf_dataset(file, depth):
    path = os.path.join("data", file)
    df = Sample.read_csv(path)

    print(f"Dataset: {file}")
    fft = FFTForest(df, max_depth = depth)
    print(fft)


def test_fft_forest_weather():
    fftf_dataset("weather.csv", 1)

def test_fft_forest_auto93():
    fftf_dataset("auto93.csv", 4)

def test_fft_forest_pom3a():
    fftf_dataset("pom3a.csv", 2)