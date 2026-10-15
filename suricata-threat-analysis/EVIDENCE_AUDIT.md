# 公開前エビデンス監査報告（2026-10-15）

対象：旧版 `suricata-threat-analysis.zip` の全14ファイル。外部リポジトリへのアップロードは行っていない。

## 監査の範囲

- ZIP CRC検査：合格（破損なし）
- Markdown内部相対リンク：合格（リンク切れ0）
- シェルスクリプト：Bash構文チェック合格、模擬EVE JSONによるjq出力テスト合格
- 外部出典：既存のMITRE ATT&CK IDとSuricata 8.0.6公式資料の主要リンクの到達性・記述内容を確認。一部Microsoft動的ページはブラウザから本文取得が難しいため、検証できるMSRCの公式記事を優先した。
- **未実施**：ユーザー教材のPCAP分析、教材ルール実行、Malwareの実検体解析、各通信IOCの再現試験、Suricata 8.0.6のローカル実行。

## 監査結果（リスクと修正）

| 種別 | 旧ZIPでの問題 | 監査版での処置 |
|---|---|---|
| 出典の粒度 | MITRE IDとSuricataの一般仕様だけのページが多く、個別の通信観測根拠が薄い | 各脅威に資料別の対応説明と調査上の限界を追記 |
| BlueKeep | SID 2027369の根拠URLがなかった | NCC Group原本（SID 1）とET公開索引（SID 2027369）を両方提示し混同を禁止 |
| BlueKeep | MicrosoftブログURLが現行検索でたどりにくい | 公式MSRCの現行URLを追加 |
| Emotet | URI / POSTの具体的報告資料が不足 | CISA AA20-280Aの通信記述を追記。ただし2020年の事例に限定 |
| LockBit | マルウェア本体と攻撃者の活動の区別が不足 | CISA AA23-165Aの「アフィリエイトの攻撃行動」を明確化 |
| 再現性 | 出力先のディレクトリ作成を記載していなかった | `mkdir -p ./logs` を追加 |
| PCAP検証 | SID/バイト/攻撃元IPの実測データなし | 未検証を明記したまま維持。**実証済みとしない** |

## 主な検証出典

- [Suricata 8.0.6: Making sense out of Alerts](https://docs.suricata.io/en/suricata-8.0.6/make-sense-alerts.html)
- [Suricata 8.0.6: EVE JSON fields / pcap_cnt](https://docs.suricata.io/en/suricata-8.0.6/output/eve/eve-json-format.html)
- [Suricata 8.0.6: Payload keywords](https://docs.suricata.io/en/suricata-8.0.6/rules/payload-keywords.html)
- [NCC Group: 2019_05_rdp_cve_2019_0708.txt](https://github.com/nccgroup/Cyber-Defence/blob/master/Signatures/suricata/2019_05_rdp_cve_2019_0708.txt)
- [EveBox Rules: ET SID 2027369](https://rules.evebox.org/pub/et/open/2027369?variant=5.0)
- [Microsoft MSRC: CVE-2019-0708](https://www.microsoft.com/en-us/msrc/blog/2019/05/prevent-a-worm-by-updating-remote-desktop-services-cve-2019-0708/)
- [Microsoft: MS17-010](https://learn.microsoft.com/en-us/security-updates/securitybulletins/2017/ms17-010)
- [CISA AA20-280A: Emotet](https://www.cisa.gov/news-events/cybersecurity-advisories/aa20-280a)
- [CISA AA23-165A: LockBit](https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-165a)
- [MITRE ATT&CK: Emotet S0367](https://attack.mitre.org/software/S0367/)、[WannaCry S0366](https://attack.mitre.org/software/S0366/)、[TrickBot S0266](https://attack.mitre.org/software/S0266/)、[IcedID S0483](https://attack.mitre.org/software/S0483/)、[Agent Tesla S0331](https://attack.mitre.org/software/S0331/)、[LockBit 3.0 S1202](https://attack.mitre.org/software/S1202/)、[LockerGoga S0372](https://attack.mitre.org/software/S0372/)、[StealBit S1200](https://attack.mitre.org/software/S1200/)

## 公開時の判定

- **脅威情報・防御側PCAP調査のガイド**としては、出典に基づく暫定版として公開できる。
- **実PCAPの詳細解析を検証済みと称する資料**としては公開できない。教材のPCAP・SID全文・EVEが必要。
- 第三者配布が許可されていない教材PCAP・個人情報・認証情報・実行可能なマルウェアをアップロードしない。
