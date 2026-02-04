from . import components, DISP, eval, unpackage
from ..BaseError import BaseError
from .. import errors, glbls      

def engage(MACHINE, strict=False, dir=False):
    with open('__script.bh' if dir else MACHINE.bh, 'rb') as source:
        MOTIFS         = unpackage.motif_table(source)
        FILE_OFFSET    = source.tell()
        source.seek(MOTIFS[b'__script'][0] + FILE_OFFSET)            
        start_from     = {MTF:0 for MTF in MOTIFS}
        MACHINE.count  = {MTF:0 for MTF in MOTIFS}
        while True:
            status, *package = unpackage.brackethatch(source)
            if status is None: break
            if status[0] == 10:
                try:
                    tkns  = *eval.tokens(package),
                    bitmask, starts, ends, _ = package
                    motif = DISP.execute((bitmask, starts, ends, tkns), MACHINE)
                    if motif == b'%%next':
                        start_from[MACHINE.motif] += 1
                        if start_from[MACHINE.motif] < len(MOTIFS[MACHINE.motif]): 
                            source.seek(MOTIFS[MACHINE.motif][start_from[MACHINE.motif]] + FILE_OFFSET)
                        elif MACHINE.fs[-1] != b'__script': 
                            last_motif = MACHINE.fs.pop()
                            source.seek(MOTIFS[b'__script'][start_from[b'__script']] + FILE_OFFSET)
                    elif motif == b'%%quit': break
                    elif motif:
                        source.seek(MOTIFS[motif][0] + FILE_OFFSET)
                        MACHINE.motif = motif
                        start_from[MACHINE.motif] = 0
                        MACHINE.fs.append(motif)
                except Exception as e: 
                    print(f"{f"{status[-1]:02d}".ljust(6)} | {package[-1].replace(b'\0', b' ').decode('ascii')}\n")
                    try: print(BaseError[e.args[0]](package[-1], (*e.args, status[-1])))
                    except: print(e)
                    break
            else:
                if strict: 
                    print(print(f"{f"{status[-1]:02d}".ljust(6)} | {package[-1].replace(b'\0', b' ').decode('ascii')}\n"))
                    print(BaseError[status[0]](package[-1], status))
                    break
                else: continue