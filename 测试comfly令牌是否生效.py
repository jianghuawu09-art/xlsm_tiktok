import requests

# ====================== 只改这里 ======================
API_KEY = "sk-5j2cpAHhfHNpvD4X5uMSbXyC438b6foLqEV0zdxFL6296bDp"
# ======================================================

# 接口地址是官方正确地址，不用动！
API_URL = "https://ai.comfly.org/v1/chat/completions"
MODEL = "gpt-3.5-turbo"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

data = {
    "model": MODEL,
    "messages": [
        {"role": "user", "content": "测试令牌是否有效"}
    ]
}

try:
    print("正在测试 Comfly API 令牌...")
    response = requests.post(API_URL, headers=headers, json=data, timeout=20)

    print(f"\n状态码：{response.status_code}")
    print(f"返回结果：\n{response.text}\n")

    if response.status_code == 200:
        print("✅ 令牌有效！接口正常！")
    else:
        print("❌ 令牌无效 或 账号被限制！")

except Exception as e:
    print(f"请求失败：{e}")