"""
一键“打开 Windows 系统代理”（对应 Clash Verge 里红色开关：系统代理）

逻辑：
  - 如果当前 ProxyEnable=0（关闭），则设置为 1（打开）
  - 如果本来就是打开的，则不做任何更改

注意：
  - 仅打开 ProxyEnable 通常会沿用系统里已保存的 ProxyServer/ProxyOverride 配置。
  - 如果你希望脚本同时写入代理地址（比如 127.0.0.1:7890），可以用 --server 参数。

用法：
  python enable_system_proxy.py
  python enable_system_proxy.py --server "127.0.0.1:7890"
  python enable_system_proxy.py --server "127.0.0.1:7890" --bypass "<local>"
  python enable_system_proxy.py --clear-pac
"""

from __future__ import annotations

import argparse
import ctypes
import sys
import winreg


REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"


def refresh_internet_settings() -> None:
    """通知系统刷新代理设置。"""
    wininet = ctypes.WinDLL("wininet", use_last_error=True)
    internet_set_option = wininet.InternetSetOptionW
    internet_set_option.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint]
    internet_set_option.restype = ctypes.c_bool

    # 39 = INTERNET_OPTION_SETTINGS_CHANGED, 37 = INTERNET_OPTION_REFRESH
    for opt in (39, 37):
        ok = internet_set_option(None, opt, None, 0)
        if not ok:
            err = ctypes.get_last_error()
            print(f"提示：刷新系统代理设置失败（InternetSetOption opt={opt}, err={err}）。")


def reg_get(name: str, default=None):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ) as k:
        try:
            v, _ = winreg.QueryValueEx(k, name)
            return v
        except FileNotFoundError:
            return default


def reg_set_dword(name: str, value: int) -> None:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, name, 0, winreg.REG_DWORD, int(value))


def reg_set_str(name: str, value: str) -> None:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, name, 0, winreg.REG_SZ, value)


def reg_delete(name: str) -> None:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE) as k:
        try:
            winreg.DeleteValue(k, name)
        except FileNotFoundError:
            pass


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--server",
        help='可选：写入系统代理地址（会写入 ProxyServer），例如 "127.0.0.1:7890" 或 "http=127.0.0.1:7890;https=127.0.0.1:7890"',
    )
    ap.add_argument(
        "--bypass",
        help='可选：写入绕过列表（ProxyOverride），例如 "<local>" 或 "<local>;*.example.com"',
    )
    ap.add_argument(
        "--clear-pac",
        action="store_true",
        help="可选：清空 PAC（AutoConfigURL），避免 PAC 覆盖系统代理（谨慎使用）",
    )
    args = ap.parse_args(argv)

    enabled = int(reg_get("ProxyEnable", 0) or 0)
    if enabled == 1:
        print("系统代理本来就是打开的，已忽略。")
        return 0

    # 关闭状态 -> 打开
    if args.server:
        reg_set_str("ProxyServer", args.server)
    if args.bypass:
        reg_set_str("ProxyOverride", args.bypass)
    if args.clear_pac:
        reg_delete("AutoConfigURL")

    reg_set_dword("ProxyEnable", 1)
    refresh_internet_settings()
    print("已打开 Windows 系统代理（对应 Clash Verge：系统代理 开关）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

