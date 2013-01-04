class MockCommonDepends:
    common = ""

    def mock(self):
        import sys
        from mock import Mock
        sys.path.append("../plugin/")
        sys.path.append("../plugin/lib/")

        # Setup default test various values
        sys.modules["__main__"].plugin = "CommonFunctions Beta-1.3.0"
        sys.modules["__main__"].dbg = True
        sys.modules["__main__"].dbglevel = 10
        sys.modules["__main__"].login = ""
        sys.modules["__main__"].language = Mock()

        sys.modules["__main__"].log_override = self

    def mockXBMC(self):
        import sys
        from mock import Mock
        sys.path.append("../xbmc-mocks/")
        import xbmc
        import xbmcaddon
        import xbmcgui
        import xbmcplugin
        import xbmcvfs

        # Setup sqlite
        sys.modules["sqlite"] = __import__("mock")
        sys.modules["sqlite"].connect = Mock()
        sys.modules["sqlite3"] = __import__("mock")
        sys.modules["sqlite3"].connect = Mock()

        # Setup basic xbmc dependencies
        sys.modules["__main__"].xbmc = Mock(spec=xbmc)
        sys.modules["__main__"].xbmc.translatePath = Mock()
        sys.modules["__main__"].xbmc.translatePath.return_value = "testing"
        sys.modules["__main__"].xbmc.getSkinDir = Mock()
        sys.modules["__main__"].xbmc.getSkinDir.return_value = "testSkinPath"
        sys.modules["__main__"].xbmc.getInfoLabel.return_value = "some_info_label"
        sys.modules["__main__"].xbmcaddon = Mock(spec=xbmcaddon)
        sys.modules["__main__"].xbmcgui = Mock(spec=xbmcgui)
        sys.modules["__main__"].xbmcgui.WindowXMLDialog.return_value = "testWindowXML"

        sys.modules["__main__"].xbmcplugin = Mock(spec=xbmcplugin)
        sys.modules["__main__"].xbmcvfs = Mock(spec=xbmcvfs)
        sys.modules["__main__"].settings = Mock(spec=xbmcaddon.Addon())
        sys.modules["__main__"].settings.getAddonInfo.return_value = "somepath"

    def log(self, description, level=0):
        import inspect
        print "[%s] %s : '%s'" % ("YouTube", inspect.stack()[1][3], description)
