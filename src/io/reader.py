from abc import ABC, abstractmethod

# Abstract class reader
# Analyzes input of a particular format
# Returns a matrix with the data within
class Reader(ABC):
    
    @staticmethod
    @abstractmethod
    def read_file(path):
        pass


class CSV(Reader):
    
    @staticmethod
    def read_file(path):
        with open(path, 'r',  encoding='utf-8') as file:
            matrix = []
            row_length = 0
            previous = []
            i = 0
            
            while line := file.readline():
                i += 1
                
                # Remove blanks, remove comments, and split by comma
                row = line.strip().split("#")[0].split(",")
                
                # Strip each element
                row = [ s.strip() for s in row ]
                
                # If we are appending to last row, we recover the last element
                # Otherwise it makes no difference
                previous.extend(row)
                row = previous
                
                # If last element is blank, its a split-row
                if row[-1] == "":
                    # We have to save
                    previous = row[:-1]
                else:
                    # We have a complete row, save
                    
                    # If the length is undefined, its the first row
                    # We use it as our standard length
                    if row_length == 0:
                        row_length = len(row)
                        
                    # However, check size
                    if row_length == len(row):
                        # Only add if the length matches
                        matrix.append(row)
                    else:
                        print("File %s: error on row %d. Bad shape." % (path, i))
                    previous = []
                
            return matrix


if __name__ == "__main__":
    import os
    import random
    import string
    
    
    temp_path = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    tf = open(temp_path, "w")
    
    # Create 5x5 garbage file
    # Random text generation from https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
    tf.write(
        "\n".join([
            ','.join(
                [''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                     for i in range(5)]
                )
            for i in range(6)])
        )
    tf.close()
    try:
        res = CSV.read_file(temp_path)
        print(res)
    finally:
        os.remove(temp_path)
    
