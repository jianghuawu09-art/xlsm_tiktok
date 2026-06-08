import requests
import os

# ================= 配置区域 =================
DT_CLIENT_ID = 'dingyzwmwrqoumv2xyjb'
DT_CLIENT_SECRET = 'mh0WB_3cqnOI3znHRr7Yj1BD5MQjwr_rrFHTYZtaJAx-4J2oQavuRk-KwU8kddH3'

BASE_ID = '4lgGw3P8vRLPeRmXsp40mBj285daZ90D'
SHEET_ID = 'hERWDMS'
OPERATOR_ID = "fADzjBkYl9VEvxiPwAKrF2QiEiE"

# 你要写入的固定链接（直接改这里）
YOUR_LINK = "https://你的图片链接.jpg"
# ============================================

def get_dingtalk_token():
    print("正在获取访问令牌...")
    url = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
    payload = {"appKey": DT_CLIENT_ID, "appSecret": DT_CLIENT_SECRET}
    response = requests.post(url, json=payload)
    return response.json()["accessToken"]

def get_all_records(token):
    print("正在读取表格数据...")
    url = f"https://api.dingtalk.com/v1.0/notable/bases/{BASE_ID}/sheets/{SHEET_ID}/records/list?operatorId={OPERATOR_ID}"
    headers = {
        "x-acs-dingtalk-access-token": token,
        "Content-Type": "application/json"
    }
    payload = {"pageSize": 500}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# ===================== 写入转链接字段 =====================
def update_transfer_link(token, record_id, link_text):
    url = f"https://api.dingtalk.com/v1.0/notable/bases/{BASE_ID}/sheets/{SHEET_ID}/records?operatorId={OPERATOR_ID}"
    
    headers = {
        "x-acs-dingtalk-access-token": token,
        "Content-Type": "application/json"
    }

    # 严格匹配你的格式：转链接 → {"link": "", "text": ""}
    payload = {
        "records": [
            {
                "id": record_id,
                "fields": {
                    "转链接": {
                        "link": link_text,
                        "text": ""
                    }
                }
            }
        ]
    }

    try:
        response = requests.put(url, json=payload, headers=headers)
        print(f"✅ 行 {record_id} | 转链接写入成功 | 状态码：{response.status_code}")
    except Exception as e:
        print(f"❌ 行 {record_id} | 更新失败：{str(e)}")

# ===================== 只执行：读取 + 写入链接 =====================
if __name__ == "__main__":
    try:
        token = get_dingtalk_token()
        records = get_all_records(token)

        # 遍历所有行 → 写入固定链接
        for record in records.get("records", []):
            record_id = record["id"]
            # 写入你设置的固定链接
            update_transfer_link(token, record_id, YOUR_LINK)

        print("\n🎉 所有行「转链接」字段更新完成！")

    except Exception as e:
        print(f"\n❌ 错误：{e}")