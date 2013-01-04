# -*- coding: utf-8 -*-
import nose
import BaseTestCase
import sys
import os
from mock import Mock, patch
import CommonFunctions


class TestCommonFunctions(BaseTestCase.BaseTestCase):
    link_html = "<a href='bla.html'>Link Test</a>"
    false_positive_link_html = "<a href='fake.html' id='link'>Link Test fake</a><a href='real.html' id='link' class='real'>Link Test real</a><a href='reallyfake.html' id='link' class='really fake'>Link Test really fake</a>"
    link_artist_html = '<a href="/watch?v=bla-id&amp;feature=artist">Link Test</a>'
    img_html = "<img src='bla.png' alt='Thumbnail' />"

    def setUp(self):
        super(self.__class__, self).setUp()
        reload(CommonFunctions)

    def test_fetchPage_should_add_headers(self):
        common = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        ret = common.fetchPage({"link": "http://api.themoviedb.org/3/movie/tt1558246/images?api_key=4be68d7eab1fbd1b6fd8a3b80a65a95e", "headers": [("Accept", "application/json")]})
        print repr(ret["content"])
        assert(ret['status'] == 200)
        assert(len(ret['content']) > 200)

    def test_fetchPage_should_return_content_and_success_return_code_on_valid_link(self):
        common = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        ret = common.fetchPage({"link": "http://tobiasussing.dk"})

        assert(ret['status'] == 200)
        assert(ret['content'] == "Nothing here\n")

    def test_fetchPage__should_return_failing_error_code_on_broken_link(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        ret = common.fetchPage({"link": "http://tobiasussing.dk/DoesNotExist.html"})

        assert(ret['status'] == 500)
        assert(ret['content'] == "")

    def test_parseDOM_should_correctly_extract_the_href_attribute_of_a_link_tag(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        ret = common.parseDOM(self.link_html, "a", ret="href")

        assert(len(ret) == 1 )
        assert(ret[0] == "bla.html")

    def test_parseDOM_should_remove_false_positives(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        ret = common.parseDOM(self.false_positive_link_html, "a", attrs={"id": "link", "class": "real" }, ret="href")
        assert(len(ret) == 1)
        assert(ret[0] == "real.html")

    def test_parseDOM_should_correctly_extract_the_href_attribute_of_a_link_tag_with_wildcard_search(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        ret = common.parseDOM(self.link_artist_html, "a", attrs={"href": ".*feature=artist" }, ret="href")

        assert(len(ret) == 1 )
        assert(ret[0] == "/watch?v=bla-id&amp;feature=artist")

    def test_parseDOM_should_correctly_extract_the_text_content_of_a_link_tag(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        ret = common.parseDOM(self.link_html, "a", attrs={"href": "bla.html" })

        assert(len(ret) == 1 )
        assert(ret[0] == "Link Test")

    def test_parseDOM_should_correctly_extract_the_text_content_of_a_link_tag_with_container_tags(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        ret = common.parseDOM('<videos on_this_page="50" page="1">\n<video id="1">title1</video><video id="2">title2</video></videos>', "video", ret=True)

        print repr(ret)
        assert(len(ret) == 2 )
        assert(ret[0] == '<video id="1">title1</video>')
        assert(ret[1] == '<video id="2">title2</video>')

    def test_parseDOM_should_correctly_extract_the_src_attribute_of_an_img_tag(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        ret = common.parseDOM(self.img_html, "img", attrs={"alt": "Thumbnail" }, ret="src" )

        assert(len(ret) == 1 )
        assert(ret[0] == "bla.png")

    def test_parseDOM_should_not_extract_the_src_attribute_of_an_img_tag_with_wrong_alt(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        ret = common.parseDOM(self.img_html, "img", attrs={"alt": "Thumb broken" }, ret="src" )

        assert(len(ret) == 0 )
        assert(ret == [])

    def test_parseDOM_should_correctly_extract_the_alt_attribute_of_an_img_tag(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        ret = common.parseDOM(self.img_html, "img", ret="alt")

        assert(len(ret) == 1 )
        assert(ret[0] == "Thumbnail")

    def test_parseDOM_should_be_able_to_extract_flashvars_content_from_a_youtube_video_page(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        ret = common.parseDOM(self.readTestInput("watch-gyzlwNvf8ss-standard.html", False), "embed", attrs={"id": "movie_player" }, ret="flashvars")

        assert(len(ret) == 1 )
        assert(ret[0].strip() == self.readTestInput("watch-gyzlwNvf8ss-flashvars.txt", False).strip())

    def test_parseDOM_should_be_able_to_extract_the_src_attribute_of_a_flashvars_element_from_a_youtube_video_page(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        print repr(type(self.readTestInput("watch-gyzlwNvf8ss-standard.html", False)))
        ret = common.parseDOM(self.readTestInput("watch-gyzlwNvf8ss-standard.html", False), "embed", attrs={"id": "movie_player"}, ret="src")

        assert(len(ret) == 1 )
        assert(ret[0] == "http://s.ytimg.com/yt/swfbin/watch_as3-vflCwc_mi.swf")

    def test_parseDOM_should_not_get_duplicates_from_bliptv(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        ret = common.parseDOM(self.readTestInput("bliptv_duplicate_test.html", False), "div", {"class": "ChannelDirectoryItem"})

        print str(len(ret))
        assert(len(ret) == 6 )

        verify = [['<a href="/splashnewstv">SplashNewsTV</a>'], ['<a href="/hbr-video-ideacast">HBR Video IdeaCast</a>'], ['<a href="/noisevox">NOISEVOX</a>'], ['<a href="/blizzblues-with-darnell">Blizz Blues with Darnell</a>'], ['<a href="/youcanplaythis">YOU CAN PLAY THIS</a>'], ['<a href="/Nebu1a">Dota Daily</a>']]
        for index, t in enumerate(ret):
                h3 = common.parseDOM(t, "h3")
                print "Q : " + repr(h3) + " - " + str(index)
                assert(h3 == verify[index])

    def test_parseDOM_should_correctly_extract_double_quotation_marks(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        ret = common.parseDOM(self.readTestInput("parse-title-with-quotation-marks.html", False), "span", attrs={"class": "Title"}, ret="title")
        print repr(ret)
        assert(len(ret) == 1 )
        assert(ret[0] == '"3 Minutes In Hell" - Gary Anthony Williams')

    def test_parseDOM_should_be_able_to_handle_line_breaks_with_no_other_delimiter_in_tags(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log
        ret = common.parseDOM(self.readTestInput("topdocumentaryfilms-all.html", False), "div", attrs={"id": "header" })

        print repr(ret)
        assert(len(ret) == 1 )
        print repr(len(ret[0]))
        assert(len(ret[0]) > 500)

    def test_parseDOM_should_be_able_to_handle_line_breaks_with_no_other_delimiter_in_tags_content(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log
        ret = common.parseDOM(self.readTestInput("topdocumentaryfilms-all.html", False), "div", attrs={"class": "sitedesc" })

        print repr(ret)
        assert(len(ret) == 1 )
        assert(ret[0] == "Go through this great collection of documentary movies and watch free documentaries online. Share your thoughts and enjoy.")

    def test_parseDOM_should_be_able_to_handle_line_breaks(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log
        ret = common.parseDOM(self.readTestInput("2-factor.html", False), "input", attrs={"id": "uilel" }, ret="value")

        assert(len(ret) == 1 )
        assert(ret[0] == "3")

    def test_parseDOM_should_be_able_to_handle_tabs(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log
        data = '<div id="PageInfo" \n\tdata-users-id="335254" \n\tdata-ad-sales-categories="Movies (about),Channel Awesome,Entertainment (about)" \n\tdata-channels-list="Entertainment"\n\tdata-content-categories=""\n\tdata-core-value="9" \n\tdata-admin-rating="3" \n\tdata-lock="0" \n\tdata-disable-autostart="0" \n\tstyle="display:none !important;">\n</div>'
        ret = common.parseDOM(data, "div", attrs={"id": "PageInfo" }, ret="data-users-id")

        print repr(ret)
        assert(len(ret) == 1 )
        assert(ret[0] == "335254")

    def test_parseDOM_should_be_able_to_handle_tags_with_no_attributes(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log
        ret = common.parseDOM(self.readTestInput("documentarystorm.html", False), "p")

        print repr(ret)

        assert(len(ret) == 1 )
        assert(ret[0] == "Stephen Fry and zoologist Mark Carwardine head to the ends of the earth in search of animals on the edge of extinction.")

    def test_parseDOM_should_be_able_to_handle_documentarystorm2(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log
        ret = common.parseDOM(self.readTestInput("documentarystorm2.html", False), "ul", attrs = { "id": "suckerfishnav"})
        print repr(ret)

        ret2 = common.parseDOM(ret, "ul", attrs = { "class": "children"})
        print "2: " + repr(ret2[0])

        ret3 = []
        for ret in ret2:
            ret3 += common.parseDOM(ret, "li", attrs = { "class": "cat-item cat-item-[0-9]{1,}"})
            print "3: " + repr(ret3)


        print repr(len(ret3))
        assert(len(ret3) == 124 )
        assert(ret3[0] == '<a href="http://documentarystorm.com/category/around-the-world/cooking-around-the-world/" title="View all posts filed under Cooking">Cooking (5)</a>')
        assert(ret3[123] == '<a href="http://documentarystorm.com/category/war-military/weapons-war-military/" title="View all posts filed under Weapons">Weapons (15)</a>')


    def test_parseDOM_should_be_able_to_extract_login_info_with_ending_equals(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        login_info = common.parseDOM(self.readTestInput("cookie.html", False), "cookie", attrs={"name": "LOGIN_INFO" }, ret="value")
        print repr(login_info)
        assert(login_info == ["ef7fea38051171f6e8e8d64b19e67705c40AAAB7IjEiOiAxLCAiMyI6IDc3MTY5MTQ4MywgIjIiOiAiMDNyb0xSeW9CTWJzY1hxczJDRmYydz09IiwgIjUiOiA0NTAzNjAxNzY2NDY1NTM2LCAiNCI6ICJHQUlBIiwgIjciOiAxMzIzMDE3MDkwLCAiNiI6IGZhbHNlLCAiOCI6IDExNTMwODYxNzc4NH0="])

    def test_parseDOM_should_extract_variable_content_without_quotationmarks(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        login_info = common.parseDOM(self.readTestInput("cookie.html", False), "cookie", attrs={"name": "APISID" }, ret="port")
        print repr(login_info)
        assert(login_info == ["None"])

    def test_parseDOM_should_match_variable_content_without_quotationmarks(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        result = common.parseDOM(self.readTestInput("cookie.html", False), "cookie", attrs={"expires": "1638377091" }, ret="name")
        print repr(result)
        assert(result == ["APISID"])

    def test_parseDOM_should_ignore_href_inside_other_element(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log
        test_input = '<div id="yt-masthead-signin"><button class=" yt-uix-button yt-uix-button-hh-primary" type="button"  onclick=";window.location.href=this.getAttribute(&#39;href&#39;);return false;"  href="https://accounts.google.com/ServiceLogin?passive=true&amp;hl=en_US&amp;uilel=3&amp;continue=http%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26feature%3Dsign_in_button%26hl%3Den_US%26next%3D%252F%26nomobiletemp%3D1&amp;service=youtube" role="button"><span class="yt-uix-button-content">Sign in </span></button></div><div id="yt-masthead-content"><span id="masthead-upload-button-group"><a href="//www.youtube.com/my_videos_upload" class="yt-uix-button   yt-uix-sessionlink yt-uix-button-hh-default" data-sessionlink="ei=CM2Mj-nqrbQCFZiRIQod0k_VaA%3D%3D"><span class="yt-uix-button-content">Upload</span></a></span><form id="masthead-search" class="search-form consolidated-form" action="/results" onsubmit="if (_gel(&#39;masthead-search-term&#39;).value == &#39;&#39;) return false;"><button tabindex="2" dir="ltr" id="search-btn" type="submit" class="search-btn-component search-button yt-uix-button yt-uix-button-hh-default" onclick="if (_gel(&#39;masthead-search-term&#39;).value == &#39;&#39;) return false; _gel(&#39;masthead-search&#39;).submit(); return false;;return true;"  role="button"><span class="yt-uix-button-content">Search </span></button><div id="masthead-search-terms" class="masthead-search-terms-border" dir="ltr"><label><input id="masthead-search-term"  class="search-term" name="search_query" value="" type="text" tabindex="1" onkeyup="goog.i18n.bidi.setDirAttribute(event,this)"  title="Search"></label></div></form></div></div></div>  <div id="alerts" ></div>'

        result = common.parseDOM(test_input, "button", attrs={"href": ".*?ServiceLogin.*?"}, ret="href")
        print repr(result)
        assert(result == ["https://accounts.google.com/ServiceLogin?passive=true&amp;hl=en_US&amp;uilel=3&amp;continue=http%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26feature%3Dsign_in_button%26hl%3Den_US%26next%3D%252F%26nomobiletemp%3D1&amp;service=youtube"])

    def test_stripTags_should_strip_tags_correctly(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        test = common.stripTags("test <tag>mock</tag>")

        print repr(test)
        assert(test == "test mock")

    def test_replaceHTMLCodes_should_replace_correctly(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        test = common.replaceHTMLCodes("&amp;&quot;&hellip;&gt;&lt;&#39;")

        print repr(test)
        assert(test == u"&\"…><'")

    def test_replaceHTMLCodes_should_handle_missing_semicolon_on_numbers(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        test = common.replaceHTMLCodes("&#39q")

        print repr(test)
        assert(test == u"'q")

    def test_getParameters_should_convert_params_to_dict(self):
        common  = CommonFunctions
        common.getXBMCVersion = Mock(return_value = 11)
        common.log = sys.modules["__main__"].log_override.log

        test = common.getParameters("?path=/root/favorites&login=true")

        print repr(test)
        assert(test == {"path": "/root/favorites", "login": "true" })

    def test_getUserInput_should_return_default(self):
        sys.modules["__main__"].xbmc.Keyboard().getText.return_value = "Miley Cyrus"
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        test = common.getUserInput("Userpin", "Miley Cyrus")

        print repr(test)
        assert(test == "Miley Cyrus")

    def test_getUserInputNumbers_should_return_default(self):
        sys.modules["__main__"].xbmcgui.Dialog().numeric.return_value = "1234"
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        test = common.getUserInputNumbers("Userpin", "1234")

        print repr(test)
        assert(test == "1234")

    def test_openFile(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        test = common.openFile("./tmp/test-file", "w")
        test.write(u"")
        test.close()

        assert(os.path.exists('./tmp/test-file'))

    def test_Log(self):
        sys.modules["__main__"].xbmc.LOGNOTICE.return_value = 3
        common  = CommonFunctions
        common.log("log", 0)
        common.log("no log", 20)
        sys.modules["__main__"].xbmc.log.assert_call_count(1)
        assert(sys.modules["__main__"].xbmc.log.call_count >= 1)

    def test_makeAscii(self):
        patcher = patch("sys.hexversion")
        patcher.start()
        import sys
        sys.hexversion = 0x02040000

        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        test = common.makeAscii("test נלה מהי test")
        patcher.stop()

        print repr(test)
        assert(test == "test   test")

    def ttest_makeUTF8(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        test = common.makeUTF8("test נלה מהי test")

        print repr(test)
        assert(test == "test   test")
        assert(False)

    def test_extractJS_should_return_variable_new(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        test = common.extractJS(self.readTestInput("watch-54VJWHL2K3I.html", False), variable="yt.playerConfig", evaluate=True)

        print repr(test)
        print str(len(test))
        assert(len(test) == 1)
        print "BLA1: " + repr(test[0])
        #print "BLA2: " + repr(isinstance(test[0], dict))
        print "BLA3: " + repr(type(test[0]))
        assert(isinstance(test[0], dict) == True)

    def test_extractJS_should_return_variable(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        test = common.extractJS(self.readTestInput("watch-byv-wpqDydI-superbass.html", False), variable="yt.preload")

        print repr(test)
        print str(len(test))
        assert(len(test) == 1)
        print "BLA1: " + repr(test[0])
        assert(test[0] == "yt.preload = {};")

    def test_extractJS_should_return_matching_function(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        test = common.extractJS(self.readTestInput("watch-byv-wpqDydI-superbass.html", False), function="yt.setConfig", match="PLAYER_CONFIG")

        print repr(test)
        print str(len(test))
        assert(len(test) == 1)
        print "BLA1: " + repr(test[0])
        print "BLA2: " + repr(self.readTestInput("watch-byv-wpqDydI-superbass-json-function.html", False).strip())
        assert(test[0] == self.readTestInput("watch-byv-wpqDydI-superbass-json-function.html", False).strip())

    def test_extractJS_should_return_evaled_result(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        test = common.extractJS(self.readTestInput("watch-byv-wpqDydI-superbass.html", False), function="yt.setConfig", match="VIDEO_ID", evaluate=True)

        print repr(test)
        print str(len(test))
        assert(len(test) == 1)
        print "BLA1: " + repr(test[0])
        assert(test[0] == {'VIDEO_USERNAME': 'karmincovers', 'VIDEO_ID': 'byv-wpqDydI'})

    def test_extractJS_should_return_function_arguments(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        test = common.extractJS(self.readTestInput("watch-byv-wpqDydI-superbass.html", False), function="yt.timing.tick", values=True)

        print repr(test)
        print str(len(test))
        assert(len(test) == 3)
        assert(test == ["'start'", "'ct'", "'bf'"])

    def test_extractJS_should_return_variable_data(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        test = common.extractJS(self.readTestInput("watch-byv-wpqDydI-superbass.html", False), variable="img.src", values=True)

        print repr(test)
        print str(len(test))
        assert(len(test) == 1)
        assert(test == ["http:\\/\\/o-o.preferred.nianet-cph1.v5.lscache2.c.youtube.com\\/generate_204?sparams=id%2Cexpire%2Cip%2Cipbits%2Citag%2Cratebypass\\u0026fexp=908525%2C903114%2C901700%2C906918\\u0026itag=43\\u0026ip=82.0.0.0\\u0026signature=2C47F606A39460B52686041818F80CF63F801404.0B2034BAB8762FF232D1E581A9E5EC9F2197C8E3\\u0026sver=3\\u0026ratebypass=yes\\u0026expire=1316012400\\u0026key=yt1\\u0026ipbits=8\\u0026id=6f2bfec29a83c9d2"])

    def test_extractJS_should_return_variable_data_no_quotation_marks(self):
        common  = CommonFunctions
        common.log = sys.modules["__main__"].log_override.log

        test = common.extractJS(self.readTestInput("watch-byv-wpqDydI-superbass.html", False), variable="img", values=True)

        print repr(test)
        print str(len(test))
        assert(len(test) == 2)
        assert(test == ["new Image()", "null"])

if __name__ == "__main__":
        nose.runmodule()
