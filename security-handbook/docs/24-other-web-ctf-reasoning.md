# 24｜その他のWeb CTFで理論的に判断するための要点

## 1. 認証(authentication) と認可(authorization) の違い

- 認証：誰かを確かめる。セッションCookieなど。
- 認可：その利用者がその**対象オブジェクト**へアクセスしてよいか確かめる。
- SQLが完全にパラメータ化されても、認可漏れ（IDOR/BOLA）で他人のオブジェクトを表示できることがある。

```python
# 認可の設計例。ログインユーザーIDはサーバーのセッションから取得。
# この条件を含めなければ、IDだけを変えることで他人の注文を参照できる恐れ。
cur.execute('SELECT * FROM orders WHERE id=? AND owner_id=?',
            (requested_order_id, authenticated_user_id))
```

## 2. CSRF：ブラウザが認証情報を自動送信することと操作の意図は別

CSRFでは、ブラウザのCookieが自動送信され得ることと、その操作を本人が意図したかを区別。状態変更にはCSRFトークン、SameSite Cookie、Origin/Refererの追加検証など多層防御。**XSSがあるとCSRFの前提が崩れる場合もある**。

## 3. File Upload：拡張子だけでは安全ではない

アップロードされたファイルは、拡張子、MIME、マジックバイト、保存先、Webサーバーによる実行可否が別々。公開ディレクトリへ置かない、ランダム名、権限最小化、サイズ制限、必要なら画像等をデコード・再生成する設計を検討する。単に`file.php`を禁止するだけでは防御が完成しない。

## 4. パストラバーサル：WebルートとOSパスは違う

アプリがユーザーのファイル名をOSパスと連結する場合、ディレクトリの境界を越える設計になり得る。防御は親ディレクトリの固定、正規化後の許可ディレクトリ内チェック、最小権限で行う。`../`という文字列だけを拒否する実装に頼らない。

## 5. SSRF：リクエスト送信先の制御

サーバーがユーザー指定URLにアクセスする機能は、内部IPや管理用サービスへの接続、DNSの結果変化などへの対策が必要。**URL文字列が正常でも安全な接続先とは限らない**。許可スキーム・ホスト・解決後IP、リダイレクト先を確認し、ネットワークで制限する。

## 6. JWT・Cookie・セッション

JWTをデコードできることと、署名を検証できることは別。セッション管理ではCookieの`Secure`・`HttpOnly`・`SameSite`、再認証、期限、権限更新時の反映を考える。`HttpOnly`はXSSでのCookie直接読取りを制限するが、XSS全体の防御ではない。

## 7. 調査する時のフレームワーク

```text
A. 入力/変更できるものは何か（値・URL・メソッド・Cookie）
B. 保存先や実行場所はどこか（DB・FS・OS・ブラウザ）
C. どの文法で解釈されるか（SQL / Shell / HTML / JS）
D. 認証と認可がどこで検査されるか
E. 観測可能な結果は何か（応答・時間・状態）
F. 根本原因と修正確認を一文で説明できるか
```

## 一次資料

- [OWASP WSTG](https://wstg.owasp.org/)
- [OWASP File Upload](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [OWASP SSRF](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP IDOR](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html)
- [OWASP CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
