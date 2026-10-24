# GitHub Web画面での追加方法

1. ZIPを解凍する。
2. 既存の `security-web-lab` リポジトリの `Add file` → `Upload files` を開く。
3. フォルダ階層を維持して `security-handbook/docs/28-sqli-ten-scenarios.md` と `security-handbook/lab/sqlite_probe_10.py` を追加する。
4. `Commit changes` を押す。
5. リポジトリのルート `README.md` の末尾に `README_APPEND.md` の中身を追記する。

注記：これは**追加分だけのZIP**です。既存のsecurity-handbookフォルダ全体は含みません。ZIPを丸ごとGitHubへアップロードせず、解凍したファイルを追加してください。既存のHTMLメニュー `index.html` に自動的に表示されるわけではなく、HTMLのリンクも必要に応じて追加してください。

6. 自力演習用の `SELF_CHECK_10.md` も必要ならルートに追加すると、解答と演習を分けて利用できます。
