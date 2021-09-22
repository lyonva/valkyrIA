# Class bad
# Based on class o by timm
# https://github.com/txt/sin21/blob/main/docs/hw5.md
class bag:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def __repr__(self):
        return "{"+ ', '.join([f"{k} : {v}" for k, v in self.__dict__.items() if  k[0] != "_"]) + "}"