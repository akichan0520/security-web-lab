<?php
/**
 * ローカルPHP CLI用：PDO SQLiteを使った安全な値のバインド例
 * 実行: php examples/pdo_safe_demo.php
 * 必須: pdo_sqlite拡張 / ネットワーク通信・外部DBなし
 */
if (!extension_loaded('pdo_sqlite')) {
    fwrite(STDERR, "PDO SQLite driver not installed (php -m to check).\n");
    exit(2);
}
$pdo = new PDO('sqlite::memory:', null, null, [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
]);
$pdo->exec('CREATE TABLE products (name TEXT NOT NULL, price INTEGER NOT NULL)');
$stmt = $pdo->prepare('INSERT INTO products (name, price) VALUES (:name, :price)');
foreach ([['apple', 100], ['pear', 120]] as [$name, $price]) {
    $stmt->execute(['name' => $name, 'price' => $price]);
}
$search = $pdo->prepare('SELECT name, price FROM products WHERE name = :name1');
foreach (['apple', "' OR 1=1 -- -"] as $needle) {
    $search->execute(['name1' => $needle]);
    $rows = $search->fetchAll(PDO::FETCH_ASSOC);
    echo "Search: ", $needle, "\nMatches: ", count($rows), "\n";
}
// 期待：appleは1件、SQL構文に見える値は0件（単なる検索文字列）。
