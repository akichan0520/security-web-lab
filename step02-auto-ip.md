# STEP 2 IP自動取得

## 目的

STEP 1では送信元IPを手入力していた。

STEP 2では、PHPがHTTP接続元のIPアドレスを自動取得し、JavaScript経由で画面へ表示する。

```text
Windows 11
   │
   │ HTTPアクセス
   ▼
Ubuntu Server
   │
   └─ PHP
       ↓
   REMOTE_ADDR
       ↓
   JSON
       ↓
JavaScript
       ↓
HTMLへ自動表示
```

---

## 1. get_ip.php を追加

新しく以下のファイルを作成する。

```text
get_ip.php
```

内容：

```php
<?php

$ip = $_SERVER["REMOTE_ADDR"];

$data = [
    "ip" => $ip
];

echo json_encode($data);

?>
```

---

## 2. REMOTE_ADDR

重要なのはこの部分。

```php
$_SERVER["REMOTE_ADDR"]
```

これは、

```text
このHTTP接続をしてきた相手のIPアドレス
```

をWebサーバ側で取得する。

例えば、

```text
Windows 11
192.0.2.20
     │
     │ HTTP
     ▼
Ubuntu Server
192.0.2.10
```

なら、PHP側では概念的に、

```php
$_SERVER["REMOTE_ADDR"]
```

から、

```text
192.0.2.20
```

を取得できる。

---

## 3. JSONとして返す

PHPでは取得したIPを、

```php
$data = [
    "ip" => $ip
];
```

という配列にする。

そして、

```php
echo json_encode($data);
```

でJSONへ変換する。

ブラウザから見ると、

```json
{
    "ip": "192.0.2.20"
}
```

のようなレスポンスになる。

---

## 4. index.html を変更

IP入力欄を、

```html
<input type="text" id="ip">
```

から、

```html
<input type="text" id="ip" readonly>
```

へ変更する。

画面は、

```html
<p>送信元IP</p>
<input type="text" id="ip" readonly>

<p>イベント内容</p>
<input type="text" id="event">
```

となる。

`readonly` を付けることで、通常のブラウザ操作ではIP欄を書き換えられなくなる。

ただし、

```text
readonly = セキュリティ対策
```

ではない。

この点は後で検証する。

---

## 5. script.js からPHPを呼ぶ

`script.js` の先頭付近に追加する。

```javascript
fetch("get_ip.php")
    .then(response => response.json())
    .then(data => {

        document.getElementById("ip").value = data.ip;

    });
```

処理の流れ：

```text
JavaScript
   ↓
GET /get_ip.php
   ↓
PHP
   ↓
REMOTE_ADDR取得
   ↓
JSONを返す
   ↓
JavaScript
   ↓
data.ip
   ↓
HTMLのIP欄へ表示
```

---

## 6. response.json()

STEP 1では、

```javascript
response.text()
```

を使用した。

これはPHPから、

```text
記録しました
```

という普通の文字列を受信していたため。

今回はPHPから、

```json
{"ip":"192.0.2.20"}
```

というJSONが返ってくる。

そのため、

```javascript
response.json()
```

を使用する。

---

## 7. JavaScript全体

この時点では、概ね以下のようになる。

```javascript
fetch("get_ip.php")
    .then(response => response.json())
    .then(data => {

        document.getElementById("ip").value = data.ip;

    });


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

---

## 8. 時刻も自動化

`save.php` に以下を追加する。

```php
$time = date("Y-m-d H:i:s");
```

ログ作成部分を、

```php
$log = $ip . " : " . $event . "\n";
```

から、

```php
$log =
    $time . " : " .
    $ip . " : " .
    $event . "\n";
```

へ変更する。

---

## 9. save.php

この段階では以下のようになる。

```php
<?php

$data = file_get_contents("php://input");

$json = json_decode($data, true);

$ip = $json["ip"];
$event = $json["event"];

$time = date("Y-m-d H:i:s");

$log =
    $time . " : " .
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

## 10. 動作確認

ブラウザを開く。

IP欄に自動的に、

```text
192.0.2.20
```

のような値が入れば成功。

イベント内容だけ入力する。

```text
SSH Login Failed
```

記録ボタンを押したあと、

```bash
cat alerts.txt
```

で確認する。

例：

```text
2026-10-07 12:00:00 : 192.0.2.20 : SSH Login Failed
```

---

# 重要：まだ安全ではない

一見すると、

```text
IPをPHPが自動取得した
```

ので安全そうに見える。

しかし現在は、

```text
PHP
get_ip.php
   ↓
正しいIP取得
   ↓
JavaScript
   ↓
HTML
   ↓
JavaScript
   ↓
save.php
```

となっている。

つまり、

```text
一度クライアント側へ渡した値を
save.phpが再び信用している
```

状態である。

---

# readonly は信用できない

HTMLでは、

```html
<input type="text" id="ip" readonly>
```

としている。

通常操作では変更できない。

しかしブラウザのDeveloper Toolsからは変更可能。

例えばConsoleで、

```javascript
document.getElementById("ip").value = "8.8.8.8";
```

とすると、

```text
192.0.2.20
```

だった表示を、

```text
8.8.8.8
```

へ変更できる。

---

## 改ざん実験

Developer ToolsのConsoleで、

```javascript
document.getElementById("ip").value = "8.8.8.8";
```

を実行する。

その状態で記録ボタンを押す。

Ubuntu Serverで、

```bash
tail alerts.txt
```

を確認する。

脆弱な状態では、

```text
2026-10-07 12:05:00 : 8.8.8.8 : SSH Login Failed
```

のように記録される。

---

# なぜ起きるのか

原因は `save.php`。

```php
$ip = $json["ip"];
```

となっている。

つまりPHPは、

```text
ブラウザ
「自分のIPは8.8.8.8です」

        ↓

save.php
「了解」

        ↓

alerts.txt
8.8.8.8
```

と処理している。

---

# 信頼境界

Webセキュリティでは、

```text
ブラウザ
JavaScript
HTML
HTTPリクエスト
```

は基本的に、

```text
攻撃者が変更可能
```

と考える。

概念図：

```text
HTML
  ↓
JavaScript
  ↓
HTTP Request

━━━━━━━━━━━━━━━━
     信頼境界
━━━━━━━━━━━━━━━━

PHP
  ↓
サーバ側処理
  ↓
ログ・DB
```

クライアント側の値をそのまま信用してはいけない。

---

# STEP 2で覚えること

```text
REMOTE_ADDR
→ 接続元IP取得

JSON
→ PHPとJavaScript間のデータ交換

response.json()
→ JSONレスポンス解析

readonly
→ UI制御であってセキュリティ対策ではない

Developer Tools
→ ブラウザ上の値を変更可能

信頼境界
→ クライアント側の値は信用しない
```

次のSTEPでは、`save.php` がブラウザから送信されたIPを使用するのをやめる。

保存時に、

```php
$_SERVER["REMOTE_ADDR"]
```

を使用して、サーバ側でIPを再取得する。
