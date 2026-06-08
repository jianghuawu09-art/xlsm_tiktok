import uiautomator2 as u2
from threading import Thread
from time import sleep, monotonic
import random
from text_content import text_content  # 导入文本内容
import requests
import datetime
import os
from volcenginesdkarkruntime import Ark
import time
 
# Get API Key：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey
client = Ark(api_key=os.environ.get("ARK_API_KEY"))

device_ids = [
    "192.168.100.134:5555",
    # "192.168.100.133:5555",
    # "192.168.100.188:5555",

]

BASE_WIDTH = 1080
BASE_HEIGHT = 2400

def click_scaled(d, x, y, base_width=BASE_WIDTH, base_height=BASE_HEIGHT):
    width, height = d.window_size()
    target_x = int(x / base_width * width)
    target_y = int(y / base_height * height)
    d.click(target_x, target_y)
    return target_x, target_y

def bright_screen(device_id):
    try:
        d = u2.connect(device_id)  # 这条指令不知道为什么底层会偷偷把屏幕点亮了
        if not d.info.get("screenOn", False):
            print(f"设备 {device_id} 屏幕状态当前是熄灭的，正在尝试点亮屏幕...")
            import os
            os.system("adb shell input keyevent KEYCODE_POWER")
            sleep(1)  # 等待1秒，确保屏幕点亮完成
            width, height = d.window_size()
            start_x, start_y = width // 2, int(height * 0.8)
            end_x, end_y = width // 2, int(height * 0.2)
            d.swipe(start_x, start_y, end_x, end_y, 0.2) # 0.2秒快速上滑

            serial_id = getattr(d, 'serial', '未知设备')
            print(f"设备 {serial_id} 屏幕已点亮并进行上滑动解锁")
        else:
            print(f"设备 {device_id} 屏幕状态当前是点亮的，正在上滑动解锁屏幕...")
            width, height = d.window_size()
            start_x, start_y = width // 2, int(height * 0.8)
            end_x, end_y = width // 2, int(height * 0.2)
            d.swipe(start_x, start_y, end_x, end_y, 0.2) # 0.2秒快速上滑

            serial_id = getattr(d, 'serial', '未知设备')
            print(f"设备 {serial_id} 屏幕已点亮并进行上滑动解锁")
            sleep(3)
    except Exception as exc:
        print(f"设备 {device_id} 屏幕点亮或滑动失败：{exc}")

def AI_link(device_id):
    print("----- create request -----")
    d = u2.connect(device_id)
    resp = client.content_generation.tasks.create(
        model="doubao-seedance-2-0-260128", # 国内大厂的 AI 视频大模型，现在的安全审核极其严格。如果审核不通过，您可以尝试调整输入文本的内容。
        content=[
            {
                "text": (
                    "(欧美风格) 一个年轻的女士，在展示下她的卷发，是在公园环境中展示的。"
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
        return  # 失败了就不继续往下走了
    
    # 视频链接 (将此处的 URL 替换成你要下载的实际视频链接)
    video_url = resp.content.video_url 

    # 1. 在电脑本地产生一个临时文件名（如：video_20260515_120000.mp4）
    temp_filename = f"temp_video_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    
    print(f"[{device_id}] 正在从网络下载视频到电脑: {temp_filename}")
    # 发送请求下载视频
    response = requests.get(video_url, stream=True)
    response.raise_for_status() # 确保请求成功

    # 将视频数据写入本地临时文件
    with open(temp_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    print(f"[{device_id}] 本地下载完成，准备推送到手机...")
    
    # 2. 将本地文件推送到手机相册目录 (DCIM/Camera 或者 Download 都可以)
    # 这里推送到手机的 /sdcard/DCIM/Camera/ 目录下，方便在相册中直接找到
    remote_path = f"/sdcard/DCIM/Camera/{temp_filename}"
    d.push(temp_filename, remote_path)
    
    print(f"[{device_id}] 视频已成功传输到手机相册: {remote_path}")
    
    # 3. 刷新手机媒体库，让相册立即识别到新视频
    import os
    os.system(f"adb -s {device_id} shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{remote_path}")
    print(f"[{device_id}] 手机相册已刷新")
    
    # 4. 清理电脑上的本地临时文件
    if os.path.exists(temp_filename):
        os.remove(temp_filename)
        print(f"[{device_id}] 电脑端临时文件已清理")

def start_app(device_id):
    try:
        d = u2.connect(device_id)
        print(f"设备 {device_id} 连接成功")
        d.app_start("com.zhiliaoapp.musically")
        print(f"设备 {device_id} TikTok应用启动成功！")
        sleep(7)  # 等待7秒，确保应用完全启动
        recommend = d.xpath("//*[@text='推荐']")
        if recommend.exists:
            print(f"设备 {device_id} 已进入推荐界面")
        else:
            print(f"设备 {device_id} 未能进入推荐界面")
    except Exception as exc:
        print(f"设备 {device_id} 连接失败：{exc}")

def publish_video(device_id):
    try:
        d = u2.connect(device_id)
        pub = d.xpath("//*[@resource-id='com.zhiliaoapp.musically:id/nfj']")
        if not pub.exists:
            print(f"设备 {device_id} 发布按钮不存在")
            return
        print(f"设备 {device_id} 发布按钮存在：{pub.exists}")
        pub.click()
        print("点击+号发布按钮成功")
        sleep(4)
        # 点击图片选择按钮
        image_button = d.xpath("//*[@resource-id='com.zhiliaoapp.musically:id/llw']")
        if image_button.exists:
            print(f"设备 {device_id} 识别到图片选择按钮，选择点击")
            image_button.click() 
            sleep(3)   
            print(f"设备 {device_id} 点击了图片选择按钮成功")
        else:    
            print(f"设备 {device_id} 图片选择按钮不存在")
            return
        
        video = d.xpath("//*[@text='视频']")
        if video.exists:
            video.click()
            sleep(2)
            print(f"设备 {device_id} 点击视频元素成功")
        else:
            print(f"设备 {device_id} 视频元素不存在")
            return

        one_video_element = d.xpath("//*[@resource-id='com.zhiliaoapp.musically:id/k5t']")
        if one_video_element.exists:
            one_video_element.click()
            sleep(3)
            print("选择第一条视频元素成功")
        else:
            print(f"设备 {device_id} 第一条视频元素不存在")
            return
        
        # 下一步按钮
        next_step = d.xpath("//*[@resource-id='com.zhiliaoapp.musically:id/w5c']")
        if next_step.exists:
            next_step.click()
            print("点击下一步按钮成功，并等待10秒，让视频加载完成")
            sleep(10)
        else:
            print(f"设备 {device_id} 下一步按钮不存在")
            return
        
        # 下一步按钮
        next_step2 = d.xpath("//*[@resource-id='com.zhiliaoapp.musically:id/os5']")
        if next_step2.exists:
            next_step2.click()
            sleep(5)
            print("点击下一步按钮成功，跳转到发布页面")
        else:
            print(f"设备 {device_id} 下一步按钮不存在")
            return
        
        # 输入视频描述
        text_description = d.xpath("//*[@resource-id='com.zhiliaoapp.musically:id/gkn']")
        if text_description.exists:
            # 将 text_content 按多行分割，过滤掉空白项，并去掉末尾的逗号和空格
            texts = [t.strip().strip(',') for t in text_content.split('\n') if t.strip()]
            random_text = random.choice(texts) if texts else text_content
            
            text_description.set_text(random_text)
            sleep(2)
            print(f"输入视频描述成功: {random_text}")
        else:
            print(f"设备 {device_id} 视频描述输入框不存在")

        # 发布视频
        publish = d.xpath("//*[@resource-id='com.zhiliaoapp.musically:id/rwx']")
        if publish.exists:
            publish.click()
            print("点击发布按钮成功，并且等待10秒，确保发布完成")
            sleep(10)
        else:
            print(f"设备 {device_id} 发布按钮不存在")
            return

    except Exception as exc:
        print(f"设备 {device_id} 发布失败：{exc}")
        return
    
# 这里是任务列表，后面如果要加功能，可以继续增加函数并放到这个列表里
task_functions = [
    bright_screen, # 亮屏幕并解锁屏幕
    AI_link, # 使用AI生成视频链接，下载AI生成的视频到手机相册
    start_app, # 启动TokTok应用
    publish_video, # 发布AI生成的视频到TokTok
]


def run_one_device(device_id, functions):
    for func in functions:
        func(device_id)
        

def run_tasks(functions, device_ids):
    threads = []
    for device_id in device_ids:
        t = Thread(target=run_one_device, args=(device_id, functions))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


if __name__ == "__main__":
    run_tasks(task_functions, device_ids)
