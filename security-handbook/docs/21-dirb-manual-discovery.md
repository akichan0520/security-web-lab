# 21｜DIRB／DirBusterの原理：HTTPでパス探索を手作業で理解する

> 「dirp」は文脈上、Webディレクトリ探索ツールの **DIRB／DirBuster（ディルブ）系**として扱う。パス探索は小規模な許可済CTFでのみ。公開サイトを無差別に総当たりしない。

## 0. DIRBは何をしているのか

DIRB、DirBuster、dirsearch、Gobusterなどの違いは主に使い勝手や探索速度で、**原理は「候補パスへHTTPを送り、レスポンスを比較する」**こと。ツールがなくても理解できる。

```text
候補パス： /, /about, /lab/map/public, /lab/map/hidden, /no-such-path
                     ↓
HTTP GET を送信 → 200 / 301 / 403 / 404 / 405 + 本文長 + Location
                     ↓
既知の404応答を基準に「違うもの」を調べる
```

`200`をすべて発見、`403`を不在、`302`を成功とするのは誤り。URLの後処理、アクセス制御、ログイン状態、soft404を区別する。

## 1. ステータスだけを手動比較

```bash
BASE='http://127.0.0.1:8767'
for path in / /lab/map/public /lab/map/forbidden /lab/map/absent; do
  curl -sS -o /dev/null -w "$path status=%{http_code} bytes=%{size_download}\n" "$BASE$path"
done
```

存在しない `/lab/map/absent` を**基準（ベースライン）**にする。同梱ラボのルートは架空の案内文だけ。実際の管理コンソールや秘匿ファイルは含まない。

## 2. 小さな辞書を「1秒あけて」確認（ローカル専用）

```bash
# テスト候補を最小限にし、対象の負荷を抑える
printf '%s\n' 'public' 'forbidden' 'absent' > paths.txt
while IFS= read -r p; do
  curl -sS -o /dev/null \
    -w "$p status=%{http_code} bytes=%{size_download}\n" \
    "http://127.0.0.1:8767/lab/map/$p"
  sleep 1
done < paths.txt
```

**重要**：HTTPで参照しているのはOSの`/`以下のファイルとは限らない。Webフレームワークのルーティング、逆プロキシ、静的配信設定がURLと処理の対応を決める。`find / -name`とは目的もアクセス権限も違う。

## 3. 「発見」の解釈を間違えない

| 見たもの | 意味の可能性 | 必ず比較するもの |
|---|---|---|
| 200 + 本文が固定 | 通常ページまたはsoft404 | 不存在パスと長さ・本文を比較 |
| 301/308 | 末尾スラッシュやHTTPS強制 | Locationを確認 |
| 302 | ログインへ転送など | Location、Cookie、認証状態 |
| 403 | ルートがあるが禁止、または一律拒否 | 他の禁止パスとの違い |
| 404 | ルーティング不一致、非公開、マスキング | 不存在パスと比較 |
| 405 | パスは処理するがメソッドが違う | `Allow`を確認 |
| 500 | アプリのバグや入力処理ミス | エラーに重要情報がないか（公開禁止） |

## 4. リンクから候補語を「推測」する論理

初級：トップページのHTML内の`href`や`src`を確認する。

中級：JavaScriptが呼ぶAPIルート、`robots.txt`の記述、リダイレクト先の存在を観察する。ただし**robots.txtはアクセス制御ではない**。

上級：URLの命名規則、認証前後のパス差、同じルートにGET/POSTを送った場合の応答差を論理的に分類する。大量の辞書より、観測から少数候補を作る。

```bash
curl -i 'http://127.0.0.1:8767/robots.txt'
curl -i 'http://127.0.0.1:8767/lab/map/public'
curl -i 'http://127.0.0.1:8767/lab/map/absent'
```

## 5. CTFでありがちな落とし穴

- リダイレクトを自動追跡すると、元パスの302を見落とすことがある。まず`-i`で`Location`を確認。
- gzipなどの圧縮、動的時刻、セッションIDで本文長が変化する。サイズ1つだけに頼らない。
- HTTP/1.1とHTTP/2、URLの大文字小文字、末尾の`/`、URLエンコード、パス正規化の違い。
- 403/404が意図的に均一化されていることもある。禁止先の探索には権限が必要。
- 何も見つからなくても対象の安全性を保証しない。

## 6. 予習・復習のチェック

1. ツールを使わず、4つのURLにGETを送り、ステータスと本文サイズを比較できる。
2. 200をsoft404と区別できる。
3. 301/302で元のLocationを確認できる。
4. 405を入力ミスだけと決めず、メソッドの違いを考察できる。
5. WebのパスとOSファイルシステムを混同しない。

## 一次資料

- [OWASP WSTG: Unreferenced files](https://wstg.owasp.org/latest/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management/04-Review_Old_Backup_and_Unreferenced_Files_for_Sensitive_Information/)
- [OWASP Forced browsing](https://community.owasp.org/attacks/Forced_browsing)
- [Kali DIRBの公式説明](https://www.kali.org/tools/dirb/)
