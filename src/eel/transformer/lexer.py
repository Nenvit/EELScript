from ..glbls import els, MultiDelim
from ..codepoints import *

CNDTN_DELIM = MultiDelim(KQ, KCLN)

def verify_statement(exp_pkg, overide_code = 0):
    code = (FAITHFUL, 0, -1)
    try:
        if not exp_pkg[0]: return (0, 0, 0)
        if exp_pkg[0][-1] != KSEMI: raise Exception(0xF0, exp_pkg[1][-1], exp_pkg[2][-1])
        dispatcher(exp_pkg)
        if overide_code: raise Exception(overide_code, 0, 3)
    #except: return (0, 0, 0)
    except Exception as err: 
        code = err.args
    return code
       

def dispatcher(exp_pkg):
    exp_mask = exp_pkg[0]
    if len(exp_mask) == 0: return bytearray()

    key1 = exp_mask[0]
    if KMTFD == key1:
        if HEDR == exp_mask[1]:
            handle_header(exp_pkg)
            return exp_mask
        handle_motifd(exp_pkg)
        if len(exp_mask) == 1:
            return exp_mask
    elif KDFN == key1:
        handle_decl(exp_pkg)
    elif KMTFC == key1:
        handle_call(exp_pkg)
    elif KKW == key1:
        handle_kws(exp_pkg)
    elif KFOR == key1:
        handle_for(exp_pkg)
    elif KFROM == key1:
        handle_from(exp_pkg)
    elif BRO == key1:
        handle_compound(exp_pkg)
    elif BRC == key1:
        handle_compound_close(exp_pkg)
    elif KEQ in exp_mask or AUGA in exp_mask:
        handle_assn(exp_pkg)
    elif KQ in exp_mask:
        handle_q(exp_pkg)
    else:
        verify_operation(exp_pkg)

def handle_q(exp_pkg):
    exp, idxs, lens = exp_pkg
    condition, *true, false = els(exp, CNDTN_DELIM, pad=2, keep=True, group_open=b'[', group_close=']')
    cdtn_len = len(condition)
    mvi, mvb = memoryview(idxs), memoryview(lens)
    verify_operation((condition, mvi[:cdtn_len], mvb[:cdtn_len])) #Time to slice out a little.
    if true:
        tmp = []
        for branch in true:
            tmp.extend(branch)
        tmp[-1] = KSEMI
        true = tmp
    else:
        true = false
        false = []
    true_end = cdtn_len + len(true)
    dispatcher((true, mvi[cdtn_len: true_end], mvb[cdtn_len:true_end]))
    dispatcher((false, mvi[true_end:], mvb[true_end:]))
    
ANYwCOLO = ANY | {KCOLO}
ANYwCOLOwU = ANYwCOLO | {KUNARY, TMPS}
def verify_operation(exp): 
    mask, idxs, ends = exp
    p, l = 1, len(mask)
    curr = mask[0]
    if curr in ANYwCOLOwU: pass
    else: raise Exception(0xE0, idxs[0], ends[0])

    while p < l:
        next = mask[p]
        if curr in ANY:
            if next in {KBINARY, KCOLC, KSEMI, KQ, TMPA, TMPS, KCOMM}: pass
            else: raise Exception(0xE0, idxs[p], ends[p])
        elif curr == KUNARY:
            if not next in ANYwCOLO:   raise Exception(0xE0, idxs[p - 1], ends[p])
        elif curr == KBINARY:
            if not next in ANYwCOLOwU: raise Exception(0xE0, idxs[p - 1], ends[p])
        elif curr == KCOLO:
            if not next in ANYwCOLOwU: raise Exception(0xE0, idxs[p - 1], ends[p])
        elif curr == KCOLC:
            if not next in {KBINARY, KCOLC, KSEMI, KCOMM, KQ}: raise Exception(0xE0, idxs[p - 1], ends[p])
        elif curr == TMPS:
            if mask[p-2] == KATOM and not next in {KSEMI, KBINARY, KCOLC, KQ, KCOMM,}: raise Exception(0xE1, idxs[p - 2], ends[p])
            elif next != KATOM: raise Exception(0xE1, idxs[p - 1], ends[p])

        if next == KSEMI or next == KQ or next == KCOMM:
            break
        p += 1
        curr = next

def handle_header(buf_exp):
    mask, idxs, ends = buf_exp
    p = 1
    curr = mask[0]
    while p < len(mask):
        next = mask[p]
        if curr == KMTFD:
            if next != HEDR: (0xAF, idxs[1], ends[1])
        else:
            if next == KSEMI:
                break
            if not next in {KATOM, KSTR}: (0xAF, idxs[p - 1], idxs[p])
        p += 1
        curr = next


def handle_decl(buf_exp):
    mask, idxs, ends = buf_exp
    if len(mask) < 3: raise Exception(0xB0, idxs[len(mask)], ends[len(mask)])
    vars, vals = els(mask[1:-1], KDFN, 2, keep=True)
    
        #Verify vars
    nvrs = 0
    p = 1
    curr = vars[0]
    if curr != KATOM: raise Exception(0xB1, idxs[p], ends[p])
    while p < len(vars):
        next = vars[p]
        if curr == KATOM:
            if not next in {KCOMM, KEQ, KSEMI}:
                print("NOPE")
                raise Exception(0xB1, idxs[p + 1], ends[p + 2])
            nvrs += 1
        elif curr == KCOMM:
            if next != KATOM:
                print('NUh-UH')
                raise Exception(0xB1, idxs[p + 1], ends[p + 2])
        if next in {KEQ, KSEMI}:
            break
        p += 1
        curr = next        

    if KDFN == vars[-1]: #Now we have determined state if there is one present.
        vals = *els(vals, KCOMM, keep = True), #Do the heavy stuff here.
        if vals[0]:
            if len(vals) != nvrs: raise Exception(0xB3, idxs[p + 1], ends[-1])
        else: raise Exception(0xB0, idxs[p + 1], ends[p + 1])
        ofst = p + 1
        for val in vals:
            val[-1] = KSEMI #Replace the kept commas.
            verify_operation((val, idxs[ofst: ofst + len(val)], ends[ofst: ofst + len(val)]))
            ofst += len(val)


def handle_call(exp):
    mask, idxs, ends = exp
    p = 1
    curr = mask[0]
    while p < len(mask):
        next = mask[p]
        if curr == KMTFC:
            if not next in {KATOM, KQUIT}: raise Exception(0xA0, idxs[0], ends[1])
        elif curr == KATOM or curr == KQUIT:
            if not next in {KSEMI, KINT, KATOM, KCLN}: raise Exception(0xAC, idxs[p - 1], ends[p])
        elif curr == KCLN:
            if not next in {KINT, KATOM, KCLN, KSEMI}: raise Exception(0xAB, idxs[0], ends[-1])
        if next == KSEMI:
            break
        if p == 7: raise Exception(0xAA, idxs[0], ends[-1])
        p += 1
        curr = next
    
    if mask.count(KCLN) > 2: raise Exception(0xAD, idxs[2], ends[-1])

ATOMwSTR = {KATOM, KSTR}
def handle_for(exp):
    mask, idxs, ends  = exp
    _For       = bytearray()
    _set       = bytearray()
    _at        = bytearray()
    _as        = bytearray()
    _c         = bytearray()
    ca, cn     = 0

    p, l = 1, len(mask)
    curr = mask[0]
    while p < l:
        next = mask[p]
        if curr == KFOR:
            if _For: raise Exception(0x9F, idxs[p - 1], ends[p])
            _c = _For

        elif curr == KSET:
            if len(_For) != 2: raise Exception(0x9F, idxs[p - 1], ends[p])
            if _set: raise Exception(0x9F, idxs[p - 1], ends[p])
            _c = _set

        elif curr == KAT:
            if len(_set) < 2: raise Exception(0x9F, idxs[p - 1], ends[p])
            if _at: raise Exception(0x9F, idxs[p - 1], ends[p])
            _c = _at

        elif curr == KAS:
            if len(_at) < 1: raise Exception(0x9F, idxs[p - 1], ends[p])
            if _as: raise Exception(0x9F, idxs[p - 1], ends[p])
            _c = _as

        #More assertion logic goes here.
        if _c is _For:
            if not next in {KSET, KATOM}: raise Exception(0x9E, idxs[p - 1], ends[p])
        if _c is _at:
            if curr != KAT:
                if curr == KCOMM:
                    if not next in {KINT, KATOM}: raise Exception(0x9E, idxs[p - 1], ends[p])
                    ca += 1
                elif curr in {KATOM, KINT}:
                    if not next in {KCOMM, KAS, KINT, KATOM}: raise Exception(0x9E, idxs[p - 1], ends[p])
            else:
                if not next in {KATOM, KINT}: raise Exception(0x9E, idxs[p - 1], ends[p])
                ca += 1
        elif _c is _as:
            if curr != KAS:
                if curr in ATOMwSTR:
                    if not next in {KSEMI, KCOMM}: raise Exception(0x9E, idxs[p -1], ends[p])
                    cn += 1
                elif curr == KCOMM:
                    if not next in ATOMwSTR: raise Exception(0x9E, idxs[p - 1], ends[p])
            else:
                if not next in ATOMwSTR: raise Exception(0x9E, idxs[p - 1], ends[p])
                cn += 1

        _c.append(curr)
        if next == KSEMI:
            break
        p += 1
        curr = next

    #By now, we have finalized proper segmentation, uniqueness and general typing for most things.
    #So, now me have to actually count those things.
    vals = *els(_set[1:], KCOMM),
    offst = 3
    
    for val in vals:
        verify_operation((val, idxs[offst: offst + len(val)], ends[offst: offst + len(val)]))
        offst += len(val)
    if not (cn == ca == len(vals)): raise Exception(0x90, idxs[0], ends[-1])

def handle_from(exp):
    mask, idxs, ends  = exp
    _For       = bytearray()
    _set       = bytearray()
    _as        = bytearray()
    _c         = bytearray()
    ca, cn     = 0, 0

    p, l = 1, len(mask)
    curr = mask[0]
    while p < l:
        next = mask[p]
        if curr == KFROM:
            if _For: raise Exception(0x9F, idxs[p - 1], ends[p])
            _c = _For

        elif curr == KGET:
            if len(_For) != 2: raise Exception(0x9F, idxs[p - 1], ends[p])
            if _set: raise Exception(0x9F, idxs[p - 1], ends[p])
            _c = _set

        elif curr == KAS:
            if len(_set) < 1: raise Exception(0x9F, idxs[p - 1], ends[p])
            if _as: raise Exception(0x9F, idxs[p - 1], ends[p])
            _c = _as

        #More assertion logic goes here.
        if _c is _For:
            if not next in {KGET, KATOM}: raise Exception(0x9E, idxs[p - 1], ends[p])
        if _c is _set:
            if curr != KGET:
                if curr == KCOMM:
                    if not next in {KINT, KSTR, KATOM}: raise Exception(0x9E, idxs[p - 1], ends[p])
                    ca += 1
                elif curr == KINT:
                    if not next in {KCOMM, KAS, KINT, KATOM, KSEMI}: raise Exception(0x9E, idxs[p - 1], ends[p])
                elif curr == KSTR:
                    if not next in {KCOMM, KAS, KSEMI}: raise Exception(0x9E, idxs[p-1], ends[p])
                elif curr == KATOM:
                    if not next in {KCOMM, KINT, KAS, KSEMI}: raise Exception(0x9E, idxs[p-1], ends[p])
            else:
                if not next in {KATOM, KSTR, KINT}: raise Exception(0x9E, idxs[p-1], ends[p])
        elif _c is _as:
            if curr != KAS:
                if curr in KATOM:
                    if not next in {KSEMI, KCOMM}: raise Exception(0x9E, idxs[p -1], ends[p])
                elif curr == KCOMM:
                    if not next in KATOM: raise Exception(0x9E, idxs[p - 1], ends[p])
                    cn += 1
            else:
                if not next in KATOM: raise Exception(0x9E, idxs[p - 1], ends[p])
                cn += 1

        _c.append(curr)
        if next == KSEMI:
            break
        p += 1
        curr = next

    if cn and not (cn == ca): raise Exception(0x90, idxs[0], ends[-1])

def handle_kws(exp):
    mask, idxs, ends = exp
    if len(mask) < 3: raise Exception(0x9F, idxs[0], ends[1])
    i, l = 2, len(mask) - 1
    curr = mask[1]
    if curr != KATOM: raise Exception(0xB1, idxs[1], ends[1])
    while i < l:
        next = mask[i]
        if curr == KATOM:
            if not next in {KCOMM, KSEMI}: raise Exception(0x9E, idxs[i - 1], ends[i])
        elif curr == KCOMM:
            if next != KATOM: raise Exception(0x9E, idxs[i - 1], ends[1])
        if next == KSEMI:
            break
        i += 1 #I WILL NOT FORGET THIS TIME.
        curr = next

def handle_motifd(exp):
    mask, idxs, ends = exp
    if len(mask) > 3: raise Exception(0xA6, idxs[3], ends[-2])
    if not mask[1] in {KATOM, KSEMI}: raise Exception(0xA0, idxs[1], ends[1])
    if len(mask) == 3 and mask[2] != KSEMI: raise Exception(0xA6, idxs[2], ends[2])
    
def handle_assn(buf_exp):
    mask, idxs, ends = buf_exp
    
    p, nvrs = 1, 0
    curr = mask[0]
    while True:
        next = mask[p]
        if curr == KATOM:
            if next in {KCOMM, AUGA, KEQ}: nvrs += 1
            else: raise Exception(0x9E, idxs[p - 1], ends[p])
            
        elif curr == KCOMM:
            if next != KATOM: raise Exception(0x9E, idxs[p - 1], ends[p])
        
        p += 1
        curr = next

        if next in {KEQ, AUGA}:break
    
    vals = list(els(mask[p:], KCOMM, keep=True))

    offst = p
    for val in vals:
        verify_operation((val, idxs[offst: offst + len(val)], ends[offst: offst + len(val)]))
    else:
        if len(vals) != nvrs: raise Exception(0x90, idxs[0], ends[-1])


def handle_compound(buf_exp):
    mask, idxs, ends = buf_exp
    if len(mask) < 4: raise Exception(0x9F, idxs[-3])
    
    if mask[-2] != BRC: raise Exception(0xF0, idxs[-3], ends[-1])
    closesOnSemi = mask[-3] == KSEMI

    if not closesOnSemi: mask[-2] = KSEMI


    ofst = 0
    for stmnt in els(mask[1:-2 if closesOnSemi else -1], delim=b';', keep=True):
        le = len(stmnt)
        slc = slice(ofst, ofst + le)
        ofst += le

        dispatcher((stmnt, idxs[slc], ends[slc]))

def handle_compound_close(pkg):
    bits, idxs, ends, *_ = pkg
    if len(bits) > 2: raise Exception(0xF0, idxs[1], ends[-2])