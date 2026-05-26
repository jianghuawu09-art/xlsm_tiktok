# 以下是视觉理解，多图输入
import os
from volcenginesdkarkruntime import Ark
import base64

# For more information，please check this document（https://www.volcengine.com/docs/82379/1263279）
client = Ark(api_key=os.environ.get("ARK_API_KEY"))


if __name__ == "__main__":
    # 1. 设置你的本地图片路径（把截图放在同一目录下）
    local_image_path = "test.jpg" 
    
    # 2. 读取图片并转换为 base64 格式
    with open(local_image_path, "rb") as image_file:
        base64_data = base64.b64encode(image_file.read()).decode("utf-8")
        # 拼接成 API 能识别的 base64 URL 协议
        local_image_url = f"data:image/jpeg;base64,{base64_data}"

    # 3. 发送请求，把 url 替换成咱们拼好的 local_image_url
    resp = client.chat.completions.create(
        model="doubao-seed-2-0-pro-260215", # 如果运行报错，请务必把这里改成控制台里“豆包-视觉模型”的 EndpointID (ep-xxx)
        messages=[{"content":[{"image_url":{"url": local_image_url},"type":"image_url"},{"text":"图片主要讲了什么?并且写一条夸赞的英文简短评论","type":"text"}],"role":"user"}],
    )
        
    # 深度思考模型，且触发了深度思考，打印思维链内容
    if hasattr(resp.choices[0].message, 'reasoning_content'):
        print(resp.choices[0].message.reasoning_content)
        
    print(resp.choices[0].message.content)