# XSS：CTF実戦フィールドマニュアル

## 最短判別

| 観測 | 疑う問題 | 次の確認 |
|---|---|---|
| URLの値がHTTP Responseに混入 | 反射型XSSの入口 | HTML本文・属性・JS文字列のどこか |
| 投稿が保存・再表示 | 蓄積型XSSの入口 | 別セッション・再読み込み |
| Responseに値はないのにDOMに反映 | DOM-based XSS | `location.search`/`hash`→sinkの流れ |

反射、蓄積、DOMは直交する観点を含む。必ず「**どこがデータ源（source）で、どこが危険な出力先（sink）か**」を示す。

## 入力→HTTP→レスポンス→DOMの4点観測

1. 入力欄に `CTF_MARKER_123` を入れる。
2. Burp/Networkで **HTTPリクエストの送信先・パラメータ** を確認。
3. ResponseのHTML/JSON内でマーカーが存在するか確認。
4. ElementsのDOMに反映された場所と、Response元のHTMLを比較する。

Response内にない場合、DOM操作でURLやStorageの値を取り出している可能性もある。単に`?q=...`をURLに付けるだけでは実行されない。

## 反射位置ごとの防御を理解する

| 出力文脈 | 危険の原因 | 防御の第一候補 |
|---|---|---|
| HTML本文 | HTMLとして解釈 | HTMLエスケープ |
| HTML属性 | 引用符境界やイベント属性 | 属性としてのエスケープ + 属性名固定 |
| JavaScript文字列 | JSソースへ直埋め | JSON安全シリアライズ・JSへの直埋め回避 |
| URL (`href`) | 危険なURLスキーム | 許可スキーム・URL検証 |
| DOM (`innerHTML`) | HTMLとして再解析 | `textContent` / `createTextNode` |

### 3番目の `<p>` を書き換えるJavaScript（自分のブラウザでの学習）

```javascript
const p = document.querySelectorAll('p')[2];
if (p) p.textContent = 'CTF成功';
```

IDがある場合は `document.getElementById('target')`。`querySelectorAll('p')[2]` は **0始まり**なので3番目の要素を指す。DOMへの変更は「ページのソースを表示」の元HTMLとは異なる。

URL全文がCTFのフラグになる場合は、URL中の値がサーバーのHTMLへ反射されるか、ページJSが値を危険なsinkへ渡しているかを **実際のコードか通信** で確かめる。適当な`?name=`は根拠にならない。

## 安全実装

PHPのHTML本文：

```php
echo '<p>' . htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '</p>';
```

JavaScriptで文字列を表示：

```javascript
document.getElementById('target').textContent = userInput;
```

蓄積型XSSでは、PDOで安全にINSERTしても表示時に `innerHTML` などを使えばXSSが残り得る。**DBへの保存安全性とブラウザへの出力安全性は別**。

## エラー/観測の読み方

- 太字タグが有効になっただけでは **JS実行の証明ではない**。
- CSPでスクリプトが禁止されたなら、ConsoleのCSPエラーとヘッダーを確認。
- `innerHTML` に `<script>` 文字列を代入しても、ブラウザはそのscript要素を必ずしも実行しない。DOMイベント等の評価と分ける。
- HTTPで反射されていても、HTMLエスケープされていれば文字として扱われる。
- `HttpOnly` cookieはJSから直接読み取れないが、XSSの全影響を無効化するものではない。

## 根拠

- [PortSwigger XSS](https://portswigger.net/web-security/cross-site-scripting)
- [OWASP XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP DOM XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html)
