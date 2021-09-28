# From https://stackoverflow.com/questions/25827160/importing-correctly-with-pytest
import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))

import pytest
from src.df import Sample
import time
from src.ml import FFT

def fft_dataset(file):
    path = os.path.join("data", file)
    df = Sample.read_csv(path)

    print(f"Dataset: {file}")
    fft = FFT(df)
    print(fft)


def test_fft_weather():
    fft_dataset("weather.csv")

def test_fft_auto93():
    fft_dataset("auto93.csv")

def test_fft_pom3a():
    fft_dataset("pom3a.csv")