import os
# Install SDK:  pip install 'volcengine-python-sdk[ark]'
from volcenginesdkarkruntime import Ark 

client = Ark(
    # The base URL for model invocation
    base_url="https://ark.cn-beijing.volces.com/api/v3", 
    # Get API Key：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
    api_key=os.getenv('ARK_API_KEY'), 
) 
imagesResponse = client.images.generate( 
    # Replace with Model ID
    model="doubao-seedream-5-0-260128",
    prompt="将图1的服装换为图2的服装",
    image=["https://img-reg-ab.imagency.cn/e/e60b492cdf9214f836d3e97bc713db58.jpg", "https://img-reg-ab.imagency.cn/e/f444a920d7e9a3862a2740d8fc608fbe.png"],
    size="2K",
    sequential_image_generation="disabled",
    output_format="png",
    response_format="url",
    watermark=False
) 
print("图片链接生成中...")
print("图片链接生成成功："+imagesResponse.data[0].url)