from .tokens import parse_ready
from ..glbls import *
from .lexer import verify_statement
from .mask import alliterate
from ..codepoints import *
from array import array
from os import utime, remove, path
from struct import pack

__script = b'__script'

def lex(fio):
    print(f"[LEX RCPT]: {fio.name}")
    line = 0
    *_, ext = fio.name.split('.')
    fname = '.'.join(_)
    bh_src = fname + '.mtf'
    lt_src = fname + '.bh'
    motif = __script
    lt_tbl = {__script: array('I')}
    overwrite_code = 0
    
    try:
        if path.exists(bh_src) and path.isfile(bh_src): remove(bh_src)
        if path.exists(lt_src) and path.isfile(lt_src): remove(lt_src)
    except Exception as e: raise e

    try:
        bh = open(bh_src, 'ab+')
        
        for stmnt in parse_ready(fio):
            #step 1: split the statement.
            state_ment              = [_ for _ in stmnt.split(TKN) if _]
            if not state_ment: break
            #Step 2: Acquire bitmaps, indices, and lengthss, bonus: prtty
            *map_package, prtty     = alliterate(state_ment)
            
            #Step 3: Validate the statement, acquire signature.
            status                  = verify_statement(map_package, overwrite_code)
            #Step 3.1: Prescribe motif Table.
            if KMTFD == map_package[0][0]:
                if 0xA0 <= status[0] <= 0xAF: overwrite_code = status[0]
                elif overwrite_code: overwrite_code = 0
                
                if state_ment[0] == b';' or state_ment[1] == b';':
                    motif = __script
                else:
                    motif = bytes(state_ment[1])
                if not motif in lt_tbl:         lt_tbl[motif] = array('H')
                lt_tbl[motif].append(bh.tell())

            #Step 4: Begin enscribing. Manually.
            bh.write(BRKO)
            bh.write(pack('<3hI', *status, line))
            bh.write(PRM)
            bh.write(pack(f'<{len(map_package[0])}B', *map_package[0]))
            bh.write(CDE)
            bh.write(pack(f'<{len(map_package[1])}H', *map_package[1]))
            bh.write(IDX)
            bh.write(pack(f'<{len(map_package[2])}H', *map_package[2]))
            bh.write(LEN)
            bh.write(BRKC)
            bh.write(prtty)
            bh.write(SRC)

        #Step 6: Enscribe MOTIF REFERENCE table!
        lt = open(lt_src, 'ab')
        for mtf in lt_tbl:
            lt.write(b'@')
            lt.write(mtf)
            lt.write(b' =>\n\t')
            lt.write(TBL)
            lt.write(pack(f'<{len(lt_tbl[mtf])}I', *lt_tbl[mtf]))
            lt.write(STP)
            lt.write(b'\n')
        else: lt.write(BDY)
        bh.seek(0)
        buffer = bh.read(1024)
        while buffer:
            lt.write(buffer)
            buffer = bh.read(1024)
        bh.close()
        remove(bh_src)
    finally:
        print(f"Closing...")
        lt.close()
        utime(lt_src, (0, 0))
        utime(fio.name, (0, 0))