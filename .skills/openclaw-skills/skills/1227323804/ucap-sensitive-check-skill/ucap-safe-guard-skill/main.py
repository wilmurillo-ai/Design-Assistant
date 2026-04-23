import requests
import json
import re
from urllib.parse import urlparse
import ipaddress
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


# ====================
# 安全配置：SSRF 防护机制
# ====================

# 阻止的内网 IP 段标识
PRIVATE_KEYWORDS = {
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '::1',
}


def is_private_ip(hostname: str) -> bool:
    """
    检查主机名是否为内网 IP
    :param hostname: 主机名
    :return: 是内网 IP 返回 True
    """
    if not hostname:
        return False

    hostname_lower = hostname.lower()

    # 检查常见内网标识
    if hostname_lower in PRIVATE_KEYWORDS:
        return True

    # 检查是否包含内网关键词
    for keyword in PRIVATE_KEYWORDS:
        if keyword in hostname_lower:
            return True

    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
    except ValueError:
        # 不是 IP 地址，返回 False
        pass

    return False


def validate_url_security(url: str) -> tuple:
    """
    验证 URL 是否符合安全要求（仅阻止内网地址）
    :param url: 待验证的 URL
    :return: (是否安全, 错误信息)
    """
    if not url:
        return False, "URL 不能为空"

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname

        if not hostname:
            return False, "无法解析域名"

        # 检查是否为内网 IP
        if is_private_ip(hostname):
            return False, f"不允许访问内网地址: {hostname}"

        return True, ""

    except Exception as e:
        return False, f"URL 解析错误: {str(e)}"


def is_url(text: str) -> bool:
    """
    判断输入文本是否为有效的 URL
    :param text: 待判断的文本
    :return: 是 URL 返回 True，否则返回 False
    """
    if not text or not isinstance(text, str):
        return False

    text = text.strip()

    # 简单的 URL 格式判断
    url_pattern = re.compile(
        r'^(https?:\/\/)?'  # http:// 或 https://（可选）
        r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'  # 域名
        r'(\/[^\s]*)?$'  # 路径（可选）
    )

    return bool(url_pattern.match(text))


def fetch_url_content(url: str, wait_time: int = 5) -> dict:
    """
    使用 Selenium 获取 URL 指定的网页内容（支持动态渲染页面）
    安全限制：阻止访问内网地址
    :param url: 目标网址
    :param wait_time: 等待页面加载的时间（秒），默认5秒
    :return: 包含状态码和内容的字典
    """
    # 确保URL带有协议前缀
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # ========== 安全验证：SSRF 防护检查 ==========
    is_safe, error_msg = validate_url_security(url)
    if not is_safe:
        return {"code": -100, "message": error_msg, "data": None}
    # ============================================

    driver = None
    try:
        # 配置 Chrome 选项
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 无头模式，不显示浏览器窗口
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--window-size=1920,1080')

        # 初始化 WebDriver（使用 webdriver-manager 自动管理 ChromeDriver 版本）
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # 访问目标网页
        driver.set_page_load_timeout(30)
        driver.get(url)

        # 等待页面加载完成（等待 body 元素出现）
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # 额外等待，确保动态内容加载完成
        import time
        time.sleep(wait_time)

        # 获取页面内容
        content = driver.page_source
        final_url = driver.current_url

        return {
            "code": 0,
            "message": "获取成功",
            "data": {
                "content": content,
                "url": final_url,
                "title": driver.title
            }
        }

    except TimeoutException:
        return {"code": -101, "message": f"访问超时：无法在30秒内加载页面（{url}）", "data": None}
    except WebDriverException as e:
        error_msg = str(e)
        if "net::ERR_NAME_NOT_RESOLVED" in error_msg or "Could not resolve host" in error_msg:
            return {"code": -102, "message": f"连接失败：无法解析域名，请检查网址是否正确（{url}）", "data": None}
        elif "ERR_CONNECTION" in error_msg or "Failed to establish connection" in error_msg:
            return {"code": -102, "message": f"连接失败：无法访问 {url}，请检查网络连接或网址是否正确", "data": None}
        elif "chromedriver" in error_msg.lower() or "chrome" in error_msg.lower():
            return {"code": -103, "message": f"浏览器驱动错误：{error_msg}。请确保已安装 Chrome 浏览器", "data": None}
        else:
            return {"code": -104, "message": f"访问失败：{error_msg}（{url}）", "data": None}
    except Exception as e:
        return {"code": -104, "message": f"未知错误：{str(e)}（{url}）", "data": None}
    finally:
        # 确保关闭浏览器
        if driver is not None:
            try:
                driver.quit()
            except:
                pass


def check_sensitive(content: str, userKey: str = None, sensitive_code_list: list = None) -> dict:
    """
    错敏信息检测核心函数
    :param content: 待检测文本内容（必传）
    :param userKey: 接口调用密钥（可选，接口支持空值）
    :param sensitive_code_list: 检测类型列表（可选，不传则不携带该参数）
    :return: 标准化检测结果
    """
    # 1. 入参校验 - 文本不能为空
    if not content:
        return {"code": -1, "message": "待检测文本不能为空", "data": None}

    # 2. 构造请求参数（userKey放在请求头中，可选）
    request_data = {"content": content}
    if sensitive_code_list is not None and len(sensitive_code_list) > 0:
        request_data["sensitiveCodeList"] = sensitive_code_list

    # 3. 调用 UCAP 预发环境接口
    try:
        url = "https://safeguard-pre.ucap.com.cn/safe-apiinterface/open/skill/skillSensitiveCheck"
        headers = {"Content-Type": "application/json"}
        if userKey:
            headers["userKey"] = userKey

        # SSL 验证：默认启用，确保通信安全
        response = requests.post(
            url=url,
            headers=headers,
            json=request_data,
            timeout=15,
            verify=True
        )
        response.raise_for_status()

        # 4. 标准化返回结果
        return {
            "code": 0,
            "message": "检测成功",
            "data": response.json()
        }

    # 异常处理
    except requests.exceptions.SSLError as e:
        return {
            "code": -8,
            "message": f"SSL 证书验证失败：{str(e)}",
            "data": None
        }
    except requests.exceptions.Timeout:
        return {"code": -3, "message": "接口调用超时（15秒）", "data": None}
    except requests.exceptions.HTTPError as e:
        return {"code": -4, "message": f"接口返回错误：{str(e)}",
                "data": response.text if 'response' in locals() else None}
    except requests.exceptions.ConnectionError as e:
        return {"code": -5, "message": f"网络连接失败：{str(e)}", "data": None}
    except requests.exceptions.RequestException as e:
        return {"code": -6, "message": f"接口调用失败：{str(e)}", "data": None}
    except json.JSONDecodeError:
        return {"code": -7, "message": "接口返回非 JSON 格式数据",
                "data": response.text if 'response' in locals() else None}


# OpenClaw 标准入口函数
def run(params: dict) -> dict:
    """
    OpenClaw 对话调用的标准入口
    :param params: OpenClaw 传入的参数字典
    :return: 检测结果
    """
    content = params.get("content", "")

    # 判断输入是 URL 还是文本
    if is_url(content):
        # 是 URL，先获取网页内容
        fetch_result = fetch_url_content(content)

        # 如果获取失败，直接返回错误信息
        if fetch_result["code"] != 0:
            return fetch_result

        # 获取成功，用网页内容进行检测
        actual_content = fetch_result["data"]["content"]
        source_url = fetch_result["data"]["url"]

        # 进行检测
        check_result = check_sensitive(
            content=actual_content,
            userKey=params.get("userKey"),
            sensitive_code_list=params.get("sensitive_code_list")
        )

        # 在检测结果中添加来源URL信息
        if check_result.get("code") == 0:
            check_result["source_url"] = source_url
            check_result["source_type"] = "url"

        return check_result
    else:
        # 是普通文本，直接检测
        check_result = check_sensitive(
            content=content,
            userKey=params.get("userKey"),
            sensitive_code_list=params.get("sensitive_code_list")
        )

        # 标记来源类型
        if check_result.get("code") == 0:
            check_result["source_type"] = "text"

        return check_result


# 本地测试代码
if __name__ == "__main__":
    # 测试1：URL抓取测试
    print("=" * 50)
    print("测试1：URL 抓取（爬虫测试）")
    print("=" * 50)
    test_result1 = fetch_url_content("https://example.com")
    print(json.dumps(test_result1, ensure_ascii=False, indent=2))

    # 测试2：通过 run() 函数检测 URL
    print("\n" + "=" * 50)
    print("测试2：通过 run() 检测 URL")
    print("=" * 50)
    test_result2 = run({
        "content": "https://example.com",
        "userKey": "your_user_key_here"  # 请替换为实际 userKey
    })
    print(json.dumps(test_result2, ensure_ascii=False, indent=2))

    # 测试3：直接检测文本
    print("\n" + "=" * 50)
    print("测试3：直接检测文本")
    print("=" * 50)
    test_result3 = run({
        "content": "这是一段待检测的文本内容",
        "userKey": "your_user_key_here"  # 请替换为实际 userKey
    })
    print(json.dumps(test_result3, ensure_ascii=False, indent=2))
