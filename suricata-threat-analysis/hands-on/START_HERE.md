# まずこれを実行：解答付きPCAPハンズオン

**対象:** Suricata 8.0.7（8.0.6でも共通する構文に限定）、Wireshark、Python 3、jq。

このフォルダのPCAPは**本リポジトリで生成した安全な模擬パケット**です。実際のマルウェア攻撃を再現したものでも、公開ETルールの真正な検出テストでもありません。**アラート条件の読み方・通信の方向・バイト検索の練習**用です。実マルウェアの答え付き解析は [実事例](../cases/) を見てください。

## 準備

```bash
suricata --build-info | head
sudo suricata -T -c /etc/suricata/suricata.yaml -S "$PWD/rules/lab.rules"
python3 scripts/verify_lab.py
```

リポジトリの**一番上のディレクトリ**で実行してください。`suricata -T` は**ユーザー自身の環境で実行する必要があります**。この資料の制作環境には Suricata 実行バイナリがなく、実際のエンジンによるアラート件数・`pcap_cnt` は未計測です。

## 手順（1章ずつ）

```bash
# 例：第1章
mkdir -p logs/01
sudo suricata -c /etc/suricata/suricata.yaml \
  -S "$PWD/rules/lab.rules" \
  -r "$PWD/hands-on/pcaps/01-http-uri.pcap" \
  -l "$PWD/logs/01"

jq -r 'select(.event_type=="alert") |
  [.timestamp,.alert.signature_id,.src_ip,.dest_ip,(.pcap_cnt // "-")]|@tsv' logs/01/eve.json
```

`-S` は**演習ルールだけを読み込み**、教材とは無関係のETルールの読込エラーを避けます。`-s` は既定ルールへの**追加**です。EVE出力設定がオフなら `/etc/suricata/suricata.yaml` でEVEを有効にしてください。PCAPパケットのフレーム番号は `pcap_cnt` に表示される場合がありますが、内部pseudoイベントには付かないことがあります。

> **重要:** `logs/01` は都度別名で作り、古いEVEログが混ざらないようにしてください。`sudo` 不要な環境では外して構いません。

## Wireshark共通操作

1. `File → Open` でPCAPを開く。
2. 上部表示フィルタに `tcp.port == 80` 等を入力（これは**表示**の絞り込み）。
3. `Ctrl+F`（Macでは `Cmd+F`）→ **Hexadecimal Value** → **Packet bytes** で `4d:53:5f:54:31:32:30:00` 等を検索。
4. 一致パケットで **Follow → TCP Stream** を使い、TCP分割データの流れを確認する。
5. `frame.number == 4` のように「正解フレーム」へ移動する。

## 演習と解答

| 演習 | PCAP | まず探すもの | 答え |
|---|---|---|---|
| [01 HTTPのURI](lessons/01-http-uri.md) | `01-http-uri.pcap` | `/wp-content/` | 9900001、frame 4 |
| [02 RDPのMS_T120](lessons/02-rdp-marker.md) | `02-rdp-marker.pcap` | `MS_T120 00` | 9900002、frame 4 |
| [03 SMB1](lessons/03-smb1.md) | `03-smb1-marker.pcap` | `ff 53 4d 42` | 9900003、frame 4 |
| [04 DNS](lessons/04-dns.md) | `04-dns-query.pcap` | `task-001.training.invalid` | 9900004、frame 1 |
| [05 TCP再構成](lessons/05-tcp-split.md) | `05-http-split.pcap` | 2パケットに分割されたURI | 9900001、frame 4と6のデータ |
| [06 誤検知演習](lessons/06-false-positive.md) | `06-false-positive.pcap` | 普通の画像URIでも一致 | 9900001、frame 4 |

各章には送信元・宛先、Wireshark操作、**何が証明できたか／できないか**まで記載しています。

## 確認可能な範囲

- ✅ PCAPファイルのフレーム数・固定バイト位置・SHA256：`scripts/verify_lab.py` で確認できる。
- ✅ ルールの文法上の狙いと検索対象：公式Suricata構文との照合・人手でレビュー。
- ⏳ Suricata 8.0.7実行によるアラートの動作確認：利用者環境で `-T` と `-r` を実行して確かめる（本作業環境では未実施）。
- ❌ 実際のEmotet/BlueKeep/WannaCry攻撃の再現や感染成功：この模擬PCAPからは証明できない。

## 仕様の一次資料

- [Suricata 8.0.7コマンドライン（-S, -r, -l）](https://docs.suricata.io/en/suricata-8.0.7/command-line-options.html)
- [Suricata 8.0.7 HTTP Keyword](https://docs.suricata.io/en/suricata-8.0.7/rules/http-keywords.html)
- [Suricata 8.0.7 DNS Keyword](https://docs.suricata.io/en/suricata-8.0.7/rules/dns-keywords.html)
- [Suricata 8.0.7 EVE JSON](https://docs.suricata.io/en/suricata-8.0.7/output/eve/eve-json-format.html)
- [Wireshark User Guide: Finding packets](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkFindPacketSection.html)
