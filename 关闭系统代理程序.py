"""
一键“关闭 Windows 系统代理”（对应 Clash Verge 里红色开关：系统代理）

逻辑：
  - 如果当前 ProxyEnable=1（开启），则设置为 0（关闭）
  - 如果本来就是关闭的，则不做任何更改

用法：
  python disable_system_proxy.py
  python disable_system_proxy.py --clear-pac

说明：
  --clear-pac 会同时清空 AutoConfigURL（PAC 脚本地址），谨慎使用。
"""

from __future__ import annotations

import argparse
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
            # 刷新失败一般不影响注册表写入，但给出提示
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


def clear_pac() -> None:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE) as k:
        try:
            winreg.DeleteValue(k, "AutoConfigURL")
        except FileNotFoundError:
            pass


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clear-pac", action="store_true", help="同时清空 PAC（AutoConfigURL），谨慎使用")
    args = ap.parse_args(argv)

    enabled = get_proxy_enable()
    if enabled == 1:
        set_proxy_enable(0)
        if args.clear_pac:
            clear_pac()
        refresh_internet_settings()
        print("已关闭 Windows 系统代理（对应 Clash Verge：系统代理 开关）。")
    else:
        print("系统代理本来就是关闭的，无需处理。")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

