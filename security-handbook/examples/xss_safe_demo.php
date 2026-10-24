<?php
/**
 * ローカル教材：ユーザー入力をHTML本文へ安全に表示
 * 実行例: php -S 127.0.0.1:8080 -t examples
 * ブラウザ: http://127.0.0.1:8080/xss_safe_demo.php?name=%3Cb%3EDEMO%3C%2Fb%3E
 * 不特定多数がアクセスできるインターフェースで実行しない。
 */
$name = $_GET['name'] ?? '';
if (!is_string($name)) {
    http_response_code(400);
    exit('Invalid input');
}
$safe = htmlspecialchars($name, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
header('Content-Type: text/html; charset=UTF-8');
?><!doctype html>
<html lang="ja"><meta charset="UTF-8"><title>XSS安全な表示例</title>
<body><h1>安全な反射表示の例</h1><p><?= $safe ?></p>
<script>
  // 正規のページ内JSなら、テキストだけの変更にはtextContentを使う
  const element = document.querySelector('p');
  if (element) element.dataset.demo = 'safe';
</script></body></html>
