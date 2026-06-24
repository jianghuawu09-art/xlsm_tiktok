import sys
import logging
import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# ==================== 全局配置（仅修改这里）====================
# 薄荷图床配置
MINT_UPLOAD_URL = 'https://ok.a2k6.com/yixing01/api/upload/'
MINT_API_TOKEN = '18fe510915103f9e2ca3'

# 钉钉配置
DT_CLIENT_ID = 'dingyzwmwrqoumv2xyjb'
DT_CLIENT_SECRET = 'mh0WB_3cqnOI3znHRr7Yj1BD5MQjwr_rrFHTYZtaJAx-4J2oQavuRk-KwU8kddH3'
BASE_ID = '4lgGw3P8vRLPeRmXsp40mBj285daZ90D'
SHEET_ID = 'hERWDMS'
OPERATOR_ID = "fADzjBkYl9VEvxiPwAKrF2QiEiE"

# 本地临时保存图片
SAVE_DIR = r"D:\钉钉表格图片"
os.makedirs(SAVE_DIR, exist_ok=True)

# ==================== 薄荷图床上传函数（替换原COS上传） ====================
def upload_to_mint(local_path, filename):
    file_handle = None
    try:
        file_handle = open(local_path, 'rb')
        files = {
            'uploadedFile': (filename, file_handle, 'image/jpeg')
        }
        data = {
            'api_token': MINT_API_TOKEN,
            'upload_format': 'file',
            'mode': '1',
            'uploadPath': "",
            'watermark': '0',
        }
        headers = {"Accept-Encoding": "identity"}
        response = requests.post(
            MINT_UPLOAD_URL,
            data=data,
            files=files,
            headers=headers,
            timeout=25
        )
        raw_text = response.text.strip()
        print("薄荷接口原始返回：", repr(raw_text))
        if not raw_text:
            print("❌ 薄荷返回空白，上传失败")
            return None
        res_json = response.json()
        if res_json.get("status") == "success":
            img_url = res_json.get("url")
            print(f"✅ 薄荷上传成功，链接：{img_url}")
            return img_url
        else:
            print(f"❌ 薄荷业务报错：{res_json}")
            return None
    except Exception as e:
        print(f"❌ 薄荷上传异常：{e}")
        return None
    finally:
        if file_handle:
            file_handle.close()

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

# ==================== 批量执行主函数 ====================
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
        mint_urls = []
        # 3. 下载 + 薄荷图床上传每张图
        for img in images:
            filename = img.get("filename")
            img_url = img.get("url")
            if not filename or not img_url:
                continue
            # 下载到本地临时目录
            local_path = os.path.join(SAVE_DIR, filename)
            try:
                img_data = requests.get(img_url, timeout=15).content
                with open(local_path, "wb") as f:
                    f.write(img_data)
                print(f"  下载完成：{filename}")
            except Exception as e:
                print(f"  图片下载失败：{e}")
                continue
            # 调用薄荷图床上传
            mint_url = upload_to_mint(local_path, filename)
            if mint_url:
                mint_urls.append(mint_url)
        # 多张图片链接换行拼接
        if mint_urls:
            final_link = "\n".join(mint_urls)
            success = update_transfer_link(token, record_id, final_link)
            total_result.append({"record_id": record_id, "links": mint_urls, "success": success})
    print("\n🎉 所有任务执行完成！")
    return {"code": 200, "msg": "执行完成", "data": total_result}

# ==================== FastAPI 接口服务 ====================
app = FastAPI(title="钉钉图片转薄荷图床链接接口")
class TriggerBody(BaseModel):
    pass

# 批量处理触发接口
@app.post("/run_upload_task")
def trigger_task(body: TriggerBody):
    result = run_all_task()
    return result

# 启动服务
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)