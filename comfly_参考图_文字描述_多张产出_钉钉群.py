"""
参考图+文字 → 循环生成N张独立图片（使用 /v1/images/generations 端点）
生成完成后自动发送到钉钉群（API方式，使用APP_KEY和APP_SECRET）
"""
import base64
import re
import time
import json
import requests
from qcloud_cos import CosConfig, CosS3Client
from pathlib import Path

# ======================【Comfly 配置】======================
API_KEY = "comfly密钥"
HOST = "ai.comfly.chat"

# 使用图片生成专用端点
IMAGES_GEN_URL = f"https://{HOST}/v1/images/generations"

MODELS = [
    "gemini-3.1-flash-image-preview-4k",
]

# ======================【腾讯云 COS】======================
COS_SECRET_ID = "腾讯云SecretId"
COS_SECRET_KEY = "腾讯云SecretKey"
COS_REGION = "ap-guangzhou"
COS_BUCKET = "janny-1434564519"
COS_PREFIX = "ai_gen"

# ======================【钉钉配置（API方式）】======================
DINGTALK_APP_KEY = "钉钉APP_KEY"
DINGTALK_APP_SECRET = "钉钉APP_SECRET"
DINGTALK_CHAT_ID = "chat85d1dac922828439e037a547737fad09"

# ======================【文件路径】======================
REF_IMAGE_PATH = r"\\192.168.1.133\跑程序电脑文件共享路径\AI参考图生图\参考图.jpg"
PROMPT_TXT_PATH = r"\\192.168.1.133\跑程序电脑文件共享路径\AI参考图生图\文字描述.txt"

# ======================【图片转base64】======================
def encode_image_to_base64(image_path):
    """将本地图片转为base64格式"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_base64_with_prefix(image_path):
    """获取带前缀的base64图片数据"""
    b64 = encode_image_to_base64(image_path)
    return f"data:image/jpeg;base64,{b64}"

# ======================【解析文字描述文件】======================
def parse_prompt_file(file_path):
    """解析文字描述文件，提取基础要求和各个场景"""
    content = Path(file_path).read_text(encoding="utf-8").strip()
    
    lines = content.split('\n')
    base_prompt = ""
    scenes = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        scene_match = re.search(r'【场景\s*(\d+)】', line)
        if scene_match:
            scene_desc = re.sub(r'【场景\s*\d+】', '', line).strip()
            scenes.append(scene_desc)
        else:
            if base_prompt:
                base_prompt += " " + line
            else:
                base_prompt = line
    
    if not scenes:
        scenes = ["生成一张图片"]
        base_prompt = content
    
    return base_prompt, scenes

# ======================【COS工具】======================
def get_cos_client():
    cfg = CosConfig(Region=COS_REGION, SecretId=COS_SECRET_ID, SecretKey=COS_SECRET_KEY, Scheme="https")
    return CosS3Client(cfg)

def cos_upload_bytes(img_bin, suffix="jpg"):
    client = get_cos_client()
    key = f"{COS_PREFIX}/gen_{int(time.time())}_{time.time_ns()}.{suffix}"
    client.put_object(Bucket=COS_BUCKET, Key=key, Body=img_bin)
    try:
        client.put_object_acl(Bucket=COS_BUCKET, Key=key, ACL="public-read")
    except:
        pass
    return f"https://{COS_BUCKET}.cos.{COS_REGION}.myqcloud.com/{key}"

# ======================【钉钉 API 工具】======================
def get_dingtalk_access_token(app_key: str, app_secret: str) -> str:
    """获取钉钉access_token"""
    url = "https://oapi.dingtalk.com/gettoken"
    r = requests.get(url, params={"appkey": app_key, "appsecret": app_secret}, timeout=30)
    data = r.json()
    if data.get("errcode") != 0:
        raise RuntimeError(f"获取钉钉token失败: {data}")
    return data["access_token"]

def send_dingtalk_text(access_token: str, chat_id: str, content: str):
    """发送文本消息到钉钉群聊"""
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
    if data.get("errcode") != 0:
        raise RuntimeError(f"发送钉钉消息失败: {data}")
    return data

def send_dingtalk_markdown(access_token: str, chat_id: str, title: str, content: str):
    """发送Markdown消息到钉钉群聊"""
    url = "https://oapi.dingtalk.com/chat/send"
    payload = {
        "chatid": chat_id,
        "msg": {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": content
            }
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
    if data.get("errcode") != 0:
        raise RuntimeError(f"发送钉钉消息失败: {data}")
    return data

# ======================【核心：使用 /images/generations 端点】======================
def generate_image_with_reference(prompt, ref_image_base64, model):
    """
    使用 /v1/images/generations 端点生成图片
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "model": model,
        "temperature": 0.7,
        "aspect_ratio": "1:1",
        "image_size": "4K",
        "image": ref_image_base64
    }
    
    try:
        response = requests.post(IMAGES_GEN_URL, headers=headers, json=payload, timeout=(30, 180), verify=False)
        
        if response.status_code != 200:
            print(f"  API错误: {response.status_code} - {response.text}")
            return None, None
        
        result = response.json()
        
        if "data" in result and len(result["data"]) > 0:
            img_data = result["data"][0]
            
            if "b64_json" in img_data:
                return "jpg", img_data["b64_json"]
            
            if "url" in img_data:
                img_response = requests.get(img_data["url"], timeout=60)
                if img_response.status_code == 200:
                    img_b64 = base64.b64encode(img_response.content).decode('utf-8')
                    return "jpg", img_b64
            
        print(f"  响应格式异常: {result.keys() if result else 'empty'}")
        return None, None
        
    except Exception as e:
        print(f"  请求异常: {str(e)}")
        return None, None

# ======================【主程序】======================
if __name__ == "__main__":
    print("=" * 80)
    print("🎨 AI 图生图程序启动")
    print("=" * 80)
    
    # 1. 解析文字描述文件
    base_prompt, scenes = parse_prompt_file(PROMPT_TXT_PATH)
    
    print("\n【基础要求】")
    print(base_prompt)
    print("\n【检测到的场景】")
    for idx, scene in enumerate(scenes, 1):
        print(f"  场景{idx}: {scene}")
    print(f"\n共 {len(scenes)} 个场景，将生成 {len(scenes)} 张图片")
    print("=" * 80)
    
    # 2. 将参考图转为base64
    print(f"\n📤 正在加载参考图...")
    try:
        ref_image_base64 = get_image_base64_with_prefix(REF_IMAGE_PATH)
        print(f"✅ 参考图已加载")
    except Exception as e:
        print(f"❌ 参考图加载失败: {e}")
        exit(1)
    
    # 3. 存储所有生成的链接
    all_links = []
    model_used = MODELS[0]
    
    for model in MODELS:
        print(f"\n🚀 使用模型：{model}")
        
        for idx, scene in enumerate(scenes, 1):
            # 组合完整提示词
            full_prompt = f"""{base_prompt}

【场景要求】{scene}

【输出要求】生成一张高质量的图片，严格遵循参考图中的衣服。"""
            
            print(f"\n[{idx}/{len(scenes)}] 正在生成场景{idx}...")
            print(f"  场景描述：{scene}")
            
            try:
                fmt, b64_data = generate_image_with_reference(full_prompt, ref_image_base64, model)
                
                if b64_data:
                    # 处理base64数据
                    if b64_data.startswith("http"):
                        img_response = requests.get(b64_data, timeout=60)
                        img_bin = img_response.content
                    else:
                        if "base64," in b64_data:
                            b64_data = b64_data.split("base64,")[1]
                        img_bin = base64.b64decode(b64_data)
                    
                    # 上传到COS获取公网链接
                    link = cos_upload_bytes(img_bin, fmt)
                    print(f"  ✅ 成功！链接：{link}")
                    all_links.append(link)
                else:
                    print(f"  ❌ 失败（未生成图片）")
                    all_links.append("FAILED")
                    
            except Exception as e:
                print(f"  ❌ 异常：{str(e)}")
                all_links.append(f"ERROR: {str(e)}")
            
            # 避免请求过快
            time.sleep(2)
    
    # 4. 统计结果
    success_count = sum(1 for link in all_links if link and not link.startswith(("FAILED", "ERROR")))
    
    print("\n" + "=" * 80)
    print("【生成完成！】")
    print("=" * 80)
    print(f"✅ 成功：{success_count}/{len(scenes)} 张")
    
    # 打印所有链接
    for idx, (scene, link) in enumerate(zip(scenes, all_links), 1):
        if link and not link.startswith(("FAILED", "ERROR")):
            print(f"\n场景{idx}: {scene}")
            print(f"链接: {link}")
    
    # 5. 构建钉钉发送内容
    send_content = "========== 本次图生图结果 ==========\n"
    send_content += f"生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    send_content += f"使用模型：{model_used}\n"
    send_content += f"成功率：{success_count}/{len(scenes)}\n"
    send_content += f"参考图：{REF_IMAGE_PATH}\n"
    send_content += "\n【基础要求】\n"
    send_content += base_prompt + "\n"
    send_content += "\n【生成结果】\n"
    
    for idx, (scene, link) in enumerate(zip(scenes, all_links), 1):
        if link and not link.startswith(("FAILED", "ERROR")):
            send_content += f"\n场景{idx}：{scene}\n"
            send_content += f"链接：{link}\n"
        else:
            send_content += f"\n场景{idx}：{scene} [生成失败]\n"
    
    # 6. 发送到钉钉群
    print("\n📤 正在发送结果到钉钉群...")
    
    try:
        # 获取钉钉访问令牌
        token = get_dingtalk_access_token(DINGTALK_APP_KEY, DINGTALK_APP_SECRET)
        print("✅ 钉钉token获取成功")
        
        # 发送文本消息
        send_dingtalk_text(token, DINGTALK_CHAT_ID, send_content)
        print("✅ 结果已发送到钉钉群！")
        
        # 如果消息太长被截断，可以再发送一份Markdown格式
        if len(send_content) > 5000:
            # 发送Markdown格式的汇总
            markdown_title = "AI图生图生成报告"
            markdown_content = f"# {markdown_title}\n\n"
            markdown_content += f"**生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            markdown_content += f"**使用模型**: {model_used}\n"
            markdown_content += f"**成功率**: {success_count}/{len(scenes)}\n\n"
            markdown_content += "**生成结果**:\n"
            
            for idx, (scene, link) in enumerate(zip(scenes, all_links), 1):
                if link and not link.startswith(("FAILED", "ERROR")):
                    markdown_content += f"\n### 场景{idx}\n"
                    markdown_content += f"描述: {scene}\n"
                    markdown_content += f"链接: [点击查看]({link})\n"
            
            send_dingtalk_markdown(token, DINGTALK_CHAT_ID, markdown_title, markdown_content)
            print("✅ Markdown格式报告已发送")
        
    except Exception as e:
        print(f"\n❌ 钉钉发送失败：{e}")
    
    print("\n" + "=" * 80)
    print("程序执行完毕！")
    print("=" * 80)