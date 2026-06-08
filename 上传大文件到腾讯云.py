from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging

# ---------------------- 你需要修改的配置 ----------------------
SecretId = "腾讯云密钥ID"       # 替换成你的腾讯云的密钥链接：https://console.cloud.tencent.com/cam/capi
SecretKey = "腾讯云密钥KEY"     # 替换成你的
Region = "区域"        # 替换成你的桶所在地域
Bucket = "janny-1434564519"    # 你的存储桶名称
# -------------------------------------------------------------

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

config = CosConfig(Region=Region, SecretId=SecretId, SecretKey=SecretKey)
client = CosS3Client(config)

def upload_file_and_get_url(local_file_path, cos_file_name):
    """
    上传文件到 COS，并返回访问链接
    :param local_file_path: 本地文件路径，如 "D:/test/压缩包.zip"
    :param cos_file_name: 上传后在桶里的文件名，如 "data/压缩包.zip"
    :return: 文件访问链接
    """
    print(f"正在上传：{local_file_path} → {cos_file_name}")

    # 上传文件
    response = client.upload_file(
        Bucket=Bucket,
        Key=cos_file_name,
        LocalFilePath=local_file_path,
        PartSize=10,
        MAXThread=10
    )

    if response.get('ETag'):
        print("上传成功！")
        # 生成文件访问链接（公有读权限桶可直接访问）
        url = client.get_object_url(
            Bucket=Bucket,
            Key=cos_file_name
        )
        print(f"文件链接：{url}")
        return url
    else:
        print("上传失败！")
        return None

# ------------------- 使用示例 -------------------
if __name__ == "__main__":
    # 示例：上传一个压缩包
    local_file = r"D:\要换人脸源图.zip"       # 你的本地文件路径
    cos_path = "archive/要换人脸源图.zip"        # 上传到桶里的路径（可自定义）

    upload_file_and_get_url(local_file, cos_path)