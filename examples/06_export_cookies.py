"""06_export_cookies.py — Chrome の Cookie を Playwright プロファイルにエクスポート

通常の Chrome でログイン済みのサイトの Cookie を抽出し、
Playwright の storage_state 形式（profiles/*.json）に保存する。

使い方:
  uv run python examples/06_export_cookies.py
  uv run python examples/06_export_cookies.py -p teddy -d x.com
"""

import argparse
import json
import shutil
import sqlite3
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2


CHROME_DIR = Path.home() / "Library/Application Support/Google/Chrome"
PROFILES_DIR = Path(__file__).resolve().parent.parent / "profiles"

# macOS Chrome の暗号化パラメータ
SALT = b"saltysalt"
IV = b" " * 16
KEY_LENGTH = 16
ITERATIONS = 1003


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


def get_encryption_key() -> bytes:
    """macOS Keychain から Chrome の暗号化キーを取得する。"""
    result = subprocess.run(
        [
            "security", "find-generic-password",
            "-s", "Chrome Safe Storage",
            "-w",
        ],
        capture_output=True,
        text=True,
    )
    password = result.stdout.strip()
    return PBKDF2(password.encode(), SALT, dkLen=KEY_LENGTH, count=ITERATIONS)


def decrypt_cookie_value(encrypted: bytes, key: bytes) -> str:
    """Chrome の暗号化 Cookie 値を復号する。"""
    if encrypted[:3] == b"v10":
        encrypted = encrypted[3:]
        cipher = AES.new(key, AES.MODE_CBC, IV)
        decrypted = cipher.decrypt(encrypted)
        # PKCS7 パディング除去
        padding = decrypted[-1]
        if isinstance(padding, int) and 1 <= padding <= 16:
            decrypted = decrypted[:-padding]
        # macOS Chrome は復号後の先頭 32 バイトにゴミデータが入るためスキップ
        decrypted = decrypted[32:]
        return decrypted.decode("utf-8", errors="replace")
    return encrypted.decode("utf-8", errors="replace")


def chrome_timestamp_to_unix(chrome_ts: int) -> float:
    """Chrome のタイムスタンプ（1601年基準マイクロ秒）を Unix タイムスタンプに変換。"""
    if chrome_ts == 0:
        return -1
    epoch_diff = 11644473600
    return (chrome_ts / 1_000_000) - epoch_diff


def export_cookies(
    profile_dir_name: str,
    domain_filter: str | None = None,
) -> list[dict]:
    """Chrome の Cookie DB から Cookie を読み取る。"""
    cookies_db = CHROME_DIR / profile_dir_name / "Cookies"
    if not cookies_db.exists():
        print(f"エラー: Cookie DB が見つかりません: {cookies_db}")
        return []

    # DB をコピーして読む（Chrome がロックしている可能性があるため）
    tmp = tempfile.mktemp(suffix=".db")
    shutil.copy2(cookies_db, tmp)

    key = get_encryption_key()

    try:
        conn = sqlite3.connect(tmp)
        cursor = conn.cursor()

        query = "SELECT host_key, name, path, encrypted_value, is_secure, is_httponly, samesite, expires_utc FROM cookies"
        params = []
        if domain_filter:
            query += " WHERE host_key LIKE ?"
            params.append(f"%{domain_filter}%")

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        cookies = []
        for host, name, path, encrypted_value, secure, httponly, samesite, expires in rows:
            value = decrypt_cookie_value(encrypted_value, key)

            sameSite_map = {-1: "None", 0: "None", 1: "Lax", 2: "Strict"}

            cookies.append({
                "name": name,
                "value": value,
                "domain": host,
                "path": path,
                "expires": chrome_timestamp_to_unix(expires),
                "httpOnly": bool(httponly),
                "secure": bool(secure),
                "sameSite": sameSite_map.get(samesite, "None"),
            })

        return cookies
    finally:
        Path(tmp).unlink(missing_ok=True)


def main() -> None:
    PROFILES_DIR.mkdir(exist_ok=True)
    profiles = get_chrome_profiles()

    parser = argparse.ArgumentParser(description="Chrome Cookie エクスポーター")
    parser.add_argument("-p", type=str, help="保存先プロファイル名")
    parser.add_argument("-d", type=str, help="ドメインフィルタ（例: x.com）")
    args = parser.parse_args()

    # Chrome プロファイル選択
    selected = select_profile(profiles)

    # ドメインフィルタ
    domain = args.d
    if not domain:
        domain = input("ドメインフィルタ（空欄で全て）: ").strip() or None

    # Cookie エクスポート
    print("Cookie を読み取り中...")
    cookies = export_cookies(selected["dir_name"], domain)
    print(f"  {len(cookies)} 件の Cookie を取得")

    if not cookies:
        print("Cookie が見つかりませんでした")
        return

    # プロファイル名
    profile_name = args.p
    if not profile_name:
        profile_name = input("保存先プロファイル名: ").strip()
        if not profile_name:
            print("プロファイル名を入力してください")
            return

    # Playwright storage_state 形式で保存
    profile_path = PROFILES_DIR / f"{profile_name}.json"

    # 既存プロファイルがあればマージ
    if profile_path.exists():
        existing = json.loads(profile_path.read_text())
        existing_cookies = existing.get("cookies", [])
        # 同じ name+domain の Cookie は上書き
        existing_map = {(c["name"], c["domain"]): c for c in existing_cookies}
        for cookie in cookies:
            existing_map[(cookie["name"], cookie["domain"])] = cookie
        cookies = list(existing_map.values())
        origins = existing.get("origins", [])
    else:
        origins = []

    storage_state = {
        "cookies": cookies,
        "origins": origins,
    }

    profile_path.write_text(json.dumps(storage_state, indent=2, ensure_ascii=False))
    print(f"\n保存完了: {profile_path}")
    print(f"  Cookie数: {len(cookies)}")
    print(f"\n05_chrome_launcher.py で使用:")
    print(f"  uv run python examples/05_chrome_launcher.py -p {profile_name}")


if __name__ == "__main__":
    main()
