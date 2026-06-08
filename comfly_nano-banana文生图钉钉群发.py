import http.client
import json
import re
import requests  # 钉钉需要

# ======================【钉钉发送相关函数】======================
def get_access_token(app_key: str, app_secret: str) -> str:
    url = "https://oapi.dingtalk.com/gettoken"
    r = requests.get(url, params={"appkey": app_key, "appsecret": app_secret}, timeout=30)
    data = r.json()
    if data.get("errcode") != 0:
        raise RuntimeError(f"gettoken failed: {data}")
    return data["access_token"]

def send_text_to_chat(access_token: str, chat_id: str, content: str):
    url = "https://oapi.dingtalk.com/chat/send"
    payload = {
        "chatid": chat_id,
        "msg": {
            "msgtype": "text",
            "text": {"content": content}
        }
    }
    r = requests.post(
        url,
        params={"access_token": access_token},
        data=json.dumps(payload, ensure_ascii=False),
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    data = r.json()
    return data

# ======================【文生图配置】======================
API_KEY = "comfly密钥地址"
HOST = "ai.comfly.chat"

MODELS = [
    "nano-banana",
    "nano-banana-2",
    "gpt-image-1-mini",
]

# 生成图片 + 提取链接
def generate_image(model_name, prompt):
    try:
        conn = http.client.HTTPSConnection(HOST, timeout=60)
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        payload = json.dumps({
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "stream": False
        })

        conn.request("POST", "/v1/chat/completions", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        conn.close()

        result = json.loads(data)
        if "choices" in result:
            content = result['choices'][0]['message']['content']
            match = re.search(r'\[下载1\]\((.*?)\)', content)
            if match:
                return f"\n====== {model_name} 下载链接 ======\n{match.group(1)}"
            else:
                return f"\n{model_name}：未找到图片链接"
        else:
            return f"\n{model_name} 调用失败"
    except Exception as e:
        return f"\n{model_name} 请求异常：{str(e)}"

# ======================【主程序：生成 + 打印 + 发钉钉】======================
if __name__ == "__main__":
    # 1. 读取提示词
    file_path = r"\\Star-1\素材库\AI工程师存放的文件路径\AI文生图\文字描述.txt"
    with open(file_path, "r", encoding="utf-8") as f:
        user_input = f.read()

    # 2. 拼接要发送的内容
    send_content = "==========本次绘图提示词==========\n"
    send_content += user_input
    send_content += "\n================================\n"

    print("==========本次绘图提示词==========")
    print(user_input)
    print("================================\n")

    # 3. 生成所有模型结果
    for model in MODELS:
        res = generate_image(model, user_input)
        print(res)
        send_content += res

    # 4. 发送到钉钉群
    APP_KEY = "dingyzwmwrqoumv2xyjb"
    APP_SECRET = "mh0WB_3cqnOI3znHRr7Yj1BD5MQjwr_rrFHTYZtaJAx-4J2oQavuRk-KwU8kddH3"
    CHAT_ID = "chat85d1dac922828439e037a547737fad09"

    try:
        token = get_access_token(APP_KEY, APP_SECRET)
        send_text_to_chat(token, CHAT_ID, send_content)
        print("\n✅ 结果已发送到钉钉群！")
    except Exception as e:
        print("\n❌ 钉钉发送失败：", e)