# 19｜OSコマンドインジェクション：シェルの文法から理解するCTF現場ノート

> この章の実行例は自分の端末での `printf` 等の無害な出力に限定。Web入力からの検証は主催者の許可範囲で。Webシェル作成・任意ファイル書込み・資格情報収集を目的としない。

## 0. 核心は「文字列がシェル文法に昇格するか」

SQLiが「SQL文の構造」と「入力値」の混同であるのに対し、OSコマンドインジェクションは「**シェルが解釈するコマンド構造**」と「入力文字列」の混同。`$_GET['domain']` で受信しても危険は減らず、問題はその値を**どの実行APIに渡すか**。

```php
// 原理の説明用：危険な設計（公開サーバーで使わない）
$domain = $_GET['domain'] ?? '';
// exec('nslookup ' . $domain, $result);  // シェルに文字列連結

// 基本対策：シェルを呼ばない
if (!is_string($domain) ||
    filter_var($domain, FILTER_VALIDATE_DOMAIN, FILTER_FLAG_HOSTNAME) === false) {
    http_response_code(400); exit('invalid');
}
$records = dns_get_record($domain, DNS_A | DNS_AAAA);
```

## 1. シェルの構文記号を理解（ローカルターミナルで実行）

```bash
# ; は別のコマンドとして続行する
printf 'FIRST\n'; printf 'SECOND\n'

# && は前のコマンドが成功したときだけ
true && printf 'ON_SUCCESS\n'
false && printf 'NOT_PRINTED\n'

# || は前のコマンドが失敗したときだけ
false || printf 'ON_FAILURE\n'

# | は標準出力を後続の標準入力へ
printf 'hello\n' | tr 'a-z' 'A-Z'

# $(...) は内部コマンドの出力に置き換える
printf 'value=%s\n' "$(printf 'MARK')"
```

| 文法 | シェル上の意味 | 本当に注意する点 |
|---|---|---|
| `;` | 順番に実行 | ユーザー文字列がコマンド境界になる |
| `&&` | 成功時に次を実行 | 先行コマンドの終了コードに依存 |
| `||` | 失敗時に次を実行 | エラー経路でも予期しない動作 |
| `|` | stdoutを次のstdinへ | フィルタ動作を組み替えられる |
| `$(...)` | コマンド置換 | 文字列の一部分で実行され得る |
| `'` / `"` | 引用符 | シェルの語分割・展開に影響 |
| `>` / `<` | リダイレクト | ファイル入出力の副作用が生じ得る |

これらは**シェルでの意味**。HTTPで受け取っただけで実行されるわけではない。Pythonの `subprocess.run([...], shell=False)` や専用DNS APIでは境界が違う。

## 2. 観測段階と誤認しやすい現象

| 観測 | 何が言える？ | 言えないこと |
|---|---|---|
| 検索文字がそのまま表示 | 反射かもしれない | OS実行の証明ではない |
| 記号入力で500 | 例外処理が起きた | コマンド実行の証明ではない |
| 無害な目印が返った | コマンド出力がHTTPに反映された可能性 | コマンド実行権限の範囲は不明 |
| 本文差なし・時間差 | 時間応答型の可能性 | 通信遅延を除外していない |
| `No output` | stdoutが空または回収失敗など | コマンドが実行されていないという断定は不可 |
| `Permission denied` | OS権限の境界 | SQLiの不成立を示すものではない |

**CTFで重要**：開始前に「この入力が最終的にシェルへ渡される証拠があるか」を探す。`exec()` という関数名を見つけても、固定値のみならユーザー入力によるコマンド注入とは限らない。

## 3. stdout・stderr・終了コードを区別する

```bash
# 自分のシェルでの理解用。実行結果の違いを見る
printf 'normal\n'              # stdout
printf 'warning\n' >&2          # stderr
false; printf 'last code=%s\n' "$?"

# stdoutとstderrを統合して観察する（無害なローカル例）
sh -c "printf 'out\\n'; printf 'err\\n' >&2" 2>&1
```

`No output`はコマンド実行成功でもあり得る。`shell_exec()` は標準出力を返すがstderrは自動では含まない。`echo CTF_TEST` が取れて`pwd`が取れないなどのケースは「出力回収」か「実行コマンド」の別問題である。

## 4. Blind OS command injectionの原理

普通のコマンド注入では**stdoutがHTMLに出る**場合があるが、blindでは出ない。CTFでは応答時間、状態変化、管理下の観測点などを考える。遅延判定は**複数回・基準値との比較・処理時間の中央値**を記録し、無用な長時間遅延や大量リクエストは行わない。本文差がないだけでblindと断定しない。

## 5. PHPでの防御を層別に考える

1. **シェルを呼ばない**：DNS用途なら `dns_get_record()` などドメイン専用APIへ。
2. **型検証**：`$_GET['domain']` が配列で来る可能性を拒否。
3. **ドメイン形式検証**：`FILTER_VALIDATE_DOMAIN` + `FILTER_FLAG_HOSTNAME` は構文を制限するが、ドメインの存在や通信先の安全を保証しない。
4. **到達先・通信制限**：DNS問い合わせを許可しても内部ネットワークやDNS負荷への懸念は残る。
5. **権限・ログ**：PHPユーザーを非特権化、固定タイムアウト、レート制限。

```php
<?php
$domain = $_GET['domain'] ?? '';
if (!is_string($domain) || strlen($domain) > 253 ||
    filter_var($domain, FILTER_VALIDATE_DOMAIN, FILTER_FLAG_HOSTNAME) === false) {
    http_response_code(400);
    exit('invalid domain');
}
$records = dns_get_record($domain, DNS_A | DNS_AAAA);
if ($records === false) {
    http_response_code(502);
    exit('lookup failed');
}
header('Content-Type: application/json; charset=UTF-8');
echo json_encode($records, JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR);
```

## 6. OSコマンドインジェクションと引数インジェクションは異なる

シェルを使わず固定コマンドに引数を渡しても、**値が意図しないオプションとして解釈される**場合がある。たとえばオプションの先頭記号や引数の個数を厳格に扱い、許可された値だけを渡す。「シェルを避けた」だけで必ず完成ではない。コマンドにより `--` でオプション終端を示せるが、すべてに対応するとは限らない。

## 7. 初級→上級の判断順序

```text
入力パラメータがある
  → Webアプリの処理目的を推定（名前解決? 圧縮? ファイル変換?）
  → 専用APIか外部プロセスかを判定
  → シェル経由か、引数配列かを区別
  → 通常入力/不一致/特殊文字で挙動を比較
  → 何が実行・出力されるかを限定的に確認
  → OSの最小権限・エラー・ログを評価
```

### 事故と対策

- 任意コマンド実行によるサーバー改ざん、機密へのアクセス、サービス停止が起こり得る。
- 正しいドメイン形式だから**安全な宛先**とは限らない。
- DBの`FILE`権限とPHPのOS権限は別物。SQLiからOSコマンドへ行くには追加の条件が必要。

## 一次資料

- [OWASP OS Command Injection Defense](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)
- [PortSwigger OS command injection](https://portswigger.net/web-security/os-command-injection)
- [OWASP WSTG command injection](https://wstg.owasp.org/latest/4-Web_Application_Security_Testing/07-Injection/12-Command_Injection/)
- [PHP dns_get_record](https://www.php.net/manual/en/function.dns-get-record.php)
