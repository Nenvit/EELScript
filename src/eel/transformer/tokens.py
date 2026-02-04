from io import UnsupportedOperation
from ..glbls import TKN, OPS_CODE_MAP
ALLOWED, delimq = { _ for _ in b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-_." }, {34, 39, 96}
ENCODING = 'ascii'

def parse_ready(stream):
    try: ci = ord(stream.read(1))
    except TypeError: raise FileNotFoundError(f"Can not parse from empty files.")
    except AttributeError: raise FileNotFoundError(f"Can not parse from {type(stream)}.")
    except UnsupportedOperation: raise UnsupportedOperation(f"Can not parse from unreadable file. Please make sure that the file input is readable.")

    buf_tok = bytearray()
    buf_str = bytearray()
    buf_exp = bytearray()
    lyr = 0

    while True:

        if ci == 123:   
            
            while True:
                try: ci = ord(stream.read(1))
                except TypeError: break

                if ci == 125: break

        elif ci in delimq:
            string = ci
            buf_str.append(ci)
            
            while string:
                try: ci = ord(stream.read(1))
                except TypeError:
                    buf_str.append(string)
                    break

                if ci == 92:
                    try: ci = ord(stream.read(1))
                    except TypeError: break
                    if ci in {110, 78}:   buf_str.extend(b'\\n')
                    elif ci in {84, 116}: buf_str.extend(b'\\t')
                    else: buf_str.append(ci)
                    continue

                elif ci == 10: buf_str.extend(b'\\n')
                elif ci == 9:  buf_str.extend(b'\\t')
                elif ci == 0:  buf_str.extend(b'\\0')
                elif ci == 13: continue
                elif ci == string:
                    buf_str.append(ci)
                    break

                buf_str.append(ci)
            
            if len(buf_str) > 2:
                buf_exp.extend(buf_str)
                buf_exp.extend(TKN)
                buf_str.clear()
        
        elif ci in OPS_CODE_MAP:
            buf_exp.append(ci)

            if ci == 59: 
                yield bytes(buf_exp)
                buf_exp.clear()

            POSSIBLE= OPS_CODE_MAP[ci]
            try: ci = ord(stream.read(1))
            except TypeError: break
            
            if ci in POSSIBLE:
                buf_exp.append(ci)
                try: ci = ord(stream.read(1))
                except TypeError: break
                
            buf_exp.extend(TKN)
            continue

        elif ci in ALLOWED:
            buf_tok.append(ci)

            while ci:
                try: ci = ord(stream.read(1))
                except TypeError: break

                if ci in ALLOWED: buf_tok.append(ci)
                else: break
            
            if buf_tok:
                buf_exp.extend(buf_tok)
                buf_exp.extend(TKN)
                buf_tok.clear()
            continue


        try: ci = ord(stream.read(1))
        except TypeError: break


    if len(buf_str) > 2:
        buf_exp.extend(buf_str)
        buf_exp.extend(TKN)

    if len(buf_tok):
        buf_exp.extend(buf_tok)
        buf_exp.extend(TKN)

    if buf_exp:
        yield bytes(buf_exp)