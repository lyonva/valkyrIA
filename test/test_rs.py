# From https://stackoverflow.com/questions/25827160/importing-correctly-with-pytest
import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))

from src.df import Sample
from src.ml import FFT
from src.hpt import RandomSearch, fft
import csv

import pytest


def random_search_dataset(df, random_samples):
    rs = RandomSearch(random_samples)
    res = rs.fit( FFT, df, fft )
    return res

def test_random_search_auto93_60():
    path = os.path.join("data", "auto93.csv")
    df = Sample.read_csv(path)
    res = random_search_dataset(df, 60)
    for i in res:
        print(i.best_leaf())
    print(len(res))

def generate_fft_datasets_auto93():
    filename = "auto93"
    path = os.path.join("data", filename + ".csv")
    df = Sample.read_csv(path)

    sizes = [30,60,125,250,500,1000]
    for s in sizes:
        results = random_search_dataset(df, s)
        
        result = []
        # Generate file, starting with headers
        hp_keys = results[0].hps().keys()
        row = [ str(key) for key in hp_keys] + [ y.name for y in df.y ] + ["N+"]
        result.append(row)

        # Now save each row
        for model in results:
            row = []

            # Hyper parameters
            for hp in hp_keys:
                row.append( model.hp(hp) )
            
            # Objectives
            best = model.best_leaf()
            for y in best.sample.sample_goals():
                row.append(y)
            
            row.append( best.sample.n_rows )

            result.append(row)
        
        # Save file
        with open(f"data/rs-{filename}-{s}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(result)


if __name__ == "__main__":
    generate_fft_datasets_auto93()
