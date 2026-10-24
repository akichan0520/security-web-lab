# 18｜HTTPをコマンドで読む・再現する — Burpに頼らない観測

> 対象は同梱の `127.0.0.1:8767`、または主催者が明示的に許可したCTF。実Cookie・APIキー・フラグはログやGitHubへ保存しない。

## 1. 一番大切な考え方

ブラウザの画面は**HTTPレスポンスを加工した最終結果**であって、サーバーからの生データそのものではない。HTTPレスポンスとDOMを分離して観測する。CTF中は「1回で1変数だけ変える」「基準リクエストを保存する」「差分に理由を付ける」。

```text
URL → URL解析 → HTTPリクエスト(GET/POST, path, header, body)
→ Webサーバー → アプリ(PHP/Python) → DB/OS → HTTPレスポンス
→ HTMLパーサー → JavaScript → DOM → 画面
```

## 2. HTTPリクエストを手で読めるようにする

```http
GET /lab/sql/vuln?name=Travel%20Kit HTTP/1.1
Host: 127.0.0.1:8767
Accept: text/html
User-Agent: CTF-Learning
Connection: close
```

- `GET` はメソッド。**GETは常に安全、POSTは常に変更系というわけではない**。
- `/lab/sql/vuln` はpath、`name=...` はquery。`Host` は接続先の仮想ホストの選択に影響。
- `Content-Type` は主に**メッセージの本文**の形式を表す。POSTで`application/x-www-form-urlencoded`ならフォームデータとして解析されることが多い。
- `Cookie` は認証や状態管理に使われる場合がある。機密なので公開禁止。

## 3. curlを使ってHTTPを手動観測する

まず同梱ラボを起動：`cd security-handbook && python3 lab/server.py`。

```bash
# ステータス・ヘッダー・本文を観測
curl -i 'http://127.0.0.1:8767/lab/sql/vuln?name=Travel%20Kit'

# GET値をシェルで壊さずにURLエンコード
curl -i -G 'http://127.0.0.1:8767/lab/sql/vuln' \
  --data-urlencode 'name=Travel Kit'

# 通信詳細：接続先、送信メソッド、受信ヘッダー
curl -v 'http://127.0.0.1:8767/lab/sql/safe?name=Camera'

# HTTPコードと本文サイズの小さな比較
curl -sS -o /dev/null -w 'HTTP=%{http_code} bytes=%{size_download} sec=%{time_total}\n' \
  'http://127.0.0.1:8767/lab/sql/safe?name=Travel%20Kit'

# 取得したレスポンスをファイルへ（ローカル演習だけ）
curl -sS -D headers.txt -o response.html \
  'http://127.0.0.1:8767/lab/xss/safe?name=CTFTEST'
```

`-G` はクエリとして送信、`--data-urlencode` は適切にURLエンコード、`-i` はヘッダーを表示。`-v` は機密ヘッダーも出ることがあるため共有しない。`-sS` は進捗表示を抑えつつエラーを表示する。

## 4. POSTとJSONの違い（構文練習）

```bash
# このラボはGET専用。POSTは未実装で501が返る（実装によって405もあり得る）
curl -i -X POST 'http://127.0.0.1:8767/lab/sql/vuln' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'name=Travel+Kit'

# JSONを送信するHTTPの概念（このラボにはJSON APIはない）
curl -i -X POST 'http://127.0.0.1:8767/lab/demo/json' \
  -H 'Content-Type: application/json' \
  --data '{"name":"Travel Kit"}'
```

`-X POST`だけではパラメータは送れない。`-d`は本文を送信し、通常POSTを選択する。リクエスト形式を誤った場合の405・400・415を区別する。

## 5. 観測の3点セット：正常・不一致・異常

| 比較 | 同じにすること | 変えること | 学べること |
|---|---|---|---|
| A: 正常 | path, method, headers | `name=Travel Kit` | 1件表示を確認 |
| B: 不一致 | 同上 | `name=NoSuchItem` | 0件の通常動作 |
| C: 異常 | 同上 | `name='` | 入力の構文処理と例外の違い |

`500`は脆弱性の証明ではない。`404`はファイルなしと断定できない。`302`は`Location`、`Set-Cookie`、ログイン状態も見る。200でも内容が404相当の**soft 404**がある。

## 6. HTTPステータスを誤読しない

| ステータス | 一般的な意味 | CTFでの着眼 |
|---|---|---|
| 200 | 応答は成功 | 本文・件数・長さ・DOM差を比較 |
| 301/302/307/308 | リダイレクト | `Location`と元のURLの違い。メソッド変化にも注意 |
| 401 | 認証を要する | `WWW-Authenticate`、認証方法 |
| 403 | アクセス拒否 | 存在が示唆されても権限は別 |
| 404 | 対象が見つからない | ルート分岐・soft404と比べる |
| 405 | メソッド不許可 | GET/POSTおよび`Allow`ヘッダー |
| 415 | メディア形式非対応 | Content-Typeとボディの形式 |
| 500 | サーバー内部エラー | SQLエラーとは限らない。公開ログへ機密を出さない |

## 7. URLエンコード・HTMLエンコード・JavaScript文字列は別

```text
URL : name=%3Cb%3ECTF%3C%2Fb%3E
HTTPの受信側でURL復号 → <b>CTF</b>
HTMLの安全な本文表示 → &lt;b&gt;CTF&lt;/b&gt;
DOM表示 → 「<b>CTF</b>」という文字の表示（タグ実体化しない）
```

`%3C` と `&lt;` は別の処理。二重にエンコードしたため動かないケースと、意図せず二重にデコードする設計上の問題を区別する。一般に**入力の復号と出力エンコードを混同しない**。

## 8. 記録テンプレート

```text
日時・許可スコープ:
HTTP: GET /lab/sql/vuln?name=...
変化させた箇所: nameのみ
期待: ...
実際: HTTP=... / bytes=... / 本文=... / DOM=...
確定できたこと:
まだ証明できていないこと:
次の仮説:
修正案と再検証:
```

## 一次資料

- [curl manpage](https://curl.se/docs/manpage.html)
- [MDN HTTP overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
- [PortSwigger Burp Repeater](https://portswigger.net/burp/documentation/desktop/tools/repeater)
