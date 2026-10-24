import sys, unittest, threading
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import Handler

class RouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.base = 'http://127.0.0.1:' + str(cls.server.server_address[1])
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close()

    def read(self, route):
        with urlopen(self.base + route, timeout=2) as r:
            return r.status, r.read().decode('utf8')

    def test_map_public(self):
        status, html = self.read('/lab/map/public')
        self.assertEqual(status, 200)
        self.assertIn('CTF_MAP_PUBLIC', html)

    def test_map_forbidden(self):
        with self.assertRaises(HTTPError) as cm:
            self.read('/lab/map/forbidden')
        self.assertEqual(cm.exception.code, 403)

    def test_map_missing(self):
        with self.assertRaises(HTTPError) as cm:
            self.read('/lab/map/absent')
        self.assertEqual(cm.exception.code, 404)

    def test_dom_source_not_reflected_in_html(self):
        status, html = self.read('/lab/xss/dom-vuln?name=CTFTEST923')
        self.assertEqual(status, 200)
        self.assertNotIn('CTFTEST923', html)
        self.assertIn('target.innerHTML = input;', html)
        status, safe_html = self.read('/lab/xss/dom-safe?name=CTFTEST923')
        self.assertEqual(status, 200)
        self.assertIn('target.textContent = input;', safe_html)
