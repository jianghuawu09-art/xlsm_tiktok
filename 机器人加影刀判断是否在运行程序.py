from __future__ import annotations
import asyncio
import os
import time
import subprocess
import pyautogui
import pyperclip
import logging
from collections import deque
from typing import Optional, Tuple

import dingtalk_stream
from dingtalk_stream import AckMessage

# ======================== 全局配置 ========================
DT_CLIENT_ID = "dingyzwmwrqoumv2xyjb"
DT_CLIENT_SECRET = "mh0WB_3cqnOI3znHRr7Yj1BD5MQjwr_rrFHTYZtaJAx-4J2oQavuRk-KwU8kddH3"

YINGDAO_EXE = r"C:\Program Files\ShadowBot\ShadowBot.exe"
SEARCH_BOX_POS = (1513, 162)
RUN_APP_POS = (1491, 263)

FLAG_FOLDER = r"D:\yd_run_flag"
os.makedirs(FLAG_FOLDER, exist_ok=True)
# ============================================================

RUN_STATE_LOCK = asyncio.Lock()
RUN_QUEUE = deque()
WORKER_TASK: Optional[asyncio.Task] = None
CURRENT_APP: Optional[str] = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("dingbot")

# ======================================================================
# 检测影刀是否正在运行
# ======================================================================
def is_yingdao_busy() -> Tuple[bool, str]:
    try:
        files = os.listdir(FLAG_FOLDER)
        running = [f.replace(".run", "") for f in files if f.endswith(".run")]
        if running:
            return True, f"✅ 正在运行：{', '.join(running)}"
        return False, "🟢 影刀空闲，无任务运行"
    except:
        return False, "⚠️ 状态检测异常"

# ======================================================================
# 鼠标启动影刀
# ======================================================================
def run_yingdao_app(app_name: str) -> str:
    logger.info(f"启动应用: {app_name}")
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

    return f"✅ 已启动：{app_name}"

# ======================================================================
# 排队执行
# ======================================================================
async def _ensure_worker():
    global WORKER_TASK
    async with RUN_STATE_LOCK:
        if WORKER_TASK and not WORKER_TASK.done():
            return
        WORKER_TASK = asyncio.create_task(_queue_worker())

async def _queue_worker():
    global CURRENT_APP
    while True:
        async with RUN_STATE_LOCK:
            if not RUN_QUEUE:
                CURRENT_APP = None
                return
            app_name, handler, msg = RUN_QUEUE.popleft()
            CURRENT_APP = app_name

        try:
            result = await asyncio.to_thread(run_yingdao_app, app_name)
            handler.reply_text(result, msg)
        except Exception as e:
            handler.reply_text(f"❌ 运行失败：{str(e)}", msg)

        await asyncio.sleep(1)

# ======================================================================
# 消息处理
# ======================================================================
class UniversalHandler(dingtalk_stream.ChatbotHandler):
    async def process(self, callback: dingtalk_stream.CallbackMessage):
        msg = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
        text = msg.text.content.strip() if hasattr(msg, "text") else ""
        logger.info(f"消息：{text}")

        # --------------------------
        # 查询状态（你要的功能）
        # --------------------------
        if any(k in text for k in ["状态", "查看状态", "运行状态", "当前状态"]):
            busy, info = is_yingdao_busy()
            self.reply_text(info, msg)
            return AckMessage.STATUS_OK, "OK"

        # --------------------------
        # 运行程序
        # --------------------------
        if "运行" in text:
            app_name = text.replace("运行", "").strip()
            self.reply_text(f"收到指令，准备运行：{app_name}", msg)
            if not app_name:
                self.reply_text("⚠️ 请输入：运行 程序名", msg)
                return AckMessage.STATUS_OK, "OK"

            is_busy, info = is_yingdao_busy()
            if is_busy:
                self.reply_text(f"⚠️ 目前有任务在执行，无法重复运行\n{info}", msg)
                return AckMessage.STATUS_OK, "OK"

            async with RUN_STATE_LOCK:
                RUN_QUEUE.append((app_name, self, msg))

            await _ensure_worker()
            return AckMessage.STATUS_OK, "OK"
        else:
            self.reply_text("⚠️ 无效指令，请发送：运行 程序名 或 查询状态", msg)
            return AckMessage.STATUS_OK, "OK"

# ======================================================================
# 启动
# ======================================================================
def main():
    credential = dingtalk_stream.Credential(DT_CLIENT_ID, DT_CLIENT_SECRET)
    client = dingtalk_stream.DingTalkStreamClient(credential)
    client.register_callback_handler(dingtalk_stream.chatbot.ChatbotMessage.TOPIC, UniversalHandler())
    logger.info("✅ 钉钉机器人已启动")
    client.start_forever()

if __name__ == "__main__":
    main()