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

## 実行方法

```bash
# 基本操作
uv run python examples/01_basic.py

# ページ操作（Wikipedia検索）
uv run python examples/02_interaction.py

# 応用テクニック
uv run python examples/03_advanced.py
```

各スクリプトは `headless=False` でブラウザを表示するため、操作の様子を目視で確認できる（03 の PDF 出力のみ headless モード）。

スクリーンショットや PDF は `screenshots/` ディレクトリに出力される。

## ディレクトリ構成

```
playwrite/
├── pyproject.toml
├── examples/
│   ├── 01_basic.py
│   ├── 02_interaction.py
│   └── 03_advanced.py
└── screenshots/          # 出力先（.gitignore対象）
```
