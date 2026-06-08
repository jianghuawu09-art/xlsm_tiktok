# ==================== 【1】腾讯云 COS 上传 ====================
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging
import os
import requests

# ==================== 全局配置（你只改这里）====================
# 腾讯云配置
SecretId = "腾讯云 SecretId"
SecretKey = "腾讯云 SecretKey"
Region = "ap-guangzhou"
Bucket = "janny-1434564519"
COS_PREFIX = "product_images"

# 钉钉配置
DT_CLIENT_ID = 'dingyzwmwrqoumv2xyjb'
DT_CLIENT_SECRET = 'mh0WB_3cqnOI3znHRr7Yj1BD5MQjwr_rrFHTYZtaJAx-4J2oQavuRk-KwU8kddH3'
BASE_ID = '4lgGw3P8vRLPeRmXsp40mBj285daZ90D'
SHEET_ID = 'hERWDMS'
OPERATOR_ID = "fADzjBkYl9VEvxiPwAKrF2QiEiE"

# 本地临时保存图片
SAVE_DIR = r"D:\钉钉表格图片"
os.makedirs(SAVE_DIR, exist_ok=True)

# ==================== 初始化腾讯云 ====================
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
cos_config = CosConfig(Region=Region, SecretId=SecretId, SecretKey=SecretKey)
cos_client = CosS3Client(cos_config)

# ==================== 【2】上传单张图片到 COS ====================
def upload_to_cos(local_path, filename):
    try:
        cos_key = f"{COS_PREFIX}/{filename}"
        cos_client.upload_file(
            Bucket=Bucket,
            Key=cos_key,
            LocalFilePath=local_path,
            PartSize=10,
            MAXThread=10
        )
        return cos_client.get_object_url(Bucket=Bucket, Key=cos_key)
    except Exception as e:
        print(f"上传失败：{e}")
        return None

# ==================== 【3】钉钉获取 Token ====================
def get_dingtalk_token():
    url = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
    res = requests.post(url, json={
        "appKey": DT_CLIENT_ID,
        "appSecret": DT_CLIENT_SECRET
    })
    return res.json()["accessToken"]

# ==================== 【4】读取表格数据 ====================
def get_all_records(token):
    url = f"https://api.dingtalk.com/v1.0/notable/bases/{BASE_ID}/sheets/{SHEET_ID}/records/list?operatorId={OPERATOR_ID}"
    headers = {
        "x-acs-dingtalk-access-token": token,
        "Content-Type": "application/json"
    }
    res = requests.post(url, headers=headers, json={"pageSize": 500})
    return res.json()

# ==================== 【5】写入链接到「转链接」字段 ====================
def update_transfer_link(token, record_id, final_link):
    url = f"https://api.dingtalk.com/v1.0/notable/bases/{BASE_ID}/sheets/{SHEET_ID}/records?operatorId={OPERATOR_ID}"
    headers = {
        "x-acs-dingtalk-access-token": token,
        "Content-Type": "application/json"
    }
    payload = {
        "records": [{
            "id": record_id,
            "fields": {
                "转链接": {
                    "link": final_link,
                    "text": ""
                }
            }
        }]
    }
    try:
        resp = requests.put(url, json=payload, headers=headers)
        print(f"✅ 写入成功 行:{record_id} | 状态码:{resp.status_code}")
    except Exception as e:
        print(f"❌ 写入失败：{e}")

# ==================== 【主流程：全自动执行】====================
if __name__ == "__main__":
    print("🔹 开始执行全流程...")

    # 1. 获取钉钉凭证
    token = get_dingtalk_token()
    records = get_all_records(token)

    # 2. 遍历每一行
    for record in records.get("records", []):
        record_id = record["id"]
        fields = record.get("fields", {})
        images = fields.get("产品图", [])

        if not images:
            continue

        print(f"\n🖼️ 处理行 {record_id}，共 {len(images)} 张图片")

        # 存储当前行所有COS链接
        cos_urls = []

        # 3. 下载 + 上传每张图
        for img in images:
            filename = img.get("filename")
            img_url = img.get("url")

            if not filename or not img_url:
                continue

            # 下载到本地
            local_path = os.path.join(SAVE_DIR, filename)
            try:
                img_data = requests.get(img_url, timeout=15).content
                with open(local_path, "wb") as f:
                    f.write(img_data)
                print(f"  下载：{filename}")
            except:
                continue

            # 上传COS
            cos_url = upload_to_cos(local_path, filename)
            if cos_url:
                cos_urls.append(cos_url)
                print(f"  上传COS：{cos_url}")

        # 4. 多张链接 → 自动换行
        if cos_urls:
            final_link = "\n".join(f"{url}" for url in cos_urls)
            update_transfer_link(token, record_id, final_link)

    print("\n🎉 所有任务执行完成！")