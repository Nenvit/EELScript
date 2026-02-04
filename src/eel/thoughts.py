import math, random
from . import interval

STABLE = 'stable'
CHOATIC = 'choatic'
OSCILLATING = 'oscilating'
WANDER = 'wander'
EXTINCT = 'extinct'


def strGrid(grid): #Turns a grid into a str with a length of the thought
    return ''.join([str(cell) for row in grid for cell in row])

def AutoThought(size = 0, value = 0, iter = 0, id=''):
    if size < 5:
        return MicroThought(size=size, value=value, iter=iter, id=id)
    elif size < 16:
        return Thought(size=size, value=value, iter=iter, id=id)
    else:
        return DeepThought(size=size, value=value, iter=iter, id=id)

class Thought():
    cache = {}
    ids = []
    _minimal_grid_size = 5
    _standard_grid_size = 5
    _max_grid_size = 15
    def __init__(self, size = 5, value = 0, iter = 0, id = ''):
        self.id = id
        self._grid_size = max(self._minimal_grid_size, min(size, self._max_grid_size))
        self._state = "extinct"
        self._grid = [] #Gets set by value
        self.value = value
        self._certainty = 0
        self._iter = iter
        self._cache = {
            '__init__': {
                'value': self.value,
                'size': self.size
                }
        }
    def __len__(self):
        return self._grid_size ** 2

    @property
    def size(self):
        return self._grid_size
    
    @property
    def iter(self):
        return self._iter

    def __and__(self, otherThought):
        return type(self)(self.size if len(self) > len(otherThought) else otherThought.size, self.__value & otherThought.value, (self._iter | otherThought._iter) + 1)
        
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, id=''):
        if not id:
            nid = hex(random.randint(0, 2 ** 16))[2:]
            while nid in self.__class__.ids:
                nid = hex(random.randint(0, 2 ** 16))[2:]
            self.__class__.ids.append(nid)
            self.__id = nid
        else:
            self.__id = id
            if not id in self.__class__.ids:
                self.__class__.ids.append(id)

    def __or__(self, otherThought): #Not Matric multiplication. Will be used to challenge thoughts against other thoughts.
        return type(self)(self.size if len(self) > len(otherThought) else otherThought.size, self.__value | otherThought.value,
                                        self._iter | otherThought._iter)

    def __xor__(self, otherThought): #to be implemented
        return type(self)(self.size if len(self) > len(otherThought) else otherThought.size,
                    self.__value ^ otherThought.value,
                    (self._iter | otherThought._iter) + 1)

    def __truediv__(self, otherThought): #To be implemented
        thought = type(self)(self.size if len(self) > len(otherThought) else otherThought.size)
        self_res = self.think()
        other_res = otherThought.think()
        if self_res.value < other_res.value:
            thought.value = other_res.value #The other thought was more certain.
        elif self_res.value > other_res.value:
            thought.value = self_res.value
        else:
            thought.value = self_res.value ^ other_res.value #No need to check if both are 0 at this point, the ^ will take care of that for me.
        thought._iter = (other_res._iter & self._iter) + 1
        return thought

    def __floordiv__(self, otherThought):
        self.contemplate()
        otherThought.contemplate()
        return type(self)(self.size if len(self) > len(otherThought) else otherThought.size, 
                            (self.value if self.value > otherThought.value else otherThought.value)
                            if self.value != otherThought.value else self.value ^ otherThought.value)
        
    
    def __eq__(self, otherThought):
        if not isinstance(otherThought, Thought):
            if isinstance(otherThought, int):
                return True if self.value == int else False
            else:
                return False
        return True if self.think().value == otherThought.think().value else False
    
    def __lt__(self, otherThought):
        return True if self.value < otherThought.value else False
    
    def __le__(self, otherThought):
        return True if self.think().value <= otherThought.think().value else False
    def __gt__(self, otherThought):
        return True if self.value > otherThought.value else False
    def __ge__(self, otherThought):
        return True if self.think().value >= otherThought.think().value else False

    def invert(self):
        self.value = int(''.join(['1' if cell == '0' else '0' for cell in self.bin]), 2)
        self._iter += 1
        return self

    def __add__(self, otherThought):
        if isinstance(otherThought, int):
            return type(self)(min(self.size + 1, self._max_grid_size), self.value + otherThought, self._iter + 1)
        return type(self)(min(self._max_grid_size, math.ceil((self.size + otherThought.size) / 2)), self.value + otherThought.value, (self._iter | otherThought._iter) + 1)

    def __radd__(self, otherThought):
        if isinstance(otherThought, int):
            return otherThought + self.value

    def __iadd__(self, otherThought):
        if isinstance(otherThought, int):
            self.value += otherThought
            self.size = min(self._max_grid_size, self.size + 1)
            self.iter += 1
        elif isinstance(otherThought, Thought):
            self.value += otherThought.value
            self.size = min(self._max_grid_size, math.ceil((self.size + otherThought.size) / 2))
            self.iter |= otherThought.iter + 1
        else:
            raise TypeError('Invalid Thought/Value Type entered.')

    def __mult__(self, otherThought):
        tmp = self.iter & (self.iter ^ otherThought)
        self.iter = tmp
        otherThought.iter = tmp

    def __sub__(self, otherThought):
        if isinstance(otherThought, int):
            return type(self)(self.size, abs(self.value - otherThought) % (2 ** (otherThought ** 2)), self.iter + 1)
        dif = max(self.size - otherThought.size -1, self._minimal_grid_size)
        return type(self)(dif, abs(self.value - otherThought.value) % (2 ** (dif ** 2)), (self._iter | otherThought._iter) + 1)

    def __rsub__(self, otherThought):
        if isinstance(otherThought, int):
            return otherThought - self.value

    def __isub__(self, otherThought):
        if isinstance(otherThought, int):
            self.value = abs(self.value - otherThought)
            self.size = max(self.size - 1, self._minimal_grid_size)
            self.iter += 1
        elif isinstance(otherThought, Thought):
            self.value = abs(self.value - otherThought.value)
            self.size = max(self.size - otherThought.size - 1, self._minimal_grid_size)
            self.iter |= otherThought.iter + 1
        else:
            raise TypeError('Invalid Thought/Value Type entered.')

    def __pos__(self):
        return self.value

    def __neg__(self):
        thought = self.think()
        thought.value = int(''.join(['1' if cell == '0' else '0' for cell in thought.bin]), 2)
        thought.value = self._iter + 1
        return thought
    
    def stress(self, val = 1):
        self._iter += val if isinstance(val, int) else val._iter
        return self

    def __invert__(self):
        return type(self)(self.size, int(''.join(['1' if cell == '0' else '0' for cell in self.bin]), 2), self._iter + 1)
        

    @property
    def bin(self): #returns bin string of self's value
        basestr = '0' * len(self)
        binval = bin(self.value)[2:]
        return basestr[:-len(binval)] + binval

    def __mod__(self, otherThought):
        return type(self)(self.size if self.size > otherThought.size else otherThought.size,
                            self.think().value & otherThought.think().value, (self._iter | otherThought._iter) + 1)

    @property
    def value(self):
        return self.__value

    @property
    def bytes(self):
        length = (self.size * self.size + 7) // 8
        return self.value.to_bytes(length, "big")

    @value.setter
    def value(self, value):
        self.__value = abs(value % (2 ** (self.size ** 2))) #Go ahead and cap it.
        self._grid = [[int(bit) for bit in self.bin[i : i + self.size]] for i in range(0, len(self), self.size)]
        pass

    @property
    def grid(self):
        return self._grid

    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, val):
        self._state = val if val in ['stable', 'choatic', 'wander', 'oscillating'] else 'extinct'
    
    @property
    def certainty(self):
        return 20 - self._certainty

    @certainty.setter
    def certainty(self, val):
        self._certainty = abs(math.floor(val)) % 20
    
    @property
    def parent(self):
        return self._cache['__init__']['value']

    def log(self):
        print(self._value)
    
    def think(self):
        thought = type(self)(size=self.size,
                            value=int(strGrid([[self.process(i, j) for i, _ in enumerate(self._grid[j])] for j, _ in enumerate(self._grid)]), 2),
                            iter=self._iter) #Init and return new thought.
        thought._iter += 1
        return thought
    
    def process(self, i, j):
        return self.apply_rules(( self._grid[i - 1][(j - 1)]
                                +self._grid[i - 1][j]
                                +self._grid[i - 1][(j + 1) % self.size]
                                +self._grid[i][j - 1]
                                +self._grid[i][(j + 1) % self.size] 
                                +self._grid[(i + 1) % self.size][j - 1]
                                +self._grid[(i + 1) % self.size][j]
                                +self._grid[(i + 1) % self.size][(j + 1) % self.size] ), self._grid[j][i])
    
    def apply_rules(self, neighbors, _self):
        if neighbors < 2 or neighbors > 3:
            return 0
        elif neighbors == 3:
            return 1
        else:
            return _self

    def adapt(self, num=1):
        for i in range(num):
            self._iter +=1
            tmp = [[self.process(i, j) for i, _ in enumerate(self._grid[j])] for j, _ in enumerate(self._grid)]
            if sum([sum(row) for row in self._grid]) == 0:
                self._state = EXTINCT
                self._certainty = 20
            elif self._iter < 5:
                self._state = STABLE
                self._certainty = self._iter
            elif self._iter < 10:
                self._state = OSCILLATING
                self._certainty = self._iter
            elif self._iter < 20:
                self._state = WANDER
                self._certainty = self._iter
            else:
                self._state = CHOATIC
                self._certainty = 20
            self.value = int(strGrid(tmp), 2)
        return self

    def __str__(self): #Useful for JSON
        return '{' +f'"Size": {self.size}, "Length":{len(self)}, "Binary": "{self.bin}", "Value": {self.value}, "Grid": {self.grid}, "Id": "{self.id}"' + "}"

    def __repr__(self):
        return f"'{self.size}-0x{self.value:02X}'"

    def contemplate(self):
        key = tuple(tuple(row) for row in self._grid)
        
        if key in Thought.cache:
            self.value = int(strGrid(Thought.cache[key][-1]), 2)
            return self

        iterations = []
        current = [row[:] for row in self._grid]
        
        while True:
            self._iter += 1
            tkey = tuple(tuple(row) for row in current)
            if tkey in iterations:
                loop_start = iterations.index(tkey)
                attractor = iterations[loop_start:]
                for state in iterations:
                    Thought.cache[tkey] = attractor
                break
            iterations.append(tkey)
            tmp = [[self.process(i, j) for i, _ in enumerate(self._grid[j])] for j, _ in enumerate(self._grid)]
            current = tmp
        
        self.value = int(strGrid(current), 2)
        
        if sum([sum(row) for row in self._grid]) == 0:
            self._state = EXTINCT
            self._certainty = 20
        elif self._iter < 5:
            self._state = STABLE
            self._certainty = self._iter
        elif self._iter < 10:
            self._state = OSCILLATING
            self._certainty = self._iter
        elif self._iter < 20:
            self._state = WANDER
            self._certainty = self._iter
        else:
            self._state = CHOATIC
            self._certainty = 20
        return self
    
    def restore(self):
        self._grid_size = self._cache['__init__']['size']
        self.value = self._cache['__init__']['value']
        self._iter = 0
        return self

    def backtrack(self, dis):
        self._grid_size = self._cache['__init__']['size']
        try:
            self.value = int(strGrid(self._cache[list(self._cache)[min(abs((self._iter - dis, self._iter)))]]), 2)
        except:
            self.restore()
        self._iter = dis if dis < self._iter else self._iter
        return self
    def __hash__(self):
        return 0


class DeepThought(Thought): 
    _minimal_grid_size = 16
    _standard_grid_size = 18
    _max_grid_size = 64 # ~ sys.maxsize
    
class MicroThought(Thought):
    _max_grid_size = 4
    _minimal_grid_size = 2
    _standard_grid_size = 2

class Tubeel:
    def __init__(self, thots:list[Thought] =[]): #Value has been made mandatory.
        self._grid = [] #[int(cell) for cell in list(thot.bin) for thot in thots] #Gets set by value
        self.thots = list()
        for i in range(len(thots)):
            self._grid.append([int(cell) for cell in list(thots[i].bin)])
            self.thots.append(thots[i].id)
        self._iter = 0
        
    def write(self, thought=Thought(), loc=(0,), **kwargs):
        if not isinstance(thought, Thought):
            thought = AutoThought(size= (thought % 12), val=thought)
        if loc[0] < self.num :self._grid[loc[0]] = [int(_) for _ in thought.bin]
        else: self._grid.append([int(_) for _ in thought.bin])

    @property
    def _size(self):
        return self.num

    def contemplate(self, max=20):
        t = 0
        while t < max:
            self.adapt()
            t += 1
        return self
    
    @property
    def thoughts(self):
        thots = []
        for i in range(self.num):
            thotsize, thotval = int(math.sqrt(len(self._grid[i]))), int(''.join([str(bit) for bit in self._grid[i]]), 2)
            thots.append(AutoThought(size = thotsize, value = thotval))
        return thots

    def __iter__(self):
        return iter(self.thoughts)
    
    def __getitem__(self, i):
        try:
            thotsize, thotval = int(math.sqrt(len(self._grid[i]))), int(''.join([str(bit) for bit in self._grid[i]]), 2)
            return AutoThought(thotsize, thotval, self._iter)
        except:
            return Thought(iter=self._iter)
    
    def __setitem__(self, idx, value):
        if abs(idx) >= len(self._grid):
            while len(self._grid) < idx + 1:
                self._grid.append([0 for _ in range(25)])
        self._grid[idx] = [int(_) for _ in value.bin]

    def pop(self, idx=-1):
        if abs(idx) < len(self._grid):
            thot = self._grid.pop(idx)
            thotsize, thotval = int(math.sqrt(len(thot))), int(''.join([str(bit) for bit in thot]), 2)
            return AutoThought(thotsize, thotval, iter=self._iter)
            
        return Thought(iter=self._iter)

    def __invert__(self):
        for i in range(0, self.num):
            self._grid[i] = [(j + 1) % 2 for j in self._grid[i]]
        self._iter += 1
    
    def __str__(self):
        return '[' + ', '.join(map(str, [thought for thought in self.thoughts])) + ']'

    def adapt(self):
        _ = self.think()
        self = _
        return self

    def think(self):
        self._iter +=1
        tub = Tubeel([])
        tub._grid = [[self.process(i, j) for i, _ in enumerate(self._grid[j])] for j, _ in enumerate(self._grid)]
        tub._iter = self._iter
        return tub
    
    def __repr__(self):
        return '"' + ' '.join(map(str, [thought for thought in self.thoughts])) + '"'
    
    def __hash__(self):
        return 0

    @property
    def num(self):
        return len(self._grid)
    def __len__(self):
        return self.num

    def process(self, i, j):
        ulen = len(self._grid[i - 1])
        dlen = len((self._grid + 1) % self.num)
        return self.apply_rules(( self._grid[i - 1][(j - 1)]
                                +self._grid[i - 1][j % ulen]
                                +self._grid[i - 1][(j + 1) % ulen]
                                +self._grid[i][j - 1]
                                +self._grid[i][(j + 1) % len(self._grid[i])] 
                                +self._grid[(i + 1) % self.num][j - 1]
                                +self._grid[(i + 1) % self.num][j % dlen]
                                +self._grid[(i + 1) % self.num][(j + 1) % dlen] ), self._grid[j][i])

    def apply_rules(self, neighbors, _self):
        if neighbors < 2 or neighbors > 3:
            return 0
        elif neighbors == 3:
            return 1
        else:
            return _self
    

class Eel:
    def __init__(self, size=8, immortal=False):
        self._size = max(8, min(size, 64))
        self._thoughts = {}
        self._grid = [[[0 for _ in range(self._size)]
                       for _ in range(self._size)]
                       for _ in range(self._size)]
        self.__imortal = True

    def live(self, max=20, ivl=3000):
        self.__interval = interval.Interval(func=self.think, tick=ivl, repeat=max)
        self.__interval.start()
    def die(self):
        if isinstance(self.__interval, interval.Interval):
            self.__interval.stop()
            self.__interval = None
    def write(self, thought=Thought(), loc=(0, 0, 0), dir=1, merge=False):
        size = thought.size
        id = thought.id
        axs = abs(dir)
        if axs == 1:
            ax1, ax2 = 1, 2
        elif axs == 2:
            ax1, ax2 = 0, 2
        else:
            ax1, ax2 = 0, 1
        sign = 1 if dir > 0 else -1
        off = [0, 0, 0]
        surface = thought.grid
        for i in range(thought.size):
            for j in range(thought.size):
                off[ax1] = i * sign
                off[ax2] = j * sign
                x, y, z = off[0] + loc[0], off[1] + loc[1], off[2] + loc[2]
                if not (0 <= x < self._size and 0 <= y < self._size and 0 <= z < self._size):
                    continue
                if merge:
                    self._grid[x][y][z] |= surface[i][j]
                else:
                    self._grid[x][y][z] = surface[i][j]
        self._thoughts[thought.id] = (thought.size, loc, dir)
    def __hash__(self):
        return 0
    def __str__(self):
        rtn_str = '[ '
        for size, loc, dir in self._thoughts.values():
            _, value = self.read(size, loc, dir)
            rtn_str += str(AutoThought(size, value)) + ', '
        return rtn_str[:-1] + ']'
    def __repr__(self):
        rtn_str = '"'
        for size, loc, dir in self._thoughts.values():
            _, value = self.read(size, loc, dir)
            rtn_str += repr(AutoThought(size, value)) + ' '
        return rtn_str[:-1] + '"'
    def _getter(self, x, y, z):
        if 0 <= x < self._size and 0 <= y < self._size and 0 <= z < self._size:
            return self._grid[x][y][z]
        else:
            return 0
    def read(self, thought, loc=(0, 0, 0), dir = 1):
        size = thought if isinstance(thought, int) else self._thoughts[thought.id][0] if isinstance(thought, str) else thought.size
        uloc = loc if isinstance(thought, int) else self._thoughts[thought][1] if isinstance(thought, str) else self._thoughts[thought.id]
        udir = dir if isinstance(thought, int) else self._thoughts[thought][2] if isinstance(thought, str) else self._thoughts[thought.id]
        surface = [[0 for _ in range(size)] for _ in range(size)]
        ax = abs(udir)
        sign = 1 if udir > 0 else -1
        match ax:
            case 1:
                ax1, ax2 = 1, 2
            case 2:
                ax1, ax2 = 0, 2
            case 3:
                ax1, ax2 = 0, 1
        off = [0, 0, 0]
        x_, y_, z_ = uloc
        for i in range(size):
            for j in range(size):
                off[ax1] = i * sign
                off[ax2] = j * sign
                x = x_ + off[0]
                y = y_ + off[1]
                z = z_ + off[2]
                surface[i][j] = self._getter(x, y, z)
        str_ = strGrid(surface)
        return AutoThought(size=size, value=int(str_, 2), inter=5, id=thought.id if isinstance(thought, Thought) else thought if isinstance(thought, str) else '')
    def think(self):
        tmp = [[[self.process(l, j, i) for l in self._grid[i][j]]
                for j, _ in enumerate(self._grid[i])]
                for i, _ in enumerate(self._grid)]
        self._grid = tmp
    def process(self, l, j, i):
        return self.apply_rules((self._grid[i - 1][j - 1][l - 1] + 
                self._grid[i - 1][j - 1][l] +
                self._grid[i - 1][j - 1][(l + 1) % self._size] +
                self._grid[i - 1][j][l - 1] +
                self._grid[i - 1][j][l] +
                self._grid[i - 1][j][(l + 1) % self._size] +
                self._grid[i - 1][(j + 1) % self._size][l - 1] +
                self._grid[i - 1][(j + 1) % self._size][l] +
                self._grid[i - 1][(j + 1) % self._size][(l + 1) % self._size] + 
                self._grid[i][j - 1][l - 1] + 
                self._grid[i][j - 1][l] +
                self._grid[i][j - 1][(l + 1) % self._size] +
                self._grid[i][j][l - 1] +
                self._grid[i][j][l] +
                self._grid[i][j][(l + 1) % self._size] +
                self._grid[i][(j + 1) % self._size][l - 1] +
                self._grid[i][(j + 1) % self._size][l] +
                self._grid[i][(j + 1) % self._size][(l + 1) % self._size] +
                self._grid[(i + 1) % self._size][j - 1][l - 1] + 
                self._grid[(i + 1) % self._size][j - 1][l] +
                self._grid[(i + 1) % self._size][j - 1][(l + 1) % self._size] +
                self._grid[(i + 1) % self._size][j][l - 1] +
                self._grid[(i + 1) % self._size][j][l] +
                self._grid[(i + 1) % self._size][j][(l + 1) % self._size] +
                self._grid[(i + 1) % self._size][(j + 1) % self._size][l - 1] +
                self._grid[(i + 1) % self._size][(j + 1) % self._size][l] +
                self._grid[(i + 1) % self._size][(j + 1) % self._size][(l + 1) % self._size]), (i, j, l))
    def apply_rules(self, val, idx):
        if val == 5:
            return 1
        elif val == 4:
            return self._grid[idx[0]][idx[1]][idx[2]]
        elif self.__imortal and (val == 0 or val == 7):
            return 1
        else:
            return 0
        
class Colony(Eel):
    def __init__(self, size):
        self._size = max(64, min(size, 128))
        self._thoughts = {}
        self._grid = [[0 for _ in range(self._size)]
                       for _ in range(self._size)]
        self.__imortal = False
    def write(self, thought=Thought(), loc=(0, 0), dir=1, merge=False):
        size = thought.size
        id = thought.id
        sign = 1 if dir > 0 else -1
        surface = thought.grid
        for i in range(thought.size):
            for j in range(thought.size):
                x, y = j * sign + loc[0], i * sign + loc[1]
                if not (0 <= x < self._size and 0 <= y < self._size):
                    continue
                if merge:
                    self._grid[x][y] |= surface[i][j]
                else:
                    self._grid[x][y] = surface[i][j]
        self._thoughts[thought.id] = (thought.size, loc, dir)
    def __str__(self):
        rtn_str = '[ '
        for size, loc, dir in self._thoughts.values():
            _, value = self.read(size, loc, dir)
            rtn_str += str(AutoThought(size, value)) + ', '
        return rtn_str[:-1] + ']'
    def __repr__(self):
        rtn_str = '"'
        for size, loc, dir in self._thoughts.values():
            _, value = self.read(size, loc, dir)
            rtn_str += repr(AutoThought(size, value)) + ' '
        return rtn_str[:-1] + '"'
    def _getter(self, x, y):
        if 0 <= x < self._size and 0 <= y < self._size:
            return self._grid[x][y]
        else:
            return 0
    def read(self, thought, loc=(0, 0, 0), dir = 1):
        loc = loc[0:2] #Truncates location.
        size = thought if isinstance(thought, int) else self._thoughts[thought][0] if isinstance(thought, str) else thought.size
        uloc = loc if isinstance(thought, int) else self._thoughts[thought][1] if isinstance(thought, str) else self._thoughts[thought.id][1]
        udir = dir if isinstance(thought, int) else self._thoughts[thought][2] if isinstance(thought, str) else self._thoughts[thought.id][2] 
        surface = [[0 for _ in range(size)] for _ in range(size)]
        sign = 1 if udir > 0 else -1
        x_, y_ = uloc
        for i in range(size):
            for j in range(size):
                x = x_ + j * sign
                y = y_ + i * sign
                surface[i][j] = self._getter(x, y)
        str_ = strGrid(surface)
        return AutoThought(size=size, value=int(str_, 2), inter=5, id=thought.id if isinstance(thought, Thought) else thought if isinstance(thought, str) else '')
    def think(self):
        self._grid = [[self.process(j, i) for j in self._grid[i]]
                for i, _ in enumerate(self._grid)]
    def process(self, j, i):
        return self.apply_rules( self._grid[i - 1][j - 1] + 
                self._grid[i - 1][j] +
                self._grid[i- 1][(j + 1) % self._size] +
                self._grid[i][j - 1] +
                self._grid[i][(j + 1) % self._size] +
                self._grid[(i + 1) % self._size][j - 1] +
                self._grid[(i + 1) % self._size][j] +
                self._grid[(i + 1) % self._size][(j + 1) % self._size])
    def apply_rules(self, val):
        if val == 3:
            return 1
        elif self.__imortal and (val == 0 or val == 5):
            return 1
        elif val < 2 or val > 3:
            return 0