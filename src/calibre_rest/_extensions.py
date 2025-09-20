import os
import sys
import icu as _icu
import unicodedata as _ud

sys.path.insert(0,os.environ.get("CALIBRE_LIBRARY", "/usr/lib/calibre"))

class icu:
    unicode_version = _icu.VERSION
    NFC="NFC"
    NFD="NFD"
    NFKC="NFKC"
    NFKD="NFKD"
    UPPER_CASE="upper"
    LOWER_CASE="lower"
    TITLE_CASE="title"
    swap_case="swap"
    def change_case(w,s,x):
        if s == "lower":
            return w.lower()
        if s == "upper":
            return w.upper()
        raise RuntimeError((w,s,x))
    chr="chr"
    ord_string="ord"
    utf16_length="utf16_length"

sys.modules["calibre_extensions"] = sys.modules[__name__]

class speedup:
    @staticmethod
    def parse_date(_x):
        raise NotImplementedError
    def parse_iso8601(dt):
        dt, aware, tzseconds = speedup.parse_iso8601(date_string)
        return dt, aware, tzseconds

    clean_xml_chars="clean_xml_chars"
sys.modules["calibre_extensions.speedup"] = speedup

class sqlite:
    def set_ui_language(_lang):
        pass
sys.modules["calibre_extensions.sqlite_extension"] = sqlite

from calibre.constants import plugins
def _no_apsw(conn, name):
    pass
plugins.load_sqlite3_extension = _no_apsw
plugins.load_apsw_extension = _no_apsw


def _singleinstance(_x):
    return True
import calibre.db.cli.main as _main
_main.singleinstance = _singleinstance


from calibre.db.cache import Cache
Cache.fts_queue_thread = None


def _dateparse(date_string, assume_utc=False, as_utc=True, require_aware=False):
    from dateutil import parser
    return parser.parse(date_string)
from calibre.utils import iso8601
iso8601.parse_iso8601 = _dateparse
