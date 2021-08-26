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
        pass
    
