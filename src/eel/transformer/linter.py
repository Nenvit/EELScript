from io import BytesIO, BufferedIOBase, TextIOBase
from ..runtime.components import VFile as vfile
from ..glbls import LEXER_OPS, els
from . import lexer, tokens, mask
from ..codepoints import *
verify = lexer.verify_statement
parse = tokens.parse_ready

BOLD = '\033[31m'
RED = '\033[1m'
RESET = '\033[0m'
GREEN = "\033[32m"
GOTH = '\033[12m'

ljust = {KCOLO, KMTFC, KMTFD, KUNARY, KDFN} #xmpl: # Mtf 00 ; -> #Mtf 00; # <- Mtf 00 <- ;
rjust = {KCOLC, KCLN, KCOMM, KQ, KSEMI} # 4 -> ) = 4)
def pretty(stmnt):
    res = []
    bitmask = mask.gen_mask(stmnt)
    for tkn, justify in zip(stmnt, bitmask):
        if justify in rjust:
            res.append(tkn.decode('ascii'))
            
        elif justify in ljust:
            if res and res[-1] == ' ':
                res.pop()
            res.append(tkn.decode('ascii'))
            res.append(' ')
        else:
            res.append(tkn.decode('ascii'))
            res.append(' ')

    return ''.join(res)
    
EX_tup = (str, bytes, bytearray,  BufferedIOBase,  TextIOBase)
def examine(stmnt, flat=False, full=False):
    file = vfile()
    verified = []
    illicit = []
    errors = []
    if isinstance(stmnt, EX_tup):
        write(stmnt, file)
    elif isinstance(stmnt, dict):
        for val in stmnt.values():
            if isinstance(val, EX_tup):
                write(stmnt, file)
            else:
                for iterable in val:
                    if isinstance(iterable, EX_tup):
                        write(iterable, file)
    else:
        for iterable in stmnt:
            if isinstance(iterable, EX_tup):
                write(iterable, file)
    for pointer in range(len(file)):
        try: 
            *_, stt = verify(file[pointer], pointer)
            verified.append((pointer, file[pointer]))
        except Exception as e:
            raise e
            illicit.append((pointer, file[pointer], e))
    if full:
        print(f'[EXMN INPT] {GOTH}(These dare come before the council?){RESET} =>', end=' ' if flat else '\n')
        file.seek(0)
        for _ in range(len(file)):
            if not flat:
                print(f"\t{_:02d} | {pretty(file[_])}")
            else:
                print(pretty(file[_]), end =' ')
    if verified:
        print(f"{'\n' if flat else ''}{GREEN}[EXMN RCPT]{RESET}: Verified {GREEN}{GOTH}(These are right and just.){RESET} =>", end = ' ' if flat else '\n')
        for _, stt in verified:
            if not flat:
                print(f'\t{_:02d} | {pretty(stt)}')
            else:
                print(pretty(stt), end=' ')
    if illicit:
        print(f"{'\n' if flat else ''}{BOLD}{RED}[EXMN RCPT]{RESET}: Illicit {RED}{GOTH}(INFIDELS!){RESET} =>", end = ' ' if flat else '\n')
        for _, stt, e, in illicit:
            if not flat:
                string = f'  {_:02d} | {pretty(stt)}'
                print(string)
                if isinstance(e, lexer.Error):
                    print(' ' * (e.index + 7),f'{RED}^^^ {BOLD}[ERR]{RESET}{GOTH} {e}{RESET}')
                else:
                    print(" " * 7, f"{RED}{BOLD}!!! {GOTH}[Forgive me, for I hath sinned]{RESET}: {RED}{e}{RESET}")
            else:
                print(f"{pretty(stt)} <= {RED}({e}){RESET}", end=' ')
    if flat:
        print()

def write(stmnt, file):
    type_ = type(stmnt)
    if not isinstance(stmnt, ( BufferedIOBase,  TextIOBase)):
        ino =  BytesIO(bytes(stmnt, 'ascii') if type_ is str else bytes(stmnt))
    else:
        ino = stmnt
    for tokens in parse(ino):
        file.write(tokens[:-1].split(b' '))