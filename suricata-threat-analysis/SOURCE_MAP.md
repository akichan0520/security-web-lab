# エビデンスと技術的主張の対応表（2026-10-15）

| 主張 | エビデンス | 判定 |
|---|---|---|
| Suricata安定版として8.0.7が2026年9月15日に公開 | [OISF公開情報](https://suricata.io/2026/09/15/suricata-8-0-7-released/) | 公式 |
| `-S` は指定ルールを単独でロードする | [Suricata 8.0.7 CLI](https://docs.suricata.io/en/suricata-8.0.7/command-line-options.html) | 公式 |
| PCAP中のパケット番号を `pcap_cnt` で扱う | [Suricata EVE JSON](https://docs.suricata.io/en/suricata-8.0.7/output/eve/eve-json-format.html) | 公式 |
| HTTP URIは正規化後バッファを照合 | [Suricata HTTP](https://docs.suricata.io/en/suricata-8.0.7/rules/http-keywords.html) | 公式 |
| DNSの`dns.query`はワイヤの長さバイトをドットへ正規化 | [Suricata DNS](https://docs.suricata.io/en/suricata-8.0.7/rules/dns-keywords.html) | 公式 |
| WiresharkでASCII/Hex検索が可能 | [Wireshark公式](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkFindPacketSection.html) | 公式 |
| BlueKeepルールで`MS_T120`を検査する公開パターン | [NCC Group原本](https://github.com/nccgroup/Cyber-Defence/blob/master/Signatures/suricata/2019_05_rdp_cve_2019_0708.txt) | ルール公開者。教材SID 2027369と**同一ルールの保証はない** |
| Emotetの公開PCAPにHTTP POST C2やDLL取得があった | [Unit 42の解析記事](https://unit42.paloaltonetworks.com/wireshark-tutorial-emotet-infection/) | 2021年当時の具体例 |
| IcedIDの2021年PCAPで172.16.4.213が感染端末 | [SANS ISC／Brad Duncan](https://isc.sans.edu/diary/27232) | 2021年当時の具体例 |
| WannaCryとSMBv1・MS17-010の関係 | [Microsoft MS17-010](https://learn.microsoft.com/en-us/security-updates/securitybulletins/2017/ms17-010)、[MITRE S0366](https://attack.mitre.org/software/S0366/) | 公式／研究集約 |
| 模擬PCAPのバイト列とframe番号 | 同梱 [`generate_lab_pcaps.py`](scripts/generate_lab_pcaps.py)、[`verify_lab.py`](scripts/verify_lab.py)、[`pcap-manifest.json`](hands-on/answers/pcap-manifest.json) | 本リポジトリ内で独立再現・検査済み |


## 検証の限界（明示）

制作環境に Suricata と TShark のバイナリがないため、**実際の `-T` 成功・アラート件数・pcap_cntを実測したとは記載しない**。模擬PCAPのデータそのものはPython標準ライブラリで生成・検証している。外部の実PCAPは本ZIPに同梱せず、SANS/Unit42が公開した結果を解答として紹介している。
