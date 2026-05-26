import http.client
import json

conn = http.client.HTTPSConnection("")
payload = json.dumps({
   "model": "gpt-4o-image",
   "stream": False,
   "messages": [
      {
         "role": "user",
         "content": "画只猫"
      }
   ]
})
headers = {
   'Accept': 'application/json',
   'Authorization': 'Bearer {{YOUR_API_KEY}}',
   'Content-Type': 'application/json'
}
conn.request("POST", "https://ai.comfly.org/v1/chat/completions", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
