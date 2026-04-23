#!/usr/bin/env python3
"""测试获取活动笔记详情"""
from playwright.sync_api import sync_playwright
import time
import json

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://localhost:18800')
    
    for ctx in browser.contexts:
        for page in ctx.pages:
            if 'search_result' in page.url and 'openclaw' in page.url:
                # 获取所有近期活动笔记 URL
                notes = page.evaluate("""
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
                                const parent = a.closest('div');
                                const grandParent = parent ? parent.parentElement : null;
                                const contextText = grandParent ? grandParent.innerText : '';
                                const lines = contextText.split('\\n').filter(l => l.trim());
                                
                                // 只取前3条
                                if (results.length < 3) {
                                    results.push({
                                        url: href,
                                        context: lines.slice(0, 6).join(' | ')
                                    });
                                }
                            }
                        });
                        
                        return results;
                    }
                """)
                
                print(f"Found {len(notes)} notes")
                
                # 遍历每个笔记获取详情
                for i, note in enumerate(notes):
                    print(f"\\n{'='*60}")
                    print(f"Note {i+1}: {note['context'][:80]}")
                    print(f"URL: {note['url'][:80]}")
                    
                    note_page = ctx.new_page()
                    note_page.goto(note['url'], timeout=15000)
                    time.sleep(3)
                    
                    # 获取完整内容
                    content = note_page.evaluate("""
                        () => {
                            // 获取所有文本内容
                            const body = document.body.innerText;
                            
                            // 尝试找时间地点关键词
                            const text = body.toLowerCase();
                            let timeInfo = '';
                            let locationInfo = '';
                            
                            // 提取时间相关
                            const timePatterns = [
                                /\\d{1,2}[月年\\-.]\\d{1,2}[日号]?/g,
                                /\\d{1,2}:\\d{1,2}/g,
                                /今天|明天|后天|周日|周一|周二|周三|周四|周五|周六/g,
                                /上午|下午|晚上/g
                            ];
                            
                            // 提取地点相关
                            const locPatterns = [
                                /北京[^\\n]{0,30}/g,
                                /上海[^\\n]{0,30}/g,
                                /深圳[^\\n]{0,30}/g,
                                /地址[^\\n]{0,30}/g,
                                /地点[^\\n]{0,30}/g,
                                /北京市[^\\n]{0,50}/g
                            ];
                            
                            // 获取正文内容（排除页头页脚）
                            const nav = document.querySelector('header, nav, .nav, .header');
                            if (nav) nav.remove();
                            const footer = document.querySelector('footer, .footer');
                            if (footer) footer.remove();
                            
                            return {
                                fullText: body.substring(0, 5000),
                                title: document.title
                            };
                        }
                    """)
                    
                    print(f"Title: {content['title']}")
                    print("-" * 40)
                    print("Content:")
                    print(content['fullText'][:2000])
                    
                    note_page.close()
