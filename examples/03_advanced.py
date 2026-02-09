"""03_advanced.py — 応用テクニック

複数タブ操作、ネットワークリクエスト傍受、PDF エクスポートを学ぶ。
"""

from pathlib import Path

from playwright.sync_api import sync_playwright


SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "screenshots"


def demo_multiple_tabs() -> None:
    """複数タブの操作デモ。"""
    print("=== 複数タブ操作 ===")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        # タブ1: example.com
        page1 = context.new_page()
        page1.goto("https://example.com")
        print(f"タブ1: {page1.title()}")

        # タブ2: example.org
        page2 = context.new_page()
        page2.goto("https://www.example.org")
        print(f"タブ2: {page2.title()}")

        # 全タブの情報を表示
        for i, page in enumerate(context.pages):
            print(f"  ページ{i}: {page.url}")

        # タブ1に戻って操作
        page1.bring_to_front()
        heading = page1.text_content("h1")
        print(f"タブ1に戻った — 見出し: {heading}")

        browser.close()

    print()


def demo_network_intercept() -> None:
    """ネットワークリクエスト傍受デモ。"""
    print("=== ネットワークリクエスト傍受 ===")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # リクエスト/レスポンスのイベントリスナーを設定
        captured_requests: list[dict[str, str]] = []

        def on_request(request) -> None:
            captured_requests.append({
                "method": request.method,
                "url": request.url,
                "resource_type": request.resource_type,
            })

        page.on("request", on_request)

        # ページにアクセス
        page.goto("https://example.com")

        # キャプチャしたリクエストを表示
        print(f"キャプチャしたリクエスト数: {len(captured_requests)}")
        for req in captured_requests[:10]:
            print(f"  {req['method']} {req['resource_type']}: {req['url'][:80]}")

        browser.close()

    print()


def demo_pdf_export() -> None:
    """PDF エクスポートデモ。

    注意: PDF生成は headless モードでのみ動作する。
    """
    print("=== PDF エクスポート ===")

    SCREENSHOTS_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        # PDF生成は Chromium の headless モードでのみサポート
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://example.com")

        pdf_path = SCREENSHOTS_DIR / "03_example.pdf"
        page.pdf(path=str(pdf_path), format="A4")
        print(f"PDF保存: {pdf_path}")

        browser.close()

    print()


def main() -> None:
    demo_multiple_tabs()
    demo_network_intercept()
    demo_pdf_export()
    print("すべてのデモ完了!")


if __name__ == "__main__":
    main()
