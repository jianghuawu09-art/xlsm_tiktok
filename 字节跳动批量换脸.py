import os
# Install SDK:  pip install 'volcengine-python-sdk[ark]'
from volcenginesdkarkruntime import Ark 

client = Ark(
    # The base URL for model invocation
    base_url="https://visual.volcengineapi.com", 
    # Get API Key：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
    api_key=os.getenv('ARK_API_KEY'), 
)
 
imagesResponse = client.images.generate( 
    # Replace with Model ID
    model="doubao-seedream-5-0-260128", 
    prompt="保持模特姿势形状不变。将脸型换成其他人的",
    image="https://img-reg-ab.imagency.cn/e/72bd65f305dd65b93fbd3e623d2da3d6.jpg",
    size="2K",
    output_format="png",
    response_format="url",
    watermark=False
) 
 
print(imagesResponse.data[0].url)