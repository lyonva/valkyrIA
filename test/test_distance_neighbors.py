# From https://stackoverflow.com/questions/25827160/importing-correctly-with-pytest
import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))

import pytest
from src.df import Sample, Sym, Num
from random import choices

import pandas as pd
import numpy as np

def test_distance_auto93():
    file = os.path.join("data", "auto93.csv")
    df = Sample.read_csv(file)
    real_df = pd.read_csv(file, na_values = "?").dropna(axis=0)

    # Select 6 random rows for 7*7 = 49 checks
    rows = choices( [i for i in range(0, df.n_rows)], k = 7 )

    for i in rows:
        for j in rows:
            # Pick rows i, j
            r1 = df.rows[i]
            r2 = df.rows[j]

            # Check their distance in terms of each column
            d = []
            n = 0
            for col in df.x:
                if type(col) in [Sym, Num]:
                    d1 = col.distance(r1[col.at], r2[col.at])
                    d.append(d1)
                    n += 1
                    if type(col) == Num:
                        norm_col = real_df[col.name]
                        norm_col = ( norm_col - norm_col.min() ) / ( norm_col.max() - norm_col.min() )
                        real = (norm_col.iloc[i] - norm_col.iloc[j])
                        assert pytest.approx(d1, 0.00001) == real
                    else:
                        real = 0 if r1[col.at] == r2[col.at] else 1
                        assert d1 == real
            
            # Now check Euclidean distance
            dist = df.distance( r1, r2 )
            real_dist = np.sqrt(np.sum([ x**2 for x in d ]) / n)
            assert pytest.approx(dist, 0.00001) == real_dist


def test_neighbors_auto93():
    file = os.path.join("data", "auto93.csv")
    df = Sample.read_csv(file)

    for i in range(df.n_rows):
        row = df.rows[i]

        # Neigbors
        neighbors = df.neighbors(row)
        assert len(neighbors) == df.n_rows - 1

        print("Row: ", row)
        print(f"Nearest: d = {neighbors[0][0]}", neighbors[0][1])
        print(f"Farthest: d = {neighbors[-1][0]}", neighbors[-1][1])
        print("")

    