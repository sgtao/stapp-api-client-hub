# stapp-api-client-hub

様々な API サービスへ接続・テストするための [Streamlit](https://streamlit.io/) アプリ。
YAML 設定ファイルでリクエストをプリセット化し、LLM チャット・アクション連鎖実行・ログ管理まで一元操作できる。

## 機能一覧（ページ構成）

| ページ | 概要 |
|---|---|
| `11` Simple API Client | HTTP メソッド・URI・ヘッダーを手動入力して API を叩く基本クライアント |
| `12` Config API Client | YAML プリセットをロードしてワンクリックでリクエスト送信 |
| `13` Chat with Config | YAML 設定 + LLM API を使ったチャット UI |
| `21` API Server Control | ローカル FastAPI サーバーの起動・停止・テストを GUI 操作 |
| `22` Serviced API Client | 起動済み API サーバー経由でリクエストを送信 |
| `23` Action Config Client | YAML で定義したアクションを連鎖実行（`request` → `extract` → `append_message`） |
| `31` Chat with Actions | アクション連鎖 + チャット履歴を統合した上位チャット UI |
| `91` Logs Viewer | API 通信ログの閲覧・ローテート管理 |

## セットアップ

[Poetry](https://python-poetry.org/docs/) で依存パッケージをインストールする。

```sh
poetry install
```

### API キーの設定

サイドバーの入力欄から UI 上で設定するか、環境変数 `API_KEY` で起動前に渡すことができる。  
環境変数が設定されている場合は起動時に自動的に読み込まれる（優先順位: UI入力値 > 環境変数）。

```sh
# Bash / Zsh
export API_KEY="your_api_key_here"

# PowerShell
$env:API_KEY = "your_api_key_here"
```

> **補足**: YAML 設定ファイルに保存する際、API キーは自動的に `＜API_KEY＞` にマスクされる。

### 仮想環境の有効化

```sh
# Bash / Zsh / Csh（Poetry 2.x）
eval $(poetry env activate)

# PowerShell（Poetry 2.x）
Invoke-Expression (poetry env activate)

# Fish（Poetry 2.x）
eval (poetry env activate)

# 終了
deactivate
```

## 起動

```sh
task run
# → streamlit run src/main.py
# → http://localhost:8501
```

## よく使うタスク

```sh
task --list          # 全タスク一覧

task check-format    # black フォーマット + flake8 lint を一括実行
task test            # pytest でテスト実行
task test-cov        # C1 カバレッジを表示
task test-report     # HTML カバレッジレポートを出力
```

## 配布パッケージのビルド（Python 不要で実行できるバイナリ）

```sh
task make-dist       # dist/ 以下にパッケージを生成
task rm-dist         # dist/ を削除

# 生成したバイナリの実行（Linux）
./dist/run_stapp/run_stapp
```

> **注意**: PyInstaller はクロスコンパイル非対応。ターゲット OS 上でビルドすること。

## requirements.txt のエクスポート

```sh
task export-requirements      # 本番依存のみ
task export-req-with-dev      # 開発依存を含む
```

## プロジェクト構成

```
src/
├── main.py          # エントリーポイント（ホーム画面）
├── pages/           # 各ページ（オーケストレーター層）
├── ui/              # Streamlit UI コンポーネント層
├── logic/           # UI 非依存のビジネスロジック層
└── api/             # FastAPI サーバー定義
assets/              # YAML プリセット設定ファイル
tests/               # pytest テストスイート
```

## ライセンス
MIT License
詳細は [LICENSE](./LICENSE) を参照。

ただし、本プロジェクトは Apache License 2.0 の [Streamlit](https://github.com/streamlit/streamlit/blob/develop/LICENSE) を使用してます。
