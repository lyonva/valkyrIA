# Homework 2 Report
- CSC 791 Sinless Software Engineering
- By: Leonardo Villalobos Arias

## Description
For the second homework of the class, a reader for CSV files was implemented. The reader follows the file standard defined by [professor Menzies](https://github.com/txt/sin21/blob/main/data/auto93.csv). The reader works as follows:
1. Load the contents of the specified file
2. Convert contents to a matrix structure, rows not compliant with size are removed
3. Convert each column to the type specified in the header:
   1. If name is uppercase, convert to int, float or bool
   2. If name is lowercase, leave as string
   3. if name starts with ?, still include row but ignore conversion
4. Return data as matrix: list of lists in Python

The conversor is on the [src.io](https://github.com/lyonva/valkyrIA/blob/main/src/io) package, on the [reader](https://github.com/lyonva/valkyrIA/blob/main/src/io/reader.py) file.

## Example
```python
from src.io import CSV

data = CSV.read_file("data.csv")
```

## Tests
Tests are available on [test/test_read_csv.py](https://github.com/lyonva/valkyrIA/blob/main/test/test_read_csv.py)

The code was tested on the following 3 datasets on the [data](https://github.com/lyonva/valkyrIA/data) directory: [weather](https://github.com/lyonva/valkyrIA/blob/main/data/weather.csv), [auto93](https://github.com/lyonva/valkyrIA/blob/main/data/auto93.csv), and [pom3a](https://github.com/lyonva/valkyrIA/blob/main/data/pom3a.csv). The test cases verify that the CSV reader loads the file correctly by checking the 1) size of the resulting matrix and 2) the contents of each cell. The reader was compared against the respective dataframe loader in pandas. The tests were templated as follows:

```python
data = CSV.read_file("data.csv")
true_data = pd.read_csv("data.csv")

# Check size
assert len(data) == true_data.shape[0] + 1 # +1 because our reader includes header
    for row in data:
        assert len(row) == true_data.shape[1]

# Check data
    for j in range(true_data.shape[1]):
        assert data[0][j] == header[j]
    for i in range(true_data.shape[0]):
        for j in range(true_data.shape[1]):
            assert data[i+1][j] == true_data[i][j]
```

## Results
The test cases passed, showing that the CSV loader works as intended.
