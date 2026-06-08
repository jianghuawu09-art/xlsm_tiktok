import os
import io
from PIL import Image, ImageSequence

# --- 用户配置 ---

# 1. 源图片文件夹路径
SOURCE_DIR = r"D:\人脸素材"

# 2. 处理后图片的保存路径
OUTPUT_DIR = r"D:\处理后的图片"

# 3. 支持的图片格式
SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.webp', '.gif')

# 4. 约束条件
MAX_FILE_SIZE_MB = 30  # 最大文件大小 (MB)
MIN_SIDE_LEN = 200    # 最小边长 (像素)
MAX_SIDE_LEN = 2048   # 最大边长 (像素)

# --- 脚本正文 ---

def process_image(source_path, output_path):
    """
    处理单个图片，根据尺寸和大小要求进行调整并保存。
    """
    try:
        # 打开图片
        img = Image.open(source_path)
        
        # 记录原始格式用于保存
        original_format = img.format
        
        # --- 步骤 1: 调整尺寸 ---
        w, h = img.size
        min_side = min(w, h)
        max_side = max(w, h)
        
        needs_resize = False
        # 检查是否需要缩小
        if max_side >= MAX_SIDE_LEN:
            needs_resize = True
            ratio = (MAX_SIDE_LEN - 1) / max_side
            w, h = int(w * ratio), int(h * ratio)
        # 检查是否需要放大
        elif min_side <= MIN_SIDE_LEN:
            needs_resize = True
            ratio = (MIN_SIDE_LEN + 1) / min_side
            w, h = int(w * ratio), int(h * ratio)
            # 放大后再次检查是否超出最大限制
            if max(w, h) >= MAX_SIDE_LEN:
                print(f"  [警告] 图片 '{os.path.basename(source_path)}' 调整后尺寸冲突，已跳过。")
                return

        # --- 步骤 2: 处理动图 (GIF) ---
        if original_format == 'GIF':
            frames = []
            duration = img.info.get('duration', 100)
            for frame in ImageSequence.Iterator(img):
                # 转换每一帧为 RGBA 以保持兼容性
                frame = frame.convert('RGBA')
                if needs_resize:
                    frame = frame.resize((w, h), Image.Resampling.LANCZOS)
                frames.append(frame)

            # 如果只有一帧，当作静态图处理
            if len(frames) <= 1:
                img = frames[0].convert("RGB") # 转为静态图
            else:
                # 直接保存动图，GIF压缩是另一回事，主要靠尺寸减小
                print(f"  正在处理动图: {os.path.basename(source_path)}")
                frames[0].save(output_path, save_all=True, append_images=frames[1:], duration=duration, loop=0, optimize=True)
                # 检查文件大小
                if os.path.getsize(output_path) / (1024 * 1024) > MAX_FILE_SIZE_MB:
                     print(f"  [警告] GIF '{os.path.basename(source_path)}' 压缩后仍 > {MAX_FILE_SIZE_MB}MB。")
                return # GIF处理完毕

        # 对于非GIF或单帧GIF，如果需要则执行缩放
        if needs_resize and original_format != 'GIF':
            img = img.resize((w, h), Image.Resampling.LANCZOS)

        # --- 步骤 3: 压缩大小 ---
        # 使用内存流进行尝试，避免多次写入磁盘
        buffer = io.BytesIO()
        
        # 准备保存参数
        save_params = {}
        img_format_to_save = original_format.upper()
        
        # 处理透明度，JPEG不支持
        if img_format_to_save in ['JPEG', 'JPG']:
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            save_params['quality'] = 95 # 初始质量
        elif img_format_to_save == 'PNG':
            save_params['optimize'] = True
        elif img_format_to_save == 'WEBP':
            save_params['quality'] = 95

        # 首次保存到内存
        img.save(buffer, format=original_format, **save_params)

        # 如果大小超标，循环降低质量 (仅对JPEG/WEBP有效)
        while buffer.tell() / (1024 * 1024) > MAX_FILE_SIZE_MB and save_params.get('quality', 0) > 10:
            print(f"  '{os.path.basename(source_path)}' 大小超标，尝试压缩...")
            save_params['quality'] -= 5
            buffer.seek(0)
            buffer.truncate(0)
            img.save(buffer, format=original_format, **save_params)
            print(f"    -> 质量: {save_params.get('quality', 'N/A')}, 大小: {buffer.tell() / (1024*1024):.2f}MB")

        # --- 步骤 4: 保存到文件 ---
        with open(output_path, 'wb') as f:
            f.write(buffer.getvalue())
        
        print(f"  处理完成 -> '{os.path.basename(output_path)}'")

    except Exception as e:
        print(f"  [错误] 处理图片 '{os.path.basename(source_path)}' 时发生错误: {e}")


def main():
    """
    主函数，遍历源文件夹并处理所有支持的图片。
    """
    print("--- 开始处理图片 ---")
    
    # 检查源目录是否存在
    if not os.path.isdir(SOURCE_DIR):
        print(f"[错误] 源文件夹 '{SOURCE_DIR}' 不存在。请检查路径。")
        return

    # 创建输出目录
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"创建输出文件夹: '{OUTPUT_DIR}'")

    # 遍历文件
    for filename in os.listdir(SOURCE_DIR):
        if filename.lower().endswith(SUPPORTED_FORMATS):
            source_path = os.path.join(SOURCE_DIR, filename)
            output_path = os.path.join(OUTPUT_DIR, filename)
            
            print(f"\n正在处理: {filename}")
            
            # 如果文件已存在且大小和尺寸符合，可选择跳过
            if os.path.exists(output_path):
                try:
                    existing_img = Image.open(output_path)
                    ex_w, ex_h = existing_img.size
                    ex_size = os.path.getsize(output_path) / (1024 * 1024)
                    if min(ex_w, ex_h) > MIN_SIDE_LEN and max(ex_w, ex_h) < MAX_SIDE_LEN and ex_size <= MAX_FILE_SIZE_MB:
                        print("  目标文件已存在且符合要求，跳过。")
                        continue
                except Exception:
                    pass # 如果目标文件损坏，则重新处理

            process_image(source_path, output_path)

    print("\n--- 所有图片处理完毕 ---")


if __name__ == "__main__":
    main()