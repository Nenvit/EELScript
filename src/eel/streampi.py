def readuntil(f, d=b';', c=4096, keep=False, skip=True):
    buf = bytearray()
    stack = bytearray()
    l = len(d)
    pos = f.tell()
    chunk = f.read(c)
    isText = isinstance(chunk, str)
    if isText:
        chunk = bytes(chunk, 'ascii')
    while chunk:
        buf.extend(chunk)
        mv = memoryview(buf)
        idx = buf.find(d)
        if idx >= 0:
            idx += l if keep else 0
            stack.extend(mv[:idx])
            f.seek(pos + (idx + l if skip else idx))
            return bytes(stack)
        else:
            stack.extend(mv)
            del mv, buf[:]
        pos = f.tell()
        chunk = f.read(c)
        if isText:
            chunk = bytes(chunk, 'ascii')
    if stack:
        return bytes(stack)

def readeach(f, d=b';', c=4096, keep=False):
    buf = bytearray()
    stack = bytearray()
    l = len(d)
    chunk = f.read(c)
    isText = isinstance(chunk, str)
    if isText:
        chunk = bytes(chunk, 'ascii')
    while chunk:
        buf.extend(chunk)
        for i in range(buf.count(d)):
            idx = buf.find(d) + (l if keep else 0)
            stack.extend(buf[:idx])
            if len(stack):
                yield bytes(stack)
                del stack[:]
            del buf[:idx if keep else idx + l]
        else:
            stack.extend(buf)
            del buf[:]
        chunk = f.read(c)
        if isText:
            chunk = bytes(chunk, 'ascii')
    if stack: #Technically not required, since it does not contain the deliminater.
        yield bytes(stack)


def EachByByte(f, d=b'\n', keep=False):
    stack = bytearray()
    byte = f.read(1)
    isText = isinstance(byte, str)
    if isText:
        byte = bytes(byte, 'ascii')
    while byte:
        if byte == d:
            if keep:
                stack.append(byte[0])
            yield bytes(stack)
        else:
            stack.append(byte[0])
        byte = f.read(1)
        if isText:
            byte = bytes(byte, 'ascii')
    if stack: #Technically not required, since it does not contain the deliminater.
        yield bytes(stack)

def EachByByteWindow(f, d=b';\n', c=1028, keep=False):
    l = len(d)
    assert l < c, f"Delimiter Size too big ({str(l)}): {repr(d)}"
    if isinstance(d, bytes):
        delim = bytearray(d)
    elif isinstance(d, str):
        delim = bytearray(d, 'ascii')
    delimv = memoryview(delim)
    buf_ = bytearray()
    stack_ = bytearray()
    chunk = f.read(c)
    isText = isinstance(chunk, str)
    if isText:
        chunk = bytes(chunk, 'ascii')
    start = end = 0
    while chunk:
        del buf_[:]
        stackview = memoryview(stack_)
        buf_.extend(stackview[-l:])
        del stackview, stack_[-l:]
        buf_.extend(chunk)
        chunk = f.read(c)
        if isText:
            chunk = bytes(chunk, 'ascii')
        mv = memoryview(buf_)
        l2 = len(buf_)
        start = end =0
        while end < l2:
            end += 1
            window = mv[start : end + l]
            if window == delimv:
                start = end + l
                end += l
                if keep:
                    stack_.extend(window)
                yield bytes(stack_)
                del stack_[:]
                continue
            stack_.append(window[0])

def EachFromFile(f, d=b'\n', keep=False):
    data = bytes(f.read())
    return (segment for segment in data.split(d) if segment) if not keep else (segment + d for segment in data.split(d) if segment)
 