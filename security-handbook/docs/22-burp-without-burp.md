# 22｜Burp Suiteでの観測を「HTTPを読める力」に置き換える

> Burp Repeaterは便利だが、勝敗を分けるのはツールではなく、どの1バイトを変えて何を観測したか。以下はCTFの手動検証・再現・レポートに使う。

## 1. Burpの主要画面と役割

| Burpの機能 | 見ている本質 | 手動・コマンドでの代替 |
|---|---|---|
| Proxy HTTP history | ブラウザの通信履歴 | F12 Network、`curl -v` |
| Repeater | HTTP要求の少しずつの変更 | `curl -i -G --data-urlencode` |
| Decoder | エンコード変換 | Python `urllib.parse`、URLデコード |
| Comparer | 2つの応答差 | `diff -u response_a response_b` |
| Intruder | 入力候補を入れ替えて繰返し | 少数候補のみ手動・ループ（許可範囲） |
| Logger | 再現性の証拠 | ヘッダー・本文・日時を記録 |

ツールに頼らないとは、**HTTPメッセージとブラウザの実行結果を区別できる**こと。

## 2. リクエストを1つ保存して3つの応答を比べる

```bash
BASE='http://127.0.0.1:8767/lab/sql/vuln'
curl -sS -G "$BASE" --data-urlencode 'name=Travel Kit' -o A.html
curl -sS -G "$BASE" --data-urlencode 'name=NoSuchItem' -o B.html
curl -sS -G "$BASE" --data-urlencode 'name=CTF_TEST' -o C.html

diff -u A.html B.html || true
```

通常値から**一度に複数条件を変えない**。これを守らないと見た目の差がどの入力の影響か分からなくなる。

## 3. 生HTTPリクエスト：これだけで問題を切り分ける

```http
POST /submit HTTP/1.1
Host: ctf.local
Content-Type: application/x-www-form-urlencoded
Cookie: session=REDACTED
Content-Length: 17

name=Travel%20Kit
```

- リクエスト行：method・path・protocol version
- `Content-Type`：ボディの解析方法
- `Content-Length`：本文のバイト数（手で書き換えるなら再計算が必要）
- Cookie：秘密情報。公開のスクリーンショットやREADMEへ絶対載せない
- 改行1行：headersとbodyの区切り

**GETなのにPOSTで送る→405**、パラメータ名を`name=`のまま`-p`に書く→対象認識が狂う、といった典型的なミスが以前の演習でも起きた。

## 4. HTTPとHTMLとDOMの差を例で示す

```text
Request : GET /lab/xss/vuln?name=%3Cb%3ECTF%3C%2Fb%3E
Response: <p>検索語：<b>CTF</b></p>
DOM     : <p>検索語：<b>CTF</b></p>
画面    : 検索語：CTF（太字）
```

安全版ではResponseに`&lt;b&gt;`として入り、ブラウザには文字として見える。Burp Responseに見えないのにElementsに現れるなら、JSによるDOM変形を検討。

## 5. URL・文字コードの手動確認

```bash
python3 - <<'PY'
from urllib.parse import quote, unquote, urlencode
s = '<b>CTF</b>'
print('ENCODE:', quote(s, safe=''))
print('DECODE:', unquote('%3Cb%3ECTF%3C%2Fb%3E'))
print('QUERY :', urlencode({'name': s}))
PY
```

``などの見慣れない文字列はどの段階で復号されるかを追う。URLエンコードとHTMLエンコードは異なる。

## 6. レスポンス比較時の注意

- Cookie、CSRFトークン、時刻、広告、nonce、圧縮の影響で差が出る。脆弱性の差だと断定しない。
- `--string`相当の真偽判定文字列は**HTTPレスポンス本文**に実在する必要がある。JS描画後だけの文字列は使えない。
- チェックを自動化する前に、手で真条件・偽条件が2〜3回安定するか確認。

## 7. 観測から一歩進む：サーバー側とクライアント側の責任範囲

```text
Web検索欄 → HTTP → Python/PHP → DB
                        ↓
                     HTML応答
                        ↓
          HTMLパーサー → JS → DOM
```

- SQLiは主に**DBへSQL構文を渡した**とき。
- OS command injectionは主に**OSシェルへユーザー値を渡した**とき。
- XSSは主に**HTML/JSの命令として入力値が扱われた**とき。

WebアプリがPython/Werkzeugなら、PHPコードをWebに置いてもPHPとして動くとは限らない。構成を根拠なく推定しない。

## 一次資料

- [Burp Repeater](https://portswigger.net/burp/documentation/desktop/tools/repeater)
- [Burp Comparer](https://portswigger.net/burp/documentation/desktop/tools/comparer)
- [curl公式](https://curl.se/docs/manpage.html)
