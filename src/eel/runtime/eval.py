from ..glbls import els, LEXER_OPS
from .components import Decimal, Binary, Hexadecimal, Octal, Random, NaN, NaT, String, BIT
from ..thoughts import *
from ..codepoints import *
#Debug Controls:

#Setup:
INPT = "[{id} INPT]: Pre-process[ {s} ]"
RCPT = "[{id} RCPT]: Post-process[ {s!r} ]"
DBG_SUB = True #This is the switch for the recursive function, instead of recursive decorators.
DEBUG = {'eval', 'attemptThoughtLiteral', 'collapse', 'typeint', 'sub_exp', 'parse_literal', 'evalint'}
DEBUG_REGISTRY = {'eval': "EVAL", 'sub_exp':'CMPT', 'attemptThoughtLiteral': "ATLP", 'typeint': "TPNT", 'parse_literal': "PRSL", 'collapse': "EXPR", 'evalint': "VLNT"}
NO_DEBUG = set({'attemptThoughtLiteral', 'collapse', 'typeint', 'parse_literal', 'evalint'})
SILENCE_REGISTRY = False
DEBUG_TOGGLE = False
#
def debug(f):
    if not DEBUG_TOGGLE: return f
    # if not SILENCE_REGISTRY:
    #     print(f"[DEBUG REGISTRY]: {f.__name__} [{'Y' if f.__name__ in DEBUG else 'N'}]")
    # if not f.__name__ in DEBUG:
    #     return f
    # id = DEBUG_REGISTRY.get(f.__name__, None)
    # if id is None:
    #     return f
    id = f.__name__
    depth = 0
    def wrapper(*args, **kwargs):
        nonlocal depth
        is_top = depth == 0
        depth += 1
        if is_top:
            args_list = ', '.join(list(map(repr, args)) + [f"{k}={v!r}" for k, v in kwargs.items()])
            print(INPT.format(id=id, s=args_list))
        out = f(*args, **kwargs)
        if is_top:
            print(RCPT.format(id=id, s=out))
        depth -= 1
        return out
    return wrapper

    

def typeint(prefix):
    prefix = prefix.lower()
    if prefix == b'd.':
        return Decimal
    elif prefix == b'r.' or prefix == b'0r':
        return Random
    elif prefix == b'b.' or prefix == b'0b':
        return Binary
    elif prefix == b'h.' or prefix == b'0x':
        return Hexadecimal
    elif prefix == b'o.' or prefix == b'0o':
        return Octal
    elif prefix.isdigit():
        return int
    else:
        return NaN

def isint(tkn):
    try:
        type_ = typeint(tkn[:2])
        if type_ is NaN:
            return False
        if type_ is int:
            return True
        type_(tkn[2:])
        return True
    except:
        return False

def isthgt(tkn):
    size, *val = tkn.split(b'-')
    if not val:
        return False
    else: val = b''.join(val)
    return isint(size) and isint(val)

str_delim = {96, 39}
def isstr(tkn):
    return True if tkn[0] in str_delim and tkn[-1] in str_delim and tkn[0] == tkn[-1] else False


def evalint(candidate):
    if isinstance(candidate, (int, Thought, Tubeel, Eel, Colony)):
        return candidate
    try:
        type_= typeint(candidate[:2])
        if type_ == NaN:
            raise BaseException(f"{candidate.decode('ascii')} is NaN.")
        return type_(candidate) if type_ is int else type_(candidate[2:])
    except BaseException as e:
        if 'evalint' in DEBUG:
            print(f'[EVNT RJCT]:Rejected integer literal on account of: {e}')
        return NaN(candidate)

def attemptThoughtLiteral(candidate):
    try:
        size, value = [_ for _ in els(candidate, b'-', 2)]
        return AutoThought(evalint(size), evalint(value))
    except Exception as e:
        if 'attemptThouhgtLiteral' in DEBUG:
            print(f"[ATLP RJCT]: Rejected thought attempt on account of: {e}")
        return NaT(candidate)

@debug
def discern_var(literal, vm=None):
    if isinstance(literal, (int, Thought, Tubeel, Colony, Eel, String)): return literal
    try: return vm.vars[literal]
    except: return literal

@debug
def eval(num=0, den=None, opr=b''):
    if den is None:
        den = num
    match opr:
        case b'==':
            return num == den
        case b'!=':
            return num != den
        case b'>=':
            return num >= den
        case b'<=':
            return num <= den
        case b':>':
            return num.restore().adapt(den)
        case b':<':
            return num.backtrack(den)
        case b'//':
            return num // den
        case b'/':
            return num / den
        case b'*':
            return num * den
        case b'**':
            return num ** den
        case b'>':
            return num > den
        case b'<':
            return num < den
        case b':':
            return AutoThought(num._cache['__init__']['size'],num._cache['__init__']['value'])
        case b'&':
            return num & den
        case b'^':
            return num ^ den
        case b'|':
            return num | den
        case b'%':
            return num % den
        case b'\\':
            return den.think()
        case b'\\\\':
            return den.adapt()
        case b':(':
            return den.contemplate()
        case b'>>':
            return num >> den
        case b'<<':
            return num << den
        case b'+':
            return num + den
        case b'-':
            return num - den if num else -den
        case b'~':
            return ~den
    return den

#Precedence Sets
HIGHEST = {b':<', b':>', b'**', b'\\', b'\\\\'}
HIGH = {b'*', b'/', b'//', b'%'}
MEDIUM = {b'+', b'-'}
LOW = {b'!', b'^', b'&', b'|', b':(', b'('}
LOWEST = {b'<', b'>', b'!=', b'==', b'<=', b'>='}
UNARY_PASS = set()

levels = (UNARY_PASS, HIGHEST, HIGH, MEDIUM, LOW, LOWEST)

@debug
def sub_exp(pkg):
    parcel = list(zip(*pkg))
    res = []
    hop = False

    for level in levels: 
        for index, tkn_mtd in enumerate(parcel):

            bit, idx, end, tkn = tkn_mtd

            if hop:
                hop = False
                continue
            elif tkn is None: continue

            if bit == KUNARY or (bit == KCOLO and tkn in level):
                nbit, nidx, nend, ntkn = parcel[index + 1]
                try: res.append((KATOM, idx, nend, eval(den=ntkn, opr=tkn)))
                except: raise Exception(0xEF, idx, nidx)
                hop = True

            elif bit == KBINARY and tkn in level:
                pbit, pidx, pend, ptkn = res[-1]
                nbit, nidx, nend, ntkn = parcel[index + 1]
                try: res[-1] = ((KATOM, pidx, nend, eval(num=ptkn, den=ntkn, opr=tkn)))
                except: raise Exception(0xEF, pidx, nend)
                hop = True

            elif bit == KCOLO: res.append(tkn_mtd)

            elif bit in {KCOLC, KQ, KSEMI, KCOMM}:
                pass
            
            else:
                res.append(tkn_mtd)
        else:
            parcel = res[:]
            del res[:]

    else: return parcel[0][3]

@debug
def deepest_level_of(bits):
    lyr, deepest = 1, 1
    for bit in bits:
        if bit == KCOLO:
            lyr += 1

            if lyr > deepest: deepest = lyr
        elif bit == KCOLC: lyr -= 1
    
    else: return deepest

@debug
def all_of_level(bits, level):
    lyr, start = 1, 0
    for idx, bit in enumerate(bits):
        if   bit == KCOLO: start, lyr = idx, lyr + 1
        elif bit == KCOLC: 
            if lyr == level and start < idx -1: yield slice(start, idx + 1)
            lyr -= 1
    else:
        if lyr == level and start < idx -1: yield slice(start, idx + 1)


@debug
def collapse(package):
    bits, idxs, ends, tkns = (list(_) for _ in package)
    for layer in range(deepest_level_of(bits), 0, -1):
        slices = *all_of_level(bits, layer),
        for slice in reversed(slices):
            pkg = bits[slice], idxs[slice], ends[slice], tkns[slice]
            __idx, __end = pkg[1][0], pkg[2][0]
            __res = sub_exp(pkg)
            del bits[slice], idxs[slice], ends[slice], tkns[slice]
            
            start = slice.start
            bits.insert(start, KATOM)
            idxs.insert(start, __idx)
            ends.insert(start, __end)
            tkns.insert(start, __res)
    else: return tkns[0]

def tokens(package):
    bitmask, starts, ends, pretty = package
    mv = memoryview(pretty)
    for mask, start, end in zip(bitmask, starts, ends):
        tkn = mv[start: end]

        if mask == KINT:
            yield evalint(tkn.tobytes())

        elif mask == KTHT:
            yield attemptThoughtLiteral(bytes(tkn))

        elif mask == KSTR:
            yield String(tkn)

        else:
            yield tkn.tobytes()