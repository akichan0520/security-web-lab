# STEP 5 検知ロジックの共通化

## 目的

STEP 4では、イベント判定ロジックを `get_status.php` や `save.php` にそれぞれ書いていた。

このままだと、同じ条件を複数ファイルに書くことになり、

```text
修正漏れ
判定差異
コード重複
```

が起こりやすい。

STEP 5では、判定処理を `detect.php` にまとめて共通化する。

---

## 1. detect.php を作る

```php
<?php

function detectEvent($userAgent, $method, $expectedMethod)
{
    $event = "PAGE_ACCESS";
    $severity = "INFO";

    if ($userAgent == "") {

        $event = "MISSING_USER_AGENT";
        $severity = "WARNING";
    }

    if (
        strpos($userAgent, "curl") !== false ||
        strpos($userAgent, "wget") !== false
    ) {

        $event = "AUTOMATED_CLIENT";
        $severity = "NOTICE";
    }

    if ($method != $expectedMethod) {

        $event = "UNEXPECTED_METHOD";
        $severity = "WARNING";
    }

    return [
        "event" => $event,
        "severity" => $severity
    ];
}

?>
```

---

## 2. 関数とは

今回初めて、

```php
function detectEvent(...)
```

という関数を使う。

関数は、

```text
よく使う処理を
ひとまとまりの部品にする
```

ための仕組み。

例えば、

```php
detectEvent(
    $userAgent,
    $method,
    "GET"
);
```

と呼び出すと、

```text
User-Agent
HTTP Method
正常とみなすMethod
```

を使ってイベント判定を行う。

---

## 3. 引数

関数定義：

```php
function detectEvent($userAgent, $method, $expectedMethod)
```

3つの値を受け取る。

```text
$userAgent
→ HTTP User-Agent

$method
→ 実際のHTTP Method

$expectedMethod
→ 本来期待しているHTTP Method
```

---

## 4. なぜ expectedMethod が必要か

`get_status.php` は通常、

```text
GET
```

で呼ばれる。

一方 `save.php` は、

```text
POST
```

を想定している。

そのため、

```php
detectEvent(
    $userAgent,
    $method,
    "GET"
);
```

や、

```php
detectEvent(
    $userAgent,
    $method,
    "POST"
);
```

のように使い分ける。

---

## 5. 戻り値

最後に、

```php
return [
    "event" => $event,
    "severity" => $severity
];
```

としている。

例えば通常アクセスなら、

```php
[
    "event" => "PAGE_ACCESS",
    "severity" => "INFO"
]
```

が返る。

curlなら、

```php
[
    "event" => "AUTOMATED_CLIENT",
    "severity" => "NOTICE"
]
```

となる。

---

## 6. get_status.php を変更

```php
<?php

require_once "detect.php";

$userAgent = $_SERVER["HTTP_USER_AGENT"] ?? "";

$method = $_SERVER["REQUEST_METHOD"];

$result = detectEvent(
    $userAgent,
    $method,
    "GET"
);

echo json_encode($result);

?>
```

---

## 7. require_once

今回新しく出てきたのが、

```php
require_once "detect.php";
```

である。

これは、

```text
別ファイルのPHPコードを読み込む
```

という意味。

これにより `get_status.php` から、

```php
detectEvent()
```

を使えるようになる。

`once` が付いているため、同じファイルを重複して読み込むことも防げる。

---

## 8. save.php を変更

```php
<?php

require_once "detect.php";

$ip = $_SERVER["REMOTE_ADDR"];

$userAgent = $_SERVER["HTTP_USER_AGENT"] ?? "";

$method = $_SERVER["REQUEST_METHOD"];

$time = date("Y-m-d H:i:s");

$result = detectEvent(
    $userAgent,
    $method,
    "POST"
);

$event = $result["event"];

$severity = $result["severity"];

$log =
    $time . " : " .
    $severity . " : " .
    $ip . " : " .
    $event . "\n";

file_put_contents(
    "alerts.txt",
    $log,
    FILE_APPEND
);

echo "記録しました";

?>
```

---

## 9. 処理の流れ

```text
get_status.php
      │
      └──────┐
             │
             ▼
         detect.php
         判定ロジック
             ▲
             │
      ┌──────┘
      │
   save.php
```

判定処理は `detect.php` に1回だけ書く。

---

## 10. JavaScript側

JavaScriptはイベント判定をしない。

PHPから結果を取得して表示するだけにする。

```javascript
fetch("get_status.php")
    .then(response => response.json())
    .then(data => {

        document.getElementById("event").value =
            data.event;

    });
```

役割分担：

```text
JavaScript
→ 表示

PHP
→ 判定
```

---

## 11. なぜサーバ側で判定するのか

JavaScriptは利用者側で動作する。

そのため、

```text
Developer Tools
JavaScript書き換え
HTTPリクエスト変更
```

などが可能。

一方、PHPはUbuntu Server側で実行される。

```text
Browser
   ↓
変更可能

━━━━━━━━━━━━━━
   信頼境界
━━━━━━━━━━━━━━

PHP
   ↓
サーバ側判定
```

重要な判定はサーバ側に置く。

---

## 12. 改ざん実験

画面上のイベントを、

```javascript
document.getElementById("event").value =
    "CRITICAL_ATTACK";
```

などに変更する。

表示上は、

```text
CRITICAL_ATTACK
```

となる。

しかし `save.php` は画面の値を信用せず、

```php
detectEvent()
```

を再実行する。

そのためログには、

```text
PAGE_ACCESS
```

などPHPが判定したイベントが保存される。

---

## 13. 現在の構成

```text
security_web/
├── index.html
├── script.js
├── get_ip.php
├── get_status.php
├── detect.php
├── save.php
├── access.php
└── alerts.txt
```

---

## 14. この構成の利点

例えば今後、

```text
Python Requests
特定URI
大量アクセス
不審Method
特定User-Agent
```

などを追加したい場合、

基本的には、

```text
detect.php
```

だけを拡張すればよい。

---

# STEP 5で覚えること

```text
function
→ 処理を部品化する

引数
→ 関数へ値を渡す

return
→ 関数から結果を返す

require_once
→ 別PHPファイルを読み込む

共通化
→ 同じ処理を1か所で管理する

Server-side validation
→ 重要な判定はサーバ側で行う
```

---

# セキュリティ的な意味

今回の構造は簡単だが、考え方はIDSにも近い。

```text
HTTP通信
   ↓
特徴を取得
   ↓
detectEvent()
   ↓
ルール判定
   ↓
Event
   ↓
Severity
   ↓
ログ保存
```

将来的には、

```text
PHP検知
↓
Suricata検知
↓
eve.json
↓
Elastic
↓
Kibana
```

へ発展させる。

---

# 次のSTEP

次は検知結果に、

```text
Reason
```

を追加する。

例えば、

```text
Event:
AUTOMATED_CLIENT

Severity:
NOTICE

Reason:
User-Agent contains curl
```

のように、

```text
何を検知したか
どれくらい重要か
なぜ検知したか
```

まで自動生成する。

これは後のSuricataの、

```text
signature
category
severity
```

の理解にもつながる。
