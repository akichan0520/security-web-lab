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
$time = date("Y-m-d H
