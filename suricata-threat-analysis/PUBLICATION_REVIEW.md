# 公開直前レビュー（2026-10-15）

## 今版で実施した監査

1. 全Markdownページを検索し、同一ZIP内の**相対リンク切れ0件**を確認。
2. 同梱PCAP6本について、[`scripts/verify_lab.py`](scripts/verify_lab.py)により**元PCAP内の該当フレームと実バイト**を確認。
3. [`scripts/generate_lab_pcaps.py`](scripts/generate_lab_pcaps.py) をPython標準ライブラリで実行し、SHA256付きのマニフェストを出力。
4. Pythonスクリプトの構文コンパイル、既存シェルスクリプトの`bash -n`を通過。
5. 事実の出典URLは[出典対応表](SOURCE_MAP.md)に整理。
6. **Suricata 8.0.7実行バイナリなし**のため、`-T` とEVEアラート発火については本環境では再現確認できていないことを明記。

## 安全性

- 模擬PCAPはRFC 5737の文書用IPアドレス（192.0.2.0/24、198.51.100.0/24）を利用。
- 実際の攻撃コード、マルウェア実行ファイル、実際の認証情報は含めない。
- 公開事例に含まれるIOCは過去の観測情報として**defangした形式**で解説。
- 一般的なSMB1ヘッダーや`/wp-content/`を特定マルウェアの専用シグネチャだと誤認させない。

## 残る制約

- 公開ETシグネチャの`SID`/`rev`は更新され得る。現行ルールの具体的な適合性は実行環境で検証が必要。
- 本ZIPはオフライン演習のために作成した無害な模擬トラフィックを主としており、実在マルウェアのトレースを偽装していない。
- 実際のEmotet/TrickBot/IcedIDについてはUnit 42/SANSが公開した**解答済み研究結果の引用・再解説**であり、ZIP作者の独立再解析ではない。

## 作成・監査の一次参考

- [OISF Suricata 8.0.7](https://suricata.io/2026/09/15/suricata-8-0-7-released/)
- [Suricata Rules](https://docs.suricata.io/en/suricata-8.0.7/rules/intro.html)
- [Wireshark Find Packet](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkFindPacketSection.html)
- [Unit 42 Emotet PCAP](https://unit42.paloaltonetworks.com/wireshark-tutorial-emotet-infection/)
- [SANS ISC IcedID 2021](https://isc.sans.edu/diary/27232)
