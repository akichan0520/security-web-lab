# 実例・答え付き：Unit 42 の Emotet 通信解析（2021年）

**データ種別：実際に観測されたマルウェア通信の公開解析結果。PCAPはこのZIPには含めない。**

## 入手先・正解の出典

- [Palo Alto Networks Unit 42: Wireshark Tutorial: Examining Emotet Infection Traffic](https://unit42.paloaltonetworks.com/wireshark-tutorial-emotet-infection/)
- 公式記事内の公開GitHub PCAPリンクから `Example-1-2021-01-06-Emotet-infection.pcap` を取得して分析する。リンク先アーカイブには検体が混入する可能性があるので、**PCAP以外は取り出さず実行しない**。PCAPも隔離VMでの閲覧が望ましい。

## 模範解答（記事が実際に報告した2021年の事実）

| 問い | 答え（2021年の当該PCAPに限る） |
|---|---|
| 何を最初に観察する？ | HTTP GETでDLL取得試行、次にPOST C2通信 |
| 4つのDLL取得候補ホスト | `hangarlastik[.]com`、`padreescapes[.]com`、`sarture[.]com`、`seo.udaipurkart[.]com` |
| レスポンスで失敗と分かる例 | `padreescapes[.]com` が401、`sarture[.]com` が403、suspendedページ200もDLLの取得成功を意味しない |
| DLL取得が記事で確認された先 | `seo.udaipurkart[.]com` のTCPストリーム |
| C2のHTTP POST宛先 | `5.2.136[.]90:80` と `167.71.4[.]0:8080` |
| 取得DLLのSHA256 | `8e37a82ff94c03a5be3f9dd76b9dfc335a0f70efc0d8fd3dca9ca34dd287de1b` |
| このPCAPに二次マルウェアは？ | Unit 42によれば、このExample 1には後続マルウェア活動の証拠なし |

## Wiresharkでの再現

```text
(http.request or http.response or tls.handshake.type == 1) && !ssdp
http.request.method == "POST"
ip.addr == 5.2.136.90 && tcp.port == 80
ip.addr == 167.71.4.0 && tcp.port == 8080
```

IPアドレスの接続先は**記事掲載当時のIOC**であり、現在の悪性ホスト一覧ではありません。現在のネットワークへ通信を送って試さないでください。

`Follow TCP Stream` でHTTP POST本文がエンコード／暗号化されて見えることと、HTTPレスポンスの戻りを確認します。**POSTというだけでEmotetと断定できない**ため、記事の解析結果と各通信の文脈を照合してください。

## 資料としての結論

Unit 42記事のExample 1は、**複数のDLL取得試行→一部失敗→実際のDLL取得→POST C2通信**という因果の理解に向く。この記事の事実を引用した「解答付き実例」であり、**ここで筆者がPCAPを新たにダウンロード・解析したものではない**。
