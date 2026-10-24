# SQLインジェクション：CTF実戦フィールドマニュアル

> 対象：自分の `127.0.0.1` 演習環境、または主催者が明示的に許可したCTF。実IP、Cookie、パスワード、フラグは公開しない。
>
> この章は **発見 → HTTP再現 → 原因特定 → 方式分類 → 影響評価 → 修正 → 再テスト** の順に、作業中そのまま参照できることを目標にする。コマンドの `127.0.0.1:8767` は同梱ローカルラボに限定。

## 0｜30秒で判断する早見表

| 画面で観測した現象 | 最初に疑うこと | 比較するもの | 誤判定の注意 |
|---|---|---|---|
| `'` だけで500 | 引用符でSQL文が壊れた | 通常文字列・特殊文字・エラー詳細 | 500はSQLi成立の証明ではない |
| 真条件と偽条件で結果が変わる | Boolean-based blind | 1=1 と 1=2 を同一文脈で比較 | 元の検索条件が真かを固定する |
| 応答本文が同じなのに時間差 | Time-based blind | 同一条件を複数回測定 | 通信遅延と区別する |
| カラム数エラーが変化 | UNION条件の推定 | SELECT列数・型・表示位置 | 2列判明≠2列とも表示可能 |
| SQL関連の詳細エラーに値が出る | Error-based | 原因DB関数・エラー内容 | DBMSの版で動かない関数がある |
| SQLmapが405ばかり出す | HTTPメソッド/URL違い | Chrome/Burpとの通信差 | サーバーやアプリの特性を確かめる |
| `No output` | シェル結果未取得・権限・未実行 | 終了コード、stdout/stderr | ファイルが存在しない証拠にはならない |

---

## 1｜事前準備：スコープを定義

許可範囲をノートに明記する。

```text
演習名: LOCAL-SQLI-01
許可されたホスト: 127.0.0.1:8767
対象機能: /lab/sql/vuln?name=...
破壊的変更: 実施しない
保存する証拠: 入力値・HTTPステータス・レスポンス文字列（架空データのみ）
禁止: 第三者サーバーへの試行、セッション情報のGitHub公開
```

Burpを使う場合はHTTP historyから **Method / Host / Path / Query / Body / Cookie / Content-Type** を控える。特に GET/POST を誤ると SQLmapに405が出ることがある。ブラウザが描画した文字列がHTTPレスポンスにあるとは限らない。JavaScriptが後で生成した文言ではないか確認する。

## 2｜基本モデル：なぜ入力がSQL構文になるのか

安全でない例：

```python
name = request_value
sql = "SELECT id, name FROM products WHERE name = '" + name + "'"
```

本来のクエリは文字列リテラル `'旅行セット'` と比較するだけだが、ユーザー入力に引用符などが混ざるとSQLの **字句解析・構文解析** に作用する。DBはHTTPを知らず、完成したSQLだけを解釈する。失敗の根本原因は「**SQL構造とユーザー入力の境界が消える**」こと。

安全な代替：

```python
cursor.execute("SELECT id, name FROM products WHERE name = ?", (name,))
```

PDOの場合は [`prepare` と `:name1`](05-php-pdo.md)。**`prepare()` の呼び出しそのものより、動的な値を正しくバインドしているか**が重要。

## 3｜ローカルラボで最初に試す四つの入力

起動：リポジトリの `security-handbook/` で `python3 lab/server.py`。ブラウザ：`http://127.0.0.1:8767/`。

以下は同梱ラボの **架空の商品検索** にだけ使用する値。`name` はWeb入力欄に相当する。

| 番号 | 入力値 | 期待する現象 | 意味 |
|---|---|---|---|
| A | `Travel Kit` | 1件 | 通常値の基準 |
| B | `NoSuchItem` | 0件 | 通常の不一致 |
| C | `' OR '1'='1' -- ` | 複数件 | 真条件の比較材料 |
| D | `' OR '1'='2' -- ` | 0件 | 偽条件の比較材料 |

MySQLでは `--` コメントに空白などの条件がある。**上表の末尾には空白がある**。このラボはSQLite方言で動くため、別のCTFへそのままコピペして同じ結果になるとは限らない。入力の型・引用符・括弧・WHERE文脈が違えば結果も違う。

### 重要：`OR 1=2` で「偽」が証明されない場合

`WHERE name='Travel Kit' OR 1=2` は商品自体が見つかれば **真**。真偽ペアは元条件を常に偽にできる値で比較するか、元条件を固定して `AND` の結果を比較する。

### HTML表示の「1件」「複数」「検索失敗」の差

レスポンス本文、HTTP status、文字列長、処理時間を分けて記録。「検索失敗」は0件なのかSQLエラーなのか区別する。通常値・該当なし・構文エラーで3点比較する。

## 4｜Boolean-based blind：一文字ずつ推測する原理

```text
対象値がASCII値で 100 より大きい？
       ├─ TRUE  → 検証対象を 101 以上へ狭める
       └─ FALSE → 検証対象を 100 以下へ狭める
```

二分探索では範囲を半分ずつ絞る。例えばASCIIの 32〜126（95通り）なら約7回の比較で1文字を推定できる。ただしDB照合順序、NULL、関数の結果、符号化方式に注意。

概念的なMySQL式（独立したSQL式として読むための例）：

```sql
SELECT ASCII(SUBSTRING('DEMO', 1, 1)) > 70;
SELECT LENGTH('DEMO') > 3;
```

`ASCII()` / `SUBSTRING()` / `LENGTH()` は値の一部分を条件へ変換する道具。**情報の取得そのものではなく、TRUE/FALSEを繰り返し観測する**のがblind方式。

**確認チェック**

- [ ] 真/偽が各3回以上安定して再現する
- [ ] 0件とSQLエラーを取り違えていない
- [ ] URLエンコードの有無で結果が変わらない
- [ ] 応答本文に「真」を表す文字列が確かにある
- [ ] サーバーへ負荷をかけすぎない

## 5｜Time-based blind：HTTP本文が同じでも観測できる場合

MySQLのSQL式の **概念例**：

```sql
SELECT IF(1=1, SLEEP(2), 0);
```

ただし、この構文はDBMS依存であり、たとえばSQLiteにそのまま適用できない。ネットワーク遅延を区別するため、正常リクエストと条件付きリクエストを交互に複数回測定。中央値・分散を記録し、攻撃的な長時間遅延や高並列は避ける。

## 6｜UNION-based：2列なら何を確かめる？

UNIONには以下の前提がある。

1. 左右のSELECTの **出力列数が一致** する。
2. 対応列の **型に互換性** が必要。
3. アプリがどの列を **HTMLに表示するか** 別途確認が必要。
4. 先頭の元レコードと追加レコードの並びは保証されない。

MySQL/SQLite両方で読める **独立クエリ**：

```sql
SELECT 'Travel Kit' AS name, 2500 AS price
UNION ALL
SELECT 'CTF_TEST' AS name, 0 AS price;
```

CTFで列数が2列と分かっても、そのうち文字列表示に使えるのがどの列かまでは確定しない。`NULL` で列数と型の影響を切り分け、画面のテンプレート側も確認する。

**SQLmapの意味**：`--technique=U --union-cols=2` は「UNION検証を2列に限定」の指定であり、データの表示や取得の保証ではない。

## 7｜Error-based：EXTRACTVALUEとDBエラー

古い学習資料で見る `EXTRACTVALUE()` は、XML/XPathの評価エラーから情報が画面に出る挙動の説明によく登場する。**DBMS、版、関数の有無、エラー処理に依存する**ので、CTFの環境で再確認すること。

MySQL系の **独立した式** の例：

```sql
SELECT EXTRACTVALUE(1, '~DEMO');
```

意味：XPathとして解釈できない引数によってエラーが発生し、詳細なDBエラーをHTTP本文へ表示するアプリでは、診断情報が漏れることがある。`CONCAT()`（文字列連結）、`information_schema`（DB構造）、`LIMIT`（対象行）も周辺概念。**サブクエリ・SQL式の成否と、OSファイルの読取り能力は別物**。

注意：`information_schema` の綴りは `infomation_schema` ではない。SQL構文エラー1064、XPathエラー1105、未知の関数1305は意味が異なる。

## 8｜Burp Repeater：観測の証拠を作る

GETの架空リクエスト：

```http
GET /lab/sql/vuln?name=Travel%20Kit HTTP/1.1
Host: 127.0.0.1:8767
Accept: text/html
Connection: close
```

**手順**：通常値で200を記録 → Repeaterで `name` だけ変更 → HTTP statusと本文を並べて比べる → Responseの実文字列を記録 → 実行回数・時刻・結果の再現性を記録。

**POSTの場合**は method と body と Content-Type の両方を同じ通信から保存する。Burpの「Copy to file」などを使って完全なHTTPリクエストを保存すると、SQLmapの`-r`で利用できる。

## 9｜sqlmapのチートシート：意味を理解して使う

以下は**同梱のローカルラボにだけ適用する例**。通常アクセスで動作を確認してから実行する。

```bash
# 基本調査（ローカル専用の検証用URL）
sqlmap -u 'http://127.0.0.1:8767/lab/sql/vuln?name=Travel%20Kit' \
  -p name --technique=B --batch --threads=1 --delay=0.2

# Burpで保存した、同じローカルHTTPリクエストを再現
sqlmap -r request.txt -p name --technique=B --batch -v 3

# SQLmapが送ったリクエストとレスポンスをログへ保存
sqlmap -r request.txt -p name --technique=B -t traffic.txt -v 3
```

**オプションの意味**

| オプション | 説明 | 失敗時のチェック |
|---|---|---|
| `-u` | URLとパラメータを指定 | URL先が実際に存在するか |
| `-r` | Burpの生HTTPリクエスト | Cookie/Host/POST bodyが合っているか |
| `-p name` | `name`キーだけを検証 | `name=`と書かない |
| `--technique=B/E/U/T` | Boolean / Error / UNION / Timeに絞る | 該当DB方言と入力文脈 |
| `--string` | TRUE応答に実際にある文字列 | JS生成の表示なら原文にない |
| `--not-string` | FALSE応答の文字列 | 真偽のラベルにエラー表示を混ぜない |
| `--dbms=MySQL` | DBMSを指定 | 不明なら固定しない |
| `--union-cols=2` | UNIONの列数範囲を2に限定 | 列の表示有無は別 |
| `--prefix`,`--suffix` | 特定文脈へ組み込む補助 | 引用符/コメントが重複しないか |
| `--flush-session` | 解析セッションを破棄 | 再検出が必要なときだけ |
| `--batch` | 問い合わせを既定値で回答 | 意図しない自動回答に注意 |
| `-t` | HTTP通信ログ保存 | 秘匿値をGitHubに公開しない |

### 405 / 500 / not injectable の違い

- **405 Method Not Allowed**：URL/Method不一致が第一候補。ブラウザの実通信と比較。
- **500 Internal Server Error**：SQLエラーやアプリ例外など多くの原因。詳細ログが必要。
- **not injectable**：sqlmapのその条件・技術では検出できなかった。安全の証明ではない。
- **未知のDB関数 1305**：DBMS推測で試した関数がない可能性。「全部失敗」ではない。
- **タイムアウト**：過負荷、ネットワーク、レート制限。検証間隔を空ける。

## 10｜DB構造を読む方法と限界

```text
データベース → テーブル → カラム → 行
      例：demo_db → products → name,price → Travel Kit,2500
```

MySQLの `information_schema.tables` / `columns` は **メタデータ**。その存在から「全データを読める」とは結論づけられない。DB接続ユーザーの権限・ビュー・アプリのSQLi文脈に左右される。既知の架空データだけを使い、フラグや認証情報はリポジトリへ載せない。

## 11｜DBとOSの境界：FILE・secure_file_priv

- `@@datadir` はデータファイル配置先。Webルートとは限らない。
- `@@secure_file_priv` が空文字列なら、この設定によるディレクトリ制限がないことを意味するが、FILE権限やOS権限は必要。
- `NULL` は当該入出力機能を制限する設定。空文字列とは異なる。
- SQLiが見つかっても **OSシェルを取得できるとは限らない**。実DBサーバーとWebサーバーが別コンテナのこともある。
- `find / -type f -name 'sample.txt'` は **OSでのファイル名検索**。SQLmapの `--search` はDB名等の検索で別物。

**ファイル名検索の学習**（ローカルの安全なフォルダだけ）：

```bash
mkdir -p /tmp/ctf-example
printf 'example\n' > /tmp/ctf-example/sample.txt
find /tmp/ctf-example -type f -name 'sample.txt'
```

DB権限を起点としたWebシェル配置や任意コマンド実行は、複数の権限境界が破れる危険な連鎖であり、本公開教材では **成立条件・検知・防御設計** を中心に扱う。

## 12｜修正手順：同じURLで比較する

**危険**（文字列連結）：

```php
$sql = "SELECT * FROM products WHERE name = '" . $name . "'";
```

**安全**（PDO名前付きパラメータ）：

```php
$stmt = $pdo->prepare(
  'SELECT * FROM products WHERE name = :name1'
);
$stmt->bindValue(':name1', $name, PDO::PARAM_STR);
$stmt->execute();
```

**加えて必要**：識別子の許可リスト、認可チェック、DB最小権限、詳細エラーの利用者向け非表示。`prepare`が1か所あるだけでサイト全体が安全になるわけではない。

### 修正後の回帰テスト

| ケース | 安全実装の期待値 |
|---|---|
| 正常な商品名 | 該当商品のみ |
| 検索対象なし | 0件 |
| `' OR '1'='1' -- ` | その文字列に一致する商品がなければ0件 |
| 引用符だけ | 0件、SQL構文エラーを画面に出さない |
| 空文字列 | 仕様通り扱う |
| 不正な `sort` キー | 許可済みのデフォルト列にフォールバック |

## 13｜CTF現場チェックリスト

- [ ] ルールと許可対象URLを記録した
- [ ] 通常入力でWeb機能を理解した
- [ ] GET/POST、パラメータ、body、Cookieを確認した
- [ ] HTTP応答の生データを観測した
- [ ] SQLi方式を確定前に断定していない
- [ ] 同じ条件で複数回再現した
- [ ] DBMS/バージョンは根拠とともに記録した
- [ ] SQLmapのオプションの意味を説明できる
- [ ] DBデータとOSファイル/権限を区別できる
- [ ] フラグ、認証情報、Cookie、実IPを公開資料から除去した
- [ ] 修正策を記載した
- [ ] 安全実装で同じ条件を再テストした

## 14｜参考文献・根拠

- [PortSwigger SQL injection](https://portswigger.net/web-security/sql-injection) — 概念とラボ
- [PortSwigger SQLi Cheat Sheet](https://portswigger.net/web-security/sql-injection/cheat-sheet) — DBMSごとの式の違い
- [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html) — パラメータ化と最小権限
- [SQLmap Usage](https://github.com/sqlmapproject/sqlmap/wiki/Usage) — コマンドオプション
- [SQLmap Techniques](https://github.com/sqlmapproject/sqlmap/wiki/Techniques) — 検出方式
- [MySQL XML Functions](https://dev.mysql.com/doc/refman/8.4/en/xml-functions.html) — XML/XPath関数の仕様
- [PHP PDO::prepare](https://www.php.net/manual/ja/pdo.prepare.php) — 名前付きプレースホルダー

**証拠の強さ**：上記は一般技術・仕様の根拠。あなたが検証しているCTFでの成立を裏付けるには、HTTP応答・再現条件・バージョンなどの独立した観測が必要。
