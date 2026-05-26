import uiautomator2 as u2
from threading import Thread
from time import sleep, monotonic
import random
from text_content import text_content  # 导入文本内容

device_ids = [
    "192.168.100.134:5555",
    "192.168.100.133:5555",
    "192.168.100.188:5555",
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
            print(f"设备 {device_id} 屏幕状态当前是点亮的，不需要解锁屏幕")
            # width, height = d.window_size()
            # start_x, start_y = width // 2, int(height * 0.8)
            # end_x, end_y = width // 2, int(height * 0.2)
            # d.swipe(start_x, start_y, end_x, end_y, 0.2) # 0.2秒快速上滑

            # serial_id = getattr(d, 'serial', '未知设备')
            # print(f"设备 {serial_id} 屏幕已点亮并进行上滑动解锁")
            # sleep(3)
    except Exception as exc:
        print(f"设备 {device_id} 屏幕点亮或滑动失败：{exc}")

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

def random_swipe(d):
    width, height = d.window_size()
    # 随机生成上滑的起点和终点，模拟真实用户手指滑动（从下往上滑）
    start_x = random.randint(int(width * 0.4), int(width * 0.6))
    start_y = random.randint(int(height * 0.7), int(height * 0.85))
    end_x = random.randint(int(width * 0.4), int(width * 0.6))
    end_y = random.randint(int(height * 0.15), int(height * 0.3))
    # 随机滑动时长 0.1秒 到 0.7秒
    duration = random.uniform(0.1, 0.7)
    d.swipe(start_x, start_y, end_x, end_y, duration)

def watch_videos(device_id, duration_minutes=30):
    try:
        d = u2.connect(device_id)
        print(f"设备 {device_id} 连接成功，开始观看视频...随机停留20-160秒每个视频，持续约{duration_minutes}分钟")
        start_time = monotonic()
        while monotonic() - start_time < duration_minutes * 60:
            wait_time = random.uniform(10, 120)
            print(f"设备 {device_id} 正在观看视频，当前视频将停留 {wait_time:.2f} 秒...")
            sleep(wait_time)  # 随机停留10-120秒
            
            # 引入随机操作：例如有 10% 的概率对该视频进行点赞（双击屏幕）
            if random.random() < 0.1:  # 10% 的概率点赞
                # 存在❤️的点赞按钮时才进行点赞
                zang = d.xpath('//*[@resource-id="com.zhiliaoapp.musically:id/fmb"]')
                if zang.exists:
                    print(f"设备 {device_id} 识别到点赞按钮，准备点赞...")
                    width, height = d.window_size()
                    # 在屏幕中央附近随机找一个坐标进行双击
                    click_x = random.randint(int(width * 0.4), int(width * 0.6))
                    click_y = random.randint(int(height * 0.4), int(height * 0.6))
                    d.double_click(click_x, click_y)
                    print(f"设备 {device_id} 触发了随机双击操作(模拟点赞)！")
                    sleep(random.uniform(1, 4))  # 模拟点赞后稍微停留 1~4 秒再划走

            random_swipe(d)  # 随机向上滑动屏幕，模拟刷到下一个视频
            print(f"设备 {device_id} 模拟观看视频并刷到下一个...")
        print(f"设备 {device_id} 已完成观看视频任务，持续了约{duration_minutes}分钟")
    except Exception as exc:
        print(f"设备 {device_id} 发生错误：{exc}")

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

def home(device_id):
    try:
        d = u2.connect(device_id)
        print(f"设备 {device_id} 正在准备返回桌面并清理后台...")
        
        # 启动应用切换键，打开多任务后台界面
        d.press("recent")
        sleep(3)
        print(f"设备 {device_id} 已点击应用切换键，打开多任务后台界面")
    
        # 在多任务界面中，从屏幕中间向上滑动清理后台（基于坐标滑动避免不同手机UI元素不一致）
        width, height = d.window_size()
        start_x, start_y = width // 2, height // 2
        end_x, end_y = width // 2, int(height * 0.1)
        d.swipe(start_x, start_y, end_x, end_y, 0.2)
        sleep(2)
        print(f"设备 {device_id} 已从屏幕中间上滑清理后台")
     
    except Exception as exc:
        print(f"设备 {device_id} 返回桌面或清理后台失败：{exc}")

# 这里是任务列表，后面如果要加功能，可以继续增加函数并放到这个列表里
task_functions = [
    bright_screen, # 亮屏幕并解锁屏幕
    start_app, # 启动应用
    watch_videos, # 观看视频
    home, # 返回桌面并清理后台
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
