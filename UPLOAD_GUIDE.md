# 既存 security-web-lab への追加・更新手順（破壊しない方式）

**このZIPはGitHubへ直接アップロードしても展開されません。** ZIPをMacで展開してください。

1. GitHubの既存リポジトリ `security-web-lab` を開く。
2. `Add file` → `Upload files` を開く。
3. 展開した `security-handbook/` フォルダ全体（フォルダ構造が保たれるように）をドラッグ&ドロップ。
4. 既に前版の `security-handbook/` がある場合は、**同名ファイルは最新版へ置き換える**（教材・HTMLメニュー・演習の整合性を保つため）。別の用途のファイルは上書きしない。
5. 差分を確認して `Commit changes`。
6. 既存リポジトリのトップ `README.md` を編集し、`README_APPEND.md` の内容を **末尾へ追記** する。
7. トップにHTMLサイトを出している場合は、既存の `index.html` にリンクを1個追加する。**本ZIPで既存index.htmlを上書きしないこと。**

トップのindex.htmlに入れるリンク例：

```html
<a href="./security-handbook/index.html">Webセキュリティ実践ハンドブック</a>
```

## 開き方

- GitHubリポジトリ上：`security-handbook/README.md` が本として読める。
- GitHub Pagesがリポジトリのルートから配信されている場合：`https://<account>.github.io/security-web-lab/security-handbook/` でクリック式教材を表示できる（Pagesの公開元設定次第）。
- ローカル：`security-handbook/index.html` を直接開ける。完全オフライン。

## 注意

この作業では元リポジトリを取得できなかったため、既存ファイルの完全な互換性や既存ページ構造は確認していません。独立したフォルダ名を使い、既存README/HTMLを上書きせず安全に追加できる方式にしています。

## 更新版の特記事項

- 新たに `docs/18`〜`docs/25` を追加し、既存の `security-handbook/index.html` と章ページ内のナビゲーションも更新してある。
- **ZIPをGitHubへ置くだけでは中身は展開されない。** 解凍したディレクトリをアップロード。
- GitHubでは一度に多数のファイルをアップロードするとブラウザ制限に達する場合がある。`security-handbook/docs/`、HTML、`lab/`などに分割してアップロードできるが、最終的にフォルダ構成を維持すること。
- 実IP、Cookie、認証情報、フラグ、シェル等を追加しない。公開前に `PUBLICATION_CHECKLIST.md` を読む。
