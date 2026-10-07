
# STEP 1 基本フォーム

## 目的

HTML、JavaScript、PHPを連携させて、入力したセキュリティイベントをUbuntu Server側のファイルへ保存する。

この段階では、セキュリティ対策はほとんど行わない。

---

## 構成

```text
Windows 11
  │
  │ Webブラウザ
  ▼
Ubuntu Server
  │
  ├── index.html
  ├── script.js
  ├── save.php
  └── alerts.txt
```

処理の流れ：

```text
HTML
 ↓
ユーザー入力
 ↓
JavaScript
 ↓
JSON
 ↓
HTTP POST
 ↓
PHP
 ↓
alerts.txt
```

---

## 1. index.html

```html
<!DOCTYPE html>
<html lang="ja">

<head>
    <meta charset="UTF-8">
    <title>Security Event Logger</title>
</head>

<body>

    <h1>Security Event Logger</h1>

    <p>送信元IP</p>
    <input type="text" id="ip">

    <p>イベント内容</p>
    <input type="text" id="event">

    <br><br>

    <button id="sendButton">
        記録
    </button>

    <p id="result"></p>

    <script src="script.js"></script>

</body>

</html>
```

### ポイント

```html
<input type="text" id="ip">
```

`id="ip"` をJavaScriptから指定する。

```javascript
document.getElementById("ip")
```

HTMLとJavaScriptを `id` で関連付けている。

---

## 2. script.js

```javascript
const button = document.getElementById("sendButton");

button.addEventListener("click", function() {

    const ip = document.getElementById("ip").value;
    const eventText = document.getElementById("event").value;

    const data = {
        ip: ip,
        event: eventText
    };

    fetch("save.php", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify(data)

    })

    .then(response => response.text())

    .then(message => {

        document.getElementById("result").textContent = message;

    });

});
```

### JavaScriptの処理

入力された値を取得する。

```javascript
const ip = document.getElementById("ip").value;
```

データをまとめる。

```javascript
const data = {
    ip: ip,
    event: eventText
};
```

JSONへ変換する。

```javascript
JSON.stringify(data)
```

例えば、

```json
{
    "ip": "192.0.2.20",
    "event": "SSH Login Failed"
}
```

のようなデータになる。

そのJSONを `fetch()` でPHPへ送る。

---

## 3. save.php

```php
<?php

$data = file_get_contents("php://input");

$json = json_decode($data, true);

$ip = $json["ip"];
$event = $json["event"];

$log = $ip . " : " . $event . "\n";

file_put_contents(
    "alerts.txt",
    $log,
    FILE_APPEND
);

echo "記録しました";

?>
```

### PHPの処理

HTTPリクエストの本文を取得する。

```php
$data = file_get_contents("php://input");
```

JSONをPHPで扱える形式へ変換する。

```php
$json = json_decode($data, true);
```

値を取り出す。

```php
$ip = $json["ip"];
$event = $json["event"];
```

ログ形式を作る。

```php
$log = $ip . " : " . $event . "\n";
```

ファイルへ追記する。

```php
file_put_contents(
    "alerts.txt",
    $log,
    FILE_APPEND
);
```

---

## 4. PHP簡易Webサーバ起動

Ubuntu Serverで作業ディレクトリへ移動する。

```bash
cd ~/security_web
```

PHPサーバを起動する。

```bash
php -S 0.0.0.0:8000
```

Windows 11側のブラウザから、

```text
http://サーバIP:8000
```

へアクセスする。

※ Public教材では実環境のIPアドレスは掲載しない。

---

## 5. 動作確認

例：

```text
送信元IP
192.0.2.20

イベント内容
SSH Login Failed
```

「記録」を押す。

Ubuntu Serverで確認する。

```bash
cat alerts.txt
```

例：

```text
192.0.2.20 : SSH Login Failed
```

---

## 6. この時点の問題点

このSTEPでは意図的にセキュリティを甘くしている。

```text
入力値検証        なし
IP形式検証        なし
文字数制限        なし
認証              なし
CSRF対策          なし
Rate Limit        なし
改ざん対策        なし
```

特に重要なのは、

```text
ブラウザから送られてきた値を
PHPがそのまま信用している
```

ことである。

現在は、

```text
ブラウザ
   ↓
「IPは192.0.2.20です」
   ↓
PHP
   ↓
そのまま信用
```

という状態。

以降のSTEPでは、この問題を実際に確認しながら段階的に改善する。

---

## STEP 1で覚えること

```text
HTML
→ 画面を作る

JavaScript
→ ブラウザ側で値を取得・通信する

PHP
→ サーバ側で処理する

JSON
→ JavaScriptとPHPの間でデータを渡す

HTTP POST
→ クライアントからサーバへデータを送る
```

次のSTEPでは、IPアドレスを手入力せず、PHPの `REMOTE_ADDR` を使って自動取得する。
