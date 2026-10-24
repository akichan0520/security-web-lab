# 06｜OS Command Injection — DNS照会を例に

## 何が危険か

Webの入力値を文字列としてOSコマンドへ連結し、`exec()`/`shell_exec()`で**シェルに渡す**と、シェル構文（区切り・リダイレクトなど）に解釈される場合がある。

```php
// NG：概念上の脆弱な例（実サービスでは使わない）
$domain = $_GET['domain'] ?? '';
exec('nslookup ' . $domain, $output);
```

`$_GET['domain']`は**値を受け取るだけ**。代入そのものに安全化の作用はない。

## 推奨：用途別APIでシェルを排除

```php
$domain = $_GET['domain'] ?? '';
if (!is_string($domain) ||
    filter_var($domain, FILTER_VALIDATE_DOMAIN, FILTER_FLAG_HOSTNAME) === false) {
    http_response_code(400);
    exit('Invalid domain');
}

// サーバーが許可されたドメインだけを扱う用途なら、さらに許可リスト
$allowed = ['example.com', 'example.org'];
if (!in_array(strtolower($domain), $allowed, true)) {
    http_response_code(403);
    exit('Not allowed');
}

$records = dns_get_record($domain, DNS_A | DNS_AAAA);
if ($records === false) {
    http_response_code(502);
    exit('Lookup failed');
}
header('Content-Type: application/json; charset=utf-8');
echo json_encode($records, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
```

このコードは用途を説明する小さな例。運用では認証・アクセス制御、DNSクエリのレート制限、内部名前解決/リゾルバの設計、ログ管理を追加する。

### フィルターの役割

- `FILTER_VALIDATE_DOMAIN`：一般的なドメイン形式を検証。
- `FILTER_FLAG_HOSTNAME`：ホスト名としての要件を追加。**PHP公式は、付けないと空白やメタ文字まで許容し得ると明記**している。
- ただし**ドメイン形式が正しいことと、照会してよい対象であることは別**。内部DNS名、意図しない解決先、DNSリバインディング等は別に考える。
- `dns_get_record()`：PHPからDNSレコードを照会する関数。`exec('nslookup ...')`のような**シェル文字列連結**を不要にする。

## OSコマンドをどうしても使う場合

実行コマンドの固定、引数の厳格な分離、許可リスト、最小権限、タイムアウト、ログ管理を重ねる。`escapeshellarg()`のみを万能とみなさず、可能な限り専用ライブラリ/関数へ置き換える。

## SQLi・XSSとの共通原理

| ケース | 危険な混合 | 基本方針 |
|---|---|---|
| SQLi | SQLとデータ | バインド |
| OSコマンド | シェル文法とデータ | シェル自体を使わない |
| XSS | HTML/JS文法とデータ | 文脈別エンコード、安全なDOM API |

ローカルで動作を確認するサンプル：[DNS安全例](../examples/dns_safe_demo.php)。

**根拠**：[OWASP OS Command Injection Defense](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)、[PHP Validation Filters](https://www.php.net/manual/en/filter.constants.validation.php)、[PHP dns_get_record](https://www.php.net/manual/en/function.dns-get-record.php)、[OWASP SSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)。
