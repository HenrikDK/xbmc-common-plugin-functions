import sys
import unittest2
import io
import MockCommonDepends

MockCommonDepends.MockCommonDepends().mockXBMC()

sys.path.append('../plugin/')
sys.path.append('../plugin/lib/')
sys.path.append('../xbmc-mocks/')


class BaseTestCase(unittest2.TestCase):
    def setUp(self):
        MockCommonDepends.MockCommonDepends().mockXBMC()
        MockCommonDepends.MockCommonDepends().mock()

    def readTestInput(self, filename, should_eval=True):
        testinput = io.open("resources/" + filename)
        inputdata = testinput.read()
        if should_eval:
            inputdata = eval(inputdata)
        return inputdata

    def raiseError(self, exception):
        raise exception

    def TearDown(self):
        self.xbmc.stop()
