"""
一键“打开 Windows 系统代理”（对应 Clash Verge 里红色开关：系统代理）

逻辑：
  - 如果当前 ProxyEnable=1（开启），则提示：系统代理本来就是打开的，已忽略。
  - 如果当前 ProxyEnable=0（关闭），则设置为 1（打开）

用法：
  python enable_system_proxy.py
"""

from __future__ import annotations

import ctypes
import sys
import winreg


REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"


def refresh_internet_settings() -> None:
    """
    通知系统刷新代理设置（等价于“设置已更改/刷新”）。
    """

    wininet = ctypes.WinDLL("wininet", use_last_error=True)
    internet_set_option = wininet.InternetSetOptionW
    internet_set_option.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint]
    internet_set_option.restype = ctypes.c_bool

    INTERNET_OPTION_SETTINGS_CHANGED = 39
    INTERNET_OPTION_REFRESH = 37

    for opt in (INTERNET_OPTION_SETTINGS_CHANGED, INTERNET_OPTION_REFRESH):
        ok = internet_set_option(None, opt, None, 0)
        if not ok:
            err = ctypes.get_last_error()
            print(f"提示：刷新系统代理设置失败（InternetSetOption opt={opt}, err={err}）。")


def get_proxy_enable() -> int:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ) as k:
        try:
            v, _ = winreg.QueryValueEx(k, "ProxyEnable")
            return int(v)
        except FileNotFoundError:
            return 0


def set_proxy_enable(value: int) -> None:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, "ProxyEnable", 0, winreg.REG_DWORD, int(value))


def main(argv: list[str]) -> int:
    enabled = get_proxy_enable()
    
    # 已经打开 → 忽略
    if enabled == 1:
        print("系统代理本来就是打开的，已忽略。")
        return 0

    # 关闭状态 → 打开
    set_proxy_enable(1)
    refresh_internet_settings()
    print("已打开 Windows 系统代理（对应 Clash Verge：系统代理 开关）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))