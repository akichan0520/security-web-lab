# STEP 4 イベント自動判定

## 目的

これまでイベント内容は手入力していた。

STEP 4では、PHPがHTTPリクエストの状態を見てイベントを自動判定する。

例：

```text
通常アクセス
→ PAGE_ACCESS

User-Agentなし
→ MISSING_USER_AGENT

curl / wget
→ AUTOMATED_CLIENT

想定外HTTPメソッド
→ UNEXPECTED_METHOD
```

---

## 1. get_status.php を作る

```php
<?php

$userAgent = $_SERVER["HTTP_USER_AGENT"] ?? "";

$method = $_SERVER["REQUEST_METHOD"];

$event = "PAGE_ACCESS";

if ($userAgent == "") {

    $event = "MISSING_USER_AGENT";

}

if (
    strpos($userAgent, "curl") !== false ||
    strpos($userAgent, "wget") !== false
) {

    $event = "AUTOMATED_CLIENT";

}

if ($method != "GET") {

    $event = "UNEXPECTED_METHOD";

}

$data = [
    "event" => $event
];

echo json_encode($data);

?>
```

---

## 2. index.html を変更

イベント欄を手入力から表示専用へ変更する。

```html
<p>イベント状態</p>
<input type="text" id="event" readonly>
```

これでユーザーがイベント内容を入力しなくてもよくなる。

---

## 3. script.js から状態を取得

IP取得処理と同じように、

```javascript
fetch("get_status.php")
    .then(response => response.json())
    .then(data => {

        document.getElementById("event").value =
            data.event;

    });
```

を追加する。

---

## 4. 自動入力の流れ

```text
ブラウザ
   ↓
GET /get_status.php
   ↓
PHP
   ↓
HTTP情報を確認
   ↓
イベント判定
   ↓
JSON
   ↓
JavaScript
   ↓
HTMLへ自動表示
```

画面例：

```text
送信元IP
[192.0.2.20]

イベント状態
[PAGE_ACCESS]
```

---

## 5. User-Agent

PHPでは、

```php
$_SERVER["HTTP_USER_AGENT"]
```

からUser-Agentを取得できる。

通常のブラウザなら、

```text
Mozilla/5.0 ...
```

のような値になる。

curlなら、

```text
curl/8.x
```

のような値になる。

---

## 6. User-Agentがない場合

```php
if ($userAgent == "") {

    $event = "MISSING_USER_AGENT";

}
```

User-Agentが空の場合、

```text
MISSING_USER_AGENT
```

として判定する。

---

## 7. curl / wgetを判定

```php
if (
    strpos($userAgent, "curl") !== false ||
    strpos($userAgent, "wget") !== false
) {

    $event = "AUTOMATED_CLIENT";

}
```

`strpos()` は文字列の中に特定文字列が含まれているか調べる。

例えば、

```text
curl/8.5.0
```

に、

```text
curl
```

が含まれていれば検知する。

---

## 8. HTTP Methodを確認

```php
if ($method != "GET") {

    $event = "UNEXPECTED_METHOD";

}
```

`get_status.php` はGETアクセスを想定しているため、

```text
GET
→ 正常

POST
→ UNEXPECTED_METHOD
```

として扱う。

---

## 9. curlで実験

Ubuntu Serverから、

```bash
curl http://127.0.0.1:8000/get_status.php
```

を実行する。

例：

```json
{"event":"AUTOMATED_CLIENT"}
```

---

## 10. User-Agentなし

```bash
curl -A "" http://127.0.0.1:8000/get_status.php
```

すると、

```json
{"event":"MISSING_USER_AGENT"}
```

になる。

---

## 11. User-Agent偽装

```bash
curl -A "Mozilla/5.0" \
http://127.0.0.1:8000/get_status.php
```

すると、

```text
PAGE_ACCESS
```

として扱われる可能性がある。

ここが重要。

```text
User-Agent
=
クライアント自己申告
```

なので、完全には信用できない。

---

## 12. 自動検知の考え方

今回やっていることは、

```text
HTTP通信
   ↓
特徴取得
   ↓
条件判定
   ↓
イベント分類
```

という流れ。

これは後のIDSにもつながる。

```text
通信
 ↓
ルール
 ↓
一致
 ↓
Alert
```

---

## 13. 重要度を追加

イベントだけでなくSeverityも付ける。

```php
$event = "PAGE_ACCESS";
$severity = "INFO";
```

例えば、

```php
if ($userAgent == "") {

    $event = "MISSING_USER_AGENT";
    $severity = "WARNING";

}
```

curlの場合：

```php
if (
    strpos($userAgent, "curl") !== false ||
    strpos($userAgent, "wget") !== false
) {

    $event = "AUTOMATED_CLIENT";
    $severity = "NOTICE";

}
```

想定外メソッド：

```php
if ($method != "GET") {

    $event = "UNEXPECTED_METHOD";
    $severity = "WARNING";

}
```

---

## 14. 現在の問題

ここまでで自動判定はできるようになった。

しかし、

```text
get_status.php
```

と、

```text
save.php
```

で同じ判定ロジックを書くと、

```text
コード重複
```

が発生する。

例えば、

```php
if (strpos($userAgent, "curl") !== false)
```

を両方に書く必要がある。

これは、

```text
修正漏れ
判定差異
保守性低下
```

につながる。

---

# STEP 4で覚えること

```text
User-Agent
HTTP Method
strpos()
条件分岐
イベント自動判定
Severity
クライアント情報は偽装可能
```

---

# 次のSTEP

STEP 5では、

```text
判定ロジックを1か所へまとめる
```

ため、

```text
detect.php
```

を作る。

そして、

```text
get_status.php
save.php
```

の両方から同じ関数を呼び出す。

これにより、

```text
表示用判定
保存用判定
```

を同じロジックで管理できる。
