#!/usr/bin/env python3
"""Loopback-only demo. Deliberately vulnerable examples; never deploy publicly."""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from html import escape
import sqlite3
from pathlib import Path

HOST, PORT = '127.0.0.1', 8767
SEED = [('Travel Kit', 2500), ('Camera', 4900), ('Notebook', 600)]


def lookup(name: str, vulnerable: bool):
    with sqlite3.connect(':memory:') as db:
        db.execute('CREATE TABLE products (name TEXT, price INTEGER)')
        db.executemany('INSERT INTO products (name, price) VALUES (?, ?)', SEED)
        if vulnerable:
            sql = "SELECT name,price FROM products WHERE name = '" + name + "'"
            return db.execute(sql).fetchall()
        return db.execute('SELECT name,price FROM products WHERE name=?', (name,)).fetchall()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        request = urlparse(self.path)
        q = parse_qs(request.query)
        name = q.get('name', [''])[0]
        if len(name) > 1200:
            self.respond('Input too long', 400)
            return
        if request.path == '/':
            body = """<h1>Local CTF Practice</h1>
            <p>ローカル専用：架空のデータのみ</p>
            <ul><li><a href="/lab/sql/vuln?name=Travel+Kit">SQLi：脆弱版</a></li>
            <li><a href="/lab/sql/safe?name=Travel+Kit">SQLi：安全版</a></li>
            <li><a href="/lab/xss/vuln?name=CTFTEST">XSS：脆弱版</a></li>
            <li><a href="/lab/xss/safe?name=CTFTEST">XSS：安全版</a></li>
            <li><a href="/lab/xss/dom-vuln?name=CTFTEST">DOM-XSS：比較版</a></li>
            <li><a href="/lab/xss/dom-safe?name=CTFTEST">DOM-XSS：安全版</a></li>
            <li><a href="/lab/map/public">HTTPルート探索</a></li></ul>"""
            self.respond(body)
        elif request.path in ('/lab/sql/vuln', '/lab/sql/safe'):
            vulnerable = request.path.endswith('/vuln')
            try:
                rows = lookup(name, vulnerable)
                if len(rows) > 1:
                    summary = '複数の商品が見つかりました'
                elif len(rows) == 1:
                    summary = '1件見つかりました'
                else:
                    summary = '該当なし'
                data = ''.join(f'<li>{escape(str(x))}: {price}</li>' for x, price in rows)
                self.respond(self.form(name, request.path) + f'<p>{summary}</p><ul>{data}</ul>')
            except sqlite3.Error:
                # The HTTP 500 is intentional in this demo, but the full database
                # exception is not leaked in a real application.
                self.respond(self.form(name, request.path) +
                             '<p>SQL構文エラー（演習用の模擬エラー表示）</p>', 500)
        elif request.path == '/lab/map/public':
            self.respond('<h1>Public demo page</h1><p>CTF_MAP_PUBLIC</p>')
        elif request.path == '/lab/map/forbidden':
            self.respond('<h1>Access denied (training only)</h1>', 403)
        elif request.path in ('/lab/xss/dom-vuln', '/lab/xss/dom-safe'):
            unsafe = request.path.endswith('/dom-vuln')
            # This exercise demonstrates a browser-side source-to-sink boundary.
            # Server response never echoes the "name" value. Fixed localhost only.
            sink = "target.innerHTML = input;" if unsafe else "target.textContent = input;"
            body = ("<h1>DOM source/sink exercise</h1>"
                    "<p id='dom-target'>Before</p>"
                    "<script>const params = new URLSearchParams(location.search);"
                    "const input = params.get('name') || '';"
                    "const target = document.getElementById('dom-target');"
                    + sink + "</script>")
            self.respond(body)
        elif request.path in ('/lab/xss/vuln', '/lab/xss/safe'):
            vulnerable = request.path.endswith('/vuln')
            rendered = name if vulnerable else escape(name, quote=True)
            self.respond(self.form(name, request.path) +
                         f'<p>① 固定文章</p><p>② 固定文章</p><p>③ 固定文章</p>'
                         f'<p>検索語：{rendered}</p>')
        else:
            self.respond('Not found', 404)

    def form(self, value: str, path: str):
        return ('<form method="GET" action="' + escape(path, quote=True) + '">'
                '<label>検索名 <input name="name" value="' + escape(value, quote=True)
                + '"></label><button>送信</button></form>')

    def respond(self, body: str, status: int = 200):
        document = ('<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">'
                    '<title>LOCAL CTF ONLY</title><style>body{font:16px system-ui;'
                    'max-width:720px;margin:50px auto;padding:20px;line-height:1.7}'
                    'input{min-width:350px;padding:8px}button{padding:8px}'
                    '</style></head><body><a href="/">← menu</a>' + body + '</body></html>')
        output = document.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(output)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(output)

    def log_message(self, *_args):
        pass


if __name__ == '__main__':
    print(f'LOOPBACK DEMO ONLY: http://{HOST}:{PORT}/', flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
