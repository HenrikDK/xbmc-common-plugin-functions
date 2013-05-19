# -*- coding: utf-8 -*-
import nose
import BaseTestCase
from mock import Mock, patch
import sys
import CommonFunctions


class TestCommonFunctions(BaseTestCase.BaseTestCase):
    link_html = "<a href='bla.html'>Link Test</a>"
    false_positive_link_html = "<a href='fake.html' id='link'>Link Test fake</a><a href='real.html' id='link' class='real'>Link Test real</a><a href='reallyfake.html' id='link' class='really fake'>Link Test really fake</a>"
    link_artist_html = '<a href="/watch?v=bla-id&amp;feature=artist">Link Test</a>'
    img_html = "<img src='bla.png' alt='Thumbnail' />"

    def setUp(self):
        super(self.__class__, self).setUp()
        reload(CommonFunctions)

    def test_log_should_call_xbmc_log_with_properly_formated_message(self):
        description = "Logging"
        sys.modules["__main__"].xbmc.LOGNOTICE = 0
        common = CommonFunctions
        common.log(description)
        assert (sys.modules["__main__"].xbmc.log.call_count >= 1)

    def test_log_should_not_call_xbmc_log_if_level_too_high(self):
        description = "Logging"
        sys.modules["__main__"].xbmc.LOGNOTICE = 0
        common = CommonFunctions
        common.log(description, 1000)

        assert(sys.modules["__main__"].xbmc.log.call_count == 0)

    def testfetchPage_should_return_content_and_success_return_code_on_valid_link(self):
        patcher = patch("urllib2.urlopen")
        patcher.start()
        import urllib2
        dummy_connection = Mock()
        dummy_connection.read.return_value = "Nothing here\n"
        patcher(urllib2.urlopen).return_value = dummy_connection
        common  = CommonFunctions
        common.log = sys.modules["__main__" ].log_override.log

        ret = common.fetchPage({"link": "http://tobiasussing.dk"})
        patcher.stop()

        assert(ret['status'] == 200)
        assert(ret['content'] == "Nothing here\n")

    def testfetchPage_should_hide_post_data(self):
        patcher = patch("urllib2.urlopen")
        patcher.start()
        import urllib2
        dummy_connection = Mock()
        dummy_connection.read.return_value = "Nothing here\n"
        patcher(urllib2.urlopen).return_value = dummy_connection
        common  = CommonFunctions
        common.log = Mock()
        common.log.side_effect = sys.modules["__main__" ].log_override.log

        ret = common.fetchPage({"link": "http://tobiasussing.dk", "post_data": {"uname": "name", "pword": "pass"}, "hide_post_data": "true"})
        patcher.stop()

        print repr(ret)
        common.log.assert_called_with('Posting data', 2)

    def testfetchPage__should_return_failing_error_code_on_broken_link(self):
        patcher = patch("urllib2.urlopen")
        patcher.start()
        import urllib2
        fp = Mock()
        fp.read.return_value = ""
        patcher(urllib2.urlopen).side_effect = urllib2.HTTPError("http://tobiasussing.dk/DoesNotExist.html", 500, "", "", fp)
        common  = CommonFunctions
        common.log = sys.modules["__main__" ].log_override.log

        ret = common.fetchPage({"link": "http://tobiasussing.dk/DoesNotExist.html"})
        patcher.stop()

        assert(ret['status'] == 500)
        assert(ret['content'] == "")

    def test_stripTags_should_correctly_extract_the_text_content_of_a_link_tag(self):
        common = CommonFunctions
        common.log = sys.modules["__main__" ].log_override.log
        inp = self.link_html

        ret = common.stripTags(inp)

        assert(ret == "Link Test")

    def test_parseDOM_should_fail_if_name_is_empty(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__" ].log_override.log

        ret = common.parseDOM(self.link_html, "")

        assert(ret == "" )

    def test_parseDOM_should_call__getDOMElements_to_get_list_of_matching_elements(self):
        common  = CommonFunctions
        common._getDOMElements = Mock()
        common._getDOMElements.return_value = "bla.html"
        common.log = sys.modules["__main__" ].log_override.log

        ret = common.parseDOM(self.link_html, "a", attrs={"href": "bla.html" }, ret="href")

        print repr(ret)

        common._getDOMElements.assert_called_with("<a href='bla.html'>Link Test</a>", 'a', {'href': 'bla.html'})

    def test_parseDOM_should_call_getDOMAttribute_to_extract_attributes(self):
        common  = CommonFunctions
        common._getDOMAttributes = Mock()
        common._getDOMAttributes.return_value = ["bla.html"]
        common._getDOMElements = Mock()
        common._getDOMElements.return_value = ["<a href='bla.html'>"]
        common.log = sys.modules["__main__" ].log_override.log

        ret = common.parseDOM(self.link_html, "a", attrs={"href": "bla.html" }, ret="href")

        print repr(ret)

        assert(common._getDOMElements.call_count == 1)
        common._getDOMAttributes.assert_called_with("<a href='bla.html'>", 'a', 'href')
        assert(ret == ["bla.html"])

    def test__getDOMElements_should_match_simple_tag(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__" ].log_override.log
 
        ret = common._getDOMElements("<p>sample</p>", "p", {})

        print repr(ret)
        assert(ret == ["<p>"])

    def test__getDOMElements_should_handle_garbage_tags(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__" ].log_override.log
 
        ret = common._getDOMElements("<p !-->sample</p>", "p", {})

        print repr(ret)
        assert(ret == ["<p !-->"])

    def test__getDOMElements_should_match_with_args(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__" ].log_override.log
 
        ret = common._getDOMElements("<p>sample</p><p id='test'>sample match</p>", "p", {"id": "test"})

        print repr(ret)
        assert(ret == ["<p id='test'>"])

    def test__getDOMElements_should_filter_false_positives_with_multiple_args(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__" ].log_override.log
 
        ret = common._getDOMElements("<p>sample</p><p id='test1' subid='test'>sample match</p><p id='test2' subid='test'>sample match</p>", "p", {"id": "test2", "subid": "test"})

        print repr(ret)
        assert(ret == ["<p id='test2' subid='test'>"])

    def test_parseDOM_should_call_getDOMContent_to_extract_content_of_an_element(self):
        common  = CommonFunctions
        common._getDOMContent = Mock()
        common._getDOMContent.return_value = "Link Test"
        common._getDOMElements = Mock()
        common._getDOMElements.return_value = ["<a href='bla.html'>"]
        common.log = sys.modules["__main__" ].log_override.log

        ret = common.parseDOM(self.link_html, "a", attrs={"href": "bla.html" })

        print repr(ret)

        assert(common._getDOMElements.call_count == 1)
        common._getDOMContent.assert_called_with("<a href='bla.html'>Link Test</a>", 'a', "<a href='bla.html'>", False)

    def test_getDOMAttributes_should_handle_double_quotation_marks(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__" ].log_override.log
        ret = common._getDOMAttributes('<element name="                 "3 Minutes In Hell" - Gary Anthony Williams             " />', "element", "name")

        print repr(ret)
        assert(len(ret) == 1 )
        assert(ret[0] == '"3 Minutes In Hell" - Gary Anthony Williams')

    def test_getDOMAttributes_should_handle_no_quotation_marks_space(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__" ].log_override.log
        ret = common._getDOMAttributes("<cookie port=None secure=False></cookie>", "cookie", "port")

        print repr(ret)
        assert(len(ret) == 1 )
        assert(ret[0] == 'None')

    def test_getDOMAttributes_should_handle_no_quotation_marks_slash(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__" ].log_override.log
        ret = common._getDOMAttributes("<cookie port=None/>", "cookie", "port")

        print repr(ret)
        assert(len(ret) == 1 )
        assert(ret[0] == 'None')

    def test_getDOMAttributes_should_handle_no_quotation_marks(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__" ].log_override.log
        ret = common._getDOMAttributes("<cookie port=None>", "cookie", "port")

        print repr(ret)
        assert(len(ret) == 1 )
        assert(ret[0] == 'None')

    def test_getDOMContent_should_correctly_extract_the_content_of_an_element(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__" ].log_override.log
        inp = self.link_html

        ret = common._getDOMContent(inp, "a", "<a href='bla.html'>", False)

        assert(ret == "Link Test")

    def test_getDOMContent_should_add_container_tags_to_result(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__" ].log_override.log
        inp = self.link_html

        ret = common._getDOMContent(inp, "a", "<a href='bla.html'>", True)
        print repr(ret)

        assert(ret == "<a href='bla.html'>Link Test</a>")

    def test_getDOMContent_should_properly_remove_matched_content(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__" ].log_override.log
        seasons = ['<span class="yt-uix-button-content">3</span><span class="yt-uix-button-content">2</span><span class="yt-uix-button-content">1</span><']

        common._getDOMElements = Mock()
        common._getDOMElements.return_value = ['<span class="yt-uix-button-content">', '<span class="yt-uix-button-content">', '<span class="yt-uix-button-content">']

        season_list = common.parseDOM(seasons, "span", attrs={"class": "yt-uix-button-content"})
        print "Season List: " + repr(season_list)

        assert(common._getDOMElements.call_count == 1)
        assert(season_list == ['3', '2', '1'])

    def test_getDOMContent_should_not_extract_the_content_of_a_link_tag_that_doesnt_match_the_search_string(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__" ].log_override.log
        inp = "<a href='bla2.html'>Link Test</a>"

        ret = common._getDOMContent(inp, "a", "<a href='bla.html'>", False)

        assert(ret == "")

    def test_getDOMContent_should_extract_dom_correctly_when_there_are_matching_sub_elements(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__" ].log_override.log
        inp = "<div class='match'>Here is an: <div>Inner div</div>!</div>"

        ret = common._getDOMContent(inp, "div", "<div class='match'>", False)
        print repr(ret)
        assert(ret == "Here is an: <div>Inner div</div>!")

    def test_parseDOM_should_convert_newline_within_tags_to_space(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__" ].log_override.log
        content = '<img src="//s.ytimg.com/yt/img/pixel-vfl3z5WfW.gif" alt="Thumbnail"\ndata-thumb="http://i3.ytimg.com/vi/bud6Ljyzq80/poster.jpg?v=adb5d7" >'
        content = '<div><span\nid="info">more\ninformation</span></div>'
        common._getDOMElements = Mock()
        common._getDOMElements.return_value = ['<span id="info">']

        ret = common.parseDOM(content, "span", attrs={"id": "info"})
        print repr(ret)

        assert(common._getDOMElements.call_count == 1)
        assert(len(ret) == 1 )
        assert(ret[0] == 'more\ninformation')

    def test_getUserInput_should_call_xbmc_keyboard_to_recieve_text_input(self):
        common = CommonFunctions
        sys.modules["__main__"].xbmc.Keyboard().getText.return_value = "mock"

        result = common.getUserInput()
        print repr(result)

        sys.modules["__main__"].xbmc.Keyboard.assert_called_with("", "Input")
        assert(result == "mock")

    def test_getUserInput_should_set_title_and_default_text_if_provided(self):
        common = CommonFunctions
        sys.modules["__main__"].xbmc.Keyboard().getText.return_value = "user_result"

        result = common.getUserInput("SomeTitle", "SomeDefault")

        sys.modules["__main__"].xbmc.Keyboard.assert_called_with("SomeDefault", "SomeTitle")
        sys.modules["__main__"].xbmc.Keyboard().setHiddenInput.assert_called_with(False)
        sys.modules["__main__"].xbmc.Keyboard().doModal.assert_called_with()
        sys.modules["__main__"].xbmc.Keyboard().isConfirmed.assert_called_with()
        assert(result == "user_result")

    def test_getUserInputNumbers_should_call_xbmc_keyboard_to_recieve_text_input(self):
        common = CommonFunctions
        sys.modules["__main__"].xbmcgui.Dialog().numeric.return_value = 1234

        result = common.getUserInputNumbers()

        sys.modules["__main__"].xbmcgui.Dialog().numeric.assert_called_with(0, 'Input', '')
        assert(result == "1234")

    def test_getUserInputNumbers_should_set_title_and_default_text_if_provided(self):
        common = CommonFunctions

        common.getUserInputNumbers("SomeTitle", "SomeDefault")

        sys.modules["__main__"].xbmcgui.Dialog().numeric.assert_called_with(0, "SomeTitle", "SomeDefault")

    def test_getParameters_should_parse_param_string(self):
        params_string = "/Some/parth?key1=value1&key2=value2&"
        sys.modules["__main__"].xbmc.getInfoLabel.return_value = "12.0-RC2"
        common = CommonFunctions

        result = common.getParameters(params_string)

        assert(result["key1"] == "value1")
        assert(result["key2"] == "value2")

    def test_getParameters_should_not_unquote_with_dharma(self):
        params_string = "?folder=true&login=false&path=%2froot%2fsearch&store=searches"
        sys.modules["__main__"].xbmc.getInfoLabel.return_value = "11.0 Git:20120702"
        common = CommonFunctions

        result = common.getParameters(params_string)

        print repr(result)
        assert(result["path"] == "%2froot%2fsearch")

    def test_getParameters_should_unquote_with_frodo(self):
        params_string = "?folder=true&login=false&path=%2froot%2fsearch&store=searches"
        sys.modules["__main__"].xbmc.getInfoLabel.return_value = "12.1"
        common = CommonFunctions

        result = common.getParameters(params_string)

        print repr(result)
        assert(result["path"] == "/root/search")

    def test_getParameters_should_handle_params_with_missing_value(self):
        params_string = "/Some/parth?key1=value1&key2=&"
        sys.modules["__main__"].xbmc.getInfoLabel.return_value = "12.0-RC2"
        common = CommonFunctions

        result = common.getParameters(params_string)

        assert(result["key1"] == "value1")
        assert(result["key2"] == "")

    def test_getParameters_should_handle_missing_question_mark(self):
        params_string = "key1=value1&key2=value2&"
        sys.modules["__main__"].xbmc.getInfoLabel.return_value = "12.0-RC2"
        common = CommonFunctions

        result = common.getParameters(params_string)

        assert(result["key1"] == "value1")
        assert(result["key2"] == "value2")

    def test_replaceHTMLCodes_should_handle_ampersand(self):
        input = "&amp;"
        common = CommonFunctions

        result = common.replaceHTMLCodes(input)

        print repr(result)

        assert(result == "&")

    def test_replaceHTMLCodes_should_handle_quotationmark(self):
        input = "&quot;"
        common = CommonFunctions

        result = common.replaceHTMLCodes(input)
        print repr(result)

        assert(result == '"')

    def test_replaceHTMLCodes_should_handle_hellip(self):
        input = "&hellip;"
        common = CommonFunctions

        result = common.replaceHTMLCodes(input)

        print repr(result)

        assert(result == u"…")

    def test_replaceHTMLCodes_should_handle_yuml(self):
        input = "&yuml;"
        common = CommonFunctions

        result = common.replaceHTMLCodes(input)

        print repr(result)

        assert(result == u"ÿ")

    def test_replaceHTMLCodes_should_handle_apos(self):
        input = "&apos;"
        common = CommonFunctions

        result = common.replaceHTMLCodes(input)

        print repr(result)

        assert(result == u"'")

    def test_replaceHTMLCodes_should_handle_number192(self):
        input = "&#192;"
        common = CommonFunctions

        result = common.replaceHTMLCodes(input)

        print repr(result)

        assert(result == u"À")

    def test_replaceHTMLCodes_should_handle_Agrave(self):
        input = "&Agrave;"
        common = CommonFunctions

        result = common.replaceHTMLCodes(input)

        print repr(result)

        assert(result == u"À")

    def test_replaceHTMLCodes_should_handle_iquest(self):
        input = "&iquest;"
        common = CommonFunctions

        result = common.replaceHTMLCodes(input)

        print repr(result)

        assert(result == u"¿")

    def test_replaceHTMLCodes_should_handle_greater_than_and_less_than(self):
        input = "&gt;&lt;"
        common = CommonFunctions

        result = common.replaceHTMLCodes(input)

        print repr(result)

        assert(result == "><")

    def test_replaceHTMLCodes_should_handle_standard_ascii_low(self):
        input = "&#32;&#126;"
        common = CommonFunctions

        result = common.replaceHTMLCodes(input)

        print repr(result)

        assert(result == u" ~")

    def test_replaceHTMLCodes_should_handle_standard_ascii_high(self):
        input = "&#160;&#255;"
        input = "&#160;&#255;"
        common = CommonFunctions

        result = common.replaceHTMLCodes(input)

        print repr(result)

        assert(result == u"\xa0ÿ")  # Non breaking space can't print.

    def test_replaceHTMLCodes_should_handle_version_401_low(self):
        input = "&#338;&#402;"
        common = CommonFunctions

        result = common.replaceHTMLCodes(input)

        print repr(result)

        assert(result == u"Œƒ")

    def test_replaceHTMLCodes_should_handle_version_401_high(self):
        input = "&#8211;&#8482;"
        common = CommonFunctions

        result = common.replaceHTMLCodes(input)

        print repr(result)

        assert(result == u"–™")

    def test_makeAscii_should_convert_to_ascii(self):
        hexversion = sys.hexversion
        sys.hexversion = 0x02040000
        common = CommonFunctions
        input = "æøåa"
        print "input " + repr(input)

        result = common.makeAscii(input)
        print "result " + repr(result)

        sys.hexversion = hexversion
        assert(result == "a")

    def test_openFile_should_call_io_open(self):
        patcher = patch("io.open")
        patcher.start()
        import io
        io.open.return_value = "my_result"
        common = CommonFunctions

        result = common.openFile("someFile")
        patcher.stop()

        assert(result == "my_result")

    def test_extractJS_should_call_parsedom_for_scripts(self):
        common = CommonFunctions
        common.parseDOM = Mock()
        common.parseDOM.return_value = ["data"]

        res = common.extractJS("data")
        print repr(res)

        common.parseDOM.assert_called_with("data", "script")

    def test_extractJS_should_assume_js_file_on_no_script(self): 
        common = CommonFunctions
        common.parseDOM = Mock()
        common.parseDOM.return_value = []

        res = common.extractJS("data")
        print repr(res)

        assert(res == ["data"])

    def test_extractJS_should_find_function(self):
        common = CommonFunctions
        common.parseDOM = Mock()
        common.parseDOM.return_value = ["testfunct('somedata', 4);\n imgsrc = 'source';"]

        res = common.extractJS("data", function="testfunct")
        print repr(res)
        assert(res == ["testfunct('somedata', 4);"])

    def test_extractJS_should_find_complex_variable(self):
        common = CommonFunctions
        common.parseDOM = Mock()
        common.parseDOM.return_value = ["var myArray=new Array();\n myArray[0] = 'data';"]

        res = common.extractJS("data", variable="myArray[0]")
        print repr(res)
        assert(res == ["myArray[0] = 'data';"])

    def test_extractJS_should_extract_function_value(self):
        common = CommonFunctions
        common.parseDOM = Mock()
        common.parseDOM.return_value = ["testfunct({'data': 'input'});\n imgsrc = 'source';"]

        res = common.extractJS("data", function="testfunct", values=True)
        print repr(res)
        assert(res == ["{'data': 'input'}"])

    def test_extractJS_should_evaluate_non_json_function_values(self):
        common = CommonFunctions
        common.parseDOM = Mock()
        common.parseDOM.return_value = ["testfunct('somedata', 4);\n imgsrc = 'source';"]

        res = common.extractJS("data", function="testfunct", evaluate=True)

        print repr(res)
        assert(res == [('somedata', 4)])

    def test_extractJS_should_extract_variable_value(self):
        common = CommonFunctions
        common.parseDOM = Mock()
        common.parseDOM.return_value = ["testfunct('somedata', 4);\n imgsrc = 'source';"]

        res = common.extractJS("data", variable="imgsrc", values=True)
        print repr(res)

        assert(res == ["source"])

    def test_extractJS_should_parse_JSON(self):
        common = CommonFunctions
        common.parseDOM = Mock()
        common.parseDOM.return_value = ["testfunct('somedata', 4);\n imgsrc = {'source': 'http'};"]

        res = common.extractJS("data", variable="imgsrc", evaluate=True)
        print repr(res)
        assert(res == [{'source': 'http'}])

if __name__ == "__main__":
        nose.runmodule()
