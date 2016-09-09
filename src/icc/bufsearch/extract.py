import olefile
import io
import pkg_resources
from icc.bufsearch import Raita


def resource(filename):
    return pkg_resources.resource_filename("icc.bufsearch",
                                           "../data/" + filename)


TEMPLATES = {
    "doc": "template-lo.doc",
    "xls": "template-lo.xls",
    "ppt": "template-lo.ppt"
}

STREAMMAP = {"WordDocument": "doc"}

ZIP_EDIR_SIGNATURE = b"PK\x05\x06"
ZIP_SIGNATURE = b"PK\x03\x04"
R_ZIP_EDIR_SIGNATURE = Raita(ZIP_EDIR_SIGNATURE)
ZIP_ADD = 18  # bytes


def extract_ole(buffer, pos, pattern=None):
    if type(pos) in [list, tuple]:
        rc = []
        for i, p in enumerate(pos):
            if pattern is None:
                rc.append(extract_ole(buffer, p))
            else:
                extract_ole(buffer, p, str(i) + pattern)
        return rc

    i = io.BytesIO(buffer[pos:])
    if not olefile.isOleFile(i):
        raise ValueError("BAD OLE file")
    olei = olefile.OleFileIO(i, write_mode=False)
    listdir = olei.listdir()
    print(listdir)
    for k, ext in STREAMMAP.items():
        print(k)
        if [k] in listdir:
            break
    else:
        raise RuntimeError("format is not supported yet")
    template = TEMPLATES[ext]
    if pattern is None:
        _data = open(resource(template), "rb").read()
        o = io.BytesIO(_data)
    else:
        # TODO Copy template at first
        o = open(pattern, "wb")
    oleo = olefile.OleFileIO(o, write_mode=True)
    for name in listdir:
        si = olei.openstream(name)
        data = si.read()
        oleo.write_stream(name, data)
    olei.close()
    oleo.close()
    if pattern is None:
        return oleo.getbuffer()


def extract_zip(buffer, pos, pattern=None):
    if type(pos) in [list, tuple]:
        rc = []
        for p in pos:
            rc.append(extract_zip(buffer, p, pattern=pattern))
        return rc
    start_sig = buffer[pos:pos + 4]
    if start_sig != ZIP_SIGNATURE:
        print(repr(start_sig), ZIP_SIGNATURE)
        raise ValueError("no start signatore found")
    ps, _ = R_ZIP_EDIR_SIGNATURE.search(
        buffer, start=pos + len(ZIP_SIGNATURE), count=1)
    if ps is None:
        raise RuntimeError(_)
    epos=ps[0]+len(ZIP_EDIR_SIGNATURE)+ZIP_ADD
    return buffer[pos:epos]
