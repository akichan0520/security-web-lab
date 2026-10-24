# 認証・認可・CSRF・ファイルアップロード：CTF調査メモ

## 認証（Authentication）と認可（Authorization）

- 認証：**誰か**を判定する（ログイン、セッション、トークンなど）。
- 認可：**その人が特定の操作・データを扱ってよいか**判定する。
- PDOでSQLiを防いでいても、IDを書き換えると他人の注文が見られるなら **認可不備**（IDOR/BOLA）になり得る。

### CTFでの着眼点

| 観測 | 説明すべきこと | 防御 |
|---|---|---|
| 通常ユーザーが管理操作を見られる | ロールとエンドポイントの許可チェック | deny-by-default、サーバー側権限判定 |
| 所有者以外のオブジェクトが見える | `id` の照合不足 | オブジェクトごとの所有権検証 |
| ログアウト後もセッションが生きる | 失効処理 | セッション再生成と失効 |
| 重要操作でCSRFトークンがない | 別サイトからの操作 | CSRFトークン、SameSite等 |
| 拡張子のみでアップロード許可 | コンテンツと実行設定の問題 | 保存先分離、MIME/拡張子許可リスト、実行禁止 |

## パスワード保存

PHPの `password_hash()` と `password_verify()` を使う。**暗号化文字列として復号するのではなく、専用の一方向ハッシュで照合**する。ソルトやコスト管理は公式推奨APIに任せる。DBのパスワードハッシュが流出した場合のリスクは、平文保存よりは小さいがゼロではない。

## CSRFとXSSの関係

CSRFは認証済みブラウザに望まないリクエストを送らせる問題。XSSが成立するとCSRF防御も弱まることがあるため、**両方の対策が必要**。

## アップロードのファイル名と実体

画像拡張子だけのチェック、公開Webルートへの保存、実行権限のまま配布する設計を避ける。Webルート外へ保存し、ランダム名で管理し、実行権限を外し、内容を検査する。ダウンロードは適切なContent-Type / Content-Dispositionで返す。

## 根拠

- [OWASP Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [OWASP CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP File Upload](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [PHP Password Hashing](https://www.php.net/manual/en/function.password-hash.php)
