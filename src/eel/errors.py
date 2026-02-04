from .BaseError import BaseError as e
from .codepoints import *

#Motif Errors:
class Illicit_Motif_Name(e, code=0xA0, msg='Thou shalt not use this in thy namespaces!', base='MTF'): pass
class ILLICIT_HEADER(e, code=0xAF, msg='Thy scroll shall not be recognized.', base='mtf'): pass
class MOTIF_CALL_NONEXISTANT(e, code=0xAA, base='mtf', msg='Upon whom thou hast calleth, he respondeth not.'): pass
class MOTIF_CALL_BAD_INDICE(e, code=0xAB, base='mtf', msg='From whence doth thou calleth this?'): pass
class MOTIF_META_NOTICE (e, code=0xA6, base='mtf', msg='Non-header motif metadata is supported yet.'): pass


#Operation Errors:
class NON_ATOMIC_OPERATION(e, code=0xE0, base='OPR', msg='This hath not a place here. Much like thyself.'): pass
class ILLICIT_TEMPORAL(e, code=0xE1, base='OPR', msg='Thy sin is black indeed.'): pass
class EXPRESSION_FAILURE(e, code=0xEF, base='etf', msg='Old wine hath not a place in new skins. Neither doth these live in harmony.'): pass

#Variable Errors.
class NON_EXISTANT_VARIABLE(e, code=0xB0, base='var', msg='For whom doth ye call?'): pass
class NON_VARIABLE_DECLARATION(e, code=0xB1, base='var', msg='This is abhorent! HANG THE HERETIC!!'): pass
class INEQUAL_VARIABLE_DECLARATION(e, code=0xB3, base='var', msg='The scales are unbalanced. The council rebuke you!'): pass

#Misc.
class NO_SUBSTANCE(e, code=0x9F, base='err', msg='The council expected substance. Ye shall pay with thy head!'): pass
class BAD_SUBSTANCE(e, code=0x9E, base='err', msg='BEGONE WITH THY FILTH!'): pass
class UNBALANCED_SUBSTANCE(e, code=0x90, base='err', msg='Thou art unjust. Unjust indeed.'): pass
class LOOP_DETECTION_ERROR(e, code=0x9A, base='ILG', msg='Foolish men repeat their follies. Thou hasten to join them.'): pass

#Compounds
class UNBALANCED(e, code=0xF0, base='exp', msg='There exists no end to thy tongue!'): pass