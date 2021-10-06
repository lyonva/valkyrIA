# From https://stackoverflow.com/questions/25827160/importing-correctly-with-pytest
import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))

import pytest
from src.df import Sample
from src.ml import FFTForest

def fftf_dataset(file, depth):
    path = os.path.join("data", file)
    df = Sample.read_csv(path)

    print(f"Dataset: {file}")
    fftf = FFTForest(df, max_depth = depth)

    # Get the best tree
    print(fftf.best_tree())


def test_fft_forest_rs():
    sizes = [30, 60, 125, 250, 500, 1000]
    for s in sizes:
        fftf_dataset(f"rs-auto93-{s}.csv", 4)