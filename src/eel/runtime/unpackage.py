from ..glbls import *
from ..codepoints import CODE_MAP
from ..streampi import readuntil, readeach
from struct import unpack

SRCB = bytes(SRC)
def brackethatch(fio):
    chunk = readuntil(fio, SRCB)
    if not chunk: return None, None
    view = memoryview(chunk)
    stat = bytearray()
    code = bytearray()
    idxs = bytearray()
    ends = bytearray()
    curr = stat

    p    = len(BRKO)
    while p < len(chunk):
        word = view[p:p + 4]
        byte = chunk[p]
        if word   == PRM:
            curr  =  code
            p     += len(PRM)
        elif word == CDE:
            curr  =  idxs
            p     += len(CDE)
        elif word == IDX:
            curr  =  ends
            p     += len(IDX)
        elif word == LEN:
            p     += len(LEN) + len(BRKC)
            break
        else:
            curr.append(byte)
            p += 1

    pretty  = view[p:].tobytes()
    status  = unpack(f'<3hI', stat)
    starts  = unpack(f'<{len(idxs) // 2}H', idxs)
    stahps  = unpack(f'<{len(ends) // 2}H', ends)
    btmask  = unpack(f'<{len(code)}B', code)
    print(f"[BH] =>", 
            f"Status: {status[0]:X} ({'\033[32m\033[1mOK\033[0m\x07' if status[0] == 10 else '\033[31m\033[1mNot OK\033[0m'})",
            f"Text: \033[1m{pretty.replace(b'\0', b' ').decode('ascii')}\033[0m",
            sep='\n\t')
    return status, btmask, starts, stahps, pretty

STPB = bytes(STP) + b'\n'
TBLB = b' =>\n\t' + bytes(TBL)
STPT = bytes(BDY)
def motif_table(fio):
    chunk = readuntil(fio, bytes(STPT), skip=True)
    rtn   = dict()
    for table in chunk.split(STPB):
        if not table: continue
        motif, table = table.split(TBLB)
        rtn[motif[1:]] = unpack(f'<{len(table) // 4}I', table)
        print(motif.decode('ascii'), TBLB.decode('ascii'), rtn[motif[1:]], sep='')

    return rtn

