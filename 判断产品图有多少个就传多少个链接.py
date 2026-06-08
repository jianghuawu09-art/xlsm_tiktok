import requests
import os

# ================= 配置区域 =================
DT_CLIENT_ID = 'dingyzwmwrqoumv2xyjb'
DT_CLIENT_SECRET = 'mh0WB_3cqnOI3znHRr7Yj1BD5MQjwr_rrFHTYZtaJAx-4J2oQavuRk-KwU8kddH3'

BASE_ID = '4lgGw3P8vRLPeRmXsp40mBj285daZ90D'
SHEET_ID = 'hERWDMS'
OPERATOR_ID = "fADzjBkYl9VEvxiPwAKrF2QiEiE"

# 这里填你要批量写入的链接（会自动按图片数量生成）
BASE_URL = "https://你的图片链接.jpg"
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

# ===================== 写入转链接 =====================
def update_transfer_link(token, record_id, final_link):
    url = f"https://api.dingtalk.com/v1.0/notable/bases/{BASE_ID}/sheets/{SHEET_ID}/records?operatorId={OPERATOR_ID}"
    
    headers = {
        "x-acs-dingtalk-access-token": token,
        "Content-Type": "application/json"
    }

    payload = {
        "records": [
            {
                "id": record_id,
                "fields": {
                    "转链接": {
                        "link": final_link,
                        "text": ""
                    }
                }
            }
        ]
    }

    try:
        response = requests.put(url, json=payload, headers=headers)
        print(f"✅ 行 {record_id} | 写入成功 | 状态码：{response.status_code}")
    except Exception as e:
        print(f"❌ 行 {record_id} | 失败：{str(e)}")

# ===================== 核心逻辑 =====================
if __name__ == "__main__":
    try:
        token = get_dingtalk_token()
        records = get_all_records(token)

        for record in records.get("records", []):
            record_id = record["id"]
            fields = record.get("fields", {})
            images = fields.get("产品图", [])

            img_count = len(images)
            if img_count == 0:
                continue

            # ==============================================
            # ✅ 关键：有几张图，就生成几行链接（自动换行）
            # ==============================================
            link_lines = [BASE_URL for _ in range(img_count)]
            final_link = "\n".join(link_lines)  # 👈 这里就是自动换行

            print(f"🖼️ 行 {record_id} | 图片数量：{img_count} 张")
            update_transfer_link(token, record_id, final_link)

        print("\n🎉 全部完成！")

    except Exception as e:
        print(f"\n❌ 错误：{e}")