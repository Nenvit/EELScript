from ..glbls import SRC, TKN
from ..runtime.eval import isint, isthgt, isstr
from array import array
from ..codepoints import *

DEF_MASK = { #CONDSIDER ORDER!!
    (b'~', b'!', b'\\', b'\\\\'): KUNARY,
    (b'-', b'+', b':>', b':<', b'>', b'>>',
     b'<<', b'<', b'/', b'//', b'|', b'^', b'*',
     b'%', b'&', b'**', b'==', b'!='): KBINARY,
    (b':(', b'('): KCOLO,
    (b')',): KCOLC,
    (b';',): KSEMI,
    (b':',): KCLN,
    (b'?',): KQ,
    (b'for',): KFOR,
    (b'from',): KFROM,
    (b'set',): KSET,
    (b'get',): KGET,
    (b'at',): KAT,
    (b'as',): KAS,
    (b',',): KCOMM,
    (b'=',): KEQ,
    (b'#',): KMTFD,
    (b'@',): KMTFC,
    (b'$!', b'$'): KDFN,
    (b'adopt', b'.', b'out', b'del', b'sniff'): KKW,
    (b'__header',): HEDR,
    (b'quit', b'!!'): KQUIT,
    #(100,): KSTR,
    #(200,): KINT,
    #(300,): KTHT,
    #(400,): CMNT,
    (b'+=', b'-=', b'/=', b'%=', b'*=', b'&=', b'^=', b'|='): AUGA,
    (b'tubeel', b'colony', b'eel'): KCLS,
}
SRCB = bytes(SRC)
def gen_mask(expr): #0 => universal atom.
    rtnba = bytearray()
    rtnln = list()
    index = 0
    for item in expr: 
        if not item: continue
        if item == SRCB: break

        for tple in DEF_MASK:
            if item in tple:
                if item in {b'-', b'+'}:
                    bin = {KBINARY, KCOLO} #Keep variability available for future viability.
                    if not rtnba or rtnba[-1] in bin:
                        rtnba.append(KUNARY)
                    else:
                        rtnba.append(KBINARY)
                elif item == b';' and index == 0:
                    rtnba.append(KMTFD)
                    rtnba.append(KSEMI)
                else:
                    rtnba.append(DEF_MASK[tple])
                break
        else:
            if isstr(item):
                rtnba.append(KSTR)
            elif isint(item):
                rtnba.append(KINT)
            elif isthgt(item):
                rtnba.append(KTHT)
            else:
                rtnba.append(0)
        rtnln.append(len(item))
        index += 1
    return rtnba

rjust = {KCOLO, KMTFC, KMTFD, KUNARY, KDFN, KCLN} #xmpl: # Mtf 00 ; -> #Mtf 00; # <- Mtf 00 <- ;
ljust = {KCOLC, KCLN, KCOMM, KQ, KSEMI} # 4 -> ) = 4)

def __pretty(stmnt):
    bitmask         = gen_mask(stmnt)
    res             = bytearray()
    for tkn, justify in zip(stmnt, bitmask):
        if justify in rjust:
            res.extend(tkn)
            
        elif justify in ljust:
            if res and res[-1] == 0:
                res.pop()
            res.extend(tkn)
            res.extend(TKN)
        else:
            res.extend(tkn)
            res.extend(TKN)

    return bitmask, res

def alliterate(expr):
    btmsk, prtty     = __pretty(expr)
    idxs             = array('H')
    ends             = array('H')
    idx              = 0
    for tkn in expr:
        while idx < len(prtty) and prtty[idx] == 0: idx += 1

        idxs.append(idx)
        idx += len(tkn)
        ends.append(idx)
    else:
        return btmsk, idxs, ends, prtty