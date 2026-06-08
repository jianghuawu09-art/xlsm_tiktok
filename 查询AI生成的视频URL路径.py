import os

from volcenginesdkarkruntime import Ark

# For more information，please check this document（https://www.volcengine.com/docs/82379/1263279）
client = Ark(api_key=os.environ.get("ARK_API_KEY"))

import time

if __name__ == "__main__":
    print("----- 开始获取任务状态 -----")
    task_id = "cgt-20260515154908-bd2ks"
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