# 20｜XSS：HTMLパーサー・JavaScript・DOMを手で追うCTFマニュアル

> 対象は同梱のローカル演習または許可されたCTF。証明は画面内の無害なテキスト変更・`alert(1)`などに限定。Cookie送信や他人のセッション取得を行わない。

## 0. XSSは「いつ・どのパーサーが・何として解釈するか」

XSSはSQLiと違ってブラウザ側で起こる。次の5つを**別々に**観測すること。

```text
入力値 → HTTP Request → HTTP Response (生HTML)
      → HTMLパーサー → JavaScript → DOM → 画面
```

例： `?name=CTF_MARK_824` を開き、**生レスポンスにマーカーがあるか**、ElementsのDOMにあるか、描画画面にあるかをそれぞれ確認する。生レスポンスにないがDOMに現れたら、ページのJavaScriptが作った可能性を疑う（それだけではDOM XSS成立の証明ではない）。

## 1. 反射型・蓄積型・DOM型の発生場所

| 類型 | 入力の移動先 | 判定の手掛かり | ありがちな誤解 |
|---|---|---|---|
| Reflected | HTTPレスポンスに埋め込まれる | リクエストと直後レスポンスの対応 | 画面に出ただけでXSS成立と断定 |
| Stored | DBや記録領域へ保存され、後で表示 | 再読込や別セッションでも残る | `INSERT`が安全ならXSSも防げる |
| DOM-based | JSがsource→sinkへ値を渡す | 生HTMLとDOM差、JSコードの追跡 | `location.search`の存在だけで脆弱と判断 |

### 重要：反射型とDOM型は排他的ではない

レスポンス中へ反射された値を、さらにJSが `innerHTML` へ移動すれば、両者が組み合わさる。名前の暗記より **source → transformation → sink** を追う。

## 2. 検証の順番（必ず段階を踏む）

```text
STEP 1: CTF_MARK_824                      // 一意な目印
STEP 2: <b>CTF_MARK_824</b>               // HTMLとして解析されるか
STEP 3: <script>alert(1)</script>         // 実行文脈に入るか（許可済ラボのみ）
```

同梱ラボでHTTPレスポンスを比較する：

```bash
curl -sS -G 'http://127.0.0.1:8767/lab/xss/vuln' \
  --data-urlencode 'name=<b>CTF_MARK_824</b>'

curl -sS -G 'http://127.0.0.1:8767/lab/xss/safe' \
  --data-urlencode 'name=<b>CTF_MARK_824</b>'
```

安全版は `&lt;b&gt;...` といったエンティティに変換される。`<b>`で太字になるのは**HTMLインジェクション**の手掛かりだが、JavaScript実行まで証明したわけではない。

## 3. XSSの出力文脈は5種類以上

| 入る場所 | 出力例（概念） | 見ること | 正しい防御 |
|---|---|---|---|
| HTMLテキスト | `<p>VALUE</p>` | `<` `>` がタグとして解析されるか | HTML本文エンコード |
| HTML属性 | `<input value="VALUE">` | 引用符が終わるか、属性名へ混入するか | **引用符を付け**属性エンコード |
| JavaScript文字列 | `<script>const q="VALUE";</script>` | JS文字列として正しくエンコードか | 値をJSONとしてシリアライズし適切に埋込 |
| URL属性 | `<a href="VALUE">` | URLスキーム、URLエンコード、属性エンコード | http/https許可・属性エンコード |
| DOM HTML sink | `element.innerHTML = VALUE` | JSからHTMLパーサーを呼ぶか | `textContent` / 安全なDOM API |
| CSS属性など | `style="...VALUE..."` | CSS文脈 | 任意の動的CSSを避け、限定許可リスト |

**`htmlspecialchars()`万能説は誤り**。HTML本文に出力するなら適切だが、JS・URL・CSS文脈には別の扱いが必要。

## 4. DOM操作の位置と実行時点

以前のCTFで「3番目の`<p>`を書き換える」が目標だった場合、DOMが読み込まれた時点で次のように指定できる。

```javascript
const ps = document.querySelectorAll('p');
if (ps.length >= 3) ps[2].textContent = 'CTF成功';
```

- `[2]` は**3番目**。`NodeList`は0から始まる。
- `getElementById('msg3')` はIDがある場合に使用可能。**同じタグの3番目と同じ意味ではない**。
- `textContent` はテキストとして代入。`innerHTML` はHTMLとして解析し、XSSのsinkとなり得る。
- `DOMContentLoaded` より前に対象要素が存在しない場合、対象が`null`/未取得になり得る。
- DevTools ElementsでのDOM変更はHTTPレスポンスやサーバーのファイルを書き換えない。

### 「URLにJavaScriptを書く」だけでは動かない

`http://127.0.0.1:8767/test.html?name=...` のようなURLを作っても、ページが入力をレスポンスに埋め込むかJSで取り込んで実行可能なsinkへ渡す仕組みがなければコードは実行されない。URLパラメータやfragmentの名前は**HTML/JS側の処理から特定する**。CTFのフラグがURL全文なら、開き直して同じ挙動が再現することを確認する。

## 5. source・sinkの実例（安全／危険）

```javascript
// source：ユーザーが変えられるURL値
const q = new URLSearchParams(location.search).get('q') ?? '';

// 安全：単なる文字列として表示
const el = document.getElementById('result');
el.textContent = q;

// 危険になり得る設計：HTMLとして解析する
// el.innerHTML = q;
```

`URLSearchParams` は単にURLを解析しているだけで防御ではない。`innerHTML`はHTMLを解析し、ユーザーの値を渡すと問題になる。**sinkに届くまでの変換を追うことが核心**。ページが `textContent` へ入れているなら、同じ入力によるHTML実行は原則成立しない。

## 6. 実際のHTTPとDOMを切り分けるコマンド

```bash
# 生HTMLに文字列が反射しているかを確認
curl -sS -G 'http://127.0.0.1:8767/lab/xss/vuln' \
  --data-urlencode 'name=CTF_MARK_824' | grep -o 'CTF_MARK_824'

# URLクエリを安全に作る（自分のラボ用）
python3 - <<'PY'
from urllib.parse import urlencode
print('http://127.0.0.1:8767/lab/xss/vuln?' + urlencode({'name':'<b>CTF</b>'}))
PY
```

生レスポンスが無くてもDOMに出る場合は、ブラウザのSourcesで `location.search` / `location.hash` / `URLSearchParams` / `innerHTML` / `insertAdjacentHTML` / `document.write` / `eval` 等の参照を検討する。**見つけただけでは危険かどうかは決まらない**。

## 7. CSPと実行に関する誤解

- `<script>`が生HTMLにあっても、CSPやパーサー挙動によって実行されないことがある。
- `innerHTML`に入れた `<script>` は、多くのブラウザでそのまま実行されない。**だからinnerHTMLが安全という意味ではない**。他のHTML構文が影響し得る。
- HTTPレスポンスヘッダーの`Content-Security-Policy`は重要だが、**CSPは出力エンコードの代替ではない**。
- `HttpOnly` CookieはJSから直接読めないが、XSSによる画面改変やアカウント操作すべてを防ぐわけではない。

## 8. CTF判断マトリクス

| 現象 | 次に何を見る？ |
|---|---|
| `<b>`が文字として見える | レスポンスで `&lt;` 化されているか |
| `<b>`が太字になる | HTML注入だがJS実行をまだ証明していない |
| 生HTMLにないがDOMにある | URL→JavaScript→DOMの追跡 |
| 開き直すと残る | Storedかブラウザ保存かを区別 |
| 3番目のpが変わらない | 実行タイミング・要素の個数・セレクタ |
| XSS証拠はあるのにalertなし | CSP・JSエラー・非実行文脈など |
| クリックしたときだけ挙動 | イベントハンドラ/ユーザー操作が必要な文脈 |

## 9. 根本対策

- HTMLテキスト：サーバー出力時の適切なHTMLエンコード。
- DOM：`textContent`、`createTextNode`、`setAttribute`の正しい使い方。安易な`innerHTML`は禁止。
- URL：リンク先の許可されたスキーム・ホスト等をチェック。
- リッチテキスト：信頼できるHTMLサニタイザ（例：DOMPurify）を使用。
- CSP・Trusted Types・Cookie属性・権限制御を多層防御として導入。

## 一次資料

- [OWASP XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP DOM-based XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html)
- [PortSwigger XSS contexts](https://portswigger.net/web-security/cross-site-scripting/contexts)
- [MDN innerHTML](https://developer.mozilla.org/en-US/docs/Web/API/Element/innerHTML)
