import requests

app_key = "dingyzwmwrqoumv2xyjb"
app_secret = "mh0WB_3cqnOI3znHRr7Yj1BD5MQjwr_rrFHTYZtaJAx-4J2oQavuRk-KwU8kddH3"

# 获取 access_token
r = requests.get("https://oapi.dingtalk.com/gettoken", params={
    "appkey": app_key,
    "appsecret": app_secret,
})
access_token = r.json().get("access_token")

# 调用按手机号查用户接口
url = "https://oapi.dingtalk.com/topapi/v2/user/getbymobile"
resp = requests.post(url, params={"access_token": access_token}, json={"mobile":"18470368336"})
print(resp.json())