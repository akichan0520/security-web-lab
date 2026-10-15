# 公開済みの実PCAP・感染調査の模範解答

本章は、プロの研究者・SOC教育者が公開した**実際の過去の通信解析**を解答とし、同じPCAPを追試できるようにしています。ZIPには実PCAP・検体を同梱しません。

| 実例 | 特徴 | 何を答え合わせできるか |
|---|---|---|
| [2021 Emotet（Unit 42）](2021-emotet-unit42-solved.md) | DLL取得、HTTP POST C2、HTTPS | 実URL・C2 IP・DLファイルのSHA256、通信の成否 |
| [2021 Emotet→TrickBot（Unit 42）](2021-trickbot-unit42-solved.md) | 二次感染、非標準ポート、HTTP POST | 実例の通信上の特徴・何が推察かを答え合わせ |
| [2021 IcedID（SANS ISC）](2021-icedid-sans-solved.md) | 感染ホスト・HTTP配布・HTTPS C2 | 実IP、ドメイン、ファイルSHA256、被害ホスト証拠 |

**実PCAP追試の手順:** 元記事の指定PCAPのみを別途取得し、Wiresharkで指定フィルタを使う。`Suricata -r` の結果は利用ルールの版によって変わるため、過去の記事とSIDが同じことを要求しない。

**安全:** 歴史的IOCを現在の悪性ホストと決めつけない。元記事に付属する実行ファイルは実行しない。
