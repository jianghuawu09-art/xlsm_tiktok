import os

from volcenginesdkarkruntime import Ark

# For more information，please check this document（https://www.volcengine.com/docs/82379/1263279）
client = Ark(api_key=os.environ.get("ARK_API_KEY"))

if __name__ == "__main__":
    print("----- create request -----")
    resp = client.content_generation.tasks.create(
        model="doubao-seedance-1-0-pro-250528",
        content=[{"text":"360度环绕运镜","type":"text"},
                 {"image_url":{"url":"https://ark-project.tos-cn-beijing.volces.com/doc_image/seepro_first_frame.jpeg"},"role":"first_frame","type":"image_url"},
                 {"image_url":{"url":"https://ark-project.tos-cn-beijing.volces.com/doc_image/seepro_last_frame.jpeg"},"role":"last_frame","type":"image_url"}]
    )
    print(resp)