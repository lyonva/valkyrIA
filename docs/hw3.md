# Homework 3 Report
- CSC 791 Sinless Software Engineering
- By: Leonardo Villalobos Arias

## Description
#### Column
A family of classes "[Column](https://github.com/lyonva/valkyrIA/blob/main/src/df/column.py)" was added. These columns represent, in the context of a table with data, a summary of information of one column. For types of columns were implemented:
- **[Sym](https://github.com/lyonva/valkyrIA/blob/main/src/df/column.py#L60)**: Stores information about symbols (i.e. non-numbers, text) and keeps track of the mode.
- **[Num](https://github.com/lyonva/valkyrIA/blob/main/src/df/column.py#L25)**: Stores information about numerical features (float, int) and keeps track of min, max, mean, and standard deviation.
- **[Some](https://github.com/lyonva/valkyrIA/blob/main/src/df/column.py#L84)**: Stores a sample of 256 numbers, useful for non-parametric tests.
- **[Skip](https://github.com/lyonva/valkyrIA/blob/main/src/df/column.py#L19)**: Does not store any information.

#### Sample
Moreover, a class "[Sample](https://github.com/lyonva/valkyrIA/blob/main/src/df/sample.py)" was implemented. The class stores a series of rows (lists of data). Said rows can be added one by one. The first row added to a sample is assumed as the header, and determines the amount and type of columns the sample will hold. For a description of the supported types of columns, see the [report of homework 2](https://github.com/lyonva/valkyrIA/blob/main/docs/hw2.md). Bulk adding of data is supported using a list of lists (i.e. a matrix). Reading from a csv file is additionally supported. The sample employs the column class to summarize the information of each feature or column of the data matrix. Sample also supports distinction between independent features (stored as x) and target or dependent features (stored as y for numbers, klass for symbols). 

Important methods of the sample class:
- *add*: Adds a new row to the sample, and updates each column
- *read*: From a list of rows, adds each row to the sample
- *read_csv*: Static method that takes a path of a csv file, and returns a Sample with said data.
- *clone*: Clones the structure of the sample. Cloning of underlying data is not currently implemented.
- *sort*: Sorts the sample by its target attributes using the multi-objective indicator by [Zitler and Künzli](https://www.simonkuenzli.ch/docs/ZK04.pdf) as a score function.

Lastly, the sample can be converted into a string to show the structure of its contents. This includes headers, and the first and last 5 rows.
