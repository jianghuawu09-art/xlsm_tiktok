# 1、把运营提供的深圳亚马逊测评费用-Vanlov.xls文件进行读取
# 2、从文件夹中读取vanlov sheet的数据
# 3、把里面的A,C,D,E,F列的数据提取出来，保存到一个新的Excel文件中，命名为深圳亚马逊测试费用.xlsx


import pandas as pd
import os
from openpyxl.styles import Alignment, Border, Side

# 1. 定义源文件路径和目标文件路径
input_file = r"D:\Users\user\Desktop\深圳亚马逊测评费用文件夹\深圳亚马逊测评费用测试.xls"

# ================= 统一配置区域 =================
# 定义需要提取的月份（只要在这里修改一次，下面的所有函数都会用到这个月份）
TARGET_MONTH = 4
# ================================================

def vanlov_excel_data(writer):
    try:
        print(f"正在读取并处理 vanlov 的数据 ...")
        
        # 2. 读取数据
        # 指定读取的 sheet 名为 'vanlov'
        df = pd.read_excel(
            input_file, 
            sheet_name="vanlov", 
            usecols="A,C,D,E,F" # 或者使用 usecols=[0, 2, 3, 4, 5]
        )

        # ==================== 这里的作用是A列筛选日期，上面写几月份就只保留几月份的数据 ====================
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
        df = df[df.iloc[:, 0].dt.month == TARGET_MONTH].copy()
        
        # 按照日期（第一列）进行升序排列 (比如: 4月27日 -> 4月28日 -> 4月29日)
        df = df.sort_values(by=df.columns[0], ascending=True)
        # ==============================================================================================

        # 在新文件增加第6列（也就是 Excel 中的 F 列），F1 表头名为“退款方式”，所有的行值赋值为“Paypal”
        df["退款方式"] = "Paypal"

        # 格式化 A 列（在 DataFrame 中是第 0 列），转成真正的纯日期格式 date 对象，这样可以确保没有时间信息
        df.iloc[:, 0] = df.iloc[:, 0].dt.date

        # 使用外层传入的 writer 写入指定的 sheet_name
        df.to_excel(writer, index=False, sheet_name='vanlov')
        
        # 获取刚刚写入的工作表对象
        worksheet = writer.sheets['vanlov']
        
        # 创建居中对齐对象
        center_alignment = Alignment(horizontal='center', vertical='center')
        
        # 创建全边框对象（细线）
        thin_border = Border(
            left=Side(style='thin'), 
            right=Side(style='thin'), 
            top=Side(style='thin'), 
            bottom=Side(style='thin')
        )
        
        # 遍历所有列，将列宽设置为 23，并设置所有单元格文字居中及添加边框
        for col in worksheet.columns:
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = 23
            for cell in col:
                cell.alignment = center_alignment
                cell.border = thin_border
                # 强行指定 A 列的显示格式为纯日期
                if col_letter == 'A':
                    cell.number_format = 'yyyy-mm-dd'
        
        print("vanlov 处理完成！✅")

    except Exception as e:
        print(f"vanlov 发生错误: {e}")

def BeaufoxUk_excel_data(writer):
    try:
        print(f"正在读取并处理 Beaufox英国的数据 ...")
        
        # 2. 读取数据
        # 指定读取的 sheet 名为 'Beaufox英国'
        df = pd.read_excel(
            input_file, 
            sheet_name="Beaufox英国", 
            usecols="A,C,D,E,F" # 或者使用 usecols=[0, 2, 3, 4, 5]
        )

        # ==================== 这里的作用是A列筛选日期，上面写几月份就只保留几月份的数据 ====================
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
        df = df[df.iloc[:, 0].dt.month == TARGET_MONTH].copy()
        
        # 按照日期（第一列）进行升序排列 (比如: 4月27日 -> 4月28日 -> 4月29日)
        df = df.sort_values(by=df.columns[0], ascending=True)
        # ==============================================================================================

        # 在新文件增加第6列（也就是 Excel 中的 F 列），F1 表头名为“退款方式”，所有的行值赋值为“Paypal”
        df["退款方式"] = "Paypal"

        # 格式化 A 列（在 DataFrame 中是第 0 列），转成真正的纯日期格式 date 对象，这样可以确保没有时间信息
        df.iloc[:, 0] = df.iloc[:, 0].dt.date

        # 使用外层传入的 writer 写入指定的 sheet_name
        df.to_excel(writer, index=False, sheet_name='Beaufox英国')
        
        # 获取刚刚写入的工作表对象
        worksheet = writer.sheets['Beaufox英国']
        
        # 创建居中对齐对象
        center_alignment = Alignment(horizontal='center', vertical='center')
        
        # 创建全边框对象（细线）
        thin_border = Border(
            left=Side(style='thin'), 
            right=Side(style='thin'), 
            top=Side(style='thin'), 
            bottom=Side(style='thin')
        )
        
        # 遍历所有列，将列宽设置为 23，并设置所有单元格文字居中及添加边框
        for col in worksheet.columns:
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = 23
            for cell in col:
                cell.alignment = center_alignment
                cell.border = thin_border
                # 强行指定 A 列的显示格式为纯日期
                if col_letter == 'A':
                    cell.number_format = 'yyyy-mm-dd'
        
        print("Beaufox英国数据 处理完成！✅")

    except Exception as e:
        print(f"Beaufox英国数据 发生错误: {e}")

def BeaufoxFR_excel_data(writer):
    try:
        print(f"正在读取并处理 Beaufox法国的数据 ...")
        
        # 2. 读取数据
        # 指定读取的 sheet 名为 'BeaufoxFR'
        df = pd.read_excel(
            input_file, 
            sheet_name="Beaufox法国", 
            usecols="A,C,D,E,F" # 或者使用 usecols=[0, 2, 3, 4, 5]
        )

        # ==================== 这里的作用是A列筛选日期，上面写几月份就只保留几月份的数据 ====================
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
        df = df[df.iloc[:, 0].dt.month == TARGET_MONTH].copy()
        
        # 按照日期（第一列）进行升序排列 (比如: 4月27日 -> 4月28日 -> 4月29日)
        df = df.sort_values(by=df.columns[0], ascending=True)
        # ==============================================================================================

        # 在新文件增加第6列（也就是 Excel 中的 F 列），F1 表头名为“退款方式”，所有的行值赋值为“Paypal”
        df["退款方式"] = "Paypal"

        # 格式化 A 列（在 DataFrame 中是第 0 列），转成真正的纯日期格式 date 对象，这样可以确保没有时间信息
        df.iloc[:, 0] = df.iloc[:, 0].dt.date

        # 使用外层传入的 writer 写入指定的 sheet_name
        df.to_excel(writer, index=False, sheet_name='Beaufox法国')
        
        # 获取刚刚写入的工作表对象
        worksheet = writer.sheets['Beaufox法国']
        
        # 创建居中对齐对象
        center_alignment = Alignment(horizontal='center', vertical='center')
        
        # 创建全边框对象（细线）
        thin_border = Border(
            left=Side(style='thin'), 
            right=Side(style='thin'), 
            top=Side(style='thin'), 
            bottom=Side(style='thin')
        )
        
        # 遍历所有列，将列宽设置为 23，并设置所有单元格文字居中及添加边框
        for col in worksheet.columns:
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = 23
            for cell in col:
                cell.alignment = center_alignment
                cell.border = thin_border
                # 强行指定 A 列的显示格式为纯日期
                if col_letter == 'A':
                    cell.number_format = 'yyyy-mm-dd'
        
        print("Beaufox法国数据 处理完成！✅")

    except Exception as e:
        print(f"Beaufox法国 发生错误: {e}")

def Ayisha_excel_data(writer):
    try:
        print(f"正在读取并处理 Ayisha 的数据 ...")
        
        # 2. 读取数据
        # 指定读取的 sheet 名为 'Ayisha'
        df = pd.read_excel(
            input_file, 
            sheet_name="Ayisha", 
            usecols="A,C,D,E,F" # 或者使用 usecols=[0, 2, 3, 4, 5]
        )

        # ==================== 这里的作用是A列筛选日期，上面写几月份就只保留几月份的数据 ====================
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
        df = df[df.iloc[:, 0].dt.month == TARGET_MONTH].copy()
        
        # 按照日期（第一列）进行升序排列 (比如: 4月27日 -> 4月28日 -> 4月29日)
        df = df.sort_values(by=df.columns[0], ascending=True)
        # ==============================================================================================

        # 在新文件增加第6列（也就是 Excel 中的 F 列），F1 表头名为“退款方式”，所有的行值赋值为“Paypal”
        df["退款方式"] = "Paypal"

        # 格式化 A 列（在 DataFrame 中是第 0 列），转成真正的纯日期格式 date 对象，这样可以确保没有时间信息
        df.iloc[:, 0] = df.iloc[:, 0].dt.date

        # 使用外层传入的 writer 写入指定的 sheet_name
        df.to_excel(writer, index=False, sheet_name='Ayisha')
        
        # 获取刚刚写入的工作表对象
        worksheet = writer.sheets['Ayisha']
        
        # 创建居中对齐对象
        center_alignment = Alignment(horizontal='center', vertical='center')
        
        # 创建全边框对象（细线）
        thin_border = Border(
            left=Side(style='thin'), 
            right=Side(style='thin'), 
            top=Side(style='thin'), 
            bottom=Side(style='thin')
        )
        
        # 遍历所有列，将列宽设置为 23，并设置所有单元格文字居中及添加边框
        for col in worksheet.columns:
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = 23
            for cell in col:
                cell.alignment = center_alignment
                cell.border = thin_border
                # 强行指定 A 列的显示格式为纯日期
                if col_letter == 'A':
                    cell.number_format = 'yyyy-mm-dd'
        
        print("Ayisha 处理完成！✅")

    except Exception as e:
        print(f"Ayisha 发生错误: {e}")

def Taziza_excel_data(writer):
    try:
        print(f"正在读取并处理 Taziza英国的数据 ...")
        
        # 2. 读取数据
        # 指定读取的 sheet 名为 'Taziza'
        df = pd.read_excel(
            input_file, 
            sheet_name="Taziza英国", 
            usecols="A,C,D,E,F" # 或者使用 usecols=[0, 2, 3, 4, 5]
        )

        # ==================== 这里的作用是A列筛选日期，上面写几月份就只保留几月份的数据 ====================
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
        df = df[df.iloc[:, 0].dt.month == TARGET_MONTH].copy()
        
        # 按照日期（第一列）进行升序排列 (比如: 4月27日 -> 4月28日 -> 4月29日)
        df = df.sort_values(by=df.columns[0], ascending=True)
        # ==============================================================================================

        # 在新文件增加第6列（也就是 Excel 中的 F 列），F1 表头名为“退款方式”，所有的行值赋值为“Paypal”
        df["退款方式"] = "Paypal"

        # 格式化 A 列（在 DataFrame 中是第 0 列），转成真正的纯日期格式 date 对象，这样可以确保没有时间信息
        df.iloc[:, 0] = df.iloc[:, 0].dt.date

        # 使用外层传入的 writer 写入指定的 sheet_name
        df.to_excel(writer, index=False, sheet_name='Taziza英国')
        
        # 获取刚刚写入的工作表对象
        worksheet = writer.sheets['Taziza英国']
        
        # 创建居中对齐对象
        center_alignment = Alignment(horizontal='center', vertical='center')
        
        # 创建全边框对象（细线）
        thin_border = Border(
            left=Side(style='thin'), 
            right=Side(style='thin'), 
            top=Side(style='thin'), 
            bottom=Side(style='thin')
        )
        
        # 遍历所有列，将列宽设置为 23，并设置所有单元格文字居中及添加边框
        for col in worksheet.columns:
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = 23
            for cell in col:
                cell.alignment = center_alignment
                cell.border = thin_border
                # 强行指定 A 列的显示格式为纯日期
                if col_letter == 'A':
                    cell.number_format = 'yyyy-mm-dd'
        
        print("Taziza英国数据 处理完成！✅")

    except Exception as e:
        print(f"Taziza英国 发生错误: {e}")

def Elluipoey_excel_data(writer):
    try:
        print(f"正在读取并处理 Elluipoey的数据 ...")
        
        # 2. 读取数据
        # 指定读取的 sheet 名为 'Elluipoey'
        df = pd.read_excel(
            input_file, 
            sheet_name="Elluipoey", 
            usecols="A,C,D,E,F" # 或者使用 usecols=[0, 2, 3, 4, 5]
        )

        # ==================== 这里的作用是A列筛选日期，上面写几月份就只保留几月份的数据 ====================
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
        df = df[df.iloc[:, 0].dt.month == TARGET_MONTH].copy()
        
        # 按照日期（第一列）进行升序排列 (比如: 4月27日 -> 4月28日 -> 4月29日)
        df = df.sort_values(by=df.columns[0], ascending=True)
        # ==============================================================================================

        # 在新文件增加第6列（也就是 Excel 中的 F 列），F1 表头名为“退款方式”，所有的行值赋值为“Paypal”
        df["退款方式"] = "Paypal"

        # 格式化 A 列（在 DataFrame 中是第 0 列），转成真正的纯日期格式 date 对象，这样可以确保没有时间信息
        df.iloc[:, 0] = df.iloc[:, 0].dt.date

        # 使用外层传入的 writer 写入指定的 sheet_name
        df.to_excel(writer, index=False, sheet_name='Elluipoey')
        
        # 获取刚刚写入的工作表对象
        worksheet = writer.sheets['Elluipoey']
        
        # 创建居中对齐对象
        center_alignment = Alignment(horizontal='center', vertical='center')
        
        # 创建全边框对象（细线）
        thin_border = Border(
            left=Side(style='thin'), 
            right=Side(style='thin'), 
            top=Side(style='thin'), 
            bottom=Side(style='thin')
        )
        
        # 遍历所有列，将列宽设置为 23，并设置所有单元格文字居中及添加边框
        for col in worksheet.columns:
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = 23
            for cell in col:
                cell.alignment = center_alignment
                cell.border = thin_border
                # 强行指定 A 列的显示格式为纯日期
                if col_letter == 'A':
                    cell.number_format = 'yyyy-mm-dd'
        
        print("Elluipoey数据 处理完成！✅")

    except Exception as e:
        print(f"Elluipoey 发生错误: {e}")

def Vipobody_excel_data(writer):
    try:
        print(f"正在读取并处理 Vipobody的数据 ...")
        
        # 2. 读取数据
        # 指定读取的 sheet 名为 'Vipobody'
        df = pd.read_excel(
            input_file, 
            sheet_name="Vipobody", 
            usecols="A,C,D,E,F" # 或者使用 usecols=[0, 2, 3, 4, 5]
        )

        # ==================== 这里的作用是A列筛选日期，上面写几月份就只保留几月份的数据 ====================
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
        df = df[df.iloc[:, 0].dt.month == TARGET_MONTH].copy()
        
        # 按照日期（第一列）进行升序排列 (比如: 4月27日 -> 4月28日 -> 4月29日)
        df = df.sort_values(by=df.columns[0], ascending=True)
        # ==============================================================================================

        # 在新文件增加第6列（也就是 Excel 中的 F 列），F1 表头名为“退款方式”，所有的行值赋值为“Paypal”
        df["退款方式"] = "Paypal"

        # 格式化 A 列（在 DataFrame 中是第 0 列），转成真正的纯日期格式 date 对象，这样可以确保没有时间信息
        df.iloc[:, 0] = df.iloc[:, 0].dt.date

        # 使用外层传入的 writer 写入指定的 sheet_name
        df.to_excel(writer, index=False, sheet_name='Vipobody')
        
        # 获取刚刚写入的工作表对象
        worksheet = writer.sheets['Vipobody']
        
        # 创建居中对齐对象
        center_alignment = Alignment(horizontal='center', vertical='center')
        
        # 创建全边框对象（细线）
        thin_border = Border(
            left=Side(style='thin'), 
            right=Side(style='thin'), 
            top=Side(style='thin'), 
            bottom=Side(style='thin')
        )
        
        # 遍历所有列，将列宽设置为 23，并设置所有单元格文字居中及添加边框
        for col in worksheet.columns:
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = 23
            for cell in col:
                cell.alignment = center_alignment
                cell.border = thin_border
                # 强行指定 A 列的显示格式为纯日期
                if col_letter == 'A':
                    cell.number_format = 'yyyy-mm-dd'
        
        print("Vipobody数据 处理完成！✅")

    except Exception as e:
        print(f"Vipobody 发生错误: {e}")

def vvig_excel_data(writer):
    try:
        print(f"正在读取并处理 vvig的数据 ...")
        
        # 2. 读取数据
        # 指定读取的 sheet 名为 '飞迎'
        df = pd.read_excel(
            input_file, 
            sheet_name="飞迎", 
            usecols="A,C,D,E,F" # 或者使用 usecols=[0, 2, 3, 4, 5]
        )

        # ==================== 这里的作用是A列筛选日期，上面写几月份就只保留几月份的数据 ====================
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
        df = df[df.iloc[:, 0].dt.month == TARGET_MONTH].copy()
        
        # 按照日期（第一列）进行升序排列 (比如: 4月27日 -> 4月28日 -> 4月29日)
        df = df.sort_values(by=df.columns[0], ascending=True)
        # ==============================================================================================

        # 在新文件增加第6列（也就是 Excel 中的 F 列），F1 表头名为“退款方式”，所有的行值赋值为“Paypal”
        df["退款方式"] = "Paypal"

        # 格式化 A 列（在 DataFrame 中是第 0 列），转成真正的纯日期格式 date 对象，这样可以确保没有时间信息
        df.iloc[:, 0] = df.iloc[:, 0].dt.date

        # 使用外层传入的 writer 写入指定的 sheet_name
        df.to_excel(writer, index=False, sheet_name='飞迎')
        
        # 获取刚刚写入的工作表对象
        worksheet = writer.sheets['飞迎']
        
        # 创建居中对齐对象
        center_alignment = Alignment(horizontal='center', vertical='center')
        
        # 创建全边框对象（细线）
        thin_border = Border(
            left=Side(style='thin'), 
            right=Side(style='thin'), 
            top=Side(style='thin'), 
            bottom=Side(style='thin')
        )
        
        # 遍历所有列，将列宽设置为 23，并设置所有单元格文字居中及添加边框
        for col in worksheet.columns:
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = 23
            for cell in col:
                cell.alignment = center_alignment
                cell.border = thin_border
                # 强行指定 A 列的显示格式为纯日期
                if col_letter == 'A':
                    cell.number_format = 'yyyy-mm-dd'
        
        print("飞迎数据 处理完成！✅")
    except Exception as e:
        print(f"飞迎 发生错误: {e}")

def bangyun_excel_data(writer):
    try:
        print(f"正在读取并处理 bangyun的数据 ...")
        
        # 2. 读取数据
        # 指定读取的 sheet 名为 '邦韵'
        df = pd.read_excel(
            input_file, 
            sheet_name="邦韵", 
            usecols="A,C,D,E,F" # 或者使用 usecols=[0, 2, 3, 4, 5]
        )

        # ==================== 这里的作用是A列筛选日期，上面写几月份就只保留几月份的数据 ====================
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], errors='coerce')
        df = df[df.iloc[:, 0].dt.month == TARGET_MONTH].copy()
        
        # 按照日期（第一列）进行升序排列 (比如: 4月27日 -> 4月28日 -> 4月29日)
        df = df.sort_values(by=df.columns[0], ascending=True)
        # ==============================================================================================

        # 在新文件增加第6列（也就是 Excel 中的 F 列），F1 表头名为“退款方式”，所有的行值赋值为“Paypal”
        df["退款方式"] = "Paypal"

        # 格式化 A 列（在 DataFrame 中是第 0 列），转成真正的纯日期格式 date 对象，这样可以确保没有时间信息
        df.iloc[:, 0] = df.iloc[:, 0].dt.date

        # 使用外层传入的 writer 写入指定的 sheet_name
        df.to_excel(writer, index=False, sheet_name='邦韵')
        
        # 获取刚刚写入的工作表对象
        worksheet = writer.sheets['邦韵']
        
        # 创建居中对齐对象
        center_alignment = Alignment(horizontal='center', vertical='center')
        
        # 创建全边框对象（细线）
        thin_border = Border(
            left=Side(style='thin'), 
            right=Side(style='thin'), 
            top=Side(style='thin'), 
            bottom=Side(style='thin')
        )
        
        # 遍历所有列，将列宽设置为 23，并设置所有单元格文字居中及添加边框
        for col in worksheet.columns:
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = 23
            for cell in col:
                cell.alignment = center_alignment
                cell.border = thin_border
                # 强行指定 A 列的显示格式为纯日期
                if col_letter == 'A':
                    cell.number_format = 'yyyy-mm-dd'
        
        print("邦韵数据 处理完成！✅")
    except Exception as e:
        print(f"邦韵 发生错误: {e}")

if __name__ == "__main__":
    target_folder = r"D:\Users\user\Desktop\测试"
    os.makedirs(target_folder, exist_ok=True)
    
    # 统一定义生成的一个最终文件路径
    output_file = os.path.join(target_folder, "深圳亚马逊测试费用提取结果.xlsx")
    
    try:
        # 在最外层只创建一个 ExcelWriter
        with pd.ExcelWriter(output_file, engine='openpyxl', datetime_format='YYYY-MM-DD') as writer:
            # 把这个 writer 传给你写的两个函数，让它们往同一个本子里分别写这两页
            vanlov_excel_data(writer)  # 这个是vanlov数据
            # Ayisha_excel_data(writer)  # 这个是Ayisha数据
            # BeaufoxUk_excel_data(writer) # 这个是Beaufox英国数据
            # BeaufoxFR_excel_data(writer) # 这个是Beaufox法国数据
            # Taziza_excel_data(writer) # 这个是Taziza英国数据
            # Elluipoey_excel_data(writer) # 这个是Elluipoey数据
            # Vipobody_excel_data(writer) # 这个是Vipobody数据
            # vvig_excel_data(writer) # 这个是飞迎数据
            # bangyun_excel_data(writer) # 这个是邦韵数据

        print(f"\n🎉 恭喜！所有 Sheet 页已成功合并至同一个表格中！\n文件路径: {output_file}")
    except PermissionError:
        print(f"❌ 保存失败：权限被拒绝！\n原因：文件【{output_file}】正在被打开。\n解决办法：请先关闭该 Excel 文件，然后重新运行此脚本。")
    except Exception as e:
        print(f"合并写入发生错误: {e}")