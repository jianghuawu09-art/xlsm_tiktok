from __future__ import annotations
import asyncio
import json
import os
import time
import subprocess
import pyautogui
import pyperclip
import requests
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import Any, Dict, Tuple

import dingtalk_stream
from dingtalk_stream import AckMessage

# ======================== 全局配置（你只改这里） ========================
# 钉钉机器人
DT_CLIENT_ID = "dingyzwmwrqoumv2xyjb"
DT_CLIENT_SECRET = "mh0WB_3cqnOI3znHRr7Yj1BD5MQjwr_rrFHTYZtaJAx-4J2oQavuRk-KwU8kddH3"

# 钉钉表格
WORKBOOK_ID = "vNG4YZ7JnPbOLPNvf9Ap6XXdW2LD0oRE"
SHEET_ID = "Sheet1"
OPERATOR_UNION_ID = "fADzjBkYl9VEvxiPwAKrF2QiEiE"

# 影刀配置
YINGDAO_EXE = r"C:\Program Files\ShadowBot\ShadowBot.exe"
SEARCH_BOX_POS = (1475, 204)
RUN_APP_POS = (1453, 304)
# ======================================================================

# 表格配置
STATE_FILE = "dingtalk_msg_to_doc_table.state.json"
START_ROW = 2
REPLY_ON_SUCCESS = True

# 日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("dingbot")

# ------------------------------------------------------------------------------
# 表格写入工具类
# ------------------------------------------------------------------------------
class DingTalkApiError(RuntimeError):
    pass

def _now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"next_row": START_ROW, "seen_msg_ids": []}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("next_row", START_ROW)
        data.setdefault("seen_msg_ids", [])
        data["seen_msg_ids"] = data["seen_msg_ids"][-2000:]
        return data
    except:
        return {"next_row": START_ROW, "seen_msg_ids": []}

def save_state(state):
    with open(STATE_FILE + ".tmp", "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(STATE_FILE + ".tmp", STATE_FILE)

@dataclass
class TokenCache:
    access_token: str = ""
    expire_at: float = 0

TOKEN_CACHE = TokenCache()

def get_app_access_token(client_id, secret):
    now = time.time()
    if TOKEN_CACHE.access_token and now < TOKEN_CACHE.expire_at - 60:
        return TOKEN_CACHE.access_token
    url = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
    r = requests.post(url, json={"appKey": client_id, "appSecret": secret}, timeout=15)
    data = r.json()
    token = data["accessToken"]
    expire = data["expireIn"]
    TOKEN_CACHE.access_token = token
    TOKEN_CACHE.expire_at = now + expire
    return token

def update_range(token, workbook, sheet, range_addr, operator, values):
    url = f"https://api.dingtalk.com/v1.0/doc/workbooks/{workbook}/sheets/{sheet}/ranges/{range_addr}"
    headers = {"x-acs-dingtalk-access-token": token}
    r = requests.put(url, params={"operatorId": operator}, headers=headers, json={"values": values}, timeout=10)
    return r.json()

def append_to_table(payload):
    state = load_state()
    msg_id = payload.get("msgId", "")
    if msg_id in state["seen_msg_ids"]:
        return -1, msg_id

    text = payload.get("text", {}).get("content", "").strip()
    if not text:
        return -1, msg_id

    row = state["next_row"]
    sender = payload.get("senderNick", "")
    chat = payload.get("conversationId", "")
    values = [[_now_str(), sender, chat, text]]

    token = get_app_access_token(DT_CLIENT_ID, DT_CLIENT_SECRET)
    update_range(token, WORKBOOK_ID, SHEET_ID, f"A{row}:D{row}", OPERATOR_UNION_ID, values)

    state["seen_msg_ids"].append(msg_id)
    state["next_row"] = row + 1
    save_state(state)
    return row, msg_id

# ------------------------------------------------------------------------------
# 影刀运行工具类
# ------------------------------------------------------------------------------
def run_yingdao_app(app_name):
    logger.info(f"启动影刀应用: {app_name}")
    subprocess.Popen(YINGDAO_EXE)
    time.sleep(6)

    pyautogui.click(SEARCH_BOX_POS)
    time.sleep(1)

    pyautogui.hotkey("ctrl", "a")
    pyperclip.copy(app_name)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1.5)

    pyautogui.press("enter")
    time.sleep(2)

    pyautogui.moveTo(RUN_APP_POS, duration=0.3)
    pyautogui.click(RUN_APP_POS)
    time.sleep(2)

    return f"✅ 已运行影刀应用：{app_name}"

# ------------------------------------------------------------------------------
# 统一消息处理器（关键：运行指令不记录表格）
# ------------------------------------------------------------------------------
class UniversalHandler(dingtalk_stream.ChatbotHandler):
    async def process(self, callback: dingtalk_stream.CallbackMessage):
        data = callback.data
        msg = dingtalk_stream.ChatbotMessage.from_dict(data)
        text = msg.text.content.strip() if hasattr(msg, "text") else ""
        msg_id = data.get("msgId", "")

        logger.info(f"收到消息: {text}")

        # ====================== 核心修改 ======================
        # 如果是运行指令 → 只运行，不记录表格
        if "运行" in text:
            app_name = text.split("运行")[-1].strip()
            self.reply_text(f"收到指令，准备运行：{app_name}", msg)
            try:
                res = await asyncio.to_thread(run_yingdao_app, app_name)
                self.reply_text(res, msg)
            except Exception as e:
                self.reply_text(f"❌ 运行失败：{str(e)}", msg)
            return AckMessage.STATUS_OK, "OK"

        # 不是运行指令 → 才写入表格
        try:
            row, _ = await asyncio.to_thread(append_to_table, data)
            if row > 0 and REPLY_ON_SUCCESS:
                self.reply_text(f"✅ 已记录到表格第 {row} 行", msg)
        except Exception as e:
            logger.error(f"表格写入失败: {e}")

        return AckMessage.STATUS_OK, "OK"

# ------------------------------------------------------------------------------
# 启动
# ------------------------------------------------------------------------------
def main():
    credential = dingtalk_stream.Credential(DT_CLIENT_ID, DT_CLIENT_SECRET)
    client = dingtalk_stream.DingTalkStreamClient(credential)
    client.register_callback_handler(dingtalk_stream.chatbot.ChatbotMessage.TOPIC, UniversalHandler())
    logger.info("✅ 机器人启动成功：支持【写入表格】+【运行影刀】")
    client.start_forever()

if __name__ == "__main__":
    main()