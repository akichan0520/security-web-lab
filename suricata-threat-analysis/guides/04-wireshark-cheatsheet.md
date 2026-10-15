# Wireshark 表示フィルタ・実バイト検索 早見表

| 目的 | 表示フィルタ |
|---|---|
| RDP候補 | `tcp.port == 3389` |
| SMB候補 | `tcp.port == 445` |
| SMB1解析済み | `smb` |
| SMB2解析済み | `smb2` |
| HTTP要求だけ | `http.request` |
| POST要求だけ | `http.request.method == "POST"` |
| URIの一部 | `http.request.uri contains "/wp-content/"` |
| DNS | `dns` |
| TLS ClientHello | `tls.handshake.type == 1` |
| 通信開始SYN | `tcp.flags.syn == 1 && tcp.flags.ack == 0` |
| TCP再送 | `tcp.analysis.retransmission` |
| 送信元と宛先IPの片方 | `ip.addr == 192.0.2.10` |
| フレーム番号 | `frame.number == 4` |

## 16進数検索（**表示フィルタとは別機能**）

1. `Ctrl+F`（Mac: `Cmd+F`）で検索パネル。
2. `Hexadecimal Value` と `Packet bytes` を選択。
3. 例：`4d:53:5f:54:31:32:30:00`（ASCII `MS_T120` + NULL）。
4. `ff:53:4d:42` はSMB1の一般ヘッダーであり、**WannaCry特有ではない**。
5. 該当フレーム内に見つからなければ、TCPストリームの再構成を確認。

## ASCII検索

`String`、対象`Packet bytes`を選び、`/wp-content/` を検索。**スラッシュを含む文字列が見つかってもEmotetの十分条件ではない**。

## 実際のバイト列と仮想バッファの違い

- `http.uri` は正規化後のURI検査。TCPセグメントを跨ぐ通信やURL正規化の結果、同じバイト列がPCAPの**単一フレームに存在しない**場合がある。
- `dns.query` はドメイン名へ正規化されている。DNSワイヤ上では各ラベルの**長さバイト**と終端 `00` が存在する。
- `file.data` は復元・展開データを検査する場合がある。Packet Bytesで見つからないことだけでルールの不一致を結論にしない。
- HTTPS/RDPの暗号化後データにある文字列は、鍵なしにはPCAPで照合できないことがある。

公式：[Wireshark Find Packet](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkFindPacketSection.html)、[Suricata HTTP](https://docs.suricata.io/en/suricata-8.0.7/rules/http-keywords.html)、[Suricata DNS](https://docs.suricata.io/en/suricata-8.0.7/rules/dns-keywords.html)
