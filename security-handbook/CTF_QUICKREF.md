# CTF現場用早見表 — Web Security Lab

## HTTP確認が最初

**F12 → Network / Burp HTTP history** で `Method` / `Path` / `GETまたはPOST` / `Content-Type` / `Body` / `Cookie` / `Response` を記録。表示画面だけではなく実際のHTTPレスポンスを確認する。

| 観測 | 意味 | 次に調べること |
|---|---|---|
| 404 | URL/ルートが存在しない | Method・Pathを再確認 |
| 405 | Methodが許されていない | GET/POST違い |
| 500 | サーバー内部の例外 | アプリ/DBの詳細ログ（許可範囲） |
| 200だけど表示が変わる | 正常なアプリ応答差 | 生HTML/JSONとDOMを比較 |
| `No output` | コマンド出力未回収など | stdout, stderr, 実行可否を分離 |

## SQLi：判定の順番

1. 通常検索で確実にヒットする値とヒットしない値を調べる。
2. 文字列/数値、引用符・括弧などSQLの **入力文脈** を見極める。
3. 真条件・偽条件を **同じ元条件** で比較。元の値がヒットしているのに `OR ... false` だけで偽と決めない。
4. SQL構文エラーと0件を分けて調べる。
5. Boolean / Time / Error / UNIONのどれが観測できるか分類する。
6. Burpで生HTTP通信を保存し、必要ならSQLmapに渡す。
7. DB権限・ファイル権限・OS権限は別物と理解する。
8. 修正後、同じ入力で症状が消えることを確かめる。

**ローカル演習**：

```bash
cd security-handbook
python3 lab/server.py
# 別ターミナルから（ローカル専用）
curl -G 'http://127.0.0.1:8767/lab/sql/vuln' --data-urlencode 'name=Travel Kit'
```

詳しくは [SQLiフィールドマニュアル](docs/01-sqli-ctf-field-manual.md)。

## XSS：判定の順番

`入力 → HTTP Request → HTTP Response → DOM → JavaScript` の5段階を見比べる。

- HTTPレスポンスで反射している → 反射型を疑う。
- 保存後、別セッションでも表示 → 蓄積型を疑う。
- ResponseにはないがDOMにある → DOM-basedを疑う。
- DOMに3つ目の`p`要素があれば `[2]` で指定。DOMの変更と「ページのソースを表示」は別。
- HTML本文、属性、URL、JavaScript文脈で必要なエスケープは異なる。

詳しくは [XSSフィールドマニュアル](docs/13-xss-ctf-field-manual.md)。

## OSコマンド：検証の着眼点

`$_GET` は入力取得。`filter_var()` は形式検証。`dns_get_record()` はシェルを使わないDNS問い合わせ。対策の核心は **不要なOSコマンド呼び出しを廃止すること**。

## SQLmap：オプション読み方

`-r`=保存したHTTPリクエスト / `-p name`=nameパラメータ / `--technique=B`=Boolean / `--string`=TRUE応答内の文字列 / `-t`=HTTPトレース / `--union-cols=2`=UNIONの列数を2に限定。

## レポートに残す最少6項目

- 対象範囲（許可されたCTFのみ）
- 再現条件（入力値・HTTP Method・パラメータ）
- 通常と異常のレスポンス差
- 原因となる信頼境界
- 防御策と修正箇所
- 回帰テストと参考資料のURL

**禁止**：実IP、実Cookie、認証情報、実フラグの公開。Webシェルや外部侵入用ツールをリポジトリに置かない。

## 追加：ツール無しの手動攻略編

[HTTP/curl](docs/18-http-manual-curl.md) ｜ [OSコマンド文法](docs/19-os-command-manual.md) ｜ [XSS文脈](docs/20-xss-manual-contexts.md) ｜ [DIRBの理論](docs/21-dirb-manual-discovery.md) ｜ [解説問題](docs/25-manual-drills.md)
