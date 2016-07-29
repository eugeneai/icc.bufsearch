from nose.tools import *

import icc.bufsearch as bs # ;-)

PATTERN = b"pattern"
PATTERN2 = b"abddb"
UPATTERN = "pattern"

class test_engine:
    def setUp(self):
        self.raita=bs.Raita(PATTERN, multibuffer=False)

    def tearDown(self):
        del self.raita

    @raises(ValueError)
    def test_check_checker(self):
        self.raita.search(UPATTERN)

    def test_equal(self):
        rc, reason =self.raita.search(PATTERN)
        assert rc == [0]
        assert reason=="found"

    def test_double(self):
        rc, reason =self.raita.search(PATTERN*2)
        assert rc == [0,len(PATTERN)]


class test_engine_multibuffer:
    def setUp(self):
        self.raita=bs.Raita(PATTERN2, multibuffer=True)

    def tearDown(self):
        del self.raita

    def test_from_ex(self):
        p=PATTERN2
        rc1 = self.raita.search(p)
        print (rc1)

    def test_from_ex_full(self):
        p=b"abbaabaabddbabadbb"
        rc1 = self.raita.search(p)
        print (rc1)

    # def test_simple(self):
    #     rc1 = self.raita.search(b"ab")
    #     rc2 = self.raita.search(b"cd")
    #     print (rc1, rc2)
