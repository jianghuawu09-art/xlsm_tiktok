# ==================== 【1】腾讯云 COS 上传 ====================
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging
import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# ==================== 全局配置（你只改这里）====================
# 腾讯云配置
SecretId = "AKID0ulYE00pSxbVEktocksy0sbCdrwtgO1l"
SecretKey = "d3FICwUuDRYaVJ2hFgyCqUzMa6pQ0gQF"
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


# ==================== 【2】上传单张图片到 COS（在线预览） ====================
def upload_to_cos(local_path, filename):
    try:
        cos_key = f"{COS_PREFIX}/{filename}"
        
        # 获取文件扩展名
        ext = os.path.splitext(filename)[1].lower()
        content_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp'
        }
        content_type = content_type_map.get(ext, 'application/octet-stream')
        
        # 上传文件并设置响应头
        with open(local_path, 'rb') as f:
            response = cos_client.put_object(
                Bucket=Bucket,
                Key=cos_key,
                Body=f,
                ContentType=content_type,
                ContentDisposition='inline'  # 关键：让浏览器预览而不是下载
            )
        
        # 公共读桶永久直链
        public_url = f"https://{Bucket}.cos.{Region}.myqcloud.com/{cos_key}"
        return public_url
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
        return True
    except Exception as e:
        print(f"❌ 写入失败：{e}")
        return False

# ==================== 原有主执行函数 ====================
def run_all_task():
    print("🔹 开始执行全流程...")
    # 1. 获取钉钉凭证
    token = get_dingtalk_token()
    records = get_all_records(token)
    total_result = []
    # 2. 遍历每一行
    for record in records.get("records", []):
        record_id = record["id"]
        fields = record.get("fields", {})
        images = fields.get("产品图", [])
        if not images:
            continue
        print(f"\n🖼️ 处理行 {record_id}，共 {len(images)} 张图片")
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
        # 多张链接换行
        if cos_urls:
            final_link = "\n".join(f"{url}" for url in cos_urls)
            success = update_transfer_link(token, record_id, final_link)
            total_result.append({"record_id": record_id, "links": cos_urls, "success": success})
    print("\n🎉 所有任务执行完成！")
    return {"code": 200, "msg": "执行完成", "data": total_result}

# ==================== FastAPI 接口服务 ====================
app = FastAPI(title="钉钉图片转COS链接接口")
# 请求入参模型（预留，现在无参数也能触发全量执行）
class TriggerBody(BaseModel):
    pass

# 触发执行接口
@app.post("/run_upload_task")
def trigger_task(body: TriggerBody):
    result = run_all_task()
    return result

# 启动服务
if __name__ == "__main__":
    # 本地开放局域网访问，端口9000--8000这个端口分配给其他的了
    uvicorn.run(app, host="0.0.0.0", port=9000)
