"""02_interaction.py — ページ操作

フォーム入力、ボタンクリック、要素の待機、テキスト取得を学ぶ。
対象: Wikipedia検索（公開サイト）
"""

from pathlib import Path

from playwright.sync_api import sync_playwright


SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "screenshots"


def main() -> None:
    SCREENSHOTS_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Wikipedia にアクセス
        page.goto("https://en.wikipedia.org/wiki/Main_Page")
        print(f"タイトル: {page.title()}")

        # 検索ボックスにテキストを入力
        search_input = page.locator("#searchInput")
        search_input.fill("Playwright (software)")
        print("検索ワード入力完了")

        # 検索ボタンをクリック
        page.locator("#searchform button.cdx-search-input__end-button").click()

        # ページ遷移を待機
        page.wait_for_load_state("networkidle")
        print(f"遷移先タイトル: {page.title()}")

        # 記事の最初の段落を取得
        first_paragraph = page.locator("#mw-content-text .mw-parser-output > p").first
        first_paragraph.wait_for(state="visible")
        text = first_paragraph.text_content()
        if text:
            # 長すぎる場合は先頭200文字だけ表示
            print(f"記事冒頭: {text[:200]}...")

        # スクリーンショット保存
        screenshot_path = SCREENSHOTS_DIR / "02_wikipedia.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"スクリーンショット保存: {screenshot_path}")

        # リンクの数を数える
        links_count = page.locator("#mw-content-text a").count()
        print(f"記事内リンク数: {links_count}")

        browser.close()

    print("完了!")


if __name__ == "__main__":
    main()
