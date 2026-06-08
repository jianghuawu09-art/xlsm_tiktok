import os
# Install SDK:  pip install 'volcengine-python-sdk[ark]'
from volcenginesdkarkruntime import Ark 
from volcenginesdkarkruntime.types.images.images import SequentialImageGenerationOptions

client = Ark(
    # The base URL for model invocation
    base_url="https://ark.cn-beijing.volces.com/api/v3", 
    # Get API Key：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
    api_key=os.getenv('ARK_API_KEY'), 
) 
imagesResponse = client.images.generate( 
    # Replace with Model ID
    model="doubao-seedream-5-0-260128",
    prompt="把图1、图2、图3的服装换成图4的服装，并生成三张图片。",
    image=[
        "https://img-reg-ab.imagency.cn/e/fc1a6e2defcf2c6cddeb40a2df1de63a.jpg",
        "https://img-reg-ab.imagency.cn/e/6f100ed0b52f05d5562de86e59c72715.jpg",
        "https://img-reg-ab.imagency.cn/e/e60b492cdf9214f836d3e97bc713db58.jpg",
        "https://img-reg-ab.imagency.cn/e/f444a920d7e9a3862a2740d8fc608fbe.png", # 目标图
    ],
    size="2K",
    sequential_image_generation="auto",
    sequential_image_generation_options=SequentialImageGenerationOptions(max_images=3),
    output_format="png",
    response_format="url",
    watermark=False
) 


# Iterate through all image data
for image in imagesResponse.data:
    # Output the current image's URL and size
    print(f"URL: {image.url}, Size: {image.size}")



# 还未完成