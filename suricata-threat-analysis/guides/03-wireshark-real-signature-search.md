# Wiresharkで公開シグネチャの「実値」を検索する

> 対象: すでに保存されたPCAPを使った、防御・インシデント解析。**架空値ではなく公開ルールに存在する値**を扱う。ただし**公開ルールの実値 ≠ 手元のPCAPに観測済みの値**。

## 0. 「パケット」と「メモリ」を区別

| データ | 実際の検査位置 | Wiresharkで検索できるか |
|---|---|---|
| Suricata `content` + `pkt_data` / 特定プロトコルの検査バッファ | PCAP由来の通信／再構成／正規化データ | 平文の通信なら概ね可能。正規化後のデータは単純検索と一致しない場合もある |
| `ja3_hash` の32桁値 | TLS ClientHelloを元に算出した指紋 | **生パケット内のASCII/16進列ではない**。対応するJA3表示フィールドまたは抽出結果で比較する |
| YARAのファイル／メモリ検出シグネチャ | 実行ファイルやプロセスメモリ | **原則PCAPからは直接探せない**。転送ファイルがPCAPに含まれていて抽出できた場合に限りファイル解析へ進む |
| ログに記載されたSID | Suricataのルール識別子 | SID自体はPCAPのバイト列ではない。EVE JSONとローカルルールを照合する |

## 1. PCAPを開いて通信を絞る

1. Wiresharkで `File → Open` からPCAPを開く。
2. 上部の**表示フィルタ欄**へ、例えば `tcp.port == 3389` / `tcp.port == 445` / `http.request` を入力してEnter。
3. `Statistics → Conversations` で通信元IP／通信先IPとポートを確認。
4. 任意のTCPパケットを選び `右クリック → Follow → TCP Stream` で往復通信を確認。
5. 目的のSIDアラートで `pcap_cnt` が得られ、元PCAPが同じなら `frame.number == N` で該当フレームへ移動できる。

## 2. 実際の16進数を直接検索する

1. メニュー **`Edit → Find Packet…`（Ctrl+F）**。
2. 検索種別を **`Hexadecimal Value`** にする。
3. 検索範囲に **`Packet bytes`** を選ぶ（Wiresharkの版で項目名が異なる場合あり）。
4. 例えば `4d:53:5f:54:31:32:30:00` を入力して **Find** を押す。
5. ヒットしたパケットの **Packet Bytes（画面下部）** を開き、位置と周辺データを確認する。
6. 見つからなければ、欠落パケット・TCP分割・圧縮・復号不能・Suricataで正規化したバッファかどうかを調べる。

**注意**: 検索欄の16進数区切りは `:` を利用する（Suricataの `|4d 53 ...|` をそのまま貼らない）。

## 3. ASCII文字列を直接検索する

1. `Ctrl+F` → 検索種別 **`String`**。
2. 検索対象を **`Packet bytes`** として `MS_T120`、`/wp-content/` のような文字列を入力。
3. 見つかった箇所と原則同じ `tcp.stream` を追い、HTTPヘッダー／URIなど**ルールの検査バッファ**も確認する。
4. UTF-16LEのYARA `wide` 文字列は単純ASCIIとは一致しない。通常はバイナリ／メモリ側の分析が必要。

## 4. 表示フィルタで生パケット内を絞る

```wireshark
# バイト列を含むTCPペイロード（TCP再構成は考慮しない）
tcp.payload contains 4d:53:5f:54:31:32:30:00
# ASCII文字列を含むTCPペイロード
tcp.payload contains "MS_T120"
# 特定パケット番号（EVE pcap_cntから）
frame.number == 1250
# Emotet研究例: HTTPのURI
http.request.uri contains "/wp-content/"
# HTTP要求全体
http.request
```

> `tcp.payload contains` は分割前の各TCPセグメントに対する検索。TCP再構成後の文字列、HTTP URI正規化後、TLS内の暗号化データとは結果が異なり得る。

## 5. ルールの全条件に戻る

```
grep -n 'sid:2027369;' /var/lib/suricata/rules/suricata.rules
jq 'select(.event_type=="alert") | [.timestamp,.alert.signature_id,.alert.rev,.pcap_cnt,.src_ip,.dest_ip] | @tsv' eve.json
```

検証項目: `flow`/プロトコル、`content`、`offset`/`depth`、`distance`/`within`、`nocase`、`http.uri` 等のsticky buffer、TCP再構成。**見つけた1つの部分文字列のみではルール一致や感染成功の証明にならない**。

## 6. ファイル／メモリ用YARAの値は別経路

```bash
# 仮に解析権限のある無害化済みファイル or ハッシュ検証済みサンプルを保有する場合
# yara -s ./rules/example.yar ./evidence/suspicious-file.bin
# ※ 上のコマンドは形式説明のみ。感染性のある実行ファイルは公開GitHubへ置かない。
```

YARAの `{ 8B ... }` はPCAP固有の検出バイトではない。実際にファイル転送がPCAPへ含まれている場合、Wireshark `File → Export Objects → HTTP` などで取得できた**適法な検証対象**のみを別途検査する。

## 根拠

- [Wireshark公式 — Finding Packets](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkFindPacketSection.html)
- [Wireshark公式 — Display Filter Reference](https://www.wireshark.org/docs/man-pages/wireshark-filter)
- [Suricata 8.0.6 — Payload Keywords](https://docs.suricata.io/en/suricata-8.0.6/rules/payload-keywords.html)
- [YARA公式 — Writing YARA Rules](https://yara.readthedocs.io/en/stable/writing_yara_rules.html)
