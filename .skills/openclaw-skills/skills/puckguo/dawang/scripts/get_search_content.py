#!/usr/bin/env python3
"""从搜索页面提取完整笔记信息"""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://localhost:18800')
    
    for ctx in browser.contexts:
        for page in ctx.pages:
            if 'search_result' in page.url and 'openclaw' in page.url:
                print('Found search page')
                page.wait_for_selector('.search-layout', timeout=10000)
                time.sleep(1)
                
                # 获取所有笔记
                result = page.evaluate("""
                    () => {
                        const results = [];
                        const seenUrls = new Set();
                        const searchLayout = document.querySelector('.search-layout');
                        if (!searchLayout) return [];
                        
                        const allLinks = searchLayout.querySelectorAll('a[href]');
                        
                        allLinks.forEach(a => {
                            const href = a.href;
                            if (href.includes('/search_result/') && !seenUrls.has(href)) {
                                seenUrls.add(href);
                                
                                let container = a.closest('div');
                                while (container && container.parentElement !== searchLayout) {
                                    container = container.parentElement;
                                }
                                
                                if (container) {
                                    const text = container.innerText;
                                    results.push({
                                        url: href,
                                        context: text.substring(0, 500)
                                    });
                                }
                            }
                        });
                        
                        return results;
                    }
                """)
                
                print(f'Found {len(result)} notes')
                for r in result[:5]:
                    print('\n---')
                    print(r['context'][:400])
                break
