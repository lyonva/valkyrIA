# From https://stackoverflow.com/questions/25827160/importing-correctly-with-pytest
import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))

import pytest
from src.df import Sample, Sym, Num, Skip
import pandas as pd

def test_weather():
    file = os.path.join("data", "weather.csv")
    df = Sample.read_csv(file)

    # Assert column types
    real_names = ["outlook", "Temp", "?Humidity", "Windy", "Wins+", "Play-"]
    real_types = [Sym, Num, Skip, Num, Num, Num]
    assert df.names == real_names
    for t, c in zip(real_types, df.cols):
        assert type(c) == t
    assert len(df.x) == 4
    assert len(df.y) == 2
    assert df.klass is None
    
    real_df = pd.read_csv(os.path.join("data", "weather_fix.csv"))
    print(real_df)
    assert len(df.rows) == df.n_rows
    assert df.n_rows == real_df.shape[0]

    # Check columns
    for name, col in zip(df.names, df.cols):
        if type(col) == Num:
            assert real_df[name].max() == pytest.approx(col.hi, 0.00001)
            assert real_df[name].min() == pytest.approx(col.lo, 0.00001)
            assert real_df[name].mean() == pytest.approx(col.mu, 0.00001)
            assert real_df[name].std() == pytest.approx(col.sd, 0.00001)
        if type(col) == Sym:
            assert set(real_df[name].mode()) == set(col.mode)

def test_auto93():
    file = os.path.join("data", "auto93.csv")
    df = Sample.read_csv(file)

    # Assert column types
    real_names = ["Cylinders","Displacement","Horsepower","Weight-","Acceleration+","Model","origin","Mpg+"]
    real_types = [Num,Num,Num,Num,Num,Num,Sym,Num]
    assert df.names == real_names
    for t, c in zip(real_types, df.cols):
        assert type(c) == t
    assert len(df.x) == 5
    assert len(df.y) == 3
    assert df.klass is None
    
    real_df = pd.read_csv(file, na_values = "?").dropna(axis=0)
    print(real_df)
    assert len(df.rows) == df.n_rows
    assert df.n_rows == real_df.shape[0]

    # Check columns
    for name, col in zip(df.names, df.cols):
        if type(col) == Num:
            assert real_df[name].max() == pytest.approx(col.hi, 0.00001)
            assert real_df[name].min() == pytest.approx(col.lo, 0.00001)
            assert real_df[name].mean() == pytest.approx(col.mu, 0.00001)
            assert real_df[name].std() == pytest.approx(col.sd, 0.00001)
        if type(col) == Sym:
            mode = real_df[name].mode()
            mode = [str(m) for m in mode]
            assert set(mode) == set(col.mode)

def test_pom3a():
    file = os.path.join("data", "pom3a.csv")
    df = Sample.read_csv(file)

    # Assert column types
    real_names = ["Culture","Criticality","CriticalityModifier",
            "InitialKnown","InterDependency","Dynamism","Size",
            "Plan","TeamSize","Cost-","Scorei-","Idle-"]
    real_types = [Num] * len(real_names)
    assert df.names == real_names
    for t, c in zip(real_types, df.cols):
        assert type(c) == t
    assert len(df.x) == len(real_names) - 3
    assert len(df.y) == 3
    assert df.klass is None
    
    real_df = pd.read_csv(file, na_values = "?").dropna(axis=0)
    print(real_df)
    assert len(df.rows) == df.n_rows
    assert df.n_rows == real_df.shape[0]

    # Check columns
    for name, col in zip(df.names, df.cols):
        if type(col) == Num:
            assert real_df[name].max() == pytest.approx(col.hi, 0.00001)
            assert real_df[name].min() == pytest.approx(col.lo, 0.00001)
            assert real_df[name].mean() == pytest.approx(col.mu, 0.00001)
            assert real_df[name].std() == pytest.approx(col.sd, 0.00001)
        if type(col) == Sym:
            mode = real_df[name].mode()
            mode = [str(m) for m in mode]
            assert set(mode) == set(col.mode)
    
def test_sort():
    file = os.path.join("data", "auto93.csv")
    df = Sample.read_csv(file)
    df.sort()
    
    # Check first 5 rows
    res = [ [2130, 24.6, 40], [2335, 23.7, 40], [2110, 17.9, 50],
            [1985, 21.5, 40], [2085, 21.7, 40]  ]
    for r1, r2 in zip( df.rows[0:5], res ):
        for i, col in enumerate(df.y):
            assert r1[col.at] == r2[i]
    
    # Check last 6 rows
    res = [ [4354, 9, 10], [4312, 8.5, 10], [4952, 11.5, 10],
            [4955, 11.5, 10], [5140, 12, 10], [4951, 11, 10]  ]
    for r1, r2 in zip( df.rows[::-1][0:6][::-1], res ):
        for i, col in enumerate(df.y):
            assert r1[col.at] == r2[i]
    
    print(df)