from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging
import os
from pathlib import Path

# ---------------------- 你需要修改的配置 ----------------------
SecretId = "腾讯云SecretId"
SecretKey = "腾讯云SecretKey"
Region = "ap-guangzhou"
Bucket = "janny-1434564519"
# -------------------------------------------------------------

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

config = CosConfig(Region=Region, SecretId=SecretId, SecretKey=SecretKey)
client = CosS3Client(config)

def upload_single_image(local_file_path, cos_file_name):
    """
    上传单张图片到 COS
    :param local_file_path: 本地图片路径
    :param cos_file_name: 上传后在桶里的路径
    :return: 文件访问链接或None
    """
    try:
        # 上传文件
        response = client.upload_file(
            Bucket=Bucket,
            Key=cos_file_name,
            LocalFilePath=local_file_path,
            PartSize=10,
            MAXThread=10
        )
        
        if response.get('ETag'):
            # 生成文件访问链接
            url = client.get_object_url(
                Bucket=Bucket,
                Key=cos_file_name
            )
            return url
        else:
            return None
    except Exception as e:
        print(f"上传失败 {local_file_path}: {str(e)}")
        return None

def upload_all_images_from_folder(folder_path, cos_prefix="images"):
    """
    批量上传文件夹内的所有图片
    :param folder_path: 本地文件夹路径，如 "D:/钉钉表格图片"
    :param cos_prefix: COS中的目录前缀，如 "images" 或 "product_images"
    :return: 包含图片信息和链接的列表
    """
    # 支持的图片格式
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.ico', '.tiff', '.tif'}
    
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"错误：文件夹不存在 - {folder_path}")
        return []
    
    # 获取所有图片文件
    all_files = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        # 只处理文件，跳过文件夹
        if os.path.isfile(file_path):
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in image_extensions:
                all_files.append(file_path)
            else:
                print(f"跳过非图片文件: {file}")
    
    if not all_files:
        print(f"在 {folder_path} 中没有找到图片文件")
        return []
    
    print(f"找到 {len(all_files)} 张图片，开始上传...")
    
    # 存储上传结果
    upload_results = []
    success_count = 0
    fail_count = 0
    
    for idx, local_path in enumerate(all_files, 1):
        # 获取原始文件名
        file_name = os.path.basename(local_path)
        
        # 构建COS中的路径（保持原文件名，避免重名）
        cos_file_path = f"{cos_prefix}/{file_name}"
        
        print(f"[{idx}/{len(all_files)}] 正在上传: {file_name}")
        
        # 上传图片
        url = upload_single_image(local_path, cos_file_path)
        
        if url:
            success_count += 1
            result = {
                "local_path": local_path,
                "file_name": file_name,
                "cos_path": cos_file_path,
                "url": url
            }
            upload_results.append(result)
            print(f"  ✓ 上传成功: {url}")
        else:
            fail_count += 1
            result = {
                "local_path": local_path,
                "file_name": file_name,
                "cos_path": cos_file_path,
                "url": None,
                "error": "上传失败"
            }
            upload_results.append(result)
            print(f"  ✗ 上传失败")
    
    # 打印汇总信息
    print("\n" + "="*60)
    print(f"上传完成！")
    print(f"总计: {len(all_files)} 张图片")
    print(f"成功: {success_count} 张")
    print(f"失败: {fail_count} 张")
    print("="*60)
    
    return upload_results

def save_links_to_file(upload_results, output_file="image_links.txt"):
    """
    将所有图片链接保存到文本文件
    :param upload_results: 上传结果列表
    :param output_file: 输出文件名
    """
    if not upload_results:
        print("没有可保存的链接")
        return
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("图片链接列表\n")
            f.write("="*60 + "\n")
            f.write(f"生成时间: {__import__('datetime').datetime.now()}\n")
            f.write(f"总计: {len(upload_results)} 张图片\n")
            f.write("="*60 + "\n\n")
            
            for idx, result in enumerate(upload_results, 1):
                if result.get('url'):
                    f.write(f"{idx}. {result['file_name']}\n")
                    f.write(f"   本地路径: {result['local_path']}\n")
                    f.write(f"   COS路径: {result['cos_path']}\n")
                    f.write(f"   访问链接: {result['url']}\n\n")
                else:
                    f.write(f"{idx}. {result['file_name']} - 上传失败\n")
                    f.write(f"   错误: {result.get('error', '未知错误')}\n\n")
        
        print(f"链接列表已保存到: {output_file}")
    except Exception as e:
        print(f"保存链接文件失败: {str(e)}")

def get_all_image_urls(upload_results):
    """
    返回所有图片链接的列表（纯链接格式）
    :param upload_results: 上传结果列表
    :return: 图片链接列表
    """
    urls = []
    for result in upload_results:
        if result.get('url'):
            urls.append(result['url'])
    return urls

# ------------------- 使用示例 -------------------
if __name__ == "__main__":
    # 设置本地图片文件夹路径
    local_folder = r"D:\钉钉表格图片"
    
    # 设置COS中的目录前缀（可以根据需要修改）
    cos_folder_prefix = "product_images"  # 图片会传到 product_images/ 目录下
    
    # 批量上传所有图片
    results = upload_all_images_from_folder(local_folder, cos_folder_prefix)
    
    if results:
        
        # 方法3：如果需要导出为Markdown格式的图片链接
        print("\n" + "="*60)
        print("Markdown格式图片链接（可直接复制使用）：")
        for result in results:
            if result.get('url'):
                print(f"![{result['file_name']}]：{result['url']}")
        