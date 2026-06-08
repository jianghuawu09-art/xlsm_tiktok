import os

from volcenginesdkarkruntime import Ark

# For more information，please check this document（https://www.volcengine.com/docs/82379/1263279）
client = Ark(api_key=os.environ.get("ARK_API_KEY"))

if __name__ == "__main__":
    print("----- create request -----")
    resp = client.content_generation.tasks.create(
        model="doubao-seedance-2-0-260128",
        content=[{"text":"女孩抱着狐狸，女孩睁开眼，温柔地看向镜头，狐狸友善地抱着，镜头缓缓拉出，女孩的头发被风吹动，可以听到风声","type":"text"},
                 {"image_url":{"url":"https://ark-project.tos-cn-beijing.volces.com/doc_image/i2v_foxrgirl.png"},"type":"image_url"}]
    )
    print(resp)