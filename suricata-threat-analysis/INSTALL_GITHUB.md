# GitHubへの追加・更新：解答付きハンズオン版

対象例：`https://github.com/akichan0520/security-web-lab`

## 初回追加（Web）

1. ZIPを**解凍**する（ZIPファイル自体をアップロードしない）。
2. `security-web-lab` の **Code** タブを開く。
3. `Add file` → `Upload files`。
4. 解凍した `suricata-threat-analysis` **フォルダの中身とパスが保持されるように**フォルダごとドラッグする。ブラウザでフォルダ選択が効かなければGit CLIを使う。
5. プレビューで `suricata-threat-analysis/README.md`、`hands-on/pcaps/01-http-uri.pcap`、`hands-on/lessons/` 等の階層が正しいか確認。
6. `Commit changes` を選択。
7. `suricata-threat-analysis/README.md` を開き、演習リンクが動くか確認する。

## 同名フォルダの最新版への更新（Gitコマンド推奨）

既存のファイルの削除・差分管理にはGit CLIが確実です。**利用者が意図的に書き換えたファイルの退避を先に行ってください。**

```bash
# 自分のコンピューターで実行（既にcloneしていれば不要）
git clone https://github.com/akichan0520/security-web-lab.git
cd security-web-lab
# Finder等で解凍した suricata-threat-analysis フォルダをリポジトリ直下へコピー

git status
# 何が置き換わるか必ず差分を確認
git add suricata-threat-analysis
git commit -m "Add solved Suricata PCAP hands-on lab"
git push
```

GitHubへの追加後に、`suricata-threat-analysis/hands-on/START_HERE.md` から着手してください。ダウンロード済みの実マルウェアPCAPや検体を、このリポジトリへ無断アップロードしないこと。
