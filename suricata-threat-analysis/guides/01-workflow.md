# PCAP × IDS 実務的な調査順序

## 原則：観測事実と仮説を分ける

| 層 | 証拠 | 説明できること | 説明できないこと |
|---|---|---|---|
| ルールファイル | SID / rev / content | 何を検査する設計か | 実際に発火したか |
| `suricata.log` | rule parse error等 | 検査環境の状態 | 通信元と侵害成功 |
| `fast.log` | アラート | どのルールが発火したか | 攻撃成功 |
| `eve.json` | 5タプル/flow_id/pcap_cnt | 関連通信の探索 | 端末内のコード実行 |
| PCAP | 実パケット | 送受信・一部ペイロード | 暗号化された本文・端末内部 |
| Windows/EDR | プロセス/ログ | 感染・実行の補強 | 単独では全経路 |

## 手順

1. 配布PCAP・ルールをコピーし、SHA256を記録する。
2. バージョン・ロード成功/失敗のSIDを保存する。`suricata.log` のエラーは攻撃アラートと混同しない。
3. `eve.json` から時系列・送信元・宛先・SID・`flow_id` を抽出する。
4. 正確なローカルルールを読み、`content`がどのバッファに作用するか確認。
5. Wiresharkで同一ストリームとその前後を確認。暗号化、再構成、データ欠損に注意。
6. 分類は「不一致」「未検証」「ルール一致」「攻撃試行らしい」「侵害裏付けあり」と段階的にする。

## すぐ使えるコマンド

```bash
suricata --build-info | head -20
sha256sum sample.pcap
mkdir -p ./logs
sudo suricata -r sample.pcap -c /etc/suricata/suricata.yaml -l ./logs
jq -r 'select(.event_type=="alert") | [.timestamp,.src_ip,.src_port,.dest_ip,.dest_port,.alert.signature_id,.alert.signature,.pcap_cnt,.flow_id] | @tsv' ./logs/eve.json
```

注意：検体を不用意に実行しない。PCAPには認証情報・実IP等が入ることがあるため、公開前に確認する。

## 公式資料

- [Suricata 8.0.6: Alerts](https://docs.suricata.io/en/suricata-8.0.6/make-sense-alerts.html)
- [Suricata 8.0.6: EVE JSON](https://docs.suricata.io/en/suricata-8.0.6/output/eve/eve-json-format.html)

## 実行環境と資料の再現性

- `suricata -T -c /etc/suricata/suricata.yaml` で**設定を検査**し、読み込めなかったSIDを記録する。教材ルールの変更はコピーを取ってから判断する。
- `suricata --build-info`、`sha256sum sample.pcap`、`sha256sum /var/lib/suricata/rules/suricata.rules` を残すと、後日の再現性が高まる。
- `sudo` で出力すると`./logs`がroot所有になり得るので、ログを読む権限を確認する。
- `pcap_cnt`はPCAP入力時に出るフィールドで、内部生成イベントなどでは存在しない場合がある。根拠：[Suricata EVE JSON仕様](https://docs.suricata.io/en/suricata-8.0.6/output/eve/eve-json-format.html)。
- `HTTP POST` / `TCP 445` / `RDP 3389` などの事実と特定マルウェアへの**帰属判断**を明確に分ける。
