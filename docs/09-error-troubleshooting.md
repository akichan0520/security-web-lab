# 09｜エラー・表示の読み方 — 一覧

| 表示 | 直接言えること | 誤った推論／次に確かめること |
|---|---|---|
| HTTP `200` | Webサーバーが通常応答 | SQLi非成立の証拠ではない |
| HTTP `405 Method Not Allowed` | そのURLにそのHTTPメソッドが許可されない | Burpの実際のGET/POSTとsqlmapの送信を比較 |
| HTTP `500 Internal Server Error` | サーバー処理で問題 | DB、PHP、例外、検出ペイロードなど原因を分離 |
| MySQL `1064` | SQL構文エラー | 入力引用符・SQL構造・DBMS方言を確認 |
| MySQL `1105 XPATH syntax error` | XPath式評価のエラー（環境による） | エラー表示が情報露出に利用されないよう対策 |
| MySQL `1305 FUNCTION ... does not exist` | 指定した関数がない | DBMS検出時の試験関数か、バージョン相違か確認 |
| MySQL `1227` | DB権限不足の可能性 | アカウント権限を確認（無条件に権限付与しない） |
| MySQL `1290` | サーバー設定の制限に関係 | `secure_file_priv` 等の設定を確認 |
| MySQL `1086` | ファイルが既存の場合など | 既存ファイルの上書きを避ける設計を確認 |
| `No output` | 出力取得できていない | コマンドの動作と出力回収を区別 |
| `No such file or directory` | 指定したコマンド又はパスのどちらかがない | エラー文で対象パスを特定 |
| `Permission denied` | OS権限が不足 | 権限設計の確認とログ取得 |
| `PHP Parse error` | PHP構文が不正 | 書式・引用符・セミコロン等を静的に確認 |
| `Call to undefined function` | PHP関数が存在しない/利用不可 | スペル、拡張、PHPバージョン |
| `shell_exec()` がnull | 実行失敗または出力なし等 | nullだけで成功失敗を断定しない |

### 過去のCTFの「見た目」の落とし穴

- Web画面の「複数」「検索失敗」はアプリのビジネスロジックに過ぎない。**HTTPステータス**と**DB例外**を別々に確認。
- `find /` は大量出力や権限エラーで扱いづらい。`-type f -name`を付けると絞れるが、付けないと探せないわけではない。
- `ls`が出なくても`find`が存在する場合がある。シェルが制限された実行方法である可能性も検討する。

**根拠**：[sqlmap Usage](https://github.com/sqlmapproject/sqlmap/wiki/Usage)、[MySQL secure_file_priv](https://dev.mysql.com/doc/refman/8.4/en/server-system-variables.html)、[PHP shell_exec](https://www.php.net/manual/ja/function.shell-exec.php)、[OWASP Error Handling](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet)。
