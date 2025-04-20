# -- coding: utf-8 --
"""
Copyright (c) 2024 [Hosea]
Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import traceback
import undetected_chromedriver as uc

# 通过环境变量控制签到时是点击“试试手气”还是固定奖励，默认为 false (点击固定奖励)
ns_random_str = os.environ.get("NS_RANDOM", "false").lower()
ns_random = ns_random_str == "true"

# 通过环境变量获取Cookie
cookie = os.environ.get("NS_COOKIE") or os.environ.get("COOKIE")

# 通过环境变量控制是否使用无头模式，默认为 True（无头模式）
headless = os.environ.get("HEADLESS", "true").lower() == "true"


def click_sign_icon(driver):
    """
    尝试点击签到图标和后续按钮（试试手气或固定奖励）
    """
    try:
        print("开始查找签到图标...")
        # 使用 XPath 定位签到图标
        sign_icon = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//span[@title='签到']"))
        )
        print("找到签到图标，准备点击...")

        # 确保元素可见和可点击
        driver.execute_script("arguments[0].scrollIntoView(true);", sign_icon)
        time.sleep(0.5) # 短暂等待滚动完成

        # 打印元素信息用于调试
        # print(f"签到图标元素: {sign_icon.get_attribute('outerHTML')}")

        # 尝试点击
        try:
            sign_icon.click()
            print("签到图标点击成功")
        except Exception as click_error:
            print(f"直接点击失败，尝试使用 JavaScript 点击: {str(click_error)}")
            driver.execute_script("arguments[0].click();", sign_icon)
            print("JavaScript 点击签到图标成功")

        print("等待签到结果弹窗出现...")
        # 等待签到结果的弹窗或按钮出现，可以根据实际情况调整等待条件和时间
        # 这里假设点击签到图标后，会直接出现 "试试手气" 或 "鸡腿 x 5" 按钮
        time.sleep(5) # 给予页面反应时间，可以优化为等待特定元素

        # 打印当前URL和部分源码用于调试
        print(f"当前页面URL: {driver.current_url}")
        # print(f"当前页面源码片段: {driver.page_source[:500]}...")

        # 点击"试试手气"或"鸡腿 x 5"按钮
        try:
            print("开始查找签到奖励按钮...")
            button_xpath = ""
            if ns_random:
                button_xpath = "//button[contains(text(), '试试手气')]"
                print("配置为点击 '试试手气'")
            else:
                # 注意：固定奖励的文本可能会变，如果"鸡腿 x 5"不对，需要根据实际情况修改
                button_xpath = "//button[contains(text(), '鸡腿 x 5')]"
                print("配置为点击 '鸡腿 x 5'")

            click_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, button_xpath))
            )
            print(f"找到按钮: {click_button.text}，准备点击...")
            click_button.click()
            print("签到奖励按钮点击成功")
            print("签到完成！")
            return True

        except Exception as lucky_error:
            # 这里可能因为已经签到过，或者按钮文本不匹配等原因失败
            print(f"签到奖励按钮点击失败或已签到: {str(lucky_error)}")
            # 可以尝试检查页面是否有关闭按钮或者提示信息来确认签到状态
            # 例如，检查是否有关闭弹窗的按钮
            try:
                close_button = driver.find_element(By.XPATH, "//button[contains(text(), '关闭')] | //button[contains(@class,'close')] | //i[contains(@class,'close')]")
                print("找到关闭按钮，可能已经签到过了。")
                # close_button.click() # 如果需要关闭弹窗可以取消注释
                return True # 认为签到操作已处理（无论成功还是已签到）
            except:
                print("未找到关闭按钮，签到状态未知。")
                print("详细错误信息:")
                traceback.print_exc()
                return False # 明确表示签到后续步骤失败

    except Exception as e:
        print(f"签到过程中出错:")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        print(f"当前页面URL: {driver.current_url}")
        # print(f"当前页面源码片段: {driver.page_source[:500]}...") # 可以取消注释以获取更多调试信息
        print("详细错误信息:")
        traceback.print_exc()
        return False

def setup_driver_and_cookies():
    """
    初始化浏览器并设置cookie的通用方法
    返回: 设置好cookie的driver实例，或在失败时返回 None
    """
    global cookie # 确保使用的是全局变量 cookie
    if not cookie:
        print("错误：未在环境变量中找到 NS_COOKIE 或 COOKIE。")
        return None

    print("开始初始化浏览器...")
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    if headless:
        print("启用无头模式...")
        options.add_argument('--headless')
        # 添加以下参数来尝试绕过检测
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-gpu') # 在无头模式下通常需要
        options.add_argument('--window-size=1920,1080')
        # 设置一个常见的 User-Agent
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36')
    else:
         print("使用有头模式...")

    driver = None # 初始化 driver 变量
    try:
        print("正在启动Chrome...")
        driver = uc.Chrome(options=options)
        print("Chrome启动成功")

        if headless:
            # 在无头模式下执行 JavaScript 来修改 navigator.webdriver 属性
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print("正在访问 NodeSeek 以设置cookie...")
        # 访问一个简单的页面来设置 cookie，不一定是首页
        driver.get('https://www.nodeseek.com/signIn')
        print("等待页面加载 (5秒)...")
        time.sleep(5)

        print("正在设置cookie...")
        # 清除可能存在的旧cookie（可选，但有时有帮助）
        # driver.delete_all_cookies()
        cookie_dict_list = []
        for cookie_item in cookie.split(';'):
            cookie_item = cookie_item.strip()
            if '=' in cookie_item:
                try:
                    name, value = cookie_item.split('=', 1)
                    cookie_dict = {
                        'name': name,
                        'value': value,
                        'domain': '.nodeseek.com', # 确保域名正确
                        'path': '/',              # 通常是根路径
                        'secure': True,           # NodeSeek 使用 HTTPS，通常需要 secure
                        'httpOnly': True,         # 很多认证 cookie 是 httpOnly
                        'sameSite': 'Lax'         # 或 'None'，根据实际情况调整
                    }
                    # 尝试添加必要的属性，如果cookie字符串中没有
                    if name.lower() == 'session': # 示例： session cookie 通常是 httpOnly
                         cookie_dict['httpOnly'] = True
                    driver.add_cookie(cookie_dict)
                    cookie_dict_list.append(f"{name}=***") # 记录添加的cookie名称（隐藏值）
                except Exception as e:
                    print(f"  设置cookie '{cookie_item}' 时出错: {str(e)}")
            else:
                print(f"  跳过格式不正确的cookie片段: '{cookie_item}'")
        print(f"已尝试添加以下Cookies: {'; '.join(cookie_dict_list)}")

        print("刷新页面以应用cookie...")
        driver.refresh()
        print("等待页面刷新后加载 (5秒)...")
        time.sleep(5) # 等待cookie生效和页面加载

        # 简单验证是否登录成功 (可选)
        try:
            # 尝试查找登录后通常会存在的元素，例如用户头像或用户名区域
             WebDriverWait(driver, 10).until(
                 EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/notification']")) # 查找通知图标链接
             )
             print("Cookie 设置成功，看起来已登录。")
        except:
             print("警告：刷新后未能确认登录状态，请检查Cookie是否有效或过期。")
             # 可以选择在这里退出或继续尝试签到
             # driver.quit()
             # return None

        return driver

    except Exception as e:
        print(f"设置浏览器和Cookie时出错: {str(e)}")
        print("详细错误信息:")
        print(traceback.format_exc())
        if driver:
            driver.quit() # 如果 driver 已经创建，尝试关闭
        return None

if __name__ == "__main__":
    print("开始执行 NodeSeek 签到脚本...")
    driver = setup_driver_and_cookies()

    if driver:
        print("浏览器和Cookie设置完成，开始执行签到...")
        try:
            sign_in_successful = click_sign_icon(driver)
            if sign_in_successful:
                print("签到任务已处理。")
            else:
                print("签到任务处理失败或状态未知。")
        except Exception as main_err:
            print(f"执行签到过程中发生未捕获错误: {main_err}")
            traceback.print_exc()
        finally:
            print("关闭浏览器...")
            driver.quit()
            print("浏览器已关闭。")
    else:
        print("未能成功初始化浏览器或设置Cookie，脚本终止。")

    print("脚本执行完毕。")
