# Webセキュリティ実践ノート — SQLi / XSS / OSコマンド / PHP / CTF

**更新基準日：2026-10-24 ｜ 言語：日本語 ｜ 公開用（実環境の秘密情報なし）**

CTFで学んだWeb攻撃の原理を、**HTTP通信 → 解釈される言語 → 脆弱性が生まれる境界 → 観測方法 → 対策 → 根拠**の順に整理した学習資料です。単なるコマンド集ではなく「なぜ成立するのか」を重視します。

> **使用条件**：自分で管理する検証環境、または明示的に許可されたCTFのみで実行してください。記載のホスト名、DB名、利用者名、認証情報は架空です。演習環境で得た実IP、Cookie、パスワード、フラグ、シェルファイル等は公開しません。

## 学習マップ

```mermaid
flowchart TD
 A[ユーザー入力] --> B[HTTPリクエスト]
 B --> C[Webアプリ: PHP/Python等]
 C --> D{入力が何として扱われる?}
 D -->|SQL文の構造| S[SQL Injection]
 D -->|OSシェルの構造| O[OS Command Injection]
 D -->|HTML/JavaScript| X[XSS]
 C --> R[ランタイム/依存ライブラリ]
 R --> P[PHPランタイム脆弱性など]
 S --> SD[パラメータ化 / DB最小権限]
 O --> OD[シェル排除 / API利用 / 入力検証]
 X --> XD[文脈別出力エンコード / 安全なDOM API]
 P --> PD[公式修正版へ更新 / 隔離 / 監視]
```

## 目次

| ファイル | 理解できること |
|---|---|
| [00｜HTTPと信頼境界](docs/00-http-trust-boundaries.md) | リクエスト/レスポンス、パーサー、インジェクションの共通原理 |
| [01｜SQLインジェクション](docs/01-sqli.md) | Boolean Blind / Error-based / UNION / 原因と防御 |
| [02｜BurpとSQLmap](docs/02-burp-sqlmap.md) | GET・POST、リクエスト保存、判定、エラーの読み方 |
| [03｜DBとファイルシステム](docs/03-mysql-files-os.md) | FILE権限、`secure_file_priv`、OSシェルとの境界、`find` |
| [04｜XSS](docs/04-xss.md) | 反射型・蓄積型・DOM型、`<p>`変更、`innerHTML`の危険性 |
| [05｜PHP PDO](docs/05-php-pdo.md) | `prepare()`、`:name1`、`bindValue()`、認可・権限制御 |
| [06｜OSコマンドインジェクション](docs/06-command-injection.md) | `exec(nslookup)`の危険、DNS専用API、ドメイン検証 |
| [07｜PHP2Shell 2026](docs/07-php2shell-2026.md) | ランタイム脆弱性とDB、影響条件、公式修正版 |
| [08｜CTF調査方法](docs/08-ctf-method.md) | 仮説→観測→結論、誤判定回避、上級CTFの考え方 |
| [09｜エラー辞典](docs/09-error-troubleshooting.md) | HTTP 405/500、DBエラー、No output、シェルの診断 |
| [10｜攻撃連鎖と多層防御](docs/10-attack-chain-defense.md) | SQLiから別の権限領域へ波及する条件と遮断ポイント |
| [11｜防御コードレビュー](docs/11-code-review.md) | 発見した脆弱性をどのコードで直すか |
| [12｜CTFケーススタディ](docs/12-case-study.md) | 実際の検証で何が分かり何が未検証なのか |
| [証拠・参考文献](SOURCES.md) | 公式一次資料、参照先と検証限界 |
| [公開前チェック](PUBLICATION_CHECKLIST.md) | 秘密情報・検証根拠・安全性のレビュー |

## 要点早見表

| 技術 | 根本原因 | 代表的な対策 | よくある誤解 |
|---|---|---|---|
| SQLi | 入力がSQL構造の一部になる | パラメータ化・識別子の許可リスト | `prepare`という文字があるだけで安全 |
| XSS | 信頼できない値が実行可能なHTML/JSとして扱われる | 出力文脈別エンコード・安全なDOM API | DB保存時のSQLi対策でXSSも防げる |
| OSコマンド注入 | 入力がシェル構造の一部になる | OSコマンドをやめて専用API | `$_GET`へ代入すれば安全 |
| PHPランタイム | アプリコード外の実行環境に欠陥 | 修正版の適用、被害縮小策 | `PDO::prepare()`でPHPエンジンのRCEも防げる |

## 手元で安全に確かめる

`examples/` に**防御実装だけ**を置きました。実行する場合もローカル/隔離環境で、PHP CLIおよび必要な拡張を確認してください。攻撃用Webシェルや実サーバーの抽出データは収録していません。

## GitHubへの追加

既存リポジトリのルートにこの `security-notes` フォルダを追加すれば、既存のREADMEや教材を上書きしません。GitHubのMarkdownとMermaidでそのまま閲覧できます。Git操作の例は [公開前チェック](PUBLICATION_CHECKLIST.md) に記載。

## 学習記録の位置づけ

過去の演習での表示（例：`Werkzeug/Python`、`name`パラメータ、`Boolean-based`、`No output`）は**観測例**です。全ての環境に当てはまる一般則ではありません。資料中の「観測」「推測」「公式仕様」を区別し、過剰な結論を出さないようにしています。
