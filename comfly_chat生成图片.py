import http.client
import json

conn = http.client.HTTPSConnection("ai.comfly.org")
# ====================== 只改这里 ======================
API_KEY = "sk-5j2cpAHhfHNpvD4X5uMSbXyC438b6foLqEV0zdxFL6296bDp"
# ======================================================

payload = json.dumps({
   "model": "gpt-image-1",
   "stream": False,
   "messages": [
      {"role": "user", "content": "给我生成一个机器人的图片"}
   ]
})
headers = {
   'Accept': 'application/json',
   'Authorization': f'Bearer {API_KEY}',
   'Content-Type': 'application/json'
}

conn.request("POST", "/v1/images/completions", payload, headers)  # 改这个接口
res = conn.getresponse()
data = json.loads(res.read().decode("utf-8"))

print("状态码:", res.status)
if res.status == 200:
    # 尝试提取图片 URL
    if 'data' in data and len(data['data']) > 0:
        print("图片链接:", data['data'][0].get('url'))
    else:
        print("完整返回:", json.dumps(data, indent=2, ensure_ascii=False))
else:
    print("错误:", json.dumps(data, indent=2, ensure_ascii=False))
