# Playwright Python 学習プロジェクト

Playwright を Python で使い、ブラウザ自動操作の基本から応用までを学ぶためのサンプル集。

## 前提条件

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (パッケージマネージャ)

## セットアップ

```bash
# 依存パッケージのインストール
uv sync

# ブラウザバイナリのインストール（初回のみ）
uv run playwright install chromium
```

## サンプルスクリプト

| スクリプト | 内容 |
|---|---|
| `examples/01_basic.py` | ブラウザ起動・ページ遷移・スクリーンショット保存 |
| `examples/02_interaction.py` | フォーム入力・ボタンクリック・テキスト取得 |
| `examples/03_advanced.py` | 複数タブ操作・ネットワーク傍受・PDF出力 |
| `examples/04_login.py` | x.com ログインページへの遷移 |
| `examples/05_chrome_launcher.py` | インタラクティブシェル（セッション管理付き） |

## 実行方法

```bash
# 基本操作
uv run python examples/01_basic.py

# ページ操作（Wikipedia検索）
uv run python examples/02_interaction.py

# 応用テクニック
uv run python examples/03_advanced.py

# x.com ログインページ
uv run python examples/04_login.py
```

各スクリプトは `headless=False` でブラウザを表示するため、操作の様子を目視で確認できる（03 の PDF 出力のみ headless モード）。

スクリーンショットや PDF は `screenshots/` ディレクトリに出力される。

## インタラクティブシェル（05_chrome_launcher.py）

ブラウザをコマンドラインから対話的に操作できるシェル。セッション（Cookie・localStorage）を保存・復元できるため、ログイン状態を維持したまま再利用できる。

### 起動

```bash
# 対話モード（プロファイル選択 → コマンド入力）
uv run python examples/05_chrome_launcher.py

# プロファイルとURLを指定して起動
uv run python examples/05_chrome_launcher.py -p myprofile -u https://example.com
```

### コマンド一覧

| コマンド | 説明 |
|---|---|
| `url:<URL>` | 指定URLに遷移 |
| `click:<selector>` | 要素をクリック |
| `select:<selector>` | 要素を選択して内容を表示 |
| `input:<text>` | 選択中の要素にテキスト入力 |
| `screenshot` | スクリーンショット保存 |
| `title` | ページタイトルとURL表示 |
| `save` | セッションをプロファイルに保存 |
| `quit` | 終了（自動保存される） |

### セレクタの指定方法

`click:`, `select:` の `<selector>` には CSS セレクタまたは XPath を使用できる。

```
# CSSセレクタ
command: click:#login-button
command: select:div.main-content h1
command: click:[data-testid="submit"]

# XPath（xpath= プレフィックスを付ける）
command: click:xpath=//button[@type="submit"]
command: select:xpath=//div[@class="content"]/p[1]
```

### セッション管理のワークフロー

```
# 1. 新規プロファイル作成
uv run python examples/05_chrome_launcher.py
→ 「0: 新規作成」を選択 → プロファイル名を入力（例: teddy）

# 2. サイトにアクセスして手動ログイン
command: url:https://x.com
→ ブラウザ上で手動ログイン

# 3. セッション保存
command: save

# 4. 次回以降はログイン済みで起動
uv run python examples/05_chrome_launcher.py -p teddy -u https://x.com/home
```

## ディレクトリ構成

```
playwrite/
├── pyproject.toml
├── examples/
│   ├── 01_basic.py
│   ├── 02_interaction.py
│   ├── 03_advanced.py
│   ├── 04_login.py
│   └── 05_chrome_launcher.py
├── screenshots/          # スクリーンショット出力先（.gitignore対象）
└── profiles/             # セッションプロファイル（.gitignore対象）
```
