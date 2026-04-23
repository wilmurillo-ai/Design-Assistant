#!/usr/bin/env python3
"""测试获取笔记详情"""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://localhost:18800')
    
    for ctx in browser.contexts:
        for page in ctx.pages:
            if 'search_result' in page.url and 'openclaw' in page.url:
                # 获取第一个笔记 URL
                note_url = page.evaluate("""
                    () => {
                        const links = document.querySelectorAll("a[href*='/search_result/']");
                        return links.length > 0 ? links[0].href : null;
                    }
                """)
                
                if note_url:
                    print(f"Opening: {note_url[:80]}")
                    
                    # 在新标签页打开
                    note_page = ctx.new_page()
                    note_page.goto(note_url, timeout=15000)
                    time.sleep(3)
                    
                    print(f"URL: {note_page.url}")
                    print(f"Title: {note_page.title()}")
                    
                    # 获取正文内容
                    main_content = note_page.evaluate("""
                        () => {
                            const selectors = [
                                ".note-content",
                                ".content",
                                "article",
                                "[class*='content']"
                            ];
                            
                            for (let sel of selectors) {
                                const el = document.querySelector(sel);
                                if (el && el.innerText.length > 100) {
                                    return el.innerText.substring(0, 3000);
                                }
                            }
                            
                            // 获取所有文本，排除导航
                            const nav = document.querySelector('nav, header, .nav, .header');
                            if (nav) nav.remove();
                            return document.body.innerText.substring(0, 3000);
                        }
                    """)
                    
                    print("=" * 50)
                    print("NOTE CONTENT:")
                    print("=" * 50)
                    print(main_content)
                    
                    note_page.close()
