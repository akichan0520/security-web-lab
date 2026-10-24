# 一次資料・エビデンス台帳

**確認日：2026-10-24（参照先の内容は将来変更され得る）**

各章には本文中にも対応する公式リンクを入れている。この台帳は「どの主張を何で裏付けたか」をまとめる。一般論を個別のCTF環境での事実と混同しないこと。

| ID | 根拠資料（原典中心） | 裏付ける要点 | 適用範囲と限界 |
|---|---|---|---|
| S01 | [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html) | パラメータ化クエリ、識別子の許可リスト、最小権限 | 個々のPDOコードの実装品質までは保証しない |
| S02 | [PHP PDO::prepare](https://www.php.net/manual/ja/pdo.prepare.php) | prepare、プレースホルダーとデータ値の区別、PDO実装注意 | DBドライバー、エミュレーション設定差に注意 |
| S03 | [sqlmap Techniques](https://github.com/sqlmapproject/sqlmap/wiki/Techniques) | Boolean/Error/UNION/Stackedの分類 | 実ターゲットでの検出成功とは別 |
| S04 | [sqlmap Usage](https://github.com/sqlmapproject/sqlmap/wiki/Usage) | `-r`, `-p`, `--technique`, `--string`, `--os-shell`, ファイル操作オプション | 機能は権限・DB仕様に依存 |
| S05 | [PortSwigger Burp HTTP history](https://portswigger.net/burp/documentation/desktop/tools/proxy/http-history) | リクエスト・レスポンス観測 | Burpの版でUIが変わり得る |
| S06 | [PortSwigger Repeater](https://portswigger.net/burp/documentation/desktop/tools/repeater) | 手動送信・比較 | 許可された環境に限定 |
| S07 | [MySQL server system variables](https://dev.mysql.com/doc/refman/8.4/en/server-system-variables.html) | `secure_file_priv`, `datadir` 等の設定 | MySQL系列/版に注意 |
| S08 | [MySQL SELECT INTO](https://dev.mysql.com/doc/refman/8.4/en/select-into.html) | OUTFILE/DUMPFILE、制限、既存ファイル | 実際のOS権限は別 |
| S09 | [MySQL security against attackers](https://dev.mysql.com/doc/refman/8.4/en/security-against-attack.html) | DB権限・安全なファイル配置 | 設計指針であり個別製品の安全保証ではない |
| S10 | [OWASP Cross Site Scripting Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html) | 文脈別エンコード、安全なsink | JS・URL文脈には個別ルール |
| S11 | [PortSwigger XSS](https://portswigger.net/web-security/cross-site-scripting) | Reflected/Stored/DOMの定義 | 複合パターンもある |
| S12 | [OWASP OS Command Injection Defense](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html) | シェル排除・引数制御・許可リスト | 実行権限やOSで細部が変わる |
| S13 | [PHP Validation Filters](https://www.php.net/manual/en/filter.constants.validation.php) | FILTER_VALIDATE_DOMAIN、FILTER_FLAG_HOSTNAME | 形式検証はアクセス可否の許可ではない |
| S14 | [PHP dns_get_record](https://www.php.net/manual/en/function.dns-get-record.php) | DNSレコード取得API | リゾルバ/内部DNSの制約が残る |
| S15 | [OWASP SSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) | ドメイン検証だけでは安全を保証しない | DNSリバインディング等は構成依存 |
| S16 | [OWASP Error Handling](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html) | 例外表示で内部情報を漏らさない | 診断ログは別途保護が必要 |
| S17 | [PHP公式 News 2026-10-21](https://www.php.net/archive/2026.php#2026-10-21-5) | PHP2Shellの修正版の系列と緊急性 | 修正版は更新基準日当時の情報 |
| S18 | [PHP GHSA CVE-2026-109618](https://github.com/php/php-src/security/advisories/GHSA-w8hw-w9fx-j79w) | OOM起因のRCE可能性 | 実際の成立条件は構成による |
| S19 | [PHP GHSA CVE-2026-109619](https://github.com/php/php-src/security/advisories/GHSA-6wmf-4rv5-p3rp) | 状態残留に関係するRCE可能性 | 同上 |
| S20 | [IPA PHP2shell（2026-10-22）](https://www.ipa.go.jp/security/security-alert/2026/alert20261022.html) | 日本語での公式注意喚起 | 更新される可能性あり |
| S21 | [PHP shell_exec](https://www.php.net/manual/ja/function.shell-exec.php) | 標準出力・nullなどの実行仕様 | ファイル権限・SAPIで動作が異なる |
| S22 | [OWASP Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) | SQLi対策ができても認可不備は残る | プロジェクトごとに認可モデルが必要 |

## 「エビデンスあり」の扱い

- **仕様の根拠**：公式マニュアル・CVEアドバイザリなどで一般原理を説明できる。
- **CTFでの観測の根拠**：手元のHTTPレスポンス、コマンド表示、スクリーンショット等。**公開版には秘匿値を残さない**。
- **因果関係の根拠**：真/偽・修正前後・通常入力などの比較が必要。単なるHTTP500や`No output`は単独の証明ではない。
- **注意**：過去の会話から作った説明には、仮のパスや例示SQLが含まれる。本ノートは実端末・実DBの検証結果を保証しない。
