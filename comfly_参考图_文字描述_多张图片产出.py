"""
参考图+文字 → 循环生成N张独立图片（使用 /v1/images/generations 端点）
"""
import base64
import re
import time
import requests
from qcloud_cos import CosConfig, CosS3Client
from pathlib import Path

# ======================【Comfly 配置】======================
API_KEY = "comfly密钥"
HOST = "ai.comfly.chat"

# 使用图片生成专用端点（关键修改！）
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

def cos_upload_file(local_path, key):
    client = get_cos_client()
    client.upload_file(Bucket=COS_BUCKET, Key=key, LocalFilePath=local_path)
    try:
        client.put_object_acl(Bucket=COS_BUCKET, Key=key, ACL="public-read")
    except:
        pass

# ======================【核心：使用 /images/generations 端点】======================
def generate_image_with_reference(prompt, ref_image_base64, model):
    """
    使用 /v1/images/generations 端点生成图片
    这个端点能更好地遵循参考图
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "model": model,
        "temperature": 0.7,
        "aspect_ratio": "1:1",  # 可选：1:1, 16:9, 9:16, 4:3, 3:4
        "image_size": "4K",      # 可选：1K, 2K, 4K
        "image": ref_image_base64  # 关键：把参考图作为image参数传入
    }
    
    try:
        response = requests.post(IMAGES_GEN_URL, headers=headers, json=payload, timeout=(30, 180), verify=False)
        
        if response.status_code != 200:
            print(f"  API错误: {response.status_code} - {response.text}")
            return None, None
        
        result = response.json()
        
        # 解析返回的图片数据
        if "data" in result and len(result["data"]) > 0:
            img_data = result["data"][0]
            
            # 优先使用b64_json（base64格式）
            if "b64_json" in img_data:
                return "jpg", img_data["b64_json"]
            
            # 其次使用url（直接链接）
            if "url" in img_data:
                # 下载图片并转为base64
                img_response = requests.get(img_data["url"], timeout=60)
                if img_response.status_code == 200:
                    img_b64 = base64.b64encode(img_response.content).decode('utf-8')
                    return "jpg", img_b64
            
        print(f"  响应格式异常: {result.keys() if result else 'empty'}")
        return None, None
        
    except Exception as e:
        print(f"  请求异常: {str(e)}")
        return None, None

# ======================【保存结果】======================
def save_results(all_results, base_prompt, scenes):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    result_file = f"generation_results_{timestamp}.txt"
    
    with open(result_file, "w", encoding="utf-8") as f:
        f.write(f"生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"参考图：{REF_IMAGE_PATH}\n")
        f.write(f"基础要求：{base_prompt}\n")
        f.write(f"场景数量：{len(scenes)}\n")
        f.write("=" * 80 + "\n\n")
        
        for idx, (scene, url) in enumerate(zip(scenes, all_results), 1):
            f.write(f"【场景{idx}】{scene}\n")
            f.write(f"图片链接：{url}\n\n")
    
    return result_file

# ======================【主程序】======================
if __name__ == "__main__":
    # 1. 解析文字描述文件
    base_prompt, scenes = parse_prompt_file(PROMPT_TXT_PATH)
    
    print("=" * 80)
    print("【基础要求】")
    print(base_prompt)
    print("\n【检测到的场景】")
    for idx, scene in enumerate(scenes, 1):
        print(f"  场景{idx}: {scene}")
    print(f"\n共 {len(scenes)} 个场景，将生成 {len(scenes)} 张图片")
    print("=" * 80)
    
    # 2. 将参考图转为base64（不需要上传到COS）
    print(f"\n正在加载参考图...")
    ref_image_base64 = get_image_base64_with_prefix(REF_IMAGE_PATH)
    print(f"✅ 参考图已加载为base64格式\n")
    
    # 3. 存储所有生成的链接
    all_links = []
    
    for model in MODELS:
        print(f"使用模型：{model}")
        
        for idx, scene in enumerate(scenes, 1):
            # 组合完整提示词
            full_prompt = f"""{base_prompt}

【场景要求】{scene}

【输出要求】生成一张高质量的图片，严格遵循参考图中的衣服。"""
            
            print(f"[{idx}/{len(scenes)}] 正在生成场景{idx}...")
            print(f"  场景描述：{scene}")
            
            try:
                fmt, b64_data = generate_image_with_reference(full_prompt, ref_image_base64, model)
                
                if b64_data:
                    # 如果是URL格式，先下载再处理
                    if b64_data.startswith("http"):
                        img_response = requests.get(b64_data, timeout=60)
                        img_bin = img_response.content
                    else:
                        # base64格式，可能带有前缀
                        if "base64," in b64_data:
                            b64_data = b64_data.split("base64,")[1]
                        img_bin = base64.b64decode(b64_data)
                    
                    # 上传到COS获取公网链接
                    link = cos_upload_bytes(img_bin, fmt)
                    print(f"  ✅ 成功！链接：{link}\n")
                    all_links.append(link)
                else:
                    print(f"  ❌ 失败（未生成图片）\n")
                    all_links.append("FAILED")
                    
            except Exception as e:
                print(f"  ❌ 异常：{str(e)}\n")
                all_links.append(f"ERROR: {str(e)}")
            
            # 避免请求过快
            time.sleep(2)
    
    # 4. 打印汇总
    print("=" * 80)
    print("【生成完成！】")
    print("=" * 80)
    
    success_count = sum(1 for link in all_links if link and not link.startswith(("FAILED", "ERROR")))
    print(f"成功：{success_count}/{len(scenes)} 张")
    
    for idx, (scene, link) in enumerate(zip(scenes, all_links), 1):
        if link and not link.startswith(("FAILED", "ERROR")):
            print(f"\n场景{idx}: {scene}")
            print(f"链接: {link}")
    
    # 5. 保存结果
    result_file = save_results(all_links, base_prompt, scenes)
    print(f"\n✅ 结果已保存到：{result_file}")