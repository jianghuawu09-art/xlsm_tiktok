import os
import requests
import time
import random

# --- 用户配置 ---

# 1. Pexels API 密钥
# !!! 警告: 请务必将这里替换为你自己的 Pexels API 密钥 !!!
# 获取地址: https://www.pexels.com/api/
API_KEY = "a74TsWzgewruQxM0w1J4DMzipPF6Knu96EFzFpVJQhiwKTXI5Irwbgtx"

# 2. 图片保存路径
OUTPUT_DIR = r"D:\爬取人脸图片"

# 3. 抓取图片的总目标数量
TOTAL_IMAGES_TO_FETCH = 300
# 4. 搜索关键词 (为了多样性，涵盖男女老少)
SEARCH_QUERIES = [
    # 年轻男女
    "young man portrait", "handsome man", "young woman portrait", "beautiful woman face",
    # 小孩
    "asian child portrait", "european child portrait", "little boy face", "little girl face",
    # 不同地区面孔
    "caucasian face", "african face", "asian face", "hispanic face",
    # 青春靓丽
    "youthful smile", "vibrant portrait", "fashion model face"
]

# 5. 每页请求的图片数量 (Pexels API 最大值为 80)
PER_PAGE = 80

# --- 脚本正文 ---

def download_images():
    """
    使用 Pexels API 下载图片。
    """
    # 检查 API Key 是否已填写
    if API_KEY == "请在这里粘贴你的PEXELS_API_KEY" or not API_KEY:
        print("[错误] 请先在脚本中填写你的 Pexels API 密钥 (API_KEY)。")
        print("获取地址: https://www.pexels.com/api/")
        return

    # 创建输出目录
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"创建输出文件夹: '{OUTPUT_DIR}'")

    headers = {"Authorization": API_KEY}
    downloaded_count = 0
    page = 1
    
    print(f"--- 开始抓取图片，目标: {TOTAL_IMAGES_TO_FETCH} 张 ---")

    while downloaded_count < TOTAL_IMAGES_TO_FETCH:
        # 从关键词列表中随机选择一个进行搜索，增加多样性
        query = random.choice(SEARCH_QUERIES)
        
        # 构建 API 请求 URL
        url = f"https://api.pexels.com/v1/search?query={query}&per_page={PER_PAGE}&page={page}"
        
        try:
            print(f"\n正在搜索 '{query}' (第 {page} 页)...")
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()  # 如果请求失败 (如 4xx, 5xx), 则抛出异常

            data = response.json()
            photos = data.get("photos", [])

            if not photos:
                print(f"  '{query}' 没有更多结果了，尝试下一个关键词。")
                page = 1 # 重置页数，换个词搜
                continue

            for photo in photos:
                if downloaded_count >= TOTAL_IMAGES_TO_FETCH:
                    break
                
                # 获取图片原始 URL
                image_url = photo['src']['original']
                # 从 URL 中提取文件名和扩展名
                file_name = f"pexels_{photo['id']}{os.path.splitext(image_url.split('?')[0])[-1]}"
                output_path = os.path.join(OUTPUT_DIR, file_name)

                # 如果文件已存在，则跳过
                if os.path.exists(output_path):
                    print(f"  - 已跳过 (已存在): {file_name}")
                    continue

                # 下载图片
                print(f"  - 正在下载 ({downloaded_count + 1}/{TOTAL_IMAGES_TO_FETCH}): {file_name}")
                img_response = requests.get(image_url, timeout=20)
                if img_response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(img_response.content)
                    downloaded_count += 1
                else:
                    print(f"    [警告] 下载图片失败: {file_name} (状态码: {img_response.status_code})")
                
                # 友好的请求间隔，避免请求过于频繁
                time.sleep(random.uniform(0.5, 1.5))

            page += 1

        except requests.exceptions.RequestException as e:
            print(f"[网络错误] 请求失败: {e}")
            print("等待 30 秒后重试...")
            time.sleep(30)
        except Exception as e:
            print(f"[未知错误] 发生错误: {e}")
            break

    print(f"\n--- 任务完成 ---")
    print(f"成功下载 {downloaded_count} 张图片到 '{OUTPUT_DIR}'")


if __name__ == "__main__":
    download_images()