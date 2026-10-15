# 実在シグネチャの検証一覧

> 検証日 2026-10-15。**実値**は公開された検出ルールの文字列・バイト列であり、当該PCAPの実測値ではありません。

|対象|値の領域|公開元の実値（抜粋）|注意|
|---|---|---|---|
|[BlueKeep CVE 2019 0708](exploits/BlueKeep-CVE-2019-0708.md)|PCAPと照合可（他条件必須）|`4d 53 5f 54 31 32 30 00`|[公開出典](https://github.com/nccgroup/Cyber-Defence/blob/master/Signatures/suricata/2019_05_rdp_cve_2019_0708.txt)|
|[Emotet](malware/Emotet.md)|PCAPと照合可（他条件必須）|`2f 77 70 2d 63 6f 6e 74 65 6e 74 2f`|[公開出典](https://www.cisa.gov/news-events/cybersecurity-advisories/aa20-280a)|
|[WannaCry](malware/WannaCry.md)|PCAPと照合可（他条件必須）|`ff 53 4d 42`（SMB1ヘッダー）|[公開出典](https://github.com/Yara-Rules/rules/blob/master/malware/RANSOM_MS17-010_Wannacrypt.yar)|
|[TrickBot](malware/TrickBot.md)|PCAPと照合可（他条件必須）|`17 03 01 00 f0`|[公開出典](https://github.com/vncloudsco/suricata-rules/blob/main/pt-rules.rules)|
|[IcedID](malware/IcedID.md)|YARAファイル／メモリ用。PCAP上での出現は保証しない|`24 2c b9 09 00 00 00 2a c2 2c 07 88 44 24 0f 0f b6 c3 6b c0 43 89 44`|[公開出典](https://github.com/elastic/protections-artifacts/blob/main/yara/rules/Windows_Trojan_IcedID.yar)|
|[Agent Tesla](malware/Agent-Tesla.md)|YARAファイル／メモリ用。PCAP上での出現は保証しない|ASCII換算 `53 51 4c 69 74 65 20 66 6f 72 6d 61 74 20 33`。`wide`は実メモリ上で各ASCIIコードの後ろに `00` が入る|[公開出典](https://github.com/JPCERTCC/MalConfScan/blob/master/yara/rule.yara)|
|[LockBit 3](malware/LockBit-3.md)|YARAファイル／メモリ用。PCAP上での出現は保証しない|ASCII換算 `2e 72 64 61 74 61 24 7a 7a 7a 64 62 67`|[公開出典](https://github.com/interprobe/lockbit3.0detect_v2-byInterProbe.yara/blob/main/lockbit3.0detect_v2.yara)|
|[LockerGoga](malware/LockerGoga.md)|YARAファイル／メモリ用。PCAP上での出現は保証しない|`8b df 83 cb 0f 81 fb ff ff ff 7f 76 07 bb ff ff`|[公開出典](https://github.com/advanced-threat-research/Yara-Rules/blob/master/ransomware/RANSOM_LockerGoga.yar)|
|[StealBit](malware/StealBit.md)|YARAファイル／メモリ用。PCAP上での出現は保証しない|固定先頭 `33 c9 8b c1 83 e0 0f 8a 80`|[公開出典](https://github.com/fboldewin/YARA-rules/blob/master/Lockbit2.Stealbit.yar)|

## 検証の独立性

- `実在する公開ルール`: 出典URLに掲載された値である。
- `ローカルルールで有効`: `suricata -T` と本来のSID、revを確認する必要がある。
- `PCAP内に実在`: エビデンスとなるPCAPファイル、SHA256、フレーム番号、バイト位置を確認する必要がある。
- `感染/実行成功`: ネットワーク側だけでなく端末・EDR・Windowsログ等による確認が必要。

- Wireshark公式: https://www.wireshark.org/docs/wsug_html_chunked/ChWorkFindPacketSection.html
- 表示フィルタ仕様: https://www.wireshark.org/docs/man-pages/wireshark-filter
