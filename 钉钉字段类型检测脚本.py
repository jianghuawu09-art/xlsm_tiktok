import requests
import json

# ========== 配置（直接用你现有） ==========
DT_CLIENT_ID = 'dingyzwmwrqoumv2xyjb'
DT_CLIENT_SECRET = 'mh0WB_3cqnOI3znHRr7Yj1BD5MQjwr_rrFHTYZtaJAx-4J2oQavuRk-KwU8kddH3'
BASE_ID = '4lgGw3P8vRLPeRmXsp40mBj285daZ90D'
SHEET_ID = 'hERWDMS'
OPERATOR_ID = "fADzjBkYl9VEvxiPwAKrF2QiEiE"   # 重点：你的 unionId
TEST_RECORD_ID = '7Gtfo83ZWU'
# ==========================================

def get_token():
    url = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
    r = requests.post(url, json={"appKey": DT_CLIENT_ID, "appSecret": DT_CLIENT_SECRET})
    print("=== Token 返回 ===")
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    return r.json().get("accessToken")

def get_fields(token):
    # 接口必须带 operatorId（query 参数）
    url = (
        f"https://api.dingtalk.com/v1.0/notable/bases/{BASE_ID}/sheets/{SHEET_ID}/fields"
        f"?operatorId={OPERATOR_ID}"
    )
    headers = {
        "x-acs-dingtalk-access-token": token,
        "Content-Type": "application/json"
    }
    r = requests.get(url, headers=headers)
    print("\n=== 字段列表接口（带 operatorId）===")
    print("状态码:", r.status_code)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))

def get_one_record(token, rid):
    # 同样：operatorId 放 query
    url = (
        f"https://api.dingtalk.com/v1.0/notable/bases/{BASE_ID}/sheets/{SHEET_ID}/records/{rid}"
        f"?operatorId={OPERATOR_ID}"
    )
    headers = {
        "x-acs-dingtalk-access-token": token,
        "Content-Type": "application/json"
    }
    r = requests.get(url, headers=headers)
    print("\n=== 单条记录详情（重点看「转链接」结构）===")
    print("状态码:", r.status_code)
    data = r.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    token = get_token()
    if not token:
        print("❌ Token 获取失败")
    else:
        get_fields(token)         # 查看字段类型（richText/url/text）
        get_one_record(token, TEST_RECORD_ID)  # 查看「转链接」真实结构