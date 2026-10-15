# 6問・答え一覧（模擬PCAPのフレームとバイト列）

| 演習 | 正解フレーム | 送信元IP:Port | 宛先IP:Port | 実際の値 | 演習SID | 判定の限界 |
|---|---:|---|---|---|---:|---|
| HTTP URI | 4 | `192.0.2.10:51514` | `198.51.100.20:80` | `/wp-content/lab-checkin` | 9900001 | Emotet固有ではない |
| RDP marker | 4 | `192.0.2.21:51521` | `198.51.100.33:3389` | `4d 53 5f 54 31 32 30 00` | 9900002 | 真正なRDP/BlueKeep攻撃ではない |
| SMB1 marker | 4 | `192.0.2.31:51531` | `198.51.100.44:445` | `ff 53 4d 42` | 9900003 | WannaCry固有ではない |
| DNS query | 1 | `192.0.2.41:53241` | `198.51.100.53:53` | `task-001.training.invalid` | 9900004 | C2の確証ではない |
| HTTP split | 4, 6 | `192.0.2.51:51551` | `198.51.100.20:80` | `GET /wp-con` + `tent/lab-checkin...` | 9900001 | 両フレームを結合した解析が必要 |
| 偽陽性 | 4 | `192.0.2.61:51561` | `198.51.100.20:80` | `/wp-content/images/normal.jpg` | 9900001 | 普通の画像取得 |

`990000x` は本リポジトリのローカルな**学習用番号**で、ETや特定マルウェアのルールではありません。どのアラートが実際に発火したかは、Suricataの `-S` と `-r` を手元で実行して検証してください。**フレーム/バイト列の正解はPythonで検証済み**です。

## 実際の専門家公開の答え合わせ

- [Emotet — Unit 42](../../cases/2021-emotet-unit42-solved.md)：HTTP GET、HTTP POST、被害機の通信、既知ファイルSHA256。
- [Emotet→TrickBot — Unit 42](../../cases/2021-trickbot-unit42-solved.md)：二次感染の観測、特殊な通信ポート。
- [IcedID — SANS](../../cases/2021-icedid-sans-solved.md)：被害IP、ファイル配布、HTTP/HTTPS C2。
