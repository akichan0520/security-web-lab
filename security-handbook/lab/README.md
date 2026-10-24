# Local Web CTF Lab：外部依存なし・Macでも起動可能

## 安全のための設計

- Python標準ライブラリのみ・**127.0.0.1 に固定でバインド**。
- SQLiteはメモリ内の架空商品データ。実データを読まない。
- SQLiの脆弱版/安全版を比較できる。
- XSSの反射版/安全版、URL→DOM sinkの脆弱版/安全版を比較できる。
- ディレクトリ探索に使うステータス200/403/404の架空ルートを提供。
- **OSコマンド、ファイル書込、認証情報抽出、外部ネットワークアクセスは実装しない。**
- 本コードを本番サーバーやLAN公開に配置しないこと。

## 起動と停止

```bash
cd security-handbook
python3 lab/server.py
# ブラウザ http://127.0.0.1:8767/
# 停止 Ctrl+C
```

## 自動テスト

```bash
python3 -m unittest discover -s lab/tests -v
```

## 動作確認

```bash
curl -G 'http://127.0.0.1:8767/lab/sql/vuln' \
  --data-urlencode 'name=Travel Kit'

curl -G 'http://127.0.0.1:8767/lab/sql/safe' \
  --data-urlencode 'name=Travel Kit'
```

DOM比較URL: `/lab/xss/dom-vuln?name=HELLO` と `/lab/xss/dom-safe?name=HELLO`。

パス探索URL: `/lab/map/public` (200)、`/lab/map/forbidden` (403)、`/lab/map/absent` (404)。

`/lab/sql/vuln` は教育用にSQLの文字列連結を使い、`/lab/sql/safe` はSQLiteのプレースホルダーを使用。SQL構文エラーをHTMLへ出すことのリスクも学ぶ。

## 振り返り

結果がどう変わり、なぜ変わったかをノートに記録。**同じ入力を脆弱版と安全版の両方で試す**ことで、修正効果を説明できるようになる。
