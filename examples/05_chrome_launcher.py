"""05_chrome_launcher.py — Playwright インタラクティブシェル

プロファイル（セッション）を管理し、ログイン状態を保持してブラウザを操作する。

コマンド:
  url:<URL>          指定URLに遷移
  click:<selector>   要素をクリック
  select:<selector>  要素を選択（内容を表示）
  input:<text>       選択中の要素にテキスト入力
  screenshot         スクリーンショット保存
  title              ページタイトル表示
  save               現在のセッションをプロファイルに保存
  quit               終了

使い方:
  uv run python examples/05_chrome_launcher.py                    # 対話で選択
  uv run python examples/05_chrome_launcher.py -p myprofile       # プロファイル指定
  uv run python examples/05_chrome_launcher.py -p myprofile -u https://example.com
"""

import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "screenshots"
PROFILES_DIR = Path(__file__).resolve().parent.parent / "profiles"


def list_profiles() -> list[str]:
    """保存済みプロファイル一覧を返す。"""
    if not PROFILES_DIR.exists():
        return []
    return sorted(p.stem for p in PROFILES_DIR.glob("*.json"))


def select_profile() -> str:
    """プロファイルを選択または新規作成する。"""
    profiles = list_profiles()

    print("\n=== プロファイル選択 ===")
    print("  0: 新規作成")
    for i, name in enumerate(profiles, 1):
        print(f"  {i}: {name}")
    print()

    while True:
        choice = input(f"番号を入力 [0-{len(profiles)}]: ").strip()
        if choice == "0":
            name = input("新規プロファイル名: ").strip()
            if name:
                print(f"→ {name} を新規作成\n")
                return name
            print("名前を入力してください。")
        elif choice.isdigit() and 1 <= int(choice) <= len(profiles):
            name = profiles[int(choice) - 1]
            print(f"→ {name} を使用\n")
            return name
        else:
            print("無効な入力です。")


def run_shell(page, context, profile_name: str) -> None:
    """インタラクティブシェル。"""
    selected_element = None

    print("\n=== コマンド入力 (help でヘルプ表示) ===\n")

    while True:
        try:
            cmd = input("command: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not cmd:
            continue

        try:
            if cmd == "quit":
                break

            elif cmd == "help":
                print("  url:<URL>          指定URLに遷移")
                print("  click:<selector>   要素をクリック")
                print("  select:<selector>  要素を選択（内容を表示）")
                print("  input:<text>       選択中の要素にテキスト入力")
                print("  screenshot         スクリーンショット保存")
                print("  title              ページタイトル表示")
                print("  save               セッションを保存")
                print("  quit               終了")

            elif cmd.startswith("url:"):
                url = cmd[4:].strip()
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(1000)
                print(f"  → {page.title()} ({page.url})")

            elif cmd.startswith("select:"):
                selector = cmd[7:].strip()
                loc = page.locator(selector)
                count = loc.count()
                if count == 0:
                    print(f"  要素が見つかりません: {selector}")
                    selected_element = None
                else:
                    selected_element = loc.first
                    text = selected_element.text_content() or ""
                    tag = selected_element.evaluate("el => el.tagName")
                    print(f"  選択: <{tag}> ({count}件中1件目)")
                    if text.strip():
                        print(f"  内容: {text.strip()[:200]}")

            elif cmd.startswith("click:"):
                selector = cmd[6:].strip()
                page.locator(selector).first.click()
                page.wait_for_timeout(1000)
                print(f"  クリック完了 → {page.url}")

            elif cmd.startswith("input:"):
                text = cmd[6:].strip()
                if selected_element is None:
                    print("  先に select: で要素を選択してください")
                else:
                    selected_element.fill(text)
                    print(f"  入力完了: {text}")

            elif cmd == "screenshot":
                SCREENSHOTS_DIR.mkdir(exist_ok=True)
                path = SCREENSHOTS_DIR / "05_screenshot.png"
                page.screenshot(path=str(path))
                print(f"  保存: {path}")

            elif cmd == "title":
                print(f"  {page.title()} ({page.url})")

            elif cmd == "save":
                PROFILES_DIR.mkdir(exist_ok=True)
                path = PROFILES_DIR / f"{profile_name}.json"
                context.storage_state(path=str(path))
                print(f"  プロファイル保存: {path}")

            else:
                print(f"  不明なコマンド: {cmd}")

        except Exception as e:
            print(f"  エラー: {e}")


def main() -> None:
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    PROFILES_DIR.mkdir(exist_ok=True)

    parser = argparse.ArgumentParser(description="Playwright インタラクティブシェル")
    parser.add_argument("-p", type=str, help="プロファイル名")
    parser.add_argument("-u", type=str, help="開くURL")
    args = parser.parse_args()

    # プロファイル選択
    if args.p:
        profile_name = args.p
        profile_path = PROFILES_DIR / f"{profile_name}.json"
        if profile_path.exists():
            print(f"→ {profile_name} を使用")
        else:
            print(f"→ {profile_name} を新規作成")
    else:
        profile_name = select_profile()
        profile_path = PROFILES_DIR / f"{profile_name}.json"

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)

        # プロファイルが存在すればセッションを復元
        if profile_path.exists():
            context = browser.new_context(storage_state=str(profile_path))
            print("  セッションを復元しました")
        else:
            context = browser.new_context()
            print("  新規セッションで開始")

        page = context.new_page()

        # 初期URL
        url = args.u or ""
        if url:
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(1000)
            print(f"  → {page.title()} ({page.url})")

        run_shell(page, context, profile_name)

        # 終了時に自動保存
        PROFILES_DIR.mkdir(exist_ok=True)
        context.storage_state(path=str(profile_path))
        print(f"プロファイル自動保存: {profile_name}")

        context.close()
        browser.close()

    print("終了しました")


if __name__ == "__main__":
    main()
