# 12｜匿名化CTFケーススタディ — 調査結果と不確実性

> ここに記載した値は**過去の演習に基づく匿名化した観測の整理**。リモート環境や実データの復元に使える証拠一式ではない。変数やエラーの振る舞いは環境・バージョンによって変わる。

## ケース1：検索欄で件数・エラーが変わる

- 入口：`GET /stock?name=...` のような検索。
- 観測：一部の真偽条件で「複数」「検索できない」等の異なるメッセージ。
- 別の観測：sqlmapがBoolean-based Blindと検出し、MySQLの情報を確認できた。
- 読み方：**レスポンス本文の差を真偽判定に利用できる可能性**。元のWHERE句や0件とSQLエラーの扱いを併せて確認する。
- 根本原因：入力値が安全に分離されずSQL構文へ入ること。
- 対策：パラメータ化、SQLエラー非公開、DB権限最小化。

## ケース2：SQLmapの405と500

- 観測：`405 Method Not Allowed`、`500`、`FUNCTION ... does not exist` など。
- 誤判定：これらだけで「SQLiが成立」「DBが破壊された」とは言えない。
- 調査：ブラウザとsqlmapで実際に送ったMethod/Path/Bodyを比較。DBMS判別のテスト関数やサーバー側のエラー記録も確認。
- 対策：公開レスポンスに詳細内部エラーを出さず、運用者には追跡可能なログを残す。

## ケース3：SQLi → DBのファイル設定 → OS環境

- 観測：`@@datadir` のようなMySQL設定の値、別途 `pwd` で`/app` を表示、`find` で演習用ファイル名の場所を確認。
- ここから言えること：**DB内データとOSファイルシステムは別の扱い**。ファイル名の所在確認も、OSからの読み取り権限を保証しない。
- 誤判定：`No output`を即「ファイル不存在」と解釈しない。`find /`に `-type f -name` が必須というわけではない。
- 対策：DBのFILE権限、Web公開領域の書き込み可否、OS権限、サーバー分離を確認。

## ケース4：XSSと3番目の`<p>`

- 演習の目的：ブラウザ上の3番目の段落の文字列を変更する。
- 実装概念：`document.querySelectorAll('p')[2].textContent = 'CTF成功';`
- 重要：DOMが変わることと、**他者が同じURLを開くと実行されること**は別。`?q=...`で値が反射されないなら、URLだけでは成立を確認できない。
- 調査：Network > Responseの反射、SourcesにURLを読むJS、DOM sink、CSPを区別。
- 対策：出力時エンコード、`textContent`、保存値の表示エスケープ、必要に応じたCSP。

## ケース5：PHPがDNS照会する機能

- 改善前：`exec('nslookup ...')` でシェルを介する。
- 改善後：`filter_var`で文字列形式を検証し、`dns_get_record()`でDNS専用APIを使う。
- 最重要：安全化の理由は**入力を`$_GET`へ代入したからではなく、OSシェルを使う構造を変更したから**。
- 残存リスク：照会先制限、内部DNS、レート制限、出力エスケープ。

## ケースを報告書に書くとき

「観測」は実測で裏付け、「原因」はコードから確認できれば断定、「被害」は必要な権限や構成を条件として書く。実サーバー上のパス、ユーザー情報、レスポンスの秘密情報、CTFフラグをそのままGitHubに載せない。

**対応する仕様根拠**：[sqlmap Techniques](https://github.com/sqlmapproject/sqlmap/wiki/Techniques)、[OWASP SQLi](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)、[OWASP XSS](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)、[OWASP OS Command](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)。
