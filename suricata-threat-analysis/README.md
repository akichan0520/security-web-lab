# Suricata Threat & PCAP Analysis Lab

**Suricata 8.0.6 × Wireshark：検出ルールと通信の対応を学ぶ、日本語の防御側学習リポジトリ。**

> 教材PCAPやマルウェア実行ファイルは同梱していません。各脅威の公開資料を検証し、**一般的な脅威の特徴と、このPCAPで検証済みの事実を分離**しています。実PCAP・教材ルールの検証は未実施です。

## 目次

### 基礎

- [PCAP解析の進め方](guides/01-workflow.md)
- [シグネチャのバイト列とPCAPの照合](guides/02-rule-to-bytes.md)
- [ケース記録テンプレート](templates/case-template.md)
- [公開前エビデンス監査報告](EVIDENCE_AUDIT.md)

### 脆弱性悪用（マルウェアと区別）

- [BlueKeep / CVE-2019-0708 / SID 2027369](exploits/BlueKeep-CVE-2019-0708.md)

### マルウェア別ノート

- [Emotet](malware/Emotet.md) — HTTP(S) C2 / ダウンローダー
- [WannaCry](malware/WannaCry.md) — SMB / ワーム型ランサムウェア
- [TrickBot](malware/TrickBot.md) — C2 / モジュール取得
- [IcedID](malware/IcedID.md) — HTTPS / ローダー
- [Agent Tesla](malware/Agent-Tesla.md) — SMTP・HTTP / 情報窃取
- [LockBit 3.0](malware/LockBit-3.md) — 侵害後・暗号化／持ち出し
- [LockerGoga](malware/LockerGoga.md) — 暗号化事案とネットワーク分析の限界
- [StealBit](malware/StealBit.md) — HTTP / データ持ち出し

## 使い方

1. [調査の流れ](guides/01-workflow.md)を読む。
2. 興味のある脅威のノートで、事前に特徴・証拠・限界を把握。
3. 手元のルールの `sid` と `rev` を確認して、EVEアラートをPCAPと照合。
4. [ケーステンプレート](templates/case-template.md)に「確認できた事実」「推察」「未確認」を分けて記録。

```bash
bash scripts/alert_summary.sh ./logs/eve.json
```

## 証拠の読み方

- `suricata.log` の `error parsing signature` は**ルール読込エラー**であり攻撃検知ではない。
- `fast.log` / `eve.json` のアラートは**検出条件への一致**であり侵害成功とは限らない。
- 送信元IPは常に「攻撃者」とは限らない（C2や侵害端末からの外向き通信に注意）。
- 暗号化されたデータをPCAPだけで平文として読んだことにはしない。

## 根拠となる資料

- [Suricata 8.0.6公式ドキュメント](https://docs.suricata.io/en/suricata-8.0.6/)
- [Suricata: Making sense of alerts](https://docs.suricata.io/en/suricata-8.0.6/make-sense-alerts.html)
- [MITRE ATT&CK: Software](https://attack.mitre.org/software/)

## 今後の拡充

- 各脅威の実PCAP・SID・revを確認後、赤字（Hex）一致箇所とストリーム番号を追記
- `cases/` に根拠付きの演習ケースを追加
- マルウェア別の検知の誤検知・見逃しを比較

## 安全性

防御・学習を目的とし、実検体や実悪用コードを配布しません。公開前にPCAP・ログに含まれるIP、認証情報、個人情報を確認してください。

## エビデンスの基準

資料内の「できること」は公開ベンダー資料・公的機関・MITREの**報告された能力**であり、手元のPCAPで確認されたと限りません。具体的な通信パターンはバージョンや活動時期で変わるため、`SID`・`rev`・ルール本文・PCAPの一致を取るまでは**未検証**とします。

出典の優先順位：①Microsoft・CISAなどの一次資料、②NCC Groupなど検出ルール公開者の原本、③MITRE ATT&CK、④ルール索引（EveBox等）。個別のページは[監査報告](EVIDENCE_AUDIT.md)を参照。

## 実際の検索値を学ぶ（今回の改訂）

全ページに公開元を示した**実値（16進数・文字列）**と、Wiresharkでの検索手順を追記しました。ただし、**通信中のペイロードとファイル／プロセスメモリ用YARAの値は別物**です。公開ルールの実値を紹介しても、手元のPCAPで一致した証拠を作ったことにはなりません。

- [Wireshark 実値検索ガイド](guides/03-wireshark-real-signature-search.md)
- [公開シグネチャ実値一覧](PATTERN_EVIDENCE.md)
- BlueKeep / Emotet / WannaCry / TrickBot は**通信側**の確認値を提示（一般的なプロトコル値を含み、それのみで特定不可）
- IcedID / Agent Tesla / LockBit 3 / LockerGoga / StealBit は**検体ファイル・メモリ側YARA**の確認値を提示。PCAPの値と偽らない

**重要:** 更新対象は解説Markdownのみ。検体、実際の攻撃PCAP、マルウェア実行ファイル、検証前ルールの配布は含みません。
