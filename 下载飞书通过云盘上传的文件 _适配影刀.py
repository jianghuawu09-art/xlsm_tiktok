# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv

# 此脚本作用：是用来下载飞书上面的文件：https://dcnhi15xk2zm.feishu.cn/file/RECrbsTYKopQWdxk94kcBT9qn6e
# 下载全部飞书文件到本地下来


# 此脚本需要安装requests模块
import requests
import time
import os

# ================= 解决影刀特有网络拦截问题 =================
# 强行清空环境变量中的代理，防止 requests 被影刀内部代理拦截导致网络报错
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
# ============================================================

# ================= 配置区域 =================
# 开发者凭证
APP_ID = 'cli_a9d599d43e79dbb3'
APP_SECRET = '569TDdigOlHaiozNoredSbaNFB1syhie'

# 飞书链接中的 token（因为链接变为了 /file/，所以这是文件的 token）
FILE_TOKEN = 'RECrbsTYKopQWdxk94kcBT9qn6e'

# 保存的文件名和路径（保存在当前目录下）
OUTPUT_FILE = r'D:\Users\user\Desktop\测试\飞书下载表格.xlsx'
# ============================================

def get_tenant_access_token():
    """获取飞书 tenant_access_token"""
    print("正在获取访问令牌 (Access Token)...")
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    response = requests.post(url, json=payload)
    data = response.json()
    
    if data.get("code") != 0:
        raise Exception(f"获取 Token 失败: {data}")
    
    return data.get("tenant_access_token")

def download_drive_file(access_token, file_token, output_path):
    """直接下载飞书云空间的文件（针对 /file/ 格式的真实文件）"""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    print("正在直接从飞书云空间下载文件到本地...")
    download_url = f"https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/download"
    download_res = requests.get(download_url, headers=headers)
    
    if download_res.status_code == 200:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(download_res.content)
        print(f"✅ 下载成功！文件已保存至: {output_path}")
    else:
        raise Exception(f"下载文件失败，HTTP状态码: {download_res.status_code}，报错信息: {download_res.text}")

def main(args):
    try:
        token = get_tenant_access_token()
        download_drive_file(token, FILE_TOKEN, OUTPUT_FILE)
    except Exception as e:
        print(f"运行发生错误: {e}")
        print("\n【特别提醒】：如果是提示无权限，请确保：")
        print("1. 您的飞书应用已开通【查看、评论、下载和导出云空间所有文件】权限。")
        print("2. 必须在飞书文档的右上角「分享」->「添加协作者」中，把该应用添加进去并给与阅读权限！")