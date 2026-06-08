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

# 飞书链接中的 token（即 sheets/ 后面的那一串字符）
SHEET_TOKEN = 'Kidcs1rThhvBNntRctacCfZBnNh'

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

def export_and_download_sheet(access_token, sheet_token, output_path):
    """创建导出任务并下载"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    # 1. 创建导出任务
    print("正在向飞书服务器发送创建导出任务请求...")
    export_url = "https://open.feishu.cn/open-apis/drive/v1/export_tasks"
    export_payload = {
        "file_extension": "xlsx",
        "token": sheet_token,
        "type": "sheet"
    }
    export_res = requests.post(export_url, headers=headers, json=export_payload).json()
    
    if export_res.get("code") != 0:
        raise Exception(f"创建导出任务失败: {export_res.get('msg')}")
        
    ticket = export_res["data"]["ticket"]
    print(f"导出任务已创建，Ticket: {ticket}")

    # 2. 轮询查询导出任务状态
    query_url = f"https://open.feishu.cn/open-apis/drive/v1/export_tasks/{ticket}?token={sheet_token}"
    file_token = None
    
    while True:
        time.sleep(2) # 每隔2秒查询一次
        query_res = requests.get(query_url, headers=headers).json()
        
        if query_res.get("code") != 0:
            raise Exception(f"查询任务失败: {query_res}")
            
        status = query_res["data"]["result"]["job_status"]
        
        # job_status 状态说明：0: 成功，1: 初始化，2: 处理中，3: 失败
        if status == 0:
            file_token = query_res["data"]["result"]["file_token"]
            print("文件导出成功，准备下载...")
            break
        elif status in [1, 2]:
            print("🚀 飞书服务器正在处理导出，请稍候...")
        else:
            raise Exception(f"导出失败，状态码: {status}，报错信息: {query_res}")

    # 3. 下载已导出的文件
    print("正在下载文件到本地...")
    download_url = f"https://open.feishu.cn/open-apis/drive/v1/export_tasks/file/{file_token}/download"
    download_res = requests.get(download_url, headers=headers)
    
    if download_res.status_code == 200:
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(download_res.content)
        print(f"✅ 下载成功！文件已保存至: {output_path}")
    else:
        raise Exception(f"下载文件失败，HTTP状态码: {download_res.status_code}")

def main(args):
    try:
        token = get_tenant_access_token()
        export_and_download_sheet(token, SHEET_TOKEN, OUTPUT_FILE)
    except Exception as e:
        print(f"运行发生错误: {e}")
        print("\n【特别提醒】：如果是提示无权限（找不到文档等），请确保：")
        print("1. 您的飞书应用已开通【查看、评论、导出和下载云空间中所有文件】等云文档权限。")
        print("2. 必须在飞书文档的右上角「分享」->「添加协作者」中，把该应用添加进去并给与阅读权限！")