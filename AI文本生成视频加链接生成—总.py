import os
from volcenginesdkarkruntime import Ark
import time
 
# Get API Key：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
client = Ark(api_key=os.environ.get("ARK_API_KEY"))

if __name__ == "__main__":
    print("----- create request -----")
    resp = client.content_generation.tasks.create(
        model="doubao-seedance-2-0-260128", # 国内大厂的 AI 视频大模型，现在的安全审核极其严格。如果审核不通过，您可以尝试调整输入文本的内容。
        content=[
            {
                "text": (
                    "（欧美油画风格）一位穿着风衣的欧洲长发女孩，在展示下她的卷发的给我给我看，镜头慢慢的展示头发的细节，阳光洒在她的头发上，她的头发是卷发"
                ),
                "type": "text"
            }
        ],
        generate_audio=True, # True 生成音频，False 不生成音频
        ratio="adaptive", # 根据输入自动选择最合适的宽高比。，也可以指定为 "16:9"、"4:3"、"1:1"、"3:4"、"21:9" 等
        duration=10, # 视频时长，单位：秒，最长可生成15秒。接口有限制
        watermark=False, # 是否添加水印，默认 False
    )
    
    # 打印创建成功后的任务 ID
    task_id = resp.id
    print(f"创建成功！任务 ID: {task_id}")
    time.sleep(10)  # 等待 10 秒，确保任务创建完成，然后再开始询问状态，否则可能会遇到刚创建就查询状态的情况，导致不必要的错误。

    print("\n----- 开始获取任务状态 -----")
    while True:
        resp = client.content_generation.tasks.get(
            task_id=task_id,
        )
        # 如果状态不是 running 和 queued，说明任务已经结束（成功/失败/被取消等）
        if resp.status not in ['running', 'queued']:
            break
        print(f"当前状态: {resp.status} (视频正在排队或生成中，继续等待...)")
        time.sleep(20)  # 每隔 20秒 重新询问一次服务器
        
    print("\n----- 任务结束，最终结果 -----")
    # 把返回对象以整齐的 JSON 格式打印出来，就像您在调试平台上看到的一样
    if hasattr(resp, "model_dump_json"):
        print(resp.model_dump_json(indent=2))
    elif hasattr(resp, "json"):
        print(resp.json(indent=2))
    else:
        print(resp)

    # 提取并单独打印直达视频的下载连接
    if resp.status == 'succeeded' and getattr(resp, "content", None) and resp.content.video_url:
        print("\n==================================")
        print("✨ 制作成功！")
        print("视频下载链接：\n" + resp.content.video_url)
        print("==================================")
    elif resp.status == 'failed':
        print("\n==================================")
        print("❌ 制作失败！")
        # 尝试提取并打印错误信息
        error_info = getattr(resp, "error", None)
        if error_info:
            print(f"失败原因：\n{error_info}")
        print("==================================")