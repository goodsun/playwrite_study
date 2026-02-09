"""05_chrome_launcher.py — プロファイルとURLを選択して Chrome を開く

使い方:
  uv run python examples/05_chrome_launcher.py                  # 対話で選択
  uv run python examples/05_chrome_launcher.py -p 6 -u https://example.com
"""

import argparse
import json
import subprocess
from pathlib import Path


CHROME_DIR = Path.home() / "Library/Application Support/Google/Chrome"
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def get_chrome_profiles() -> list[dict[str, str]]:
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


def select_profile(profiles: list[dict[str, str]]) -> dict[str, str]:
    print("\n=== Chrome プロファイル選択 ===")
    for i, p in enumerate(profiles, 1):
        print(f"  {i}: {p['display_name']}  ({p['dir_name']})")
    print()

    while True:
        choice = input(f"番号を入力 [1-{len(profiles)}]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(profiles):
            selected = profiles[int(choice) - 1]
            print(f"→ {selected['display_name']} を使用\n")
            return selected
        print("無効な入力です。")


def main() -> None:
    profiles = get_chrome_profiles()

    parser = argparse.ArgumentParser(description="Chrome プロファイルランチャー")
    parser.add_argument("-p", type=int, help="プロファイル番号")
    parser.add_argument("-u", type=str, help="開くURL")
    args = parser.parse_args()

    # プロファイル選択
    if args.p and 1 <= args.p <= len(profiles):
        selected = profiles[args.p - 1]
        print(f"→ {selected['display_name']} を使用")
    else:
        selected = select_profile(profiles)

    # URL
    url = args.u or input("開くURL: ").strip()

    cmd = [CHROME_PATH, f"--profile-directory={selected['dir_name']}", url]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Chrome を起動しました: {url}")


if __name__ == "__main__":
    main()
