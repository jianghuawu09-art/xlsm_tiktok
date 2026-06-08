import os
from volcenginesdkarkruntime import Ark

client = Ark(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.getenv("ARK_API_KEY"),
)

image_urls = [
    "https://img-reg-ab.imagency.cn/e/55be9e53b289ff0978979f583b7ef92b.png",
    "https://img-reg-ab.imagency.cn/e/c04108b11f3d1558686a75bf197d3243.png",

]

result_urls = []

for idx, src_image in enumerate(image_urls, start=1):
    imagesResponse = client.images.generate(
        model="doubao-seedream-5-0-260128",
        prompt="保持模特姿势形状不变。图片高清高亮一点然后脸精致一点,人物自然一点",
        image=[src_image],
        size="4K",
        output_format="png",
        response_format="url",
        watermark=False,
    )

    # 如果每次只返回一张图，通常就是 data[0]
    for item in imagesResponse.data:
        result_urls.append(item.url)
        print(f"第 {idx} 张生成结果: {item.url}")

print("总共生成链接数量:", len(result_urls))