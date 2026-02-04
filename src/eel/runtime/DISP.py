from . import eval
from .. import glbls
from ..codepoints import *
#More imports if needed.
CDTN_DELIM = glbls.MultiDelim(b'?', b':')

@eval.debug
def register(package, vm):
    bits = package[0]
    if   bits[1] == KSEMI: motif = b'__script'
    elif bits[1] == HEDR : return  b'__script'
    else:                motif = package[3][1]
    if motif != vm.motif: return b'%%next'

@eval.debug
def call(package, vm):
    bit   = package[0][1]
    if   bit == KATOM: motif = package[3][1]
    elif bit == KSEMI: motif = b"__script"
    elif bit == KQUIT: return b'%%quit'

    if motif == vm.motif:
        if  motif == b'__script': return b'%%quit'
        elif  vm.count[motif] > 2007: 
            raise Exception(0x9A, package[1][1], package[2][-1])
        else: vm.count[motif] += 1
        return motif
    elif motif == b'->' or motif == b'return':
        try: return vm.fs[-2]
        except: return b"__script"
    elif motif == b'<-' or motif == b'again':
        try: return vm.fs[-1]
        except: return b"__script"
    else: return motif

@eval.debug
def adopt(pckg, vm):
    sub     = vm.sub(pckg[3][1].decode('ascii'))
    inp     = sub.run()
    vm.vars.update(inp)
    vm.out.update(inp)
    del inp

@eval.debug
def conditional(pkg, vm):
    qidx = slice(0, glbls.find(pkg[0], KQ))
    cidx = -1
    lyr  =  0
    for idx, tkn in enumerate(pkg[0]):
        if   tkn == KQ  : lyr += 1
        elif tkn == BRO : lyr += 1
        elif tkn == BRC : lyr -= 1
        elif tkn == KCLN: lyr -= 1
        if   lyr == 0 and tkn == KCLN: 
            cidx = idx
            break

    condition = (pkg[0][qidx], pkg[1][qidx], pkg[2][qidx], tuple(map(lambda x: eval.discern_var(x, vm), pkg[3][qidx])))
    true_path = slice(qidx.stop + 1, cidx if cidx > -1 else None)
    false_pth = slice(cidx + 1 if cidx > -1 else len(pkg[0]), None)
    print(f"Paths present ({cidx}):", f"[T]: {pkg[3][true_path]} {true_path.start, true_path.stop}", f"[F]: {pkg[3][false_pth]} {false_pth.start, false_pth.stop}", sep='\n\t')
    cdtn = eval.collapse(condition)
    print(f"Path taken: {bool(cdtn)}")
    if cdtn: return execute(tuple(morsel[true_path] for morsel in pkg), vm)
    else: return execute(tuple(morsel[false_pth] for morsel in pkg), vm)

@eval.debug
def express(pkg, vm): #Just a hot wrapper.
    eval.collapse((*pkg[:3], tuple(map(lambda x: eval.discern_var(x, vm), pkg[3]))))

@eval.debug
def define(pkg, vm):
    bits, idxs, ends, tkns = pkg
    eidx = glbls.find(bits, KEQ)
    vars, val_masks = tuple(_[0] for _ in glbls.els(tkns[1:eidx], b',')), tuple(_ for _ in glbls.els(bits[eidx + 1:-1], KCOMM, keep=True))
    offset = eidx + 1
    vals = []
    for bit_seg in val_masks:
        slc = slice(offset, offset + len(bit_seg))
        vals.append(eval.collapse((bit_seg, idxs[slc], ends[slc], map(lambda x: eval.discern_var(x, vm), tkns[slc])) ))
        offset += len(bit_seg)
    print(f"VALS: {vals}")
    var_out = tkns[0] == b'$'
    for var, val in zip(vars, vals):
        vm.vars[var] = val if offset else 0
        if var_out: vm.out.add(var)

@eval.debug
def delvar(pkg, vm):
    bitmask, length, line, usable = pkg
    p = 1
    while p < len(bitmask):
        if bitmask[p] == KATOM:
            if usable[p] in vm.vars: vm.elvar(usable[p])
            else: raise Exception(0xB0, pkg[1][p], pkg[2][p], 0)
        p+=1

@eval.debug
def sniff(pkg, vm):
    *_, usable = pkg
    p = 1
    while p < len(usable):
        if isinstance(usable[p], bytes):
            type(vm).sniff(usable[p])
        p+=1

@eval.debug
def dot(pkg, vm):
    bitmask, length, line, usable = pkg
    p = 1
    while p < len(bitmask):
        if bitmask[p] == KATOM:
            if usable[p] in vm.vars: vm.out.remove(usable[p])
        p+=1
    
@eval.debug
def out(pkg, vm):
    bitmask, length, line, usable = pkg
    p = 1
    while p < len(usable):
        if bitmask[p] == KATOM:
            if usable[p] in vm.vars: vm.out.add(usable[p])
            else: raise Exception(0xB0, pkg[1][p], pkg[2][p], 0)
        p+=1

@eval.debug
def reassign(pkg, vm):
    bits, idxs, ends, tkns = pkg
    qidx = glbls.find(bits, KEQ)
    vars = [slc[0] for slc in glbls.els(tkns[:qidx], KCOMM)]
    val_masks = glbls.els(bits[qidx + 1:], KCOMM)
    offset = qidx + 1
    vals = []
    for bit_seg, var in zip(val_masks, vars):
        slc = slice(offset, offset + len(bit_seg))
        vm.vars[var] = eval.collapse((bit_seg, idxs[slc], ends[slc], map(lambda x: eval.discern_var(x, vm), tkns[slc])) )
        offset += len(bit_seg)

@eval.debug
def augassign(pkg, vm):
    bits, idxs, ends, tkns= pkg
    aidx = glbls.find(bits, AUGA)
    operator = tkns[aidx][:1]
    vars = *(_[0] for _ in glbls.els(tkns[:aidx], b',')),
    vals = *glbls.els(bits[aidx + 1:], KCOMM, keep=True),
    offset = aidx + 1
    try: 
        for var, val in zip(vars, vals):
            slc = slice(offset, len(val) + offset)
            augval = ((KATOM, KBINARY, *val), (0, 0, *idxs[slc]), (-1, -1, *ends[slc]), (eval.discern_var(var, vm), operator, *map(lambda x: eval.discern_var(x, vm), tkns[slc])))
            vm.vars[var] = eval.collapse(augval)
            offset += len(val)
    except:
        raise Exception(0xB1, 0, -1)

DELIM = glbls.MultiDelim(KSET, KGET, KAT, KAS)

@eval.debug
def for_eel(pkg, vm):
    bits, idxs, ends, usable = pkg
    if not usable[1] in vm.vars: raise Exception(0xB0, pkg[1][1], pkg[2][1])
    sidx                         = bits.index(KSET) + 1
    _, thts, locations, allnames = glbls.els(usable, DELIM)
    thts                         = glbls.els(bits[sidx: bits.index(KAT)], KCOMM, keep=True)
    locations                    = [eval.discern_var(pos, vm) for pos in 
                                    [loc for loc in glbls.els(locations, KCOMM)]]
    names                        = glbls.els(allnames, KCOMM)

    for thought, location, name in zip(thts, locations, names):
        slc = slice(sidx, sidx + len(thought))
        vm.vars[usable[1]].write(thought=eval.collapse(thought, idxs[slc], ends[slc], map(lambda x: eval.discern_var(x, vm), usable[slc])),
                                  loc=(location[0], *location[:-1], 0, 0, 0), dir=(*location[-1], 1), id=name.decode('ascii'))
        sidx += len(thought)

@eval.debug
def from_eel(pkg, vm):
    *_, usable = pkg
    if not usable[1] in vm.vars: raise Exception(0xB0, pkg[1][1], pkg[2][1])
    _, locations, *allnames = glbls.els(usable, DELIM)
    locations  = [eval.discern_var(pos, vm) for pos in 
                                    [loc for loc in glbls.els(locations, KCOMM)]]
    if allnames: names = glbls.els(allnames, KCOMM)

    p = 0
    for location in locations:
        thought = vm[usable[1]].read(thought=location[0], loc=(location[0], *location[:-1], 0, 0, 0), dir=(*location[-1], 1))
        if names:
            vm.vars[names[p]] = thought
        else: vm.vars[thought.id] = thought
        p += 1

@eval.debug
def execute(pkg, vm): return route(pkg)(pkg, vm)

@eval.debug
def route(inp):
    print(inp)
    bits, *_, tkns = inp
    if not bits: return

    tkn = tkns[0]
    key_bit = bits[0]
    if   key_bit == KMTFD   : return register
    elif key_bit == KMTFC   : return call
    elif key_bit == KDFN    : return define
    elif key_bit == KKW     : 
        if   tkn == b'.'    : return dot
        elif tkn == b'out'  : return out
        elif tkn == b'del'  : return delvar
        elif tkn == b'adopt': return adopt
        elif tkn == b'sniff': return sniff
    elif key_bit == KFOR    : return for_eel
    elif key_bit == KFROM   : return from_eel
    elif KEQ  in bits       : return reassign
    elif AUGA in bits       : return augassign
    elif KQ   in bits       : return conditional
    else                    : return express  