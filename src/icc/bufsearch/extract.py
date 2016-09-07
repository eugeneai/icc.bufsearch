import olefile
import io

def extract_ole(buffer, pos, pattern=None):
    if type(pos) in [list, tuple]:
        rc = []
        for i, p in enumerate(pos):
            if pattern is None:
                rc.append(extract_ole(buffer, p))
            else:
                extract_ole(buffer, p, str(i)+pattern)
        return rc

    i = io.BytesIO(buffer[pos:])
    olefile.isOleFile(i)
    if pattern is None:
        o=io.BytesIO()
    else:
        o=open(pattern,"wb")
    olei=olefile.OleFileIO(i, write_mode=False)
    oleo=olefile.OleFileIO(o, write_mode=True)
    for name in olei.listdir():
        si = olei.openstream(name)
        data = si.read()
        oleo.write_stream(name, data)
    olei.close()
    oleo.close()
    if pattern is None:
        return oleo.getbuffer()
