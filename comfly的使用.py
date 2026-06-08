import http.client
import json

# 你的配置
API_KEY = "comfly密钥地址"
HOST = "ai.comfly.chat"

# 要调用的模型（你要的 Nano Banana）
MODEL = "nano-banana"

def chat_with_nano_banana(prompt):
    try:
        conn = http.client.HTTPSConnection(HOST, timeout=20)
        
        # 请求头
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 请求体
        payload = json.dumps({
            "model": MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "stream": False  # 关闭流式输出，直接返回完整结果
        })
        
        # 发送请求
        conn.request("POST", "/v1/chat/completions", payload, headers)
        
        # 获取响应
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        conn.close()
        
        # 解析结果
        result = json.loads(data)
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            return f"返回异常：{result}"
    
    except Exception as e:
        return f"请求失败：{str(e)}"

# ========== 测试调用 ==========
if __name__ == "__main__":
    user_input = "你好，请介绍一下你自己"
    response = chat_with_nano_banana(user_input)
    print("Nano Banana 回答：")
    print(response)