from nose.tools import *
import binascii as ba

import icc.bufsearch as bs  # ;-)
from icc.bufsearch.extract import extract_ole
import os
import pkg_resources
import olefile


def res(filename):
    return pkg_resources.resource_filename("icc.bufsearch",
                                           "../../tests/data/" + filename)


PATTERN = b"pattern"
PATTERN2 = b"abddb"
UPATTERN = "pattern"


class test_engine:
    def setUp(self):
        self.raita = bs.Raita(PATTERN, multibuffer=False)

    def tearDown(self):
        del self.raita

    @raises(ValueError)
    def test_check_checker(self):
        self.raita.search(UPATTERN)

    def test_equal(self):
        rc, reason = self.raita.search(PATTERN)
        assert rc == [0]
        assert reason == "found"

    def test_double(self):
        rc, reason = self.raita.search(PATTERN * 2)
        assert rc == [0, len(PATTERN)]

    def test_double_count1(self):
        rc, reason = self.raita.search(PATTERN * 2, count=1)
        print(rc)
        assert rc == [0]


class test_engine_multibuffer:
    def setUp(self):
        self.raita = bs.Raita(PATTERN2, multibuffer=True)

    def tearDown(self):
        del self.raita

    def test_from_ex(self):
        p = PATTERN2
        rc1 = self.raita.search(p)
        #print (rc1)

    def test_from_ex_full(self):
        p = b"abbaabaabddbabadbb"
        rc1 = self.raita.search(p)
        # print (rc1)

    # def test_simple(self):
    #     rc1 = self.raita.search(b"ab")
    #     rc2 = self.raita.search(b"cd")
    #     print (rc1, rc2)


DOC = "d0cf11e0a1b11ae1"
DOC_PREFIX = ba.unhexlify(DOC)

files = ["f1_25.07.doc", "f2.doc", "f1.doc"]

HEADER = b"Multielemental analysis of rocks with high calcium content by X-ray fluorescence spectrometry for environmental"

HEADER2 = []
for i in HEADER:
    HEADER2.append(i)
    HEADER2.append(0)

HEADER2 = bytes(HEADER2)


class test_engine_with_file_data:
    def setUp(self):
        self.raita = bs.Raita(DOC_PREFIX, multibuffer=False)
        pass

    def tearDown(self):
        del self.raita
        pass

    def test_from_ex(self):
        for name in files:
            name = res(name)
            doc1 = open(name, "rb")
            data = doc1.read()
            assert data.startswith(DOC_PREFIX)
            rc, _ = self.raita.search(data)
            #print ("Data:", repr(data[:len(DOC_PREFIX)]))
            #print ("Patt:", repr(DOC_PREFIX))
            #print (rc)
            assert rc.pop(0) == 0


class test_header_search:
    def setUp(self):
        self.raita = bs.Raita(HEADER, multibuffer=False)
        pass

    def tearDown(self):
        del self.raita
        pass

    def test_header_ok(self):
        name = res(files[0])
        data = open(name, "rb").read()
        rc, _ = self.raita.search(data)
        rc.pop(0)

    def test_header_no1(self):
        name = res(files[1])
        data = open(name, "rb").read()
        rc, _ = self.raita.search(data)
        assert rc == None

    def test_header_no2(self):
        name = res(files[2])
        data = open(name, "rb").read()
        rc, _ = self.raita.search(data)
        assert rc == None

# print (repr(HEADER2))


class test_header_search_2:
    def setUp(self):
        self.raita = bs.Raita(HEADER2, multibuffer=False)
        pass

    def tearDown(self):
        del self.raita
        pass

    def test_header_ok(self):
        name = res(files[0])
        data = open(name, "rb").read()
        rc, _ = self.raita.search(data)
        # print (rc)
        assert rc

    def test_header_no1(self):
        name = res(files[1])
        data = open(name, "rb").read()
        rc, _ = self.raita.search(data)
        assert rc

    def test_header_no2(self):
        name = res(files[2])
        data = open(name, "rb").read()
        rc, _ = self.raita.search(data)
        assert rc


RAND_SIZE = 40000


class TestCaseFinding:
    def setUp(self):
        self.name = res(files[0])
        self.buffer = [0, 0]
        self.buffer[0] = os.urandom(RAND_SIZE) + b"\0x1"
        self.buffer[1] = os.urandom(RAND_SIZE) + b"\0x2"
        self.content = open(self.name, "rb").read()
        self.obfusc = self.buffer[0] + self.content + self.buffer[1]
        self.raita = bs.Raita(DOC_PREFIX, multibuffer=False)

    def tearDown(self):
        pass

    def test_stub(self):
        assert self.buffer[0] != self.buffer[1]

    def test_search(self):
        rc, _ = self.raita.search(self.obfusc)
        offs = rc[0]
        assert offs == len(self.buffer[0])
        buf = extract_ole(self.obfusc, rc)
        assert len(buf[0]) > 0
