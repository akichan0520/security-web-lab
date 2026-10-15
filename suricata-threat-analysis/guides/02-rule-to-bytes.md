# ルールの `content` とPCAPを照合する練習

## ASCIIと16進数

`content:"/admin";` は `2f 61 64 6d 69 6e` のバイト列を調べる。これは **学習用の架空ルール** であり、実在する脅威のIOCではない。

```suricata
alert http any any -> any any (msg:"LAB URI admin"; flow:established,to_server; http.uri; content:"/admin"; sid:1000001; rev:1;)
```

1. `http.uri` により、検査対象はHTTPのURIとなる（TCP全バイト列ではない）。
2. `content` の値をASCII→Hexに変換する。
3. WiresharkでHTTPリクエスト行を探す。HTTPで再構成や正規化が働くため、単一フレームに元文字列がそのまま見えないこともある。
4. 一致した文字列だけでなく、ルールヘッダーと `flow` が合致することを確認する。

## 範囲指定

- `offset:3; depth:4;` は検査バッファ先頭からの絶対位置に基づく検索。
- `distance:0; within:10;` は前の一致の末尾から相対的に検索。
- `startswith` や `endswith`、`nocase` は比較結果に影響する。

## 暗号化の注意

WiresharkでTLS Application Dataしか確認できなければ、平文の `content` との直接照合は通常できない。Suricataの検査時点、TLS終端場所、復号可能性を確認する。

[Suricata 8.0.6公式 — Payload keywords](https://docs.suricata.io/en/suricata-8.0.6/rules/payload-keywords.html)
