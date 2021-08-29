# Convert a particular datum into the correct type
# Assumes input is str or other atomic element
# If it isnt, returns the same element
def atom(e):
    if type(e) not in [bool, int, float, str]:
        return e
    
    e = str(e)
    
    if e.upper() == "TRUE":
        return True
    if e.upper() == "FALSE":
        return False
    
    try:
        return int(e)
    except:
        try:
            return float(e)
        except:
            return e
