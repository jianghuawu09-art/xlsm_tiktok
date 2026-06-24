import sys
import logging
import os
import json
import requests
from fastapi import FastAPI, Request
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

# ==================== 处理单行记录 ====================
def process_single_record(token, record):
    record_id = record["id"]
    fields = record.get("fields", {})
    images = fields.get("产品图", [])
    if not images:
        print(f"⚠️ 行 {record_id} 没有产品图，跳过")
        return {"record_id": record_id, "links": [], "success": False, "msg": "无产品图"}
    print(f"\n🖼️ 处理行 {record_id}，共 {len(images)} 张图片")
    mint_urls = []
    for img in images:
        filename = img.get("filename")
        img_url = img.get("url")
        if not filename or not img_url:
            continue
        local_path = os.path.join(SAVE_DIR, filename)
        try:
            img_data = requests.get(img_url, timeout=15).content
            with open(local_path, "wb") as f:
                f.write(img_data)
            print(f"  下载完成：{filename}")
        except Exception as e:
            print(f"  图片下载失败：{e}")
            continue
        mint_url = upload_to_mint(local_path, filename)
        if mint_url:
            mint_urls.append(mint_url)
    if mint_urls:
        final_link = "\n".join(mint_urls)
        success = update_transfer_link(token, record_id, final_link)
        return {"record_id": record_id, "links": mint_urls, "success": success}
    return {"record_id": record_id, "links": [], "success": False, "msg": "图片处理失败"}

# ==================== 批量执行主函数 ====================
def run_all_task():
    print("🔹 开始执行全流程（全部行）...")
    token = get_dingtalk_token()
    records = get_all_records(token)
    total_result = []
    for record in records.get("records", []):
        result = process_single_record(token, record)
        total_result.append(result)
    print("\n🎉 所有任务执行完成！")
    return {"code": 200, "msg": "执行完成", "data": total_result}

# ==================== 单行执行函数 ====================
def run_single_task(record_id=None, title=None):
    print(f"🔹 开始执行单行任务，record_id: {record_id}, title: {title}")
    token = get_dingtalk_token()
    records = get_all_records(token)
    target_record = None
    for record in records.get("records", []):
        if record_id and record["id"] == record_id:
            target_record = record
            break
        if title:
            fields = record.get("fields", {})
            title_field = fields.get("标题", "")
            if isinstance(title_field, str) and title_field == title:
                target_record = record
                break
    if not target_record:
        print(f"❌ 未找到匹配的记录 (record_id={record_id}, title={title})")
        return {"code": 404, "msg": "未找到匹配的记录", "data": None}
    result = process_single_record(token, target_record)
    print(f"\n🎉 单行任务完成！")
    return {"code": 200, "msg": "执行完成", "data": result}

# ==================== FastAPI 接口服务 ====================
app = FastAPI(title="钉钉图片转薄荷图床链接接口")
class TriggerBody(BaseModel):
    class Config:
        extra = "allow"

# 处理接口
@app.post("/run_upload_task")
async def trigger_task(request: Request):
    raw_body = await request.body()
    body_text = raw_body.decode('utf-8')
    try:
        body_json = json.loads(body_text) if body_text else {}
    except:
        body_json = {}

    print("\n" + "="*70)
    print("📥 收到钉钉请求（全量信息Dump）")
    print("="*70)
    print(f"  请求方法: {request.method}")
    print(f"  请求URL: {request.url}")
    print(f"  请求路径: {request.url.path}")
    print(f"  Query参数: {dict(request.query_params)}")
    print(f"  路径参数: {request.path_params}")
    print(f"  原始Body: {body_text}")
    print(f"  解析JSON: {json.dumps(body_json, ensure_ascii=False)}")
    print(f"  所有Headers:")
    for k, v in request.headers.items():
        print(f"    {k}: {v}")
    print("="*70)
    
    # 把所有可能含行信息的字段都打印出来（从Header和Body里找）
    all_params = {}
    all_params.update(dict(request.query_params))
    all_params.update(body_json)
    
    # 也检查一下body里的所有字段，看有没有行ID
    print(f"  🔍 扫描所有可能含行ID的字段...")
    for k, v in all_params.items():
        print(f"    {k} = {v}")
    
    # 也检查Headers里的可疑字段
    suspicious_headers = [
        'x-ddpaas-recordid', 'x-ddpaas-rowid', 'x-ddpaas-itemid',
        'x-dingtalk-recordid', 'x-record-id', 'x-row-id',
        'ddpaas-record-id', 'record-id', 'row-id'
    ]
    for h in suspicious_headers:
        val = request.headers.get(h)
        if val:
            print(f"    ⚡ Header找到可疑字段: {h} = {val}")
    print("="*70 + "\n")

    # 可能的行ID字段名
    record_id_keys = [
        "record_id", "recordId", "id", "行ID", "记录ID",
        "recordid", "row_id", "rowId", "rowid",
        "_id", "item_id", "itemId"
    ]
    title_keys = [
        "title", "标题", "name", "名称", "产品标题",
        "产品名", "商品标题", "商品名称"
    ]

    record_id = None
    title = None

    for key in record_id_keys:
        if key in all_params and all_params[key]:
            val = str(all_params[key])
            if not val.startswith("{{") and not val.startswith("[[") and not val.startswith("${") and not val.startswith("#{") and not val.startswith("$"):
                record_id = val
                print(f"🎯 找到 record_id: {key} = {val}")
                break

    for key in title_keys:
        if key in all_params and all_params[key]:
            val = str(all_params[key])
            if not val.startswith("{{") and not val.startswith("[[") and not val.startswith("${") and not val.startswith("#{") and val != "$标题":
                title = val
                print(f"🎯 找到 title: {key} = {val}")
                break

    if record_id or title:
        result = run_single_task(record_id=record_id, title=title)
    else:
        print("ℹ️ 未找到有效的行标识，执行全量处理...")
        result = run_all_task()
    return result

# 启动服务
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)


# 还需要在钉钉里面请求参数 key=title   value=标题，
# 请求Hader key=Content-Type   value=application/json
# 请求Body={}  代表空