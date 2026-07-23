"""Import QuillBot session cookies from local Google Chrome (Windows)."""
from __future__ import annotations

import os
from typing import Any


def _chrome_cookie_domains() -> list[str]:
    return [".quillbot.com", "quillbot.com", "www.quillbot.com"]


def default_chrome_executable() -> str:
    candidates = [
        os.path.join(os.environ.get("PROGRAMFILES", r"C:\Program Files"), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(
            os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
            "Google",
            "Chrome",
            "Application",
            "chrome.exe",
        ),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return candidates[0]


def load_chrome_cookies_for_playwright() -> list[dict[str, Any]]:
    """Read quillbot.com cookies from Chrome via browser_cookie3 (Chrome closed; may need admin on Windows)."""
    try:
        import browser_cookie3
    except ImportError as exc:
        raise RuntimeError(
            "browser_cookie3 required: pip install browser_cookie3"
        ) from exc

    seen: set[tuple[str, str, str]] = set()
    out: list[dict[str, Any]] = []

    def _add_from_jar(jar) -> None:
        for c in jar:
            domain_l = (c.domain or "").lower()
            if "quillbot" not in domain_l:
                continue
            key = (c.name, c.domain, c.path)
            if key in seen:
                continue
            seen.add(key)
            same_site = "Lax"
            rest = getattr(c, "_rest", None) or {}
            if rest.get("SameSite"):
                same_site = str(rest.get("SameSite"))
            item: dict[str, Any] = {
                "name": c.name,
                "value": c.value,
                "domain": c.domain,
                "path": c.path or "/",
                "secure": bool(c.secure),
                "httpOnly": bool(rest.get("HttpOnly", False)),
                "sameSite": same_site,
            }
            if c.expires:
                item["expires"] = int(c.expires)
            out.append(item)

    try:
        _add_from_jar(browser_cookie3.chrome())
    except Exception as exc:
        msg = str(exc).lower()
        if "admin" in msg:
            raise RuntimeError(
                "Chrome cookie decrypt needs elevated PowerShell on this PC. "
                "Use sync-cdp instead, or re-run import-chrome as Administrator."
            ) from exc
        for domain in _chrome_cookie_domains():
            try:
                _add_from_jar(browser_cookie3.chrome(domain_name=domain))
            except Exception:
                continue
    return out


def default_chrome_user_data() -> str:
    local = os.environ.get("LOCALAPPDATA", "")
    return os.path.join(local, "Google", "Chrome", "User Data")


def chrome_looks_running() -> bool:
    try:
        import psutil
    except ImportError:
        return False
    for proc in psutil.process_iter(["name"]):
        name = (proc.info.get("name") or "").lower()
        if name in ("chrome.exe", "chromium.exe"):
            return True
    return False


def is_debug_port_open(port: int = 9222) -> bool:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def start_chrome_with_cdp(port: int = 9222, *, kill_existing: bool = True) -> None:
    """Restart Chrome with remote debugging on *port* and default user profile."""
    import subprocess
    import time

    chrome = default_chrome_executable()
    if not os.path.isfile(chrome):
        raise FileNotFoundError(f"Chrome not found: {chrome}")

    if kill_existing:
        for attempt in range(12):
            subprocess.run(
                ["taskkill", "/F", "/IM", "chrome.exe", "/T"],
                capture_output=True,
                check=False,
            )
            time.sleep(1)
            if not chrome_looks_running():
                break
        else:
            raise RuntimeError(
                "Chrome is still running after taskkill. "
                "Close all Chrome windows (including system tray), then retry start-chrome-debug."
            )
        time.sleep(2)

    user_data = default_chrome_user_data()
    arg_list = ",".join(
        f'"{a}"'
        for a in (
            f"--remote-debugging-port={port}",
            f"--user-data-dir={user_data}",
            "--no-first-run",
            "--no-default-browser-check",
            "https://quillbot.com/ai-content-detector",
        )
    )
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            f'Start-Process -FilePath "{chrome}" -ArgumentList {arg_list}',
        ],
        check=False,
        capture_output=True,
    )

    for _ in range(90):
        if is_debug_port_open(port):
            return
        time.sleep(1)
    raise TimeoutError(
        f"Chrome did not open debug port {port} within 90s. "
        "Ensure no other Chrome instance is using your profile."
    )
