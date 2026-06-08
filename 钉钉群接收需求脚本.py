"""
钉钉群消息 → 自动写入「钉钉文档-表格」

重要说明（先看这段，避免走弯路）：
1) 钉钉“群机器人 Webhook”（robot/send）只能“发消息”，不能用来“拉取群历史消息”。
2) 想要接收消息并处理，推荐使用钉钉 Stream 模式（本脚本即采用 Stream 模式）。
3) Stream 机器人能接收的通常是“发给机器人的消息”（例如群里 @机器人 的文本），而不是群里所有人的所有消息。

你提出的“定时检查群消息/判断新消息”：
- 钉钉开放平台一般不提供“轮询拉群消息”的能力；
- 生产上通常是“消息推送/长连接接收”（Stream）来保证实时、稳定。

本脚本功能：
- 机器人收到一条文本（建议在群里 @机器人 触发）后
- 去重（同一 msgId 只处理一次）
- 将 [时间, 发送人, 会话/群, 文本] 4 列写入钉钉表格下一行
- 可选：写入成功后给出机器人回复

准备工作：
1) 安装依赖：
   pip install dingtalk-stream requests

2) 你需要准备并填写下面配置（或用环境变量）：
   - DT_CLIENT_ID / DT_CLIENT_SECRET（你已提供）
   - WORKBOOK_ID：钉钉表格文件ID（文档里叫 workbookId）
   - SHEET_ID：工作表ID或名称（如 Sheet1 / 或 st-xxx）
   - OPERATOR_UNION_ID：操作人 unionId（需要对该表格有权限，否则会报 The operator has no permission）

运行：
   python dingtalk_msg_to_doc_table.py

参考：
- Stream SDK: https://github.com/open-dingtalk/dingtalk-stream-sdk-python
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import requests

import dingtalk_stream
from dingtalk_stream import AckMessage


DT_CLIENT_ID = "机器人应用的 AppKey"  # 可填默认值，例如 "dingxxxx"
DT_CLIENT_SECRET = "机器人的密钥"  # 可填默认值
WORKBOOK_ID = "vNG4YZ7JnPbOLPNvf9Ap6XXdW2LD0oRE"  # 可填默认值（workbookId），这里是从钉钉文档里复制的ID
SHEET_ID = "Sheet1"  # 可填默认值（工作表名称或ID）
OPERATOR_UNION_ID = "fADzjBkYl9VEvxiPwAKrF2QiEiE"  # 可填默认值（unionId），从钉钉获取operator脚本获取

# 用环境变量覆盖（环境变量为空时不会把默认值覆盖成空）
DT_CLIENT_ID = os.getenv("DT_CLIENT_ID", DT_CLIENT_ID).strip()
DT_CLIENT_SECRET = os.getenv("DT_CLIENT_SECRET", DT_CLIENT_SECRET).strip()
WORKBOOK_ID = os.getenv("DT_WORKBOOK_ID", WORKBOOK_ID).strip()
SHEET_ID = os.getenv("DT_SHEET_ID", SHEET_ID).strip()
OPERATOR_UNION_ID = os.getenv("DT_OPERATOR_UNION_ID", OPERATOR_UNION_ID).strip()

# 记录处理状态（去重 + 写入行号）
STATE_FILE = os.getenv("DT_STATE_FILE", "dingtalk_msg_to_doc_table.state.json")
START_ROW = int(os.getenv("DT_START_ROW", "2"))  # 从第几行开始写（默认跳过表头）

# 可选：写入成功后是否回复群里
REPLY_ON_SUCCESS = os.getenv("DT_REPLY_ON_SUCCESS", "1").strip() not in ("0", "false", "False")


class DingTalkApiError(RuntimeError):
    pass


def _now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def load_state() -> Dict[str, Any]:
    if not os.path.exists(STATE_FILE):
        return {"next_row": START_ROW, "seen_msg_ids": []}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "next_row" not in data:
            data["next_row"] = START_ROW
        if "seen_msg_ids" not in data or not isinstance(data["seen_msg_ids"], list):
            data["seen_msg_ids"] = []
        # 限制 seen_msg_ids 长度，避免无限增长
        data["seen_msg_ids"] = data["seen_msg_ids"][-2000:]
        return data
    except Exception:
        # 读坏了就重建，避免脚本直接挂
        return {"next_row": START_ROW, "seen_msg_ids": []}


def save_state(state: Dict[str, Any]) -> None:
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE_FILE)


@dataclass
class TokenCache:
    access_token: str = ""
    expire_at: float = 0.0  # epoch seconds


TOKEN_CACHE = TokenCache()


def get_app_access_token(client_id: str, client_secret: str) -> str:
    """
    新版获取企业内部应用 accessToken：
    POST https://api.dingtalk.com/v1.0/oauth2/accessToken
    Body: {"appKey": "...", "appSecret": "..."}
    """

    now = time.time()
    if TOKEN_CACHE.access_token and now < TOKEN_CACHE.expire_at - 60:
        return TOKEN_CACHE.access_token

    url = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
    r = requests.post(url, json={"appKey": client_id, "appSecret": client_secret}, timeout=30)
    if r.status_code != 200:
        raise DingTalkApiError(f"获取accessToken失败(HTTP {r.status_code}): {r.text}")
    data = r.json()
    token = data.get("accessToken")
    expire_in = int(data.get("expireIn", 7200))
    if not token:
        raise DingTalkApiError(f"获取accessToken失败: {data}")
    TOKEN_CACHE.access_token = token
    TOKEN_CACHE.expire_at = now + expire_in
    return token


def update_range(
    access_token: str,
    workbook_id: str,
    sheet_id: str,
    range_address: str,
    operator_union_id: str,
    values_2d: list[list[Any]],
) -> Dict[str, Any]:
    """
    更新单元格区域（写入数据）：
    PUT https://api.dingtalk.com/v1.0/doc/workbooks/{workbookId}/sheets/{sheetId}/ranges/{rangeAddress}?operatorId=xxx
    Body: {"values": [[...]]}
    """

    url = f"https://api.dingtalk.com/v1.0/doc/workbooks/{workbook_id}/sheets/{sheet_id}/ranges/{range_address}"
    params = {"operatorId": operator_union_id}
    headers = {
        "Content-Type": "application/json",
        "x-acs-dingtalk-access-token": access_token,
    }
    r = requests.put(url, params=params, headers=headers, json={"values": values_2d}, timeout=30)
    if r.status_code >= 400:
        raise DingTalkApiError(f"写入表格失败(HTTP {r.status_code}): {r.text}")
    return r.json() if r.text else {}


def extract_msg_id(payload: Dict[str, Any]) -> str:
    """
    尽量从回调 data 中抽取消息ID，用于去重。
    不同版本/场景字段可能不同，所以这里做容错。
    """

    for k in ("msgId", "msgid", "messageId", "message_id", "id"):
        v = payload.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    # 兜底：用文本+时间做弱去重（不推荐，但总比没有强）
    text = ""
    try:
        text = (payload.get("text", {}) or {}).get("content", "")  # type: ignore[union-attr]
    except Exception:
        pass
    return f"fallback:{hash(text)}:{int(time.time())}"


def extract_sender(payload: Dict[str, Any]) -> str:
    # 常见字段名做容错
    for k in ("senderNick", "sender_nick", "nick", "senderName", "sender_name"):
        v = payload.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    # 兜底：尝试从 sender 字段
    sender = payload.get("sender")
    if isinstance(sender, dict):
        for k in ("nick", "name", "senderNick"):
            v = sender.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
    return ""


def extract_chat(payload: Dict[str, Any]) -> str:
    for k in ("conversationId", "chatId", "openConversationId", "cid"):
        v = payload.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def extract_text(payload: Dict[str, Any]) -> str:
    # Stream ChatbotMessage 常见结构：{"text": {"content": "xxx"}}
    t = payload.get("text")
    if isinstance(t, dict):
        c = t.get("content")
        if isinstance(c, str):
            return c
    # 兜底：直接 content
    c = payload.get("content")
    if isinstance(c, str):
        return c
    return ""


def append_message_to_sheet(message_payload: Dict[str, Any]) -> Tuple[int, str]:
    """
    把一条消息追加写入表格，返回 (写入行号, msg_id)
    """

    if not (DT_CLIENT_ID and DT_CLIENT_SECRET):
        raise RuntimeError("请先配置 DT_CLIENT_ID / DT_CLIENT_SECRET（环境变量或脚本顶部配置区）")
    if not (WORKBOOK_ID and SHEET_ID and OPERATOR_UNION_ID):
        raise RuntimeError("请先配置 DT_WORKBOOK_ID / DT_SHEET_ID / DT_OPERATOR_UNION_ID")

    state = load_state()
    msg_id = extract_msg_id(message_payload)
    if msg_id in state["seen_msg_ids"]:
        # 已处理过
        return -1, msg_id

    row = int(state.get("next_row", START_ROW))
    sender = extract_sender(message_payload)
    chat = extract_chat(message_payload)
    text = extract_text(message_payload).strip()
    if not text:
        # 非文本消息就忽略（可按需扩展）
        state["seen_msg_ids"].append(msg_id)
        save_state(state)
        return -1, msg_id

    values = [[_now_str(), sender, chat, text]]
    range_addr = f"A{row}:D{row}"

    token = get_app_access_token(DT_CLIENT_ID, DT_CLIENT_SECRET)
    update_range(
        token,
        workbook_id=WORKBOOK_ID,
        sheet_id=SHEET_ID,
        range_address=range_addr,
        operator_union_id=OPERATOR_UNION_ID,
        values_2d=values,
    )

    state["seen_msg_ids"].append(msg_id)
    state["seen_msg_ids"] = state["seen_msg_ids"][-2000:]
    state["next_row"] = row + 1
    save_state(state)
    return row, msg_id


class ToSheetBotHandler(dingtalk_stream.ChatbotHandler):
    async def process(self, callback: dingtalk_stream.CallbackMessage):
        incoming = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
        payload = callback.data  # dict

        # 兼容：把 SDK 解析出的字段补回 payload（有些字段在不同版本 key 不一致）
        try:
            if hasattr(incoming, "text") and getattr(incoming, "text"):
                payload.setdefault("text", getattr(incoming, "text"))
        except Exception:
            pass
        try:
            if hasattr(incoming, "sender_nick") and getattr(incoming, "sender_nick"):
                payload.setdefault("senderNick", getattr(incoming, "sender_nick"))
        except Exception:
            pass

        try:
            row, msg_id = await asyncio.to_thread(append_message_to_sheet, payload)
            if REPLY_ON_SUCCESS and row != -1:
                self.reply_text(f"已写入表格第 {row} 行。", incoming)
        except Exception as e:
            # 出错也给个提示，便于排障（必要时可去掉，避免泄露细节）
            self.reply_text(f"写入表格失败：{e}", incoming)

        return AckMessage.STATUS_OK, "OK"


def main() -> None:
    if not DT_CLIENT_ID or not DT_CLIENT_SECRET:
        raise SystemExit("请先设置环境变量 DT_CLIENT_ID / DT_CLIENT_SECRET（或修改脚本顶部配置区）")

    # 启动 Stream 长连接，持续接收“发给机器人的消息”
    credential = dingtalk_stream.Credential(DT_CLIENT_ID, DT_CLIENT_SECRET)
    client = dingtalk_stream.DingTalkStreamClient(credential)
    client.register_callback_handler(dingtalk_stream.chatbot.ChatbotMessage.TOPIC, ToSheetBotHandler())
    client.start_forever()


if __name__ == "__main__":
    main()
