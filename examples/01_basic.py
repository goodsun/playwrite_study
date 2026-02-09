"""01_basic.py — Playwright 基本操作

ブラウザ起動 → ページ遷移 → スクリーンショット保存の基本フローを学ぶ。
"""

from pathlib import Path

from playwright.sync_api import sync_playwright


SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "screenshots"


def main() -> None:
    SCREENSHOTS_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        # ブラウザを起動（headless=False で実際のブラウザ画面を表示）
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # ページ遷移
        page.goto("https://example.com")
        print(f"タイトル: {page.title()}")

        # スクリーンショットを保存
        screenshot_path = SCREENSHOTS_DIR / "01_example.png"
        page.screenshot(path=str(screenshot_path))
        print(f"スクリーンショット保存: {screenshot_path}")

        # ページ内のテキストを取得
        heading = page.text_content("h1")
        print(f"見出し: {heading}")

        browser.close()

    print("完了!")


if __name__ == "__main__":
    main()
