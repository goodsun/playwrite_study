"""04_login.py — ログインページへの遷移

x.com にアクセスし、ログインボタンをクリックしてログインフォームを表示する。
起動時にChromeプロファイルを選択できる。
"""

import json
from pathlib import Path

from playwright.sync_api import sync_playwright


SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "screenshots"
CHROME_DIR = Path.home() / "Library/Application Support/Google/Chrome"


def get_chrome_profiles() -> list[dict[str, str]]:
    """Chrome プロファイル一覧を取得する。"""
    profiles = []
    for profile_dir in sorted(CHROME_DIR.iterdir()):
        prefs = profile_dir / "Preferences"
        if not prefs.exists():
            continue
        try:
            data = json.loads(prefs.read_text())
            name = data.get("profile", {}).get("name", profile_dir.name)
            profiles.append({"dir_name": profile_dir.name, "display_name": name})
        except (json.JSONDecodeError, KeyError):
            pass
    return profiles


def select_profile() -> str | None:
    """ターミナルでプロファイルを選択させる。None ならプロファイルなしで起動。"""
    profiles = get_chrome_profiles()

    print("\n=== Chrome プロファイル選択 ===")
    print("  0: プロファイルなし（新規セッション）")
    for i, p in enumerate(profiles, 1):
        print(f"  {i}: {p['display_name']}  ({p['dir_name']})")
    print()

    while True:
        choice = input(f"番号を入力 [0-{len(profiles)}]: ").strip()
        if choice == "0":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(profiles):
            selected = profiles[int(choice) - 1]
            print(f"→ {selected['display_name']} を使用\n")
            return str(CHROME_DIR / selected["dir_name"])
        print("無効な入力です。もう一度入力してください。")


def main() -> None:
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    profile_path = select_profile()

    with sync_playwright() as p:
        if profile_path:
            # プロファイル指定で起動（Cookie やログイン状態が保持される）
            context = p.chromium.launch_persistent_context(
                user_data_dir=profile_path,
                headless=False,
                channel="chrome",
            )
            page = context.pages[0] if context.pages else context.new_page()
        else:
            # 新規セッションで起動
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

        # x.com にアクセス
        page.goto("https://x.com/", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        print(f"タイトル: {page.title()}")

        # ログイン済みでなければログインボタンをクリック
        login_button = page.locator('[data-testid="loginButton"]')
        if login_button.is_visible():
            login_button.click()
            print("ログインボタンをクリック")

            page.wait_for_url("**/login**")
            print(f"遷移先URL: {page.url}")
        else:
            print("既にログイン済みのようです")

        # スクリーンショットを保存
        page.wait_for_timeout(2000)
        screenshot_path = SCREENSHOTS_DIR / "04_login.png"
        page.screenshot(path=str(screenshot_path))
        print(f"スクリーンショット保存: {screenshot_path}")

        context.close()

    print("完了!")


if __name__ == "__main__":
    main()
