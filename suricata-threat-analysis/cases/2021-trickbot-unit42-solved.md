# 答え付き実例：2021年 Emotet → TrickBot 複合感染（Unit 42）

一次情報：[Palo Alto Networks Unit 42 - Wireshark Tutorial: Examining Emotet Infection Traffic](https://unit42.paloaltonetworks.com/wireshark-tutorial-emotet-infection/) 内の **Example 4**。

指定PCAP：`Example-4-2021-01-05-Emotet-infection-with-Trickbot.pcap`（公式記事のGitHubリンクから、PCAPだけを取得してWiresharkで開く）。

## 答え（Unit 42の当時の観測）

| 問い | 研究者が報告した答え |
|---|---|
| 初期Emotet DLL取得はHTTP GETで捕捉？ | Example 4ではHTTP GETとしては確認されず、`fathekarim[.]com` へのHTTPSが最初に観察される。研究者はこれを初期取得の**可能性**として扱う |
| Emotet C2の手掛かり | 先行例同様のHTTP POSTパターン |
| TrickBotの通信で注目するポート | TCP `447` / `449` を使用したHTTPS（当時の例） |
| TrickBotのデータ送信パス例 | `/81/`、`/83/`、`/90` などのHTTP POST URL（活動・世代による） |
| 後続ファイル取得の候補 | `.png` で終わるHTTP GET URL が追加バイナリの取得に関連する事例 |

## 再現用Wiresharkフィルタ

```text
(http.request or http.response or tls.handshake.type == 1) && !ssdp
http.request.method == "POST"
tcp.port == 447 || tcp.port == 449
http.request.uri contains "/81/" || http.request.uri contains "/83/"
```

**模範回答の重要点：** これは**特定の2021年の感染事例**であって、2026年現在の全TrickBot通信や全マルウェアに共通するIOCではありません。TLSでは復号なしにコンテンツは読めないのでポート・接続相手・フローとほかの証拠を組み合わせます。

## 安全上の注意

実行可能な検体を抽出・実行する必要はありません。資料には歴史的な通信の解答のみを掲載し、実際の検体は同梱していません。
