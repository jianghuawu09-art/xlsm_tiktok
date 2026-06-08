import requests
import os

# ================= 配置区域 =================
DT_CLIENT_ID = 'dingyzwmwrqoumv2xyjb'
DT_CLIENT_SECRET = 'mh0WB_3cqnOI3znHRr7Yj1BD5MQjwr_rrFHTYZtaJAx-4J2oQavuRk-KwU8kddH3'

BASE_ID = '4lgGw3P8vRLPeRmXsp40mBj285daZ90D'
SHEET_ID = 'hERWDMS'
OPERATOR_ID = "fADzjBkYl9VEvxiPwAKrF2QiEiE"

# 图片保存文件夹
SAVE_DIR = r"D:\钉钉表格图片"
# ============================================

os.makedirs(SAVE_DIR, exist_ok=True)

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

def download_images(records):
    print("开始下载图片...\n")

    # 遍历所有记录
    for record in records.get("records", []):
        fields = record.get("fields", {})
        images = fields.get("产品图", [])

        # 遍历产品图里的所有图片
        for img in images:
            filename = img.get("filename")
            url = img.get("url")

            if not filename or not url:
                continue

            save_path = os.path.join(SAVE_DIR, filename)

            # 下载图片
            try:
                img_data = requests.get(url, timeout=10).content
                with open(save_path, "wb") as f:
                    f.write(img_data)
                print(f"✅ 已下载：{filename}")
            except Exception as e:
                print(f"❌ 下载失败：{filename}，原因：{e}")

    print(f"\n🎉 所有图片下载完成！保存目录：{SAVE_DIR}")

# ===================== 运行 =====================
if __name__ == "__main__":
    try:
        token = get_dingtalk_token()
        records = get_all_records(token)
        download_images(records)
    except Exception as e:
        print(f"\n❌ 错误：{e}")