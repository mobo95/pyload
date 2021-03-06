# -*- coding: utf-8 -*-

from module.plugins.internal.MultiHook import MultiHook


class SimplydebridCom(MultiHook):
    __name__    = "SimplydebridCom"
    __type__    = "hook"
    __version__ = "0.04"

    __config__ = [("pluginmode"    , "all;listed;unlisted", "Use for plugins"                     , "all"),
                  ("pluginlist"    , "str"                , "Plugin list (comma separated)"       , ""   ),
                  ("revertfailed"  , "bool"               , "Revert to standard download if fails", True ),
                  ("retry"         , "int"                , "Number of retries before revert"     , 10   ),
                  ("retryinterval" , "int"                , "Retry interval in minutes"           , 1    ),
                  ("reload"        , "bool"               , "Reload plugin list"                  , True ),
                  ("reloadinterval", "int"                , "Reload interval in hours"            , 12   )]

    __description__ = """Simply-Debrid.com hook plugin"""
    __license__     = "GPLv3"
    __authors__     = [("Kagenoshin", "kagenoshin@gmx.ch")]


    def getHosters(self):
        html = self.getURL("http://simply-debrid.com/api.php", get={'list': 1})
        return [x.strip() for x in html.rstrip(';').replace("\"", "").split(";")]
