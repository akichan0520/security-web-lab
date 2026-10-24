# 25｜手動CTF問題集：コマンドと理屈で解く（答え合わせ付き）

> **すべて `127.0.0.1:8767` の同梱ローカル演習環境専用**。一問ごとに「仮説→入力→HTTP応答→原因→修正」を記録。リモートの任意サーバーへそのまま送らない。

## 環境の起動

```bash
cd security-handbook
python3 lab/server.py
```

別ターミナルから検証。`Ctrl+C` で終了。ブラウザは `http://127.0.0.1:8767/`。

## 課題1｜HTTP観測：GETとPOST

1. `/lab/sql/vuln?name=Travel%20Kit`をGET。
2. 同じpathへPOSTして違いを観測。
3. HTTPコードが同じでも本文が違う場合がある理由を説明。

```bash
curl -i 'http://127.0.0.1:8767/lab/sql/vuln?name=Travel%20Kit'
curl -i -X POST 'http://127.0.0.1:8767/lab/sql/vuln' --data 'name=Travel+Kit'
```

<details><summary>解説と答え</summary>

GETは200で商品検索、POSTは実装がないので501（Python標準HTTPサーバーの未対応メソッド）になる構成。405と決め打ちしないこと。`Content-Type`やmethodはサーバー実装次第。

</details>

## 課題2｜SQLiの真偽判定

1. 正常の1件と0件を比較。
2. 真条件・偽条件で応答の件数が変わるか確認。
3. 安全版では何が起こるか説明。

```bash
curl -G 'http://127.0.0.1:8767/lab/sql/vuln' --data-urlencode 'name=Travel Kit'
curl -G 'http://127.0.0.1:8767/lab/sql/vuln' --data-urlencode "name=' OR '1'='1' -- "
curl -G 'http://127.0.0.1:8767/lab/sql/safe' --data-urlencode "name=' OR '1'='1' -- "
```

<details><summary>解説と答え</summary>

脆弱版ではSQLの字句境界が変わって複数件になる。安全版ではプレースホルダーで文字列として扱い0件。これはSQLite方言のローカルラボであり、MySQLと構文が同一とは限らない。

</details>

## 課題3｜反射型XSSのHTTPとDOMを比較

`<b>MARK</b>` を入力して脆弱版と安全版の生HTMLを比べる。`alert(1)`を使う前にHTMLが文字として表示されるか、タグとして解析されるかを確認。

```bash
curl -sS -G 'http://127.0.0.1:8767/lab/xss/vuln' --data-urlencode 'name=<b>MARK</b>'
curl -sS -G 'http://127.0.0.1:8767/lab/xss/safe' --data-urlencode 'name=<b>MARK</b>'
```

<details><summary>解説と答え</summary>

脆弱版の検索表示は生HTMLとして挿入される。安全版では`html.escape()`により文字として表示。PHPであればHTML本文に `htmlspecialchars()`。

</details>

## 課題4｜DOMベース：Responseにないのに画面にはある

1. `/lab/xss/dom-vuln?name=HELLO123`へアクセス。
2. `curl`でHTML本文に`HELLO123`があるか調べる。
3. DevTools Elementsに`HELLO123`があるか確認。
4. `/lab/xss/dom-safe`と違いを説明。

```bash
curl -sS -G 'http://127.0.0.1:8767/lab/xss/dom-vuln' \
  --data-urlencode 'name=HELLO123' | grep HELLO123 || echo 'not in raw response'
```

<details><summary>解説と答え</summary>

URL値はHTTPリクエストにあるが、サーバーがHTMLへ文字列を埋め込んでいない。ブラウザJavaScriptが `URLSearchParams` で読んで `innerHTML` へ渡すためDOMに出る。安全版は`textContent`で文字表示のみ。

</details>

## 課題5｜DIRBの論理をcurlだけで再現

1. `/lab/map/public`、`/lab/map/forbidden`、`/lab/map/absent`を比較。
2. 403で分かること／分からないことを説明。

```bash
for p in public forbidden absent; do
  curl -sS -o /dev/null -w "$p=%{http_code} size=%{size_download}\n" \
    "http://127.0.0.1:8767/lab/map/$p"
done
```

<details><summary>解説と答え</summary>

順に200、403、404（この演習環境）。403はアクセス拒否であり、他のユーザーがアクセスできる、あるいは特定のファイルが存在するという証明ではない。

</details>

## 課題6｜シェルのコマンド境界

OSへ攻撃を送らず、**自分のローカルターミナル**で比較する。

```bash
true && printf 'A\n'
false && printf 'B\n'
false || printf 'C\n'
printf 'D\n'; printf 'E\n'
```

<details><summary>解説と答え</summary>

A・C・D・Eが出力され、Bは出ない。終了ステータスとコマンド連結の意味を理解する。Webアプリが `subprocess.run([...],shell=False)`を使う場合、同じ入力文字列が同じ構文として解釈されるとは限らない。

</details>

## 課題7｜発見→修正→再テストの記録

それぞれの演習で以下を1ページにまとめてみよう。

```text
入力箇所と信頼境界:
比較した正常/異常入力:
Request/Response/DOMの相違:
脆弱性成立の理由:
攻撃可能性に必要な追加条件:
修正コードまたは防御策:
修正後の観測値:
公式資料URL:
```

## 解説対象外の範囲

他人のセッションや認証情報の取得、Webシェルの配置、実運用システムへの任意コマンド実行は、教材の練習範囲に含めていない。CTFの主催者が明示的に定めた範囲を超えて実行しない。
