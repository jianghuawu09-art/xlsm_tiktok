import requests
import datetime
import uiautomator2 as u2

# 下载视频到手机相册
def donwnload_video(device_id, video_url):
    try:
        d = u2.connect(device_id)
        print(f"设备 {device_id} 连接成功，正在准备下载视频...")
        
        # 视频链接 (将此处的 URL 替换成你要下载的实际视频链接)
        video_url = "https://ark-acg-cn-beijing.tos-cn-beijing.volces.com/xxx.mp4" 
        
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
            
    except Exception as exc:
        print(f"设备 {device_id} 下载或推送视频失败：{exc}")