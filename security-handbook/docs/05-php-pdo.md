# 05｜PHP PDO — `prepare()` + `:name1` がなぜSQLiを防ぐのか

## 3つの別物を区別する

```php
$name = $_GET['name'] ?? '';       // PHP変数
$stmt = $pdo->prepare(
    'SELECT name, price FROM products WHERE name = :name1'
);                                 // :name1 はSQLプレースホルダー
$stmt->bindValue(':name1', $name, PDO::PARAM_STR);
$stmt->execute();
$rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
```

| 名称 | 役割 |
|---|---|
| `$name` | PHPで値を保持する変数 |
| `:name1` | SQLの値を後から渡すための**名前付きプレースホルダー**。末尾1は単なる名前の一部 |
| `$pdo->prepare()` | 構造が決まったSQL文の準備 |
| `$stmt->bindValue()` | 値をパラメータへ関連付け（型指定可） |
| `$stmt->execute()` | パラメータを用いてSQL実行。`execute(['name1' => $name])` も利用可 |

重要：`prepare()`と呼んでも**入力をSQL文字列に直接連結していたら防御にならない**。プレースホルダーは通常「テーブル名・列名・SQLキーワード」には使えない。

## なぜSQLiを防ぐか

- 危険な連結：入力がSQL構文の文字列の一部になってしまう。
- パラメータ化：SQLの**構造**と**データ値**を区別する。引用符や演算子を含む値を、条件式ではなく**検索値**として扱える。
- `PDO::ATTR_EMULATE_PREPARES => false` はサーバー側のネイティブprepareを要求する構成だが、これだけで他の欠陥を解決するわけではない。

## DBアクセス自体が安全でも残るリスク

- **ORDER BYへの直接埋め込み**：ソートする列名は許可リストから選ぶ。
- **認可不備**：他人のIDを指定できてしまう問題（IDOR）はSQLiがなくても起こる。
- **XSS**：DBから取り出した文字を`innerHTML`等へ直接入れる危険。
- **詳細エラー公開**：接続情報やSQLが漏れる。
- **過剰なDB権限**：不要な`FILE`、DDL、管理権限が被害を拡大。
- **ランタイム脆弱性**：PHP自体の不具合（後述PHP2Shell）はPDOでは防げない。

## ソート列の許可リスト例

```php
$allowedSort = ['name' => 'name', 'price' => 'price'];
$sortKey = $_GET['sort'] ?? 'name';
$column = $allowedSort[$sortKey] ?? 'name';

$stmt = $pdo->prepare("SELECT name, price FROM products ORDER BY $column");
$stmt->execute();
```

**重要**：この例は固定文字列の許可リストからのみ識別子が選ばれるため成立する。ユーザーの列名をそのままSQLへ埋め込む方法ではない。

## 一体テストの観点

- 正常な商品名で1件返る
- 引用符や`OR`を含む文字列が**単なる商品名として**扱われる
- 不正なソートキーは既定値にフォールバックする
- ログインユーザー以外の注文はサーバーで権限検査される
- エラーメッセージはブラウザでは汎用表示、詳細は安全なサーバーログへ

動作サンプル：[PDO SQLiteを使ったローカル例](../examples/pdo_safe_demo.php)。

**根拠**：[PHP PDO::prepare](https://www.php.net/manual/ja/pdo.prepare.php)、[OWASP SQLi Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)、[OWASP Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)。
