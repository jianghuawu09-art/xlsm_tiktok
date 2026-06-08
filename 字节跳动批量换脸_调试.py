import os
import sys
import base64
import urllib.request
import urllib.error
from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime.types.images.images import SequentialImageGenerationOptions
from volcenginesdkarkruntime._exceptions import ArkBadRequestError, ArkAPIConnectionError


def check_image_url(url: str, timeout: int = 10) -> bool:
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            print(f"URL 可访问: {url} -> HTTP {status}")
            return 200 <= status < 300
    except urllib.error.HTTPError as e:
        print(f"URL 返回错误: {url} -> HTTP {e.code} {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"URL 访问失败: {url} -> {e.reason}")
        return False
    except Exception as e:
        print(f"URL 检测异常: {url} -> {e}")
        return False


def save_base64_image(b64_data: str, output_path: str) -> None:
    data = base64.b64decode(b64_data)
    with open(output_path, "wb") as f:
        f.write(data)
    print(f"已保存图片: {output_path}")


def main() -> int:
    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        print("请先设置环境变量 ARK_API_KEY")
        return 1

    image_urls = [
        "https://img-reg-ab.imagency.cn/e/f904881a88072327e2815d4b5594338c.png",
        "https://img-reg-ab.imagency.cn/e/d5f94165fd984328af453f30f8d94821.png",
    ]

    print("检查输入图片 URL 是否可访问...")
    for url in image_urls:
        if not check_image_url(url):
            print("请换成可以被服务端直接下载的公开图片 URL。")
            return 2

    client = Ark(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=api_key,
    )

    try:
        response = client.images.generate(
            model="doubao-seedream-5-0-260128",
            prompt="保持原图人物姿势不变，进行人脸换脸，目标风格自然、真实、面部细节清晰。",
            image=image_urls,
            size="2K",
            output_format="png",
            response_format="base64",
            watermark=False,
            sequential_image_generation="auto",
            sequential_image_generation_options=SequentialImageGenerationOptions(max_images=2),
        )

        if not response.data:
            print("返回结果中没有图片数据，请检查请求参数。")
            return 3

        for idx, item in enumerate(response.data, start=1):
            if hasattr(item, "b64_json") and item.b64_json:
                save_base64_image(item.b64_json, f"换脸结果_{idx}.png")
            elif hasattr(item, "url") and item.url:
                print(f"返回了临时下载链接，请立即访问: {item.url}")
            else:
                print(f"第 {idx} 个结果没有可用的图片字段: {item}")

        return 0

    except ArkBadRequestError as e:
        print("请求参数错误或输入图像下载失败:")
        print(e)
        return 4
    except ArkAPIConnectionError as e:
        print("网络连接失败，请检查代理/网络/SSL:")
        print(e)
        return 5
    except Exception as e:
        print("未知异常:")
        print(e)
        return 6


if __name__ == "__main__":
    sys.exit(main())
