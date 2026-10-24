# CTF問題集：答え合わせと学習目的

> `lab/server.py` をローカルで起動して取り組む。全て架空データ。ファイル閲覧・任意コマンド実行は含まれない。

## 問題SQL-01｜通常の検索と不一致

**目的**：検索欄で `Travel Kit` が1件、存在しない商品名が0件になる理由を説明する。

<details><summary>解説を見る</summary>

DBの`WHERE name = ?`という条件では、照合結果が0件か1件かを返す。これだけではSQLiを証明しない。実際のSQL構築が文字列連結かパラメータ化かを比較する。

</details>

## 問題SQL-02｜同じ入力で脆弱・安全を比較

**目的**：`' OR '1'='1' -- ` を `/lab/sql/vuln` と `/lab/sql/safe` の検索欄に入力し、何件になるか比較。どこが違うか説明する。

<details><summary>解説を見る</summary>

脆弱版は入力をSQL構文に連結している。安全版はDB-APIのプレースホルダーを使って値として渡している。DB構文と入力値の分離がポイント。

</details>

## 問題SQL-03｜SQLエラーと0件を分ける

**目的**：`'` 単独入力、存在しない商品、正常商品を比較し、HTTP status/本文の違いを記録する。

<details><summary>解説を見る</summary>

不正な引用符はSQL構文エラーになり得るが、「ヒットなし」と区別が必要。500が出るだけではSQLi成立と即断しない。公式のError Handling対策ではDB例外を利用者へ開示しない。

</details>

## 問題WEB-01｜XSSの反射位置

**目的**：文字列 `CTF_MARKER_123` を入力し、HTTPレスポンスとDOMの違いを観察する。

<details><summary>解説を見る</summary>

Responseにあるか・Elementsにあるかでサーバー反射とDOM処理の違いを考える。HTMLとして解釈されるのか文字列であるのかを別途検証する。

</details>

## 問題WEB-02｜`innerHTML` と `textContent`

**目的**：同じ任意文字列を扱う二つのAPIの挙動を比べる。

<details><summary>解説を見る</summary>

`textContent`はテキストとして扱う。`innerHTML`はHTMLとして構築される。任意のHTMLを許すなら厳密なHTMLサニタイズなどが必要。

</details>

## 問題OS-01｜DNS検証とコマンドの境界

**目的**：PHPの`$_GET`、`filter_var`、`dns_get_record()`がそれぞれ何を行うか言語化する。

<details><summary>解説を見る</summary>

`$_GET`は入力取得、フィルターは形式検証、`dns_get_record()`はシェルを利用しないDNS問い合わせ。入力検証だけでコマンド実行やSSRF周辺の全リスクは無くならない。

</details>

## 問題AUTH-01｜SQLiがなくても起きる漏洩

**目的**：他人の`order_id`を知っているだけで購入履歴を表示できる実装の問題点を説明する。

<details><summary>解説を見る</summary>

認可不備（IDOR/BOLA）の可能性。ログイン状態だけでなく注文データの所有権チェックが必要。

</details>
