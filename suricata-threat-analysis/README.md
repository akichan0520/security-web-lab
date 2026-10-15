# Suricata × Wireshark 脅威通信解析「答え付き」ハンズオン

> **2026-10-15版／Suricata 8.0.7基準（8.0.6でも主要演習が使用可能）**
>
> マルウェアや脆弱性悪用を、**検出ルール → 実際の通信バイト → Wireshark → Suricataアラート → 証拠評価**という順番で学ぶ日本語の参考書。前版の「未評価を埋めるだけ」の形式を改め、**模擬PCAP 6本＋解答集＋公開専門家の実PCAP解析答え合わせ**を追加しました。

## 3種類の「正解」を区別する

| 種類 | 収録場所 | 何が正しいと確認済みか | 留意点 |
|---|---|---|---|
| A. **自作安全PCAP** | [`hands-on/`](hands-on/START_HERE.md) | 実際にZIPに入っているバイト列、フレーム番号、送信元・宛先、SHA256をPythonで再現検証 | **実マルウェア通信ではない**。Suricata実行確認は使用者側で必要 |
| B. **公開実事件の模範解答** | [`cases/`](cases/INDEX.md) | SANS ISCとPalo Alto Unit 42の一次報告に記載された実IP、通信先、時系列、IOC | 元PCAP・危険な検体をこのZIPに同梱しない。こちらでは実PCAPを再解析していない |
| C. **実在する公開シグネチャ** | [`PATTERN_EVIDENCE.md`](PATTERN_EVIDENCE.md) | 公開ルールの実際のバイト値やYARA値、適用範囲 | **実PCAPに実在する・感染した**という意味ではない |

## まず15分で始める

1. [`hands-on/START_HERE.md`](hands-on/START_HERE.md) に移動する。
2. [演習01：HTTP URI](hands-on/lessons/01-http-uri.md) の付属PCAPをWiresharkで開く。
3. `tcp.port == 80` を表示 → `Ctrl+F` またはMacの `Cmd+F` で `/wp-content/` を検索。
4. **frame 4 / `192.0.2.10 → 198.51.100.20:80` / SID 9900001** を正解集と比べる。
5. 自分のSuricataで `-S rules/lab.rules -r ...` を実行し、ログと対応づける。

## 章ごとのおすすめ順序

| 難易度 | 章・テーマ | 目標 |
|---|---|---|
| 入門 | [01 HTTP URI](hands-on/lessons/01-http-uri.md) | 文字列/16進数検索 |
| 入門 | [02 RDP marker](hands-on/lessons/02-rdp-marker.md) | BlueKeepで使われた `MS_T120` の位置 |
| 入門 | [03 SMB1](hands-on/lessons/03-smb1.md) | WannaCry固有IOCと一般的SMB1を区別 |
| 初級 | [04 DNS](hands-on/lessons/04-dns.md) | 正規化バッファとワイヤ表現の違い |
| 中級 | [05 TCP分割](hands-on/lessons/05-tcp-split.md) | セグメント再構成とシグネチャ照合 |
| 中級 | [06 誤検知](hands-on/lessons/06-false-positive.md) | 一致＝感染ではない理由 |
| 実例 | [Emotet × Unit 42](cases/2021-emotet-unit42-solved.md) | 専門家が記録した実際の感染シーケンスを再現 |
| 実例 | [Emotet→TrickBot × Unit 42](cases/2021-trickbot-unit42-solved.md) | HTTP POST・TCP 447/449に関する公開事例 |
| 実例 | [IcedID × SANS ISC](cases/2021-icedid-sans-solved.md) | 実際の被害IP、DL通信、C2、端末証拠を突合 |

## マルウェアと攻撃別リファレンス

**脆弱性悪用：** [BlueKeep（CVE-2019-0708／ET SID 2027369）](exploits/BlueKeep-CVE-2019-0708.md)（※マルウェアではなく脆弱性）

**マルウェア：** [Emotet](malware/Emotet.md) · [WannaCry](malware/WannaCry.md) · [TrickBot](malware/TrickBot.md) · [IcedID](malware/IcedID.md) · [Agent Tesla](malware/Agent-Tesla.md) · [LockBit 3.0](malware/LockBit-3.md) · [LockerGoga](malware/LockerGoga.md) · [StealBit](malware/StealBit.md)

## Wireshark・Suricataのリファレンス

- [基本の調査手順](guides/01-workflow.md)
- [ルールとバイト列：offset/depth/distance/within](guides/02-rule-to-bytes.md)
- [実際のシグネチャ値検索](guides/03-wireshark-real-signature-search.md)
- [Wireshark検索チートシート](guides/04-wireshark-cheatsheet.md)
- [証拠レベルの判定方法](guides/05-evidence-grades.md)
- [出典・説明文の対応表](SOURCE_MAP.md)
- [公開直前レビューと未実施テスト](PUBLICATION_REVIEW.md)
- [リポジトリ導入／更新ガイド](INSTALL_GITHUB.md)

## 自分の環境で演習する（リポジトリのルートで実行）

```bash
# まず、同梱したPCAPのフレーム番号とバイト列が壊れていないか検査
python3 scripts/verify_lab.py

# ルール構文を自分のSuricataで確認。-Sで演習ルールのみロード
sudo suricata -T -c /etc/suricata/suricata.yaml -S "$PWD/rules/lab.rules"

# PCAPのオフライン解析
mkdir -p logs/01
sudo suricata -c /etc/suricata/suricata.yaml \
  -S "$PWD/rules/lab.rules" -r "$PWD/hands-on/pcaps/01-http-uri.pcap" \
  -l "$PWD/logs/01"

jq 'select(.event_type=="alert") | [.alert.signature_id,.src_ip,.dest_ip,.pcap_cnt]|@tsv' logs/01/eve.json
```

**元の教材と関係のないETルール読込エラーは `-S` で切り離す**、というのが今回の演習のポイントです。資料の制作環境ではSuricataの実行バイナリがなかったため、付属PCAPのフレームとバイトはプログラムで検証済みですが、実際のアラート件数はユーザー環境で検証してください。

## 最新Suricataの根拠

- [OISF: Suricata 8.0.7 released（2026-09-15）](https://suricata.io/2026/09/15/suricata-8-0-7-released/)
- [Suricata 8.0.7公式ユーザーガイド](https://docs.suricata.io/en/suricata-8.0.7/)
- [Suricata 8.0.7 EVE JSON](https://docs.suricata.io/en/suricata-8.0.7/output/eve/eve-json-format.html)
- [Wireshark公式：パケット検索](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkFindPacketSection.html)
- [MITRE ATT&CK Software](https://attack.mitre.org/software/)

## セキュリティとライセンス

このZIPは**実行形式のマルウェアや実悪用コードを配布しません**。同梱PCAPはすべて本プロジェクトで生成した無害な模擬データであり、外部に実際の通信は送信しません。外部事例のPCAP・アーカイブには攻撃コードや不審ファイルが混入する可能性があるため、閲覧は分離されたVMで行い、抽出した実行ファイルを開かないでください。

学術引用にあたっては、各ページの元記事・メーカー公式資料・MITRE記載の出典を優先してください。IOCは歴史的事実であり、今日のブロックリストではありません。
