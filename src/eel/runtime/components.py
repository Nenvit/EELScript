from random import random
class Decimal(int):
    def __new__(cls, val):
        return super().__new__(cls, val, 10) if val else 0
class Random(int):
    def __new__(cls, val):
        return super().__new__(cls, random() * 2 ** (int(val) ** 2)) if val else 0
class Hexadecimal(int):
    def __new__(cls, val):
        return super().__new__(cls, val, 16) if val else 0
class Binary(int):
    def __new__(cls, val):
        return super().__new__(cls, val, 2) if val else 0
class Octal(int):
    def __new__(cls, val):
        return super().__new__(cls, val, 8) if val else 0
class NaN:
    def __init__(self, _):
        self.val = _
    def __repr__(self):
        return self.val
class NaT (NaN):
    pass

#These two are empty on purpose.
class String(bytes):
    def __new__(cls, value):
        return super().__new__(cls, value[1:-1])

#Other Companents are part of other modules, e.g. all thought classes are in thoughts.property

class VFile(list):
    def __init__(self, *args):
        super().__init__(*args)
        self.__pointer = 0
    def read(self):
        if not len(self):
            return
        self.__pointer = self.__pointer + 1
        if self.__pointer > len(self):
            self.point(0) #Automatically reposition, but stop the stream.
            return None
        return self[self.__pointer - 1]
    def write(self, stmnt):
        if self.__pointer == len(self):
            self.append(stmnt)
        else:
            self[self.__pointer] = stmnt
        self.__pointer += 1
    def point(self, idx):
        self.__pointer = idx % len(self)
    def seek(self, idx):
        self.__pointer = idx
    @property
    def pointer(self):
        return self.__pointer
    def __getitem__(self, idx=None):
        self.__pointer = idx if (not idx is None) and (isinstance(idx, int)) else self.__pointer
        return super().__getitem__(self.__pointer)
        
class BIT:
    def __init__(self, value, tkn):
        self.id = value
        self.value = tkn