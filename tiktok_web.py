from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def open_tiktok_upload():
    url = "https://www.tiktok.com/tiktokstudio/upload"
    print(f"正在启动浏览器并访问: {url}")
    
    # 启动浏览器
    
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True) # 核心：这个功能是运行完后，不随Python脚本结束而关闭
    driver = webdriver.Chrome(options=options)
    driver.delete_all_cookies() # Selenium 清缓存 / Cookie：删除所有Cookie
    driver.get(url)
    time.sleep(10)  # 稍微等待一下登录页面出现
    
    # 定位“使用手机号码/电子邮箱/用户名登录”区块并点击
    login_options = driver.find_elements(By.XPATH, "//div[@data-e2e='channel-item' and @role='link']//div[text()='使用手机号码/电子邮箱/用户名登录']")
    if login_options:
        login_options[0].click()
        print("成功点击了【使用手机号码/电子邮箱/用户名登录】！")
        time.sleep(random.uniform(1, 10))  # 随机等待1~10秒
    else:
        print("点击【使用手机号码/电子邮箱/用户名登录】失败: 未能找到该元素")
        
    
    # 点击使用密码登陆
    password_logins = driver.find_elements(By.XPATH, "//a[text()='使用密码登录']")
    if password_logins:
        password_logins[0].click()
        print("成功点击了【使用密码登录】！")
        time.sleep(random.uniform(1, 10))  # 随机等待1~10秒
    else:
        print("点击【使用密码登录】失败: 未能找到该元素")

    # 点击JP+81选择框 (已修复多余的 ']')
    jp81_elements = driver.find_elements(By.XPATH, "//div[@role='button' and @aria-controls='phone-country-code-selector-wrapper']")
    if jp81_elements:
        jp81_elements[0].click()
        print("成功点击了【JP+81】！")
        time.sleep(random.uniform(1, 10))  # 随机等待1~10秒
    else:
        print("点击【JP+81】失败: 未能找到该元素")
    
    # 寻找输入框并输入+86
    search_inputs = driver.find_elements(By.ID, "login-phone-search")
    if search_inputs:
        search_inputs[0].clear()  # 清空原有内容
        search_inputs[0].send_keys("+86")  # 输入国家码
        print("成功输入了国家码【+86】！")
        time.sleep(random.uniform(1, 10))  # 随机等待1~10秒
    else:
        print("搜索【+86】失败: 未能找到对应输入框")

    china_86 = driver.find_elements(By.XPATH, "//span[contains(text(),'China mainland') and contains(text(),'+86')]")
    if china_86:
        china_86[0].click()  # 点击选择中国+86
        print("成功选择了【中国+86】！")
        time.sleep(random.uniform(1, 10))  # 随机等待1~10秒
    else:
        print("选择【中国+86】失败: 未能找到对应输入框")

    # 前置页面操作完成，把这个浏览器实例“交出去”给外部使用
    return driver


def login_with_phone(driver, phone_number, password):
    """
    输入手机号、密码并点击登录
    :param driver: 当前浏览器实例
    :param phone_number: 手机号码
    :param password: 密码
    """
    print(f"正在准备输入账号信息...")
    
    # 手机号码输入框
    phone_input = driver.find_elements(By.XPATH, "//input[@name='mobile' and @placeholder='手机号码']")
    if phone_input:
        phone_input[0].send_keys(phone_number) # 输入手机号
        print("成功输入了手机号！")
        time.sleep(random.uniform(1, 10))  # 随机等待1~10秒
    else:
        print("未能找到手机号输入框！")
        return
    
    # 密码输入框
    password_input = driver.find_elements(By.XPATH, "//input[@type='password' and @autocomplete='new-password']")
    if password_input:
        password_input[0].send_keys(password) # 输入密码
        print("成功输入了密码！")
        time.sleep(random.uniform(1, 10))  # 随机等待1~10秒
    else:
        print("未能找到密码输入框！")
        return

    # 点击登录按钮
    login_button = driver.find_elements(By.XPATH, "//button[@type='submit']//span[text()='登录']")
    if login_button:
        login_button[0].click() 
        print("成功点击了【登录】！")
        time.sleep(random.uniform(1, 10))  # 随机等待1~10秒
    else:
        print("点击【登录】失败: 未能找到该元素")


if __name__ == "__main__":
    driver = open_tiktok_upload()
    login_with_phone(driver, "15306483224", "wjh19990309@")