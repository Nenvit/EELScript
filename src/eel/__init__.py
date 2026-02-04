from . import BaseError, errors
from .runtime import eval, components
from .transformer import lexer, linter, tokens, lex
from . import glbls, vm
from .thoughts import *

#And now for these...
vfile = components.VFile
verify = lexer.verify_statement
parse = tokens.parse_ready
els = glbls.els
delim = glbls.MultiDelim
Machine = vm.Machine
typeint = eval.typeint
examine = linter.examine

__all__ = [
    "examine", "AutoThought", 'Thought', 'MicroThought', 'DeepThought', 'Tubeel', 'Colony', 'Eel',
    'vfile', 'lex','verify', 'parse', 'els', 'delim', 'Machine', 'typeint',
]