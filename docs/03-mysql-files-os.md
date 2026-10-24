# 03｜MySQLとファイルシステム・OSシェルの権限境界

## SQLiが成立してもファイルは無条件には読めない

```
Web入力 → SQLi → DBアカウントの権限
                        ├ SELECT（DBの行）
                        └ ファイル操作：FILE権限 + DB設定 + OS権限
                                            └ DBサーバーのFS
                          OS操作はさらに別の前提と実行経路が必要
```

DBサーバーとWebサーバーが別ホスト/コンテナなら、ファイルシステムも異なる場合がある。MySQLの`@@datadir`が`/var/lib/mysql/`でもWeb公開領域の場所は分からない。

## `secure_file_priv` の解釈

| 値 | ファイル入出力機能への意味 |
|---|---|
| 特定のディレクトリ | 該当ディレクトリに制限 |
| 空文字列 `''` | この設定によるディレクトリ制限なし（安全ではない） |
| `NULL` | `LOAD_FILE` / `SELECT INTO OUTFILE` など該当機能を無効化 |

値が「空欄」に見えるだけではNULLと空文字列を区別できない。DBの`FILE`権限、OS権限、ファイル既存状態、サービス配置などは独立して判断する。

```sql
-- 自分で管理するMySQLの設定調査例
SHOW VARIABLES LIKE 'secure_file_priv';
SHOW VARIABLES LIKE 'datadir';
```

- `SELECT ... INTO OUTFILE`：MySQLサーバーのファイルシステムへ結果を出力する機能。既存ファイルの上書きは原則不可。
- `LOAD_FILE()`：MySQLサーバーが読めるファイルを取得し得る関数。パス、権限、サイズ、設定に依存。
- `sqlmap --file-read` / `--file-write`：サーバー側のファイル操作機能。OSの全文検索ではない。
- `sqlmap --os-shell`：条件次第でOS操作を試す機能。Web stager等の補助ファイルを作成し得るため、明示的に許可された環境でのみ利用。

## `find`の正しい意味

```bash
# 自分の環境内の /app 配下を例に、名前でファイル検索
find /app -type f -name 'sample.csv'

# 大文字・小文字を区別しない
find /app -type f -iname 'sample.csv'

# 深さ2まで列挙
find /app -maxdepth 2 -print
```

`find /` は出力が膨大になることがある。**`-type f`（通常ファイル）と`-name`（名前一致）は必須ではない**が、出力を絞るため実用的。`2>/dev/null` は権限エラーを隠してしまうため、調査の初期段階では安易に使わない。

`pwd`が`/app`、`command -v find`が`/usr/bin/find`、`ls`が`No output`であっても、「ファイルがない」とは結論付けられない。コマンドの存在と実行結果の**回収方法**は別問題。

## PHPファイル実行へ波及するリスク（原理のみ）

DBからWeb公開可能な場所へファイルを書き込めて、Webサーバーがその種類をプログラムとして実行する条件が成立すれば、被害が拡大する。SQLi、FILE権限、Web実行権限、Web配置先の共用という**複数条件の連鎖**が必要。任意コマンドを受け取るバックドアやWebシェルはこの教材には含めない。

### 防御

- DBは必要最小限の権限。一般アプリDBユーザーに不要な`FILE`権限を付与しない。
- DBプロセスからWeb公開ディレクトリへ書き込めないようにする。
- Webのアップロード領域ではスクリプトを実行しない。
- DBとWebサーバーを権限・通信経路・ファイルシステムで分離する。
- アプリ側のSQLi対策（PDO等）を基本にする。

**根拠**：[MySQL `secure_file_priv`](https://dev.mysql.com/doc/refman/8.4/en/server-system-variables.html)、[MySQL SELECT INTO](https://dev.mysql.com/doc/refman/8.4/en/select-into.html)、[MySQL security guidance](https://dev.mysql.com/doc/refman/8.4/en/security-against-attack.html)、[sqlmap Usage](https://github.com/sqlmapproject/sqlmap/wiki/Usage)。
