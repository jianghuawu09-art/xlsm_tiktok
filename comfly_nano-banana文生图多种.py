import http.client
import json
import re

# 你的配置
API_KEY = "comfly密钥地址"
HOST = "ai.comfly.chat"

# 模型列表
MODELS = [
    "nano-banana",
    "nano-banana-2",
    "nano-banana-2-4k",
]

# 生成图片 + 提取下载链接
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

        # 🔥 修复：json.loads 正确解析字符串
        result = json.loads(data)
        
        if "choices" in result:
            content = result['choices'][0]['message']['content']
            # 提取下载链接
            match = re.search(r'\[下载1\]\((.*?)\)', content)
            if match:
                return f"\n====== {model_name} 下载链接 ======\n{match.group(1)}"
            else:
                return f"\n{model_name}：未找到图片链接"
        else:
            return f"\n{model_name} 调用失败"
    
    except Exception as e:
        return f"\n{model_name} 请求异常：{str(e)}"

# ========== 主程序 ==========
if __name__ == "__main__":
    file_path = r"\\Star-1\素材库\AI工程师存放的文件路径\AI文生图\文字描述.txt"
    
    with open(file_path, "r", encoding="utf-8") as f:
        user_input = f.read()

    # 打印提示词
    print("==========本次绘图提示词==========")
    print(user_input)
    print("================================\n")

    # 批量调用模型
    for model in MODELS:
        print(generate_image(model, user_input))