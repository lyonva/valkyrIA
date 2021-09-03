from src.etc import atom


def read_csv(path):
    return _parse_csv( _read_file_csv(path), path )

def _read_file_csv(path):
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
    
# Check headers and determine if data is compliant
def _parse_csv(matrix, path = ""):
    n_col = len(matrix[0])
    for j in range(n_col):
        col_name = matrix[0][j]
        
        if "?" in col_name:
            continue
        if col_name[0] == col_name[0].lower():
            continue # Keep as text
        
        # Now convert data to numerical type
        # and check each row
        for i, row in enumerate(matrix[1:]):
            row[j] = atom(row[j])
            if type(row[j]) not in [bool,int,float]:
                # Not of the type we wanted, delete
                matrix.remove(row)
                print("File %s: error on column %s. Incorrect type on row %d." % (path, col_name, i))
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
                [''.join(random.choices(string.ascii_lowercase, k=10))
                     for i in range(5)]
                )
            for i in range(6)])
        )
    tf.close()
    try:
        res = read_csv(temp_path)
        print(res)
    finally:
        os.remove(temp_path)
    
