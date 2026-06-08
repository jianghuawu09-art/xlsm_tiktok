import requests
import time
import os

# ================= 配置区域 =================
# 开发者凭证
APP_ID = 'cli_a9d599d43e79dbb3'
APP_SECRET = '569TDdigOlHaiozNoredSbaNFB1syhie'

# 飞书链接中的 token（因为链接变为了 /file/，所以这是文件的 token）
FILE_TOKEN = 'RECrbsTYKopQWdxk94kcBT9qn6e'

# 保存的文件名和路径（保存在当前目录下）
OUTPUT_FILE = r'D:\Users\user\Desktop\深圳亚马逊测评费用文件夹\深圳亚马逊测评费用测试-总.xls'
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

if __name__ == "__main__":
    try:
        token = get_tenant_access_token()
        download_drive_file(token, FILE_TOKEN, OUTPUT_FILE)
    except Exception as e:
        print(f"运行发生错误: {e}")
        print("\n【特别提醒】：如果是提示无权限，请确保：")
        print("1. 您的飞书应用已开通【查看、评论、下载和导出云空间所有文件】权限。")
        print("2. 必须在飞书文档的右上角「分享」->「添加协作者」中，把该应用添加进去并给与阅读权限！")