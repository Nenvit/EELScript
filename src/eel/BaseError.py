class BaseError(BaseException):
    code_map = {}
    msg_hdr = "[{base} {cde:X}]: {msg}"
    msg_bdy = "{pretty_slice} (Line: {lne}, Column {cln})"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
        
        setattr(cls, 'code', kwargs['code'])
        BaseError.code_map[kwargs['code']] = cls

        cls.msg_hdr = BaseError.msg_hdr.format(base=kwargs['base'].upper(), cde=cls.code, msg=kwargs['msg'])
 
    #Now, time for the standard format.
    def __init__(self, prtty, mtda):
        _, START, STOP, LINE = mtda
        # Reference: f"{f'{LINE:02d}'.ljust(6)} | {prtty}" #-> Len 9 up to the actual expression.
        self.ptr = f"{'|': >8} {f"{('^' * (STOP - START)):~>{START}}".ljust(len(prtty), '~')}\n"
        self.msg = f"{self.msg_hdr} {self.msg_bdy.format(pretty_slice=prtty[START: STOP].replace(b'\0', b' ').decode('ascii'), lne=LINE, cln=START)}\n"

    def __str__(self):
        return self.ptr + self.msg
    
    def __repr__(self):
        return self.msg


    @classmethod
    def __class_getitem__(cls, code):
        return BaseError.code_map[code]