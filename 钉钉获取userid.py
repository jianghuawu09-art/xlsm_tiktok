import requests

# 替换成你自己的凭证和手机号
APP_KEY = "机器人应用的 AppKey"
APP_SECRET = "机器人的密钥"
MOBILE = "13178567552"

# 1. 获取 access_token
token_url = f"https://oapi.dingtalk.com/gettoken?appkey={APP_KEY}&appsecret={APP_SECRET}"
token = requests.get(token_url).json()["access_token"]

# 2. 用手机号直接查 userid
url = f"https://oapi.dingtalk.com/user/get_by_mobile?access_token={token}&mobile={MOBILE}"
res = requests.get(url).json()

print("你的 userid =", res.get("userid"))