import asyncio
import logging
import subprocess
import pyautogui
import time
import dingtalk_stream
from dingtalk_stream import AckMessage
import pyperclip

# ===================== 配置 =====================
DT_CLIENT_ID = "钉钉机器人应用的 AppKey"
DT_CLIENT_SECRET = "机器人的密钥"

YINGDAO_EXE = r"C:\Program Files\ShadowBot\ShadowBot.exe"
# 👇 把你获取到的「搜索应用」坐标填在这里
SEARCH_BOX_POS = (1475, 204)
# 点击运行的应用坐标
RUN_APP_POS = (1453, 304)

# ==================================================

logging.basicConfig(level=logging.INFO)
SEEN_MSG = set()

# 打开影刀 + 点击搜索框并运行指定应用
def run_yingdao_app(app_name):
    # 1. 打开影刀
    subprocess.Popen(YINGDAO_EXE)
    time.sleep(6)  # 等待启动

    # 2. 点击「搜索应用」输入框（替换了原来的ctrl+f）
    pyautogui.click(SEARCH_BOX_POS[0], SEARCH_BOX_POS[1])
    time.sleep(2)

    # 3. 清空 + 粘贴中文（关键）
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.2)

    pyperclip.copy(app_name)        # 把中文放进剪贴板
    pyautogui.hotkey("ctrl", "v")   # 粘贴到搜索框
    time.sleep(1.5)

    # 4. 按下回车运行
    pyautogui.press("enter")
    time.sleep(2)

    # 通过坐标的方式进行点击运行坐标
    pyautogui.moveTo(RUN_APP_POS[0], RUN_APP_POS[1], duration=0.5)
    pyautogui.click(RUN_APP_POS[0], RUN_APP_POS[1])
    time.sleep(3)

    return f"✅ 已运行影刀应用：{app_name}"

# 钉钉机器人处理
class SimpleHandler(dingtalk_stream.ChatbotHandler):
    async def process(self, callback: dingtalk_stream.CallbackMessage):
        incoming = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
        msg_text = incoming.text.content.strip()
        msg_id = callback.data.get("msgId", "")

        # 去重
        if msg_id in SEEN_MSG:
            return AckMessage.STATUS_OK, "IGNORE"
        SEEN_MSG.add(msg_id)

        # 提取应用名
        if "运行" in msg_text:
            app_name = msg_text.split("运行")[-1].strip()
            self.reply_text(f"收到指令，准备运行：{app_name}", incoming)

            # 执行运行
            try:
                msg = run_yingdao_app(app_name)
            except Exception as e:
                msg = f"❌ 运行失败：{str(e)}"

            self.reply_text(msg, incoming)

        return AckMessage.STATUS_OK, "OK"

# 启动
def main():
    credential = dingtalk_stream.Credential(DT_CLIENT_ID, DT_CLIENT_SECRET)
    client = dingtalk_stream.DingTalkStreamClient(credential)
    client.register_callback_handler(dingtalk_stream.chatbot.ChatbotMessage.TOPIC, SimpleHandler())
    client.start_forever()

if __name__ == "__main__":
    main()