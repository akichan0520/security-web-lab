# STEP 3 サーバ側検証

## 目的

STEP 2では、IPアドレスを自動取得したものの、その値をJavaScript経由で再びPHPへ送信していた。

そのため、ブラウザ上でIPアドレスを改ざんすると、偽のIPがそのままログへ保存されてしまった。

STEP 3では、保存時にクライアント側の値を信用せず、PHPが自分で接続元IPを再取得する。

---

## STEP 2の問題点

STEP 2では、保存処理が以下のようになっていた。

```php
$ip = $json["ip"];
```

つまり、

```text
ブラウザ
   ↓
JavaScript
   ↓
「IPは8.8.8.8です」
   ↓
save.php
   ↓
そのまま信用
```

という状態だった。

---

## 改ざん実験

ブラウザのDeveloper Toolsで、

```javascript
document.getElementById("ip").value = "8.8.8.8";
```

と入力すると、画面上のIPを変更できる。

その状態で保存すると、

```text
8.8.8.8
```

がログに記録されてしまう。

これは、

```text
クライアントが送ってきた値を
サーバが無条件で信用している
```

ことが原因。

---

# 1. save.phpを修正

以下の、

```php
$ip = $json["ip"];
```

を削除する。

代わりに、

```php
$ip = $_SERVER["REMOTE_ADDR"];
```

とする。

---

## 修正後のsave.php

```php
<?php

$data = file_get_contents("php://input");

$json = json_decode($data, true);

$ip = $_SERVER["REMOTE_ADDR"];

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

# 2. なぜ安全性が上がるのか

変更前：

```text
ブラウザ
 ↓
IPを送信
 ↓
PHPが信用
 ↓
ログ保存
```

変更後：

```text
ブラウザ
 ↓
「IPは8.8.8.8です」
 ↓
PHP
 ↓
その値を使わない
 ↓
REMOTE_ADDRを取得
 ↓
本当の接続元IPを保存
```

保存に使うIPを、クライアントから受け取らなくなった。

---

# 3. JavaScriptも整理

IPアドレスをPHP側で決定するようになったため、保存時にIPを送信する必要がなくなる。

変更前：

```javascript
const ip = document.getElementById("ip").value;

const data = {
    ip: ip,
    event: eventText
};
```

変更後：

```javascript
const data = {
    event: eventText
};
```

IP欄は画面表示用として残す。

---

## 保存処理

```javascript
const button = document.getElementById("sendButton");

button.addEventListener("click", function() {

    const eventText =
        document.getElementById("event").value;

    const data = {
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

        document.getElementById("result").textContent =
            message;

    });

});
```

---

# 4. 再度改ざん実験

Developer Toolsで、

```javascript
document.getElementById("ip").value = "8.8.8.8";
```

とする。

画面上は、

```text
8.8.8.8
```

に変わる。

しかし保存後に、

```bash
tail alerts.txt
```

を確認すると、

```text
2026-10-07 13:00:00 : 192.0.2.20 : SSH Login Failed
```

のように、本来の接続元IPが保存される。

---

# 5. 画面表示と保存値は別物

ここで重要なのは、

```text
画面に表示されている値
```

と、

```text
サーバが実際に使用する値
```

は別物だということ。

画面：

```text
8.8.8.8
```

保存：

```text
192.0.2.20
```

という状態が成立する。

---

# 6. readonlyは防御ではない

HTMLの、

```html
<input type="text" id="ip" readonly>
```

は、

```text
ユーザーが普通に入力できない
```

ようにしているだけ。

Developer ToolsやJavaScriptからは変更できる。

つまり、

```text
readonly
disabled
hidden
```

などは、

```text
ユーザーインターフェース制御
```

であって、

```text
セキュリティ境界
```

ではない。

---

# 7. 信頼できる場所で再判定する

今回の考え方：

```text
クライアント
↓
変更可能

━━━━━━━━━━━━━━━
     信頼境界
━━━━━━━━━━━━━━━

サーバ
↓
ここで再取得・再判定
```

この考え方はWebセキュリティ全般で重要。

---

# STEP 3で覚えること

```text
クライアント値は信用しない

重要な値はサーバ側で取得する

表示用データと保存用データは分離できる

readonlyはセキュリティ機能ではない

REMOTE_ADDRは保存時にも再取得する
```

---

# 次のSTEP

STEP 4では、これまで手入力していたイベント内容も自動化する。

例えば、

```text
PAGE_ACCESS
AUTOMATED_CLIENT
MISSING_USER_AGENT
UNEXPECTED_METHOD
```

などをPHP側で自動判定する。

さらに、

```text
INFO
NOTICE
WARNING
```

といった重要度も自動で付与する。
