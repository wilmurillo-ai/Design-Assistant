#!/usr/bin/env python3
"""
Dynamic Web Fetch - 支持 JavaScript 动态加载的网页抓取工具
使用 Playwright 无头浏览器获取完全渲染的页面内容

用法:
    # JSON 模式
    echo '{"url": "https://example.com", "wait_seconds": 5}' | python3 fetch.py
    
    # 命令行模式
    python3 fetch.py https://example.com text 5
"""

import sys
import json
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print(json.dumps({
        "success": False,
        "error": "Playwright 未安装，请运行：pip install playwright && playwright install chromium"
    }))
    sys.exit(1)


def fetch_page(url: str, format: str = "markdown", wait_seconds: int = 3, 
               wait_selector: str = None, screenshot: str = None, 
               user_agent: str = None, timeout: int = 30000) -> dict:
    """
    抓取网页内容
    
    Args:
        url: 目标 URL
        format: 输出格式 (markdown/text/html)
        wait_seconds: 等待时间（秒）
        wait_selector: 等待的 CSS 选择器
        screenshot: 截图保存路径
        user_agent: 自定义 User-Agent
        timeout: 页面加载超时时间（毫秒）
    
    Returns:
        dict: 包含抓取结果的字典
    """
    
    default_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    try:
        with sync_playwright() as p:
            # 启动浏览器
            browser = p.chromium.launch(headless=True)
            
            # 创建上下文
            context = browser.new_context(
                user_agent=user_agent or default_ua,
                viewport={"width": 1920, "height": 1080}
            )
            
            page = context.new_page()
            
            # 访问页面 - 使用 DOMContentLoaded 加快加载
            page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            
            # 等待指定时间让 JavaScript 执行
            if wait_seconds > 0:
                page.wait_for_timeout(wait_seconds * 1000)
            
            # 等待特定元素（如果指定）
            if wait_selector:
                try:
                    page.wait_for_selector(wait_selector, timeout=5000)
                except Exception:
                    pass  # 元素未找到，继续执行
            
            # 截图（如果指定）
            if screenshot:
                page.screenshot(path=screenshot, full_page=True)
            
            # 获取页面内容
            title = page.title()
            
            if format == "html":
                content = page.content()
            elif format == "text":
                content = page.inner_text("body")
            else:  # markdown
                html = page.inner_text("body")
                content = html_to_markdown(html)
            
            browser.close()
            
            return {
                "success": True,
                "url": url,
                "title": title,
                "format": format,
                "content": content[:50000],  # 限制长度
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url
        }


def html_to_markdown(html: str) -> str:
    """简单 HTML 转 Markdown"""
    lines = html.strip().split('\n')
    markdown_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            markdown_lines.append(line)
    
    return '\n\n'.join(markdown_lines[:500])


def main():
    """主函数"""
    
    if len(sys.argv) > 1:
        # 命令行模式
        url = sys.argv[1]
        format = sys.argv[2] if len(sys.argv) > 2 else "markdown"
        wait_seconds = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        
        result = fetch_page(url, format, wait_seconds)
    else:
        # JSON 模式
        try:
            input_data = json.loads(sys.stdin.read())
            url = input_data.get("url")
            format = input_data.get("format", "markdown")
            wait_seconds = input_data.get("wait_seconds", 3)
            wait_selector = input_data.get("wait_selector")
            screenshot = input_data.get("screenshot")
            user_agent = input_data.get("user_agent")
            timeout = input_data.get("timeout", 30000)
            
            if not url:
                print(json.dumps({"success": False, "error": "缺少 url 参数"}))
                return
            
            result = fetch_page(url, format, wait_seconds, wait_selector, screenshot, user_agent, timeout)
        except json.JSONDecodeError:
            print(json.dumps({"success": False, "error": "无效的 JSON 输入"}))
            return
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
