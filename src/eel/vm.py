from . import transformer, glbls, BaseError, errors
from . import runtime
import os
import json

GOTH = "\033[12m"
RED = "\033[31m"
RESET = '\033[0m'
GREEN = '\033[32m'

def path_of(s):
    s = os.path.expandvars(s)
    s = os.path.expanduser(s)
    s = os.path.normpath(s)
    return s

SRCB = bytes(glbls.SRC)
def sniff(fio):
    *_, ext = fio.name.split('.')
    fn = '.'.join(_)
    sniffed   = fn + '.txt'
    cp = os.getcwd()

    try:
        os.chdir('__sniffed')

        if os.path.isfile(sniffed): os.remove(sniffed)

        cfile = open(sniffed, 'at')

        try:
            _ = runtime.unpackage.motif_table(fio)
            for status, *_, prtty in runtime.unpackage.brackethatch(fio, SRCB):
                prtty = prtty.replace(b'\0', b' ').decode('ascii')
                status_code, *_, line = status

                if status_code == 0x10:
                    cfile.write(f"{f"{line:02d}".ljust(6)} | {prtty}\n")
                else:
                    cfile.write(str(BaseError[status_code](prtty, status)))
        finally:
            cfile.close()

    except Exception as e: return e
    finally: os.chdir(cp)

class BaseMachine:
    VIRTUAL = False
    HOME    = os.getcwd()
    
    def __init__(self, src, defer=True, **kwargs):
        assert isinstance(src, str), 'Only strings are allowed as sources.'
        self.vars    = {b'rawrFarts':2019} #A canonically valid variable. Don't question.
        self.subs    = dict()
        self.out     = set()
        self.fs      = [b'__script']
        self.motif   = b'__script'
        self.count   = {b'__script':0}
        object.__setattr__(self, 'src', os.path.join(self.HOME, path_of(src)))
        *__, file    = src.split(os.sep)
        *_, ext      = file.split('.')
        file_name    = '.'.join(_)
        object.__setattr__(self, 'name', file_name)
        object.__setattr__(self, 'bh', file_name + '.bh')

        if defer: return
        else: self.loads(src)

    def __init_subclass__(cls, VIRTUAL=False):
        super().__init_subclass__()
        if VIRTUAL: object.__setattr__(cls, 'VIRTUAL', True)
    
    @classmethod
    def __setattr__(cls, name, value): pass

    def __setattr__(self, name, value):
        if name in {'src', 'bh', 'name'}: return
        else: object.__setattr__(self, name, value)
 
    @classmethod
    def sniff(cls, src):
        full_available_path = os.path.join(cls.HOME, path_of(src))
        cp = os.getcwd()
        to_sniff = []
        try:
            if not os.path.exists(full_available_path): raise FileNotFoundError()

            *__, file = full_available_path.split(os.sep)
            fpath = (os.sep).join(__)
            os.chdir(fpath)

            if os.path.isdir(full_available_path):
                os.chdir(full_available_path)
                for file in os.listdir():
                    if file.endswith('.eel'):
                        cls.loads(file)
                else: to_sniff = [bracket_hatch for bracket_hatch in os.listdir() if bracket_hatch.endswith('.bh')]

            elif os.path.isfile(file):
                *_, ext = file.split('.')
                file_name = '.'.join(_)
                bh = file_name + '.bh'

                if os.path.isfile(bh): to_sniff = [bh]
                else:
                    cls.loads(full_available_path)
                    to_sniff = [bh]
            
            for sniff_this in to_sniff:
                with open(sniff_this, 'rb') as under_sniffer:
                    sniff(under_sniffer)
                    
        except BaseException as e: return e #Let's not immediately show traceback yet.
        finally: os.chdir(cp)

    @classmethod
    def loads(cls, path):
        full_available_path = os.path.join(cls.HOME, path_of(path))
        cp = os.getcwd()
        try:
            if not os.path.exists(full_available_path): raise FileNotFoundError()

            *__, file = full_available_path.split(os.sep)
            fpath = (os.sep).join(__)
            os.chdir(fpath)

            if os.path.isdir(full_available_path):
                os.chdir(full_available_path) 

                file_name = '__script'
                bh = file_name + '.bh'
                if      os.path.isfile('__script.eel'):
                    if  os.path.isfile(bh) and \
                        os.path.getmtime('__script.eel') ==\
                        os.path.getmtime(bh):     return
                    
                    with open('__script.eel') as script: transformer.lex(script)

                elif   os.path.isfile('__script.bh'):
                    if os.path.getmtime(bh) == os.path.getmtime('__script.bh'): return
                    else:
                        with open('__script.bh') as script: transformer.lex(script)

                else: raise f'EELScript could not find [__script] in {full_available_path}'

            elif os.path.isfile(file):
                *_, ext = file.split('.')
                file_name = '.'.join(_)
                bh = file_name + '.bh'

                if ext == 'eel':
                    if  os.path.isfile(bh) and  \
                        os.path.getmtime(file) ==\
                        os.path.getmtime(bh):     return

                    with open(file, 'rb') as script: transformer.lex(script)

                elif ext == 'bh': return
                else: raise FileNotFoundError()
                    
        except BaseException as e: return e #Let's not immediately show traceback yet.
        finally: os.chdir(cp)

    def sub(self, src):
        return Machine(src)

    def load(self):
        BaseMachine.loads(self.src) #Ensure absolute root handles loading.

    def defvar(self, var, value):
        self.vars[var] = value

    def pullvar(self, var):
        self.out.remove(var)

    def pushvar(self, var):
        self.vars[var]
        self.out.add(var)
    
    def delvar(self, var):
        if var in self.vars and var != 'rawrFarts': del self.vars[var] #Protect the canon!!
        if var in self.out: self.out.remove(var)

    def run(self, strict=False, return_dict=True, json_fout=False, var_fout=False, **kwargs):
        try:
            if self.VIRTUAL: pass #To be implemented by the user.
            else:
                cp = os.getcwd()
                try: 
                    if os.path.isdir(self.src):
                        os.chdir(self.src)
                        assert (os.path.exists('__script.bh')), 'You must must load a directory in order to run it. Use the instance method \'.load()\' to load the directory.'
                        runtime.engage(self, dir=True, strict=strict)
                    elif os.path.isfile(self.src):
                        assert (os.path.exists(self.bh)), 'You must must load a file in order to run it. Use the instance method \'.load()\' to load the file.'
                        runtime.engage(self, dir=False, strict=strict)
                finally: os.chdir(cp)
                try:

                    if json_fout:
                        with open(self.name + '.json', 'wt') as fout:
                            out = {key.decode('ascii'):json.loads(self.vars[key].decode('ascii') if isinstance(self.vars[key], bytes) else str(self.vars[key])) for key in self.out}
                            json.dump(out, fout, indent=4)
                    if var_fout:
                        varname = self.name + '.var'
                        if os.path.isfile(varname): os.remove(varname)
                        with open(self.name + '.var', 'at') as fout:
                            for key in self.out:
                                item = self.vars[key]
                                fout.write(f"{key.decode('ascii')!r}, {item.decode('acii') if isinstance(item, bytes) else item!r}\n")
                    if return_dict: return {key:self.vars[key] for key in self.out}
                except Exception as e: return e
        except KeyboardInterrupt: pass
        except Exception as e: print(e)


class Machine(BaseMachine, VIRTUAL=False):
    def __init__(self, src):
        super().__init__(src, defer=False)

class SubMachine(Machine):
    def run(self): super().run(strict=True)