import sys


class MockCommonDepends:
    def mock(self):
        import platform
        sys.path.append("../plugin/")

        # Setup default test various values
        sys.modules["__main__"].plugin = "Common - IntegrationTest"
        sys.modules["__main__"].dbg = True
        sys.modules["__main__"].log_override = self
        try:
            plat = platform.uname()
        except:
            plat = ('', '', '', '', '', '')

        if plat[0] == "FreeBSD":
            sys.modules["__main__"].dbglevel = 10
        else:
            sys.modules["__main__"].dbglevel = 3

    def mockXBMC(self):
        from mock import Mock
        sys.path.append("../xbmc-mocks/")
        import xbmc
        import xbmcgui
        import xbmcvfs

        # Setup basic xbmc dependencies
        sys.modules["__main__"].xbmc = Mock(spec=xbmc)
        sys.modules["__main__"].xbmc.translatePath.return_value = "./tmp/"
        sys.modules["__main__"].xbmc.abortRequested = False
        sys.modules["__main__"].xbmc.log = Mock()
        sys.modules["__main__"].xbmc.log.side_effect = self.log
        sys.modules["__main__"].xbmcgui = Mock(spec=xbmcgui)
        sys.modules["__main__"].xbmcvfs = xbmcvfs
        sys.modules["__main__"].xbmcvfs = Mock(spec=xbmcvfs)
        sys.modules["__main__"].xbmcvfs.exists.return_value = False

    def log(self, description, level=0):
        import inspect
        if isinstance(description, str):
            print "[%s] %s : '%s'" % ("Common IntegrationTest", inspect.stack()[1][3], description.decode("utf-8", "ignore"))
        else:
            print "[%s] %s : '%s'" % ("Common IntegrationTest", inspect.stack()[1][3], description)  # 3 - 3 for TestYouTubeUserFeeds.py

    def execute(self, function, *args):
        return function(*args)
