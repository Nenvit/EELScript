RESERVED = {
    b'adopt', b'__header', b'__script', b'return', b'exit', b'colony',
    b'tubeel', b'eel', b'.', b'set', b'at', b'for', b'del', b'.', b'out',
    b'get', b'from', b'as', b'sniff', b'again'
}

COMPILER_OPS = set(b'!@#$%([])^&*=-+,<>~|;:/?\\')

LEXER_OPS = { b':', b'<', b'>', b'!', b'$', b',', b'$!', b';',
    b'|', b'~', b'*', b'-', b'^', b'&', b'%', b'+', b'**', b'(',  b')', b':(',
    b'@', b'/', b'//', b'=', b'<-', b'->', b'#', b'?', b'\\', b'\\\\', b'==',
    b':<', b':>', b'<=', b'>=', b'!=', b'+=', b'-=', b'=', b'+=', b'-=', b'/=', b'%=', b'*=', b'&=', b'^=', b'|='}
#{b'$': {b'', b'!'}, b'|': {b'', b'='}, b'&': {b'', b'='}, b':': {b'', b'>', b'<', b'('}, b'=': {b'', b'='}, b'<': {b'', b'-', b'='}, b'*': {b'', b'*', b'='}, b'^': {b'', b'='}, b'(': {b''}, b'@': {b''}, b'/': {b'', b'/', b'='}, b'~': {b''}, b',': {b''}, b';': {b''}, b'!': {b'', b'='}, b']': {b''}, b'#': {b''}, b'>': {b'', b'='}, b'-': {b'', b'>', b'='}, b'%': {b'', b'='}, b'+': {b'', b'='}, b'[': {b''}, b'?': {b''}, b')': {b''}, b'\\': {b'', b'\\'}}
OPS_CODE_MAP = {36: {33}, 124: {61}, 38: {61}, 
                58: {40, 60, 62}, 61: {61}, 60: {45, 61}, 
                42: {42, 61}, 94: {61}, 40: set(), 64: set(), 
                47: {61, 47}, 126: set(), 44: set(), 59: set(), 
                33: {61, 33}, 35: set(), 62: {61}, 45: {61, 62}, 
                37: {61}, 43: {61}, 63: set(), 41: set(), 92: {92}}

LEXER_RES = RESERVED

BRKO, BRKC = b'{\0{\0', b'}\0}\0}'
CDE, IDX, TBL, STP, LEN, PRM  = bytearray([ 99, 100, 101, 59]),\
                                bytearray([105, 100, 120, 59]),\
                                bytearray([116,  98, 108, 58]),\
                                bytearray([115, 116, 112, 59]),\
                                bytearray([108, 101, 110, 59]),\
                                bytearray([104, 100, 114, 59])
BDY                           = bytearray([ 98, 100, 121, 59])
TKN                           = b'\x00'
SRC                           = bytearray([123, 115, 114, 99, 125])

class MultiDelim:
    def __init__(self, *args):
        self.delims = list(args)
    def __contains__(self, arg):
        return arg in self.delims
    def __str__(self):
        return str(self.delims)
    def __repr__(self):
        return str(self)

def els (l, delim, pad=0, fill = None, keep=False, group_open=None, group_close=None):
    start = 0
    count = 0
    udelims = set()
    lyr = 0
    if not type(delim) is MultiDelim:
        delim = MultiDelim(delim)
    if isinstance(l, (bytes, str)):
        for _ in delim.delims:
            udelims.add(type(l)(_, 'ascii') if isinstance(_, str) and not isinstance(l, str) else type(l)(_))
        result = [l]
        cnstr = []
        udelims = sorted(udelims, key=len)
        for udelim in udelims:
            cnstr.clear()
            for section in result:
                cnstr.extend((section.split(udelim)).append(udelim) if keep else section.split(udelim))
            result = cnstr
        for res in result:
            count += 1
            yield res
        if pad and count <= pad:
            for _ in range(pad - count):
                yield type(l)(fill if fill else type(l)())
    else:
        for i, e in enumerate(l):
            if e == group_open: lyr += 1
            elif e == group_close and lyr: lyr -= 1
            if lyr: continue
            if e in delim:
                yield l[start:i + 1 if keep else i]
                start = i + 1
                count += 1
        yield l[start:]
        count += 1
        if pad and count <= pad:
            for _ in range(pad - count):
                yield list() if fill is None else [fill]

def slices_of(iterable, delim, start = 0):
    _start = start
    for idx, itm in enumerate(iterable):
        if idx < start: continue
        if itm == delim and _start < idx:
            yield slice(_start, idx)
            _start = idx + 1
    else:
        if _start < len(iterable): yield slice(_start, idx)

def find(iterable,  thing):
    for idx, item in enumerate(iterable):
        if item == thing: return idx
    else: return -1
