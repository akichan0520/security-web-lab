<?php
/**
 * PHP CLIデモ: ドメイン検証とdns_get_record() / OSシェル不使用
 * 実行: php examples/dns_safe_demo.php example.com
 * DNS照会が発生する。許可された環境でのみ実行。
 */
$domain = $argv[1] ?? '';
if (!is_string($domain) ||
    filter_var($domain, FILTER_VALIDATE_DOMAIN, FILTER_FLAG_HOSTNAME) === false) {
    fwrite(STDERR, "Invalid domain\n");
    exit(1);
}
$allowed = ['example.com', 'example.org'];
if (!in_array(strtolower($domain), $allowed, true)) {
    fwrite(STDERR, "Not allowed by demo policy\n");
    exit(2);
}
$records = dns_get_record($domain, DNS_A | DNS_AAAA);
if ($records === false) {
    fwrite(STDERR, "DNS error\n");
    exit(3);
}
echo json_encode($records, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES), "\n";
