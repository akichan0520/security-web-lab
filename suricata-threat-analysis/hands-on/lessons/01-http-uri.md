# HTTP URIを検査する：`/wp-content/`

**学習分類：安全な模擬PCAP／解答付き。実際のマルウェア通信ではありません。**

## 問題

`hands-on/pcaps/01-http-uri.pcap`をWiresharkで開き、検出条件に一致する通信元・宛先・対象バイトを特定してください。次に対応するSIDを調べ、アラートだけから侵害と判定できるか考えます。

## 操作手順

1. 表示フィルタに ``tcp.port == 80 && http.request`` を入力。
2. `Ctrl+F`（Macなら `Cmd+F`）→ `Hexadecimal Value` または `String` → `Packet bytes` にて `/wp-content/` または `2f:77:70:2d:63:6f:6e:74:65:6e:74:2f` を検索。
3. 関連TCP通信は右クリック → `Follow → TCP Stream` で復元。（DNSの場合はパケット詳細のQueriesを展開。）
4. `frame.number == 4` を表示フィルタへ入力し、下の答えと照合。
5. 次でSuricataのローカル演習ルールをテスト（プロジェクト直下で実行）。

```bash
mkdir -p logs/01
sudo suricata -c /etc/suricata/suricata.yaml \
  -S "$PWD/rules/lab.rules" \
  -r "$PWD/hands-on/pcaps/01-http-uri.pcap" \
  -l "$PWD/logs/01"

jq 'select(.event_type=="alert" and .alert.signature_id==9900001)' logs/01/eve.json
```

## 解答（事前に確認できるPCAP事実）

| 項目 | 正解 |
|---|---|
| 送信元IP | `192.0.2.10` |
| 宛先IP | `198.51.100.20` |
| 通信ポート | `51514 → 80` |
| 該当フレーム | **4** |
| 演習ルールのSID | `9900001`（ローカルルール・ETのSIDではない） |
| 実際のデータ | GET /wp-content/lab-checkin HTTP/1.1 |
| 意味 | `http.uri` の部分一致。正常なWordPressパスにもあり得る。Emotetの証明ではない。 |

**深掘り：** Emotetの文脈でもWeb URIは研究されるが、今回のデータは完全な模擬通信。

## 正解の扱い方

上のフレーム番号とバイト列は本リポジトリの生成コードとPCAPから検証したものです。`suricata`エンジンの出力そのものを制作環境で実行したわけではないため、**アラートの件数・フレーム番号は機械実測として断言していません**。使用者側で `suricata -T` とPCAP解析を実行し、実際の`eve.json`と照合してください。

## 出典

- [Suricata 8.0.7ルール構文](https://docs.suricata.io/en/suricata-8.0.7/rules/intro.html)
- [Suricata 8.0.7 EVE JSON](https://docs.suricata.io/en/suricata-8.0.7/output/eve/eve-json-format.html)
- [Wiresharkパケット検索公式ガイド](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkFindPacketSection.html)
