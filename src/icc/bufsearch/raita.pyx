cdef extern from "Python.h":
    object PyUnicode_FromStringAndSize(char *, int)
    object PyUnicode_FromString(char *)
    char *PyUnicode_AsUTF8(object o)

    object PyInt_FromLong(long ival)
    long PyInt_AsLong(object io)

    object PyList_New(int len)
    int PyList_SetItem(object list, int index, object item)

    void Py_INCREF(object o)

    object PyObject_GetAttrString(object o, char *attr_name)
    object PyTuple_New(int len)
    int PyTuple_SetItem(object p, int pos, object o)
    object PyObject_Call(object callable_object, object args, object kw)
    object PyObject_CallObject(object callable_object, object args)
    int PyObject_SetAttrString(object o, char *attr_name, object v)

    unsigned int PyBytes_Size(object o)
    char *PyBytes_AsString(object o)
    void PyMem_RawFree(void *p)
    void* PyMem_RawMalloc(unsigned int n)

from libc.string cimport strcat, strncat, \
    memset, memchr, memcmp, memcpy, memmove

cdef extern from "signal.h":                # Used for debugging C seaside.
    ctypedef unsigned int signal_t
    void c_raise "raise" (signal_t signal)

cdef enum:
    SIGINT = 2

cdef char * _s(o):
    return PyUnicode_AsUTF8(o)

cdef _u(const char * s):
    if s!=NULL:
        return PyUnicode_FromString(s)
    else:
        return u"<NULL>"

cdef class Raita:
    """Search buffer for a string patterns with
    Raita algorithm.
    """
    cdef unsigned int bmBc[256]
    cdef unsigned int rel_pos
    cdef unsigned int middle_pos
    cdef unsigned char first_char
    cdef unsigned char last_char
    cdef unsigned char middle_char
    cdef unsigned char * pattern
    cdef unsigned int multibuffer
    cdef unsigned int pattern_size

    def __cinit__(self):
        self.rel_pos=0
        self.middle_pos=0
        self.pattern=NULL
        self.pattern_size=0
        self.multibuffer=0

    def __init__(self, pattern, multibuffer=False):
        self.set_pattern(pattern)
        self.multibuffer=multibuffer
        self.reset()

    cdef preBmBc(self):
        cdef unsigned char * bytes
        cdef unsigned int size
        cdef unsigned int size1
        cdef unsigned int b[256]

        bytes = self.pattern
        size = self.pattern_size
        size1 = size - 1

        for i in range(256):
            self.bmBc[i]=size
        for i in range(size1):
            self.bmBc[bytes[i]]=size1 - i;

        #for i in range(32):
        #    b[i]=self.bmBc[i+97]
        #print (b)
        self.first_char=bytes[0]
        self.last_char=bytes[size1]
        self.middle_pos=size // 2
        self.middle_char=bytes[self.middle_pos]

    cpdef set_pattern(self, value):
        cdef unsigned char * s
        cdef unsigned int size
        #if type(value) == type(u""):
        #    size = unicode
        #    self._pattern=_s(value)
        if type(value) == type(b""):
            self.pattern_size = size = PyBytes_Size(value)
            s = <unsigned char *>PyBytes_AsString(value)
        else:
            raise ValueError("argument must be a bytes object")
        if size==0:
            raise ValueError("pattern is empty")
        if self.pattern != NULL:
            PyMem_RawFree(self.pattern)
            self.pattern=NULL
        self.pattern=<unsigned char *>PyMem_RawMalloc(size)
        memcpy(self.pattern, s, size)
        self.preBmBc()

    def __dealloc__(self):
        if self.pattern!=NULL:
            #PyMem_RawFree(self.pattern)
            self.pattern=NULL

    cpdef reset(self, pos=0):
        self.rel_pos=pos

    def search(self, buffer, start=0, count=None):
        cdef unsigned int buflen
        cdef unsigned char c;
        cdef unsigned char * buf
        cdef unsigned char * _p
        cdef unsigned char * _b

        if type(buffer)!=type(b""):
            raise ValueError("argument must be a buffer of bytes")

        buflen=len(buffer)

        if buflen == 0:
            return None, "empty"

        poslist=[]

        if not self.multibuffer:
            self.reset(start)
            assert self.rel_pos==start

        buf = <unsigned char *>PyBytes_AsString(buffer)
        # while (self.rel_pos <= buflen-self.pattern_size):
        _p = self.pattern + 1;
        # c_raise(SIGINT)
        while (self.rel_pos <= buflen - self.pattern_size):
            c = buf[self.rel_pos + self.pattern_size - 1]
            if     self.last_char == c and \
                   self.first_char == buf[self.rel_pos] and \
                   self.middle_char == buf[self.rel_pos + self.middle_pos]:

                _b = buf + self.rel_pos + 1
                if memcmp(_p, _b, self.pattern_size-1) == 0:
                    poslist.append(self.rel_pos)
                    if count != None:
                        count-=1
                        if count <= 0:
                            break
            assert c>=0 and c<=255
            self.rel_pos+=self.bmBc[c]

        # Here self.rel_pos > buflen - self.pattern_size
        self.rel_pos -= buflen
        if len(poslist)==0:
            return None, "not found"
        return poslist, "found"

    @property
    def relative(self):
        return self.rel_pos
