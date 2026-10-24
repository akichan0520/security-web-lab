# 11｜PHP Webアプリのコードレビュー演習 — 発見→原因→修正

本章は「CTFで脆弱性を見つける」だけでなく、**安全なコードへ修正するためのレビュー手順**。以下はすべて架空の実装で、公開Webへ配置する攻撃コードではない。

## レビューの順番

1. **入力源（source）**：`$_GET`、`$_POST`、Cookie、ヘッダー、DBから読み戻した値。
2. **変換処理**：バリデーション、正規化、型変換、エンコード、認可チェック。
3. **使用先（sink）**：SQLクエリ、シェル、HTML出力、DOM、URL遷移など。
4. **信頼境界**：「値のはずだったもの」が「命令」として解釈されていないか。
5. **実行権限・影響**：DB権限、PHPプロセス権限、DB/アプリの分離。
6. **修正後の確認**：本来の機能を保ちつつ、入力値は値のまま処理されるか。

## パターンA：SQL検索

```php
// 危険：入力値をSQL構文の途中へ連結
$sql = "SELECT * FROM products WHERE name = '" . $name . "'";

// 対策：SQLとデータを分離
$stmt = $pdo->prepare('SELECT * FROM products WHERE name = :name1');
$stmt->execute(['name1' => $name]);
```

**原因**：SQLパーサーが結合された文字列を一つの構文として読む。**修正**：DBへ構造と値を明示的に渡す。**残存リスク**：別のSQL部位で動的な識別子やソートを連結していないか。

## パターンB：投稿の表示

```php
// 危険：DBに安全に保存できても出力時にHTMLとして解釈される
print '<p>' . $row['message'] . '</p>';

// 対策：HTML本文としてエスケープ
print '<p>' . htmlspecialchars(
    $row['message'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'
) . '</p>';
```

**原因**：DB保存とHTML解釈は別の境界。**修正**：表示先に適したエンコード。**残存リスク**：HTML本文以外のJavaScript、HTML属性、URL等には別の処理が必要。

## パターンC：JavaScriptのDOM操作

```javascript
// 危険：値をHTML構文として解析する
box.innerHTML = textFromApi;

// 対策：単なる文字列ならテキストとして扱う
box.textContent = textFromApi;
```

**原因**：`innerHTML`は信頼できないデータをDOM構文として解析する。**修正**：安全なDOM APIを使う。

## パターンD：DNS照会

```php
// 危険：シェルコマンドへ外部入力を連結
exec('nslookup ' . $domain, $output);

// 対策：先に検証し、専用APIを呼ぶ
if (filter_var($domain, FILTER_VALIDATE_DOMAIN, FILTER_FLAG_HOSTNAME) === false) {
    exit('invalid');
}
$result = dns_get_record($domain, DNS_A | DNS_AAAA);
```

**原因**：入力がシェルの構文になる。**修正**：シェルを排除。**残存リスク**：内部DNS、過剰照会、対象制限など。

## パターンE：ライブラリ/ランタイムのCVE

アプリが上記の修正を満たしていても、PHPや依存ライブラリの脆弱性は別に残る。**コードレビューだけでは解決できず、SBOM/バージョン/修正パッチ/ベンダー情報の照合**が必要。

## 修正確認用ミニテスト表

| テスト | 修正前の想定問題 | 修正後の期待結果 |
|---|---|---|
| 商品名に引用符が入る | SQLの解釈が変化 | 通常の文字列として検索 |
| コメントにHTML記号 | DOMの解釈が変化 | 文字列として表示 |
| ドメインに特殊文字 | シェルへ伝播 | 入力を拒否 |
| 不正な注文ID | 他人のデータ閲覧 | 403/404や権限内のみ |
| SQLエラー | 詳細エラー公開 | 利用者には一般エラー、内部ログへ詳細 |

**根拠**：[OWASP SQLi](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)、[OWASP XSS](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)、[OWASP OS Command](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)。
