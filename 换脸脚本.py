import webbrowser
import time

URL = "https://pixnova.ai/ai-face-swap/"


def open_site(url: str = URL, new: int = 2):
    """使用系统默认浏览器打开指定 URL。
    - `new=2` 表示在新标签页中打开（如支持）。
    """
    print(f"正在使用系统默认浏览器打开: {url}")
    webbrowser.open(url, new=new)
    print("已发出打开浏览器请求。")
    time.sleep(5)  # 等待浏览器响应


def up_image_face():

    try:
        driver.get(URL)
        time.sleep(2)
        xpath = "//span[text()='click to upload']/parent::button"
        try:
            btn = driver.find_element(By.XPATH, xpath)
            btn.click()
            print("已点击目标按钮：", xpath)
        except Exception as e:
            print("未找到或点击元素失败：", e)

        input("操作完成，按回车关闭浏览器...")
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    open_site()
    up_image_face()