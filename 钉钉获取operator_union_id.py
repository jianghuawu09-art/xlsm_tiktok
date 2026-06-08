import requests

APP_KEY = "dingyzwmwrqoumv2xyjb"
APP_SECRET = "mh0WB_3cqnOI3znHRr7Yj1BD5MQjwr_rrFHTYZtaJAx-4J2oQavuRk-KwU8kddH3"
USERID = "17793502525297439"  # 你自己的，

# 1. 获取 access_token
token_url = f"https://oapi.dingtalk.com/gettoken?appkey={APP_KEY}&appsecret={APP_SECRET}"
token = requests.get(token_url).json()["access_token"]

# 2. 查用户详情，拿到 unionId
info_url = f"https://oapi.dingtalk.com/user/get?access_token={token}&userid={USERID}"
res = requests.get(info_url).json()

print("你的 unionId =", res.get("unionid")) 