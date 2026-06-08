import http.client

conn = http.client.HTTPSConnection("ai.comfly.chat")
API_KEY = "comfly密钥地址"
payload = ''
headers = {
   'Authorization': f'Bearer {API_KEY}'
}
conn.request("GET", "/v1/models", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))