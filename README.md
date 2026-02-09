# Playwright Python 学習プロジェクト

Playwright を Python で使い、ブラウザ自動操作の基本から応用までを学ぶためのサンプル集。

## 前提条件

- Python 3.13+

## セットアップ

### uv を使う場合（推奨）

```bash
# 依存パッケージのインストール
uv sync

# ブラウザバイナリのインストール（初回のみ）
uv run playwright install chromium
```

### pip を使う場合

```bash
pip install playwright pycryptodome
playwright install chromium
```

## linux環境などで利用する際の日本語フォント問題がある場合
sudo dnf install -y google-noto-sans-cjk-jp-fonts

## サンプルスクリプト

| スクリプト | 内容 |
|---|---|
| `examples/01_basic.py` | ブラウザ起動・ページ遷移・スクリーンショット保存 |
| `examples/02_interaction.py` | フォーム入力・ボタンクリック・テキスト取得 |
| `examples/03_advanced.py` | 複数タブ操作・ネットワーク傍受・PDF出力 |
| `examples/04_login.py` | x.com ログインページへの遷移 |
| `examples/05_chrome_launcher.py` | インタラクティブシェル（セッション管理付き） |
| `examples/06_export_cookies.py` | Chrome の Cookie を Playwright プロファイルにエクスポート |

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

# コマンドファイルから実行
uv run python examples/05_chrome_launcher.py -p myprofile -f commands.txt

# ヘッドレスモードで自動実行
uv run python examples/05_chrome_launcher.py -p myprofile -f commands.txt --headless
```

pip の場合は `uv run python` を `python` に置き換える。

### コマンド一覧

| コマンド | 説明 |
|---|---|
| `url:<URL>` | 指定URLに遷移 |
| `click:<selector>` | 要素をクリック |
| `select:<selector>` | 要素を選択して内容を表示 |
| `input:<text>` | 選択中の要素にテキスト入力（`\n` で改行、空で複数行モード） |
| `wait:<ms>` | 指定ミリ秒待機 |
| `ss` | スクリーンショット保存（`logs/` に出力） |
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

### コマンドファイル

コマンドを1行1つ記述したテキストファイル。`-f` で指定して自動実行できる。
`#` で始まる行はコメント。複数行入力はヒアドキュメント形式で記述する。

```
# sample/commands.txt
url:https://x.com
click://投稿ボタン
wait:2000
select://テキストエリア
input:<<END
1行目
2行目
END
click://送信ボタン
quit
```

終了時にはコマンドログとスクリーンショットが `logs/` に自動保存される。
ログファイルはそのまま `-f` で再実行できる。

## Cookie エクスポート（06_export_cookies.py）

通常の Chrome でログイン済みの Cookie を Playwright プロファイルにエクスポートする。

```bash
uv run python examples/06_export_cookies.py -p myprofile -d x.com
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
│   ├── 05_chrome_launcher.py
│   └── 06_export_cookies.py
├── sample/               # コマンドファイルのサンプル
├── profiles/             # セッションプロファイル（.gitignore対象）
├── logs/                 # コマンドログ・スクリーンショット（.gitignore対象）
└── screenshots/          # スクリーンショット出力先（.gitignore対象）
```


