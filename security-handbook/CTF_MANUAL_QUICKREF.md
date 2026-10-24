# CTF 手動検証・コマンド早見表（ローカル/許可CTF）

## HTTP：まず生レスポンスを見る

```bash
curl -i -G 'http://127.0.0.1:8767/lab/sql/vuln' --data-urlencode 'name=Travel Kit'
curl -sS -o /dev/null -w 'HTTP=%{http_code} len=%{size_download} t=%{time_total}\n' 'http://127.0.0.1:8767/'
```

## SQLi：通常1件/0件/真/偽を混同しない

```bash
curl -G 'http://127.0.0.1:8767/lab/sql/vuln' --data-urlencode "name=' OR '1'='1' -- "
curl -G 'http://127.0.0.1:8767/lab/sql/vuln' --data-urlencode "name=' OR '1'='2' -- "
```

## XSS：HTTPレスポンス→DOM

```bash
curl -G 'http://127.0.0.1:8767/lab/xss/vuln' --data-urlencode 'name=<b>MARK</b>'
```

```javascript
// DOMが読み込まれたあと、3番目のpを安全に変更
const p = document.querySelectorAll('p')[2];
if (p) p.textContent = 'CTF成功';
```

## OS：シェル文法（自分のターミナルだけで実行）

```bash
true && printf 'YES\n'
false || printf 'FALLBACK\n'
printf 'A\n'; printf 'B\n'
```

## DIRB系：候補パスを少数・低頻度で確認

```bash
for x in public forbidden absent; do
 curl -sS -o /dev/null -w "$x %{http_code} %{size_download}\n" \
  "http://127.0.0.1:8767/lab/map/$x"
done
```

## 判断の鍵

- **405** → HTTP Method。**500** → エラー種別。**200** → 本文が期待通りか。
- **SQLi** → SQLの文法に入力が混じるか。**XSS** → HTML/JSの文法に入力が混じるか。
- **OS注入** → シェルとして実行されるか。`$_GET`だけでは対策にならない。
- **DIRB** → 200/403/404を正規の未存在パスと比較。soft404に注意。
- **CTFメモ** → HTTP入力、観測差、成立理由、必要権限、修正後結果を残す。

詳細：[HTTP](docs/18-http-manual-curl.md) / [OS](docs/19-os-command-manual.md) / [XSS](docs/20-xss-manual-contexts.md) / [DIRB](docs/21-dirb-manual-discovery.md) / [演習](docs/25-manual-drills.md)
