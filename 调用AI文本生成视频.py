import os
from volcenginesdkarkruntime import Ark
 
# Get API Key：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
client = Ark(api_key=os.environ.get("ARK_API_KEY"))

if __name__ == "__main__":
    print("----- create request -----")
    resp = client.content_generation.tasks.create(
        model="doubao-seedance-2-0-260128", # 国内大厂的 AI 视频大模型，现在的安全审核极其严格。如果审核不通过，您可以尝试调整输入文本的内容。
        content=[
            {
                "text": (
                    "一位优雅的年轻女士，正在公园里散步，阳光洒在她的头发上，她的头发是卷发，然后慢慢的展示头发的细节"
                ),
                "type": "text"
            }
        ],
        generate_audio=True, # True 生成音频，False 不生成音频
        ratio="adaptive", # 根据输入自动选择最合适的宽高比。，也可以指定为 "16:9"、"4:3"、"1:1"、"3:4"、"21:9" 等
        duration=5, # 视频时长，单位：秒，最长可生成15秒。接口有限制
        watermark=False, # 是否添加水印，默认 False
    )
    
    print(resp)