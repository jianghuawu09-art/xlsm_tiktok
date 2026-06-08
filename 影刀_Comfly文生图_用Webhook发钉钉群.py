"""
影刀（xbot）模块：读取提示词 → 调用 Comfly 文生图/出图链接 → 用钉钉自定义机器人 Webhook 发到群里

为什么用 Webhook：
  - 稳定、和 VSCode/影刀环境差异更小
  - 不依赖 gettoken/chat/send 的企业内部应用权限链路

使用前你只需要改 3 处：
  1) COMFLY_API_KEY
  2) ROBOT_WEBHOOK
  3) PROMPT_FILE_PATH（你的提示词txt路径）
"""

# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

from __future__ import annotations

import json
import re
import time

import urllib3

urllib3.disable_warnings()  # 影刀环境常见证书告警，统一关闭

# import xbot
# from xbot import print, sleep
# from . import package
# from .package import variables as glv

import requests


# ======================【你只改这里comfly密钥】======================
COMFLY_API_KEY = "comfly密钥"

# Comfly OpenAI 兼容 Chat 接口（注意：不要写反引号）
COMFLY_CHAT_URL = "https://ai.comfly.chat/v1/chat/completions"

# 你使用的模型（按需增减）
MODELS = [
    "nano-banana",
]

# 提示词文件路径（影刀可读）
PROMPT_FILE_PATH = r"\\Star-1\素材库\AI工程师存放的文件路径\AI文生图\文字描述.txt"

# 钉钉自定义机器人 Webhook（注意：不要写反引号；写了也会自动去掉）
ROBOT_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# ======================================================


def _strip_backticks(s: str) -> str:
    """兼容你之前写成 `https://...` 的情况。"""
    return (s or "").strip().strip("`").strip()


def _http_session() -> requests.Session:
    """
    影刀里经常有环境代理/证书拦截：
      - trust_env=False：不使用系统代理环境变量，避免被意外代理影响
      - verify=False：关闭证书校验（你之前在影刀里也这么做）
    """
    s = requests.Session()
    s.trust_env = False
    return s


# ======================【钉钉 Webhook 发送（稳定版）】======================
def send_text_by_webhook(webhook: str, content: str, max_len: int = 1800) -> None:
    """
    用钉钉自定义机器人 webhook 发送文本（自动分段 + 重试）。
    钉钉机器人单条文本长度有限，内容太长会失败，所以需要分段发送。
    """
    webhook = _strip_backticks(webhook)
    if not webhook:
        raise RuntimeError("ROBOT_WEBHOOK 为空")

    headers = {"Content-Type": "application/json"}

    parts = [content[i : i + max_len] for i in range(0, len(content), max_len)] or [""]
    for idx, part in enumerate(parts, start=1):
        msg_text = part if len(parts) == 1 else f"[{idx}/{len(parts)}]\n{part}"
        payload = {
            "msgtype": "text",
            "text": {"content": msg_text},
            "at": {"isAtAll": False},
        }

        last_err = None
        for _ in range(3):  # 重试3次
            try:
                r = requests.post(
                    webhook,
                    data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                    headers=headers,
                    timeout=30,
                    verify=False,
                )
                # 一定要打印，影刀里才好排查
                print("DingTalk status:", r.status_code)
                print("DingTalk resp:", r.text)

                if r.status_code == 200 and r.json().get("errcode") == 0:
                    break
                last_err = RuntimeError(f"钉钉发送失败：{r.text}")
            except Exception as e:
                last_err = e
                time.sleep(1.5)
        else:
            raise last_err


# ======================【Comfly 调用：拿到“下载链接”】======================
def _extract_download_url(text: str) -> str | None:
    """
    兼容几种常见返回：
      1) Markdown: [下载1](https://xxx)
      2) 直接给出 https://xxx
    """
    if not text:
        return None

    m = re.search(r"\[下载\d*\]\((https?://[^)]+)\)", text)
    if m:
        return m.group(1).strip()

    m = re.search(r"(https?://\S+)", text)
    if m:
        return m.group(1).strip().rstrip(").,]}")

    return None


def generate_image_link(model_name: str, prompt: str) -> str:
    """
    返回一段将被发送到钉钉群里的文本（包含下载链接或错误信息）。
    """
    url = _strip_backticks(COMFLY_CHAT_URL)
    api_key = (COMFLY_API_KEY or "").strip()
    if not api_key:
        return f"{model_name}：COMFLY_API_KEY 为空"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_name,
        "stream": False,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    try:
        s = _http_session()
        r = s.post(url, headers=headers, json=payload, timeout=90, verify=False)
        # 打印出来，影刀里遇到 403/额度/风控 才能立刻看到
        print("Comfly status:", r.status_code)
        print("Comfly resp:", r.text)

        if r.status_code != 200:
            return f"{model_name}：调用失败（HTTP {r.status_code}）\n{r.text}"

        data = r.json()
        content = (
            (data.get("choices") or [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        link = _extract_download_url(content)
        if link:
            return f"====== {model_name} 下载链接 ======\n{link}"
        return f"{model_name}：未解析到下载链接。\n原始返回：\n{content}"
    except Exception as e:
        return f"{model_name}：请求异常：{e}"


# ======================【主程序】======================
def main(args):
    try:
        # 1) 读取提示词
        with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as f:
            prompt = f.read().strip()
        if not prompt:
            raise RuntimeError("提示词为空，请检查文字描述.txt")

        # 2) 组装要发送的内容
        send_content = "==========本次绘图提示词==========\n"
        send_content += prompt
        send_content += "\n================================\n\n"

        print("==========本次绘图提示词==========")
        print(prompt)
        print("================================\n")

        # 3) 调用 Comfly（逐模型）
        for model in MODELS:
            res = generate_image_link(model, prompt)
            print(res)
            send_content += res + "\n\n"

        # 4) 用 webhook 发送到群
        send_text_by_webhook(ROBOT_WEBHOOK, send_content)
        print("\n✅ 结果已通过 Webhook 发送到钉钉群！")

    except Exception as e:
        print(f"\n❌ 运行失败：{e}")
        raise


# 允许直接 python 运行（影刀“独立运行模块”也会走 main）
if __name__ == "__main__":
    class Args:
        pass

    main(Args())

