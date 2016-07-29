from nose.tools import *

import icc.bufsearch as bs # ;-)

PATTERN = b"pattern"
UPATTERN = "pattern"

class test_engine:
    def setUp(self):
        self.raita=bs.Raita(PATTERN, multibuffer=True)

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
