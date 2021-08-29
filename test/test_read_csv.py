# From https://stackoverflow.com/questions/25827160/importing-correctly-with-pytest
import sys, os
sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/.."))

import pytest
from random import randint
from src.io import CSV
from src.etc import atom

import pandas as pd

def test_read_weather():
    path = os.path.join("data", "weather.csv")
    data = CSV.read_file(path)
    
    # Check size
    assert len(data) == 15
    for row in data:
        assert len(row) == 6
    
    # Check data
    correct = "outlook,Temp,?Humidity,Windy,Wins+,Play-\nsunny,85,85,FALSE,10,20\nsunny,80,90,TRUE,12,40\novercast,83,86,FALSE,40,40\nrainy,70,96,FALSE,40,50\nrainy,68,80,FALSE,50,30\nrainy,65,70,TRUE,4,10\novercast,64,65,TRUE,30,60\nsunny,72,95,FALSE,7,20\nsunny,69,70,FALSE,70,70\nrainy,75,80,FALSE,80,40\nsunny,75,70,TRUE,30,50\novercast,72,90,TRUE,60,50\novercast,81,75,FALSE,30,60\nrainy,71,91,TRUE,50,40"
    correct = correct.split("\n")
    correct = [ c.split(",") for c in correct ]
    for i in range(15):
        for j in range(6):
            if j != 2:
                correct[i][j] = atom(correct[i][j])
            assert data[i][j] == correct[i][j]

def test_read_auto93():
    path = os.path.join("data", "auto93.csv")
    data = CSV.read_file(path)
    
    true_data = pd.read_csv(path, na_values = "?")
    
    # Remove missing values
    true_data = true_data.dropna(axis=0)
    
    header = true_data.columns
    true_data = true_data.to_numpy()
    
    # Check size
    assert len(data) == true_data.shape[0] + 1
    for row in data:
        assert len(row) == true_data.shape[1]
    
    # Check data
    for j in range(true_data.shape[1]):
        assert data[0][j] == header[j]
    for i in range(true_data.shape[0]):
        for j in range(true_data.shape[1]):
            # origin column should be text
            if j != 6:
                assert data[i+1][j] == true_data[i][j]
            else:
                assert data[i+1][j] == "%d" % true_data[i][j]

def test_read_pom3a():
    path = os.path.join("data", "pom3a.csv")
    data = CSV.read_file(path)
    
    true_data = pd.read_csv(path)
    header = true_data.columns
    true_data = true_data.to_numpy()
    
    # Last row of pom3a is missing one value, remove
    true_data = true_data[:-1]
    
    # Check size
    assert len(data) == true_data.shape[0] + 1
    for row in data:
        assert len(row) == true_data.shape[1]
    
    # Check data
    for j in range(true_data.shape[1]):
        assert data[0][j] == header[j]
    for i in range(true_data.shape[0]):
        for j in range(true_data.shape[1]):
            assert data[i+1][j] == true_data[i][j]