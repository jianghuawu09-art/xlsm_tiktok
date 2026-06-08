"""
参考图 + 文字描述 => 生成新图，并返回“新图公网链接”（上传到腾讯云 COS）。
实现思路（避免 token 超限）：
1) 先把【参考图】上传到 COS，得到一个可访问 URL
2) 调用 Comfly 多模态接口：text + image_url
3) 解析返回链接 / 若为base64则上传COS
"""

import base64
import json
import re
import time
import requests
from qcloud_cos import CosConfig, CosS3Client
from pathlib import Path

# ======================【Comfly 配置（直接写死）】======================
API_KEY = "comfly密钥"
HOST = "ai.comfly.chat"

# 多个大模型测试，看看哪个效果好（按需增减）
MODELS = [
    # "gemini-3.1-flash-image-preview-4k", # 这个大模型不行
    "nano-banana",
    "nano-banana-2-4k",
]

COMFLY_CHAT_URL = f"https://{HOST}/v1/chat/completions"

# ======================【腾讯云 COS 配置（直接写死）】======================
COS_SECRET_ID = "腾讯云SecretId"
COS_SECRET_KEY = "腾讯云SecretKey"
COS_REGION = "ap-guangzhou"
COS_BUCKET = "janny-1434564519"
COS_PREFIX = "ai_gen"
COS_PUBLIC_READ = True

# ======================【文件路径（你的路径）】======================
REF_IMAGE_PATH = r"\\192.168.1.133\跑程序电脑文件共享路径\AI参考图生图\参考图.jpg"
PROMPT_TXT_PATH = r"\\192.168.1.133\跑程序电脑文件共享路径\AI参考图生图\文字描述.txt"

# ======================【COS 工具】======================
def get_cos_client():
    cfg = CosConfig(Region=COS_REGION, SecretId=COS_SECRET_ID, SecretKey=COS_SECRET_KEY, Scheme="https")
    return CosS3Client(cfg)

def cos_upload(local_path, key):
    client = get_cos_client()
    client.upload_file(Bucket=COS_BUCKET, Key=key, LocalFilePath=local_path)
    try:
        client.put_object_acl(Bucket=COS_BUCKET, Key=key, ACL="public-read")
    except:
        pass
    return f"https://{COS_BUCKET}.cos.{COS_REGION}.myqcloud.com/{key}"

# ======================【提取链接】======================
def extract_image_url(text):
    m = re.search(r"\((https?://[^)]+)\)", text)
    if m:
        return m.group(1).strip()
    m = re.search(r"(https?://\S+)", text)
    if m:
        return m.group(1).strip().rstrip(").,]}")
    return None

def extract_base64(text):
    m = re.search(r"data:image/(png|jpeg|jpg|webp);base64,([A-Za-z0-9+/=]+)", text)
    if not m:
        return None, None
    fmt = m.group(1).replace("jpg","jpeg")
    b64 = m.group(2)
    return fmt, b64

# ======================【AI 图生图核心】======================
def generate_image(prompt, ref_image_url, model_name):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_name,
        "stream": False,
        "temperature": 0.7,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": ref_image_url}}
                ]
            }
        ]
    }

    response = requests.post(COMFLY_CHAT_URL, headers=headers, json=payload, timeout=(20, 240), verify=False)
    if response.status_code != 200:
        return f"请求失败：{response.text}"
    
    data = response.json()
    return data["choices"][0]["message"]["content"]

# ======================【主程序】======================
if __name__ == "__main__":
    prompt = Path(PROMPT_TXT_PATH).read_text(encoding="utf-8").strip()
    print("========== 提示词 ==========")
    print(prompt)
    print("===========================\n")

    ref_key = f"{COS_PREFIX}/ref_{int(time.time())}.jpg"
    ref_url = cos_upload(REF_IMAGE_PATH, ref_key)
    print("✅ 参考图已上传：", ref_url)

    # ✅ 循环跑所有模型
    for model in MODELS:
        print(f"\n⏳ 正在生成：{model}")
        result = generate_image(prompt, ref_url, model)

        img_url = extract_image_url(result)
        if img_url:
            print(f"🎉 {model} 成功！新图链接：{img_url}")
        else:
            fmt, b64 = extract_base64(result)
            if b64:
                img_bytes = base64.b64decode(b64)
                tmp_path = "tmp_gen.jpg"
                with open(tmp_path, "wb") as f:
                    f.write(img_bytes)
                gen_key = f"{COS_PREFIX}/gen_{int(time.time())}_{model}.jpg"
                gen_url = cos_upload(tmp_path, gen_key)
                print(f"🎉 {model} 成功！新图链接：{gen_url}")
            else:
                print(f"⚠️ {model} 返回：{result}")