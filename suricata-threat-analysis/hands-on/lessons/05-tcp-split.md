# TCPセグメントを再構成してURI照合

**学習分類：安全な模擬PCAP／解答付き。実際のマルウェア通信ではありません。**

## 問題

`hands-on/pcaps/05-http-split.pcap`をWiresharkで開き、検出条件に一致する通信元・宛先・対象バイトを特定してください。次に対応するSIDを調べ、アラートだけから侵害と判定できるか考えます。

## 操作手順

1. 表示フィルタに ``tcp.port == 80`` を入力。
2. `Ctrl+F`（Macなら `Cmd+F`）→ `Hexadecimal Value` または `String` → `Packet bytes` にて `/wp-content/`（単一フレーム内では見つからない） を検索。
3. 関連TCP通信は右クリック → `Follow → TCP Stream` で復元。（DNSの場合はパケット詳細のQueriesを展開。）
4. `frame.number == 4` を表示フィルタへ入力し、下の答えと照合。
5. 次でSuricataのローカル演習ルールをテスト（プロジェクト直下で実行）。

```bash
mkdir -p logs/05
sudo suricata -c /etc/suricata/suricata.yaml \
  -S "$PWD/rules/lab.rules" \
  -r "$PWD/hands-on/pcaps/05-http-split.pcap" \
  -l "$PWD/logs/05"

jq 'select(.event_type=="alert" and .alert.signature_id==9900001)' logs/05/eve.json
```

## 解答（事前に確認できるPCAP事実）

| 項目 | 正解 |
|---|---|
| 送信元IP | `192.0.2.51` |
| 宛先IP | `198.51.100.20` |
| 通信ポート | `51551 → 80` |
| 該当フレーム | **4 および 6（分割した要求）** |
| 演習ルールのSID | `9900001`（ローカルルール・ETのSIDではない） |
| 実際のデータ | frame 4は `GET /wp-con`、frame 6は `tent/lab-checkin HTTP/1.1` であり結合すると `/wp-content/lab-checkin` |
| 意味 | TCP Stream Follow ではまとまった要求が見える。単純なバイト検索では1フレームに存在しないため、陰性でもストリーム検査側でマッチし得る。 |

**深掘り：** TCP再構成とパケット単位の検索結果が異なり得ることを体験する。

## 正解の扱い方

上のフレーム番号とバイト列は本リポジトリの生成コードとPCAPから検証したものです。`suricata`エンジンの出力そのものを制作環境で実行したわけではないため、**アラートの件数・フレーム番号は機械実測として断言していません**。使用者側で `suricata -T` とPCAP解析を実行し、実際の`eve.json`と照合してください。

## 出典

- [Suricata 8.0.7ルール構文](https://docs.suricata.io/en/suricata-8.0.7/rules/intro.html)
- [Suricata 8.0.7 EVE JSON](https://docs.suricata.io/en/suricata-8.0.7/output/eve/eve-json-format.html)
- [Wiresharkパケット検索公式ガイド](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkFindPacketSection.html)
