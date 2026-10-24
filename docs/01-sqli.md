# 01｜SQL Injection（SQLi）— 理論、観測、原因、対策

## なぜ成立するか

安全でない例（教育目的。実アプリでは使用しない）：

```php
$name = $_GET['name'] ?? '';
$sql = "SELECT name, price FROM products WHERE name = '$name'";
```

ユーザー入力が引用符の内側に無条件に埋め込まれる。引用符やSQL演算子が、**値ではなくSQLの構文**になり得る。SQLの実行はDBの権限で行われる。安全な実装は [PDO章](05-php-pdo.md)。

## 主な観測方式（用途と必要条件を混同しない）

| 手法 | 観測する差 | 条件 | 典型的な落とし穴 |
|---|---|---|---|
| Boolean-based Blind | 真・偽で本文、件数、長さが変わる | 応答が条件に依存 | 元の条件が偽／エラーを0件と誤解 |
| Time-based Blind | 応答時間が違う | DB遅延が観測可能 | ネットワーク遅延・タイムアウト |
| Error-based | DBエラーに診断情報が出る | 例外・エラー漏洩 | エラー番号と影響を混同 |
| UNION-based | 追加のSELECT結果が画面に現れる | 列数・型が適合し表示される | 列数だけ合っても型や出力位置が合わない |
| Stacked queries | 複数SQL文が実行される | ドライバー/DB設定が許可 | `;`が使えるだけでは成立しない |

### Boolean-basedの考え方

検索結果が0/1/複数件に分かれるWebアプリでは「真偽の結果がレスポンスにどう出るか」を比較する。ただし `1 OR 1=2` が返す値は、元の `1` の検索条件にも依存する。**比較ペアだけでなく、元のレコード存在とSQLエラーの有無も照合**する。

```
条件A（真） → 応答X
条件B（偽） → 応答Y
XとYの差は再現するか？
通常値や構文エラーと区別できるか？
```

`LENGTH()`・`SUBSTRING()`・`ASCII()`はSQL式の一部を検証するためのDB関数。二分探索は、符号点の範囲を毎回半分に絞るため、1文字の判定に必要な回数を減らせる。`ASCII()`を使う場合、非ASCII文字や文字コードの扱いには注意。

### Error-basedとEXTRACTVALUE

`EXTRACTVALUE()`はXML/XPathを扱うDB関数で、あるMySQL系環境では不正なXPath式に対して `XPATH syntax error` を返す。エラー文に式の一部が含まれると**診断メッセージが情報流出チャネル**となる。環境や実装によって関数の有無・エラー挙動は異なる。

```sql
-- MySQLの独立した教材DB内でエラー挙動を観察する概念例
SELECT EXTRACTVALUE(1, '~DEMO');
```

代表的な解析要素は `CONCAT()`（表示文字列の結合）、`information_schema.columns`（カラムのメタデータ）、`LIMIT`（対象行の制限）。実環境の情報・認証データをGitHubへ公開しない。

### UNIONの原理

```sql
-- 構造を理解するための固定値・独立クエリ例
SELECT 'item', 100
UNION ALL
SELECT 'DEMO', 200;
```

UNIONの各SELECTは**同じ列数**が必要で、対応する列の型に互換性が要る。画面に出る列はアプリのテンプレートで決まる。`--union-cols=2` はsqlmapの列数テスト設定であり、結果を表示することまで保証するものではない。

## 防御（原因との対応）

1. **値をパラメータ化**：`PDO::prepare()` と `execute()` / `bindValue()`。動的な値をSQLへ連結しない。
2. **識別子は許可リスト**：列名・テーブル名・ORDER BYの項目を安全な固定集合から選ぶ。プレースホルダーは通常、識別子の代わりにはならない。
3. **認可・最小権限**：SQLiがなくてもIDOR/権限漏れは残る。DBアカウントには必要なSELECT/UPDATE等のみ。
4. **詳細エラー非表示**：ブラウザへDBエラー/クエリを丸出しにしない。サーバーログには適切に記録。
5. **テスト**：正常、引用符を含む文字列、空、型違い、並べ替え、権限外IDをそれぞれ確認する。

## SQLiが見つかった時の報告テンプレ

- 入口（GET/POST、パラメータ、URLは匿名化）
- 真・偽・通常値・エラーのレスポンス差（再現性）
- SQL実行層とDBMSの根拠（推測なら明記）
- 可能性のある影響（DB権限で変わる）
- 修正案（該当箇所、パラメータバインド）
- 修正後の回帰テスト

**根拠**：[OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)、[sqlmap Techniques](https://github.com/sqlmapproject/sqlmap/wiki/Techniques)、[PHP PDO::prepare](https://www.php.net/manual/ja/pdo.prepare.php)。
