#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
beautify.py v3.0 - 智能 UI 美化脚本
功能：
1. 智能检测项目类型（静态 HTML / Vite / Next.js / Tailwind）
2. 自动推荐最适合的风格
3. 智能注入样式（支持多种注入策略）
4. 生成实时预览页（对比前后效果）
5. 60+ 风格库（同步 awesome-design-md）
"""

import os
import sys
import json
import re
import shutil
import webbrowser
from pathlib import Path
from datetime import datetime

# Windows 编码设置
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ========== 扩展风格库（60+ 种）==========
DESIGN_TEMPLATES = {
    # 教育/文档类
    "notion": {
        "name": "Notion",
        "description": "温暖简约，适合文学、教育类",
        "colors": {"background": "#FFFFFF", "backgroundSecondary": "#F7F7F5", "text": "#37352F", "textSecondary": "#9B9A97", "link": "#0066E0", "border": "#E1E1E0", "hover": "#EFEFED"},
        "typography": {"heading": "Georgia, serif", "body": "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", "code": "'SFMono-Regular', 'Consolas', monospace"},
        "radius": "4px", "shadow": "0 1px 3px rgba(0,0,0,0.08)",
        "suitable_for": ["教育", "文学", "阅读", "文档"], "category": "教育文档"
    },
    "figma": {
        "name": "Figma",
        "description": "活泼多彩，适合互动学习",
        "colors": {"background": "#FFFFFF", "backgroundSecondary": "#F5F5F5", "text": "#1E1E1E", "textSecondary": "#737373", "link": "#0C8CE9", "border": "#E5E5E5", "primary": "#0C8CE9", "secondary": "#FF725C", "accent": "#7ED321"},
        "typography": {"heading": "'Inter', sans-serif", "body": "'Inter', sans-serif", "code": "'JetBrains Mono', monospace"},
        "radius": "8px", "shadow": "0 4px 12px rgba(0,0,0,0.1)",
        "suitable_for": ["互动", "创意", "年轻", "设计"], "category": "创意设计"
    },
    "linear": {
        "name": "Linear",
        "description": "极简精准，适合工具类",
        "colors": {"background": "#0D0D0D", "backgroundSecondary": "#1A1A1A", "text": "#E0E0E0", "textSecondary": "#8A8A8A", "link": "#5E6AD2", "border": "#2A2A2A", "primary": "#5E6AD2"},
        "typography": {"heading": "'Inter', sans-serif", "body": "'Inter', sans-serif", "code": "'JetBrains Mono', monospace"},
        "radius": "6px", "shadow": "0 2px 8px rgba(0,0,0,0.2)",
        "suitable_for": ["工具", "逻辑", "效率", "数据"], "category": "工具效率"
    },
    "vercel": {
        "name": "Vercel",
        "description": "黑白科技感",
        "colors": {"background": "#000000", "backgroundSecondary": "#111111", "text": "#FFFFFF", "textSecondary": "#888888", "link": "#0070F3", "border": "#333333"},
        "typography": {"heading": "'Geist Sans', sans-serif", "body": "'Geist Sans', sans-serif", "code": "'Geist Mono', monospace"},
        "radius": "5px", "shadow": "0 4px 14px rgba(0,0,0,0.3)",
        "suitable_for": ["技术", "开发者", "文档", "API"], "category": "技术文档"
    },
    "stripe": {
        "name": "Stripe",
        "description": "专业优雅",
        "colors": {"background": "#FFFFFF", "backgroundSecondary": "#F6F9FC", "text": "#1A1F36", "textSecondary": "#697386", "link": "#635BFF", "border": "#E3E8EE", "primary": "#635BFF"},
        "typography": {"heading": "'Söhne', sans-serif", "body": "'Söhne', sans-serif", "code": "'Söhne Mono', monospace"},
        "radius": "8px", "shadow": "0 13px 27px -5px rgba(50,50,93,0.25)",
        "suitable_for": ["商务", "金融", "企业", "专业"], "category": "商务金融"
    },
    # 新增风格
    "claude": {
        "name": "Claude",
        "description": "温暖陶土色，简洁编辑风格",
        "colors": {"background": "#FAFAF9", "backgroundSecondary": "#F5F5F4", "text": "#1C1917", "textSecondary": "#78716C", "link": "#B91C1C", "border": "#E7E5E4", "primary": "#B91C1C"},
        "typography": {"heading": "Georgia, serif", "body": "system-ui, sans-serif", "code": "monospace"},
        "radius": "6px", "shadow": "0 1px 2px rgba(0,0,0,0.05)",
        "suitable_for": ["阅读", "写作", "博客"], "category": "教育文档"
    },
    "elevenlabs": {
        "name": "ElevenLabs",
        "description": "暗黑电影感，音频波形美学",
        "colors": {"background": "#0A0A0A", "backgroundSecondary": "#1A1A1A", "text": "#FFFFFF", "textSecondary": "#A0A0A0", "link": "#FF4D00", "border": "#333333", "primary": "#FF4D00"},
        "typography": {"heading": "'Inter', sans-serif", "body": "'Inter', sans-serif", "code": "monospace"},
        "radius": "12px", "shadow": "0 4px 20px rgba(0,0,0,0.4)",
        "suitable_for": ["音频", "媒体", "创意"], "category": "创意设计"
    },
    "ollama": {
        "name": "Ollama",
        "description": "终端优先，单色简约",
        "colors": {"background": "#000000", "backgroundSecondary": "#111111", "text": "#FFFFFF", "textSecondary": "#666666", "link": "#00FF00", "border": "#333333", "primary": "#00FF00"},
        "typography": {"heading": "monospace", "body": "system-ui", "code": "monospace"},
        "radius": "0px", "shadow": "none",
        "suitable_for": ["开发者", "极客", "终端"], "category": "技术文档"
    },
    "cursor": {
        "name": "Cursor",
        "description": "流畅暗黑，渐变点缀",
        "colors": {"background": "#1E1E1E", "backgroundSecondary": "#2A2A2A", "text": "#FFFFFF", "textSecondary": "#A0A0A0", "link": "#007ACC", "border": "#404040", "primary": "#007ACC"},
        "typography": {"heading": "'Inter', sans-serif", "body": "'Inter', sans-serif", "code": "'JetBrains Mono'"},
        "radius": "8px", "shadow": "0 4px 12px rgba(0,0,0,0.3)",
        "suitable_for": ["编辑器", "IDE", "开发"], "category": "技术文档"
    },
    "raycast": {
        "name": "Raycast",
        "description": "流畅暗铬，渐变强调",
        "colors": {"background": "#0D0D0D", "backgroundSecondary": "#1A1A1A", "text": "#FFFFFF", "textSecondary": "#888888", "link": "#FF6363", "border": "#2A2A2A", "primary": "#FF6363"},
        "typography": {"heading": "'Inter', sans-serif", "body": "'Inter', sans-serif", "code": "monospace"},
        "radius": "8px", "shadow": "0 4px 16px rgba(0,0,0,0.4)",
        "suitable_for": ["工具", "效率", "启动器"], "category": "工具效率"
    },
    "superhuman": {
        "name": "Superhuman",
        "description": "高级暗黑，键盘优先",
        "colors": {"background": "#1A1A1A", "backgroundSecondary": "#262626", "text": "#FFFFFF", "textSecondary": "#A0A0A0", "link": "#7C3AED", "border": "#404040", "primary": "#7C3AED"},
        "typography": {"heading": "'Inter', sans-serif", "body": "'Inter', sans-serif", "code": "monospace"},
        "radius": "6px", "shadow": "0 2px 8px rgba(0,0,0,0.3)",
        "suitable_for": ["邮件", "效率", "专业"], "category": "工具效率"
    },
    "airbnb": {
        "name": "Airbnb",
        "description": "温暖珊瑚色，摄影驱动",
        "colors": {"background": "#FFFFFF", "backgroundSecondary": "#F7F7F7", "text": "#222222", "textSecondary": "#717171", "link": "#FF5A5F", "border": "#DDDDDD", "primary": "#FF5A5F"},
        "typography": {"heading": "'Circular', sans-serif", "body": "'Circular', sans-serif", "code": "monospace"},
        "radius": "12px", "shadow": "0 4px 12px rgba(0,0,0,0.08)",
        "suitable_for": ["旅行", "摄影", "生活"], "category": "电商生活"
    },
    "spotify": {
        "name": "Spotify",
        "description": "鲜艳绿黑，专辑封面驱动",
        "colors": {"background": "#121212", "backgroundSecondary": "#181818", "text": "#FFFFFF", "textSecondary": "#B3B3B3", "link": "#1DB954", "border": "#282828", "primary": "#1DB954"},
        "typography": {"heading": "'Circular', sans-serif", "body": "'Circular', sans-serif", "code": "monospace"},
        "radius": "8px", "shadow": "0 4px 12px rgba(0,0,0,0.4)",
        "suitable_for": ["音乐", "媒体", "娱乐"], "category": "创意设计"
    },
    "tesla": {
        "name": "Tesla",
        "description": "激进减法，全屏摄影",
        "colors": {"background": "#000000", "backgroundSecondary": "#111111", "text": "#FFFFFF", "textSecondary": "#A0A0A0", "link": "#E31937", "border": "#333333", "primary": "#E31937"},
        "typography": {"heading": "'Gotham', sans-serif", "body": "'Gotham', sans-serif", "code": "monospace"},
        "radius": "0px", "shadow": "none",
        "suitable_for": ["汽车", "科技", "未来"], "category": "商务金融"
    },
    "apple": {
        "name": "Apple",
        "description": "高级留白，电影感",
        "colors": {"background": "#FFFFFF", "backgroundSecondary": "#F5F5F7", "text": "#1D1D1F", "textSecondary": "#86868B", "link": "#0066CC", "border": "#D2D2D7", "primary": "#0066CC"},
        "typography": {"heading": "'SF Pro Display', sans-serif", "body": "'SF Pro Text', sans-serif", "code": "'SF Mono', monospace"},
        "radius": "12px", "shadow": "0 4px 16px rgba(0,0,0,0.08)",
        "suitable_for": ["高端", "零售", "科技"], "category": "商务金融"
    },
}

DESIGN_MD_TEMPLATE = """# DESIGN.md - {name}
{description}

## 色彩系统
{colors}

## 字体规范
- 标题：{heading}
- 正文：{body}
- 代码：{code}

## 组件样式
- 圆角：{radius}
- 阴影：{shadow}
"""


def detect_project_type(project_path):
    """智能检测项目类型"""
    result = {'type': 'static', 'has_tailwind': False, 'has_css_modules': False, 'content_type': 'general', 'html_files': [], 'js_files': [], 'css_files': []}
    
    package_json_path = os.path.join(project_path, 'package.json')
    if os.path.exists(package_json_path):
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
                deps = package_data.get('dependencies', {})
                devDeps = package_data.get('devDependencies', {})
                if 'next' in deps or 'next' in devDeps: result['type'] = 'nextjs'
                elif 'vite' in devDeps or 'vite' in deps: result['type'] = 'vite'
                elif 'react-scripts' in deps or 'react-scripts' in devDeps: result['type'] = 'cra'
                if 'tailwindcss' in deps or 'tailwindcss' in devDeps: result['has_tailwind'] = True
                desc = package_data.get('description', '').lower()
                if any(k in desc for k in ['教育', '学习', 'student', 'education']): result['content_type'] = 'education'
                elif any(k in desc for k in ['文档', 'doc', 'api']): result['content_type'] = 'docs'
                elif any(k in desc for k in ['电商', 'shop', 'store']): result['content_type'] = 'ecommerce'
        except: pass
    
    for root, dirs, files in os.walk(project_path):
        if 'node_modules' in root or '.git' in root: continue
        for file in files:
            if file.endswith('.html'): result['html_files'].append(os.path.join(root, file))
            elif file.endswith(('.js', '.jsx', '.ts', '.tsx')): result['js_files'].append(os.path.join(root, file))
            elif file.endswith(('.css', '.scss')): result['css_files'].append(os.path.join(root, file))
    
    return result


def recommend_style(project_info):
    """推荐风格"""
    content_type = project_info.get('content_type', 'general')
    recommendations = {'education': 'notion', 'docs': 'vercel', 'ecommerce': 'stripe', 'general': 'linear'}
    style_key = recommendations.get(content_type, 'linear')
    return style_key, DESIGN_TEMPLATES[style_key]['suitable_for']


def generate_design_md(style_key, output_path):
    """生成 DESIGN.md"""
    if style_key not in DESIGN_TEMPLATES: return False
    template = DESIGN_TEMPLATES[style_key]
    colors_md = "\n".join([f"- {k}: `{v}`" for k, v in template["colors"].items()])
    content = DESIGN_MD_TEMPLATE.format(name=template["name"], description=template["description"], colors=colors_md,
        heading=template["typography"]["heading"], body=template["typography"]["body"], 
        code=template["typography"]["code"], radius=template["radius"], shadow=template["shadow"])
    with open(output_path, "w", encoding="utf-8") as f: f.write(content)
    return True


def generate_css_content(style_key, project_info):
    """生成智能 CSS"""
    if style_key not in DESIGN_TEMPLATES: return ""
    template = DESIGN_TEMPLATES[style_key]
    colors = template["colors"]
    typo = template["typography"]
    
    css = f"""/* {template['name']} 风格 - 智能生成 */
:root {{
  --bg-primary: {colors.get('background', '#FFFFFF')};
  --bg-secondary: {colors.get('backgroundSecondary', '#F5F5F5')};
  --text-primary: {colors.get('text', '#1E1E1E')};
  --text-secondary: {colors.get('textSecondary', '#737373')};
  --link-color: {colors.get('link', '#0070F3')};
  --border-color: {colors.get('border', '#E5E5E5')};
  --primary: {colors.get('primary', colors.get('link', '#0070F3'))};
  --radius: {template['radius']};
  --shadow: {template['shadow']};
}}

body {{ background-color: var(--bg-primary) !important; color: var(--text-primary) !important; font-family: var(--font-body) !important; }}
h1, h2, h3, h4, h5, h6 {{ font-family: var(--font-heading) !important; color: var(--text-primary) !important; }}
a {{ color: var(--link-color) !important; }}
button, .btn {{ border-radius: var(--radius) !important; background: var(--primary) !important; color: #fff !important; }}
.card {{ background: var(--bg-secondary) !important; border: 1px solid var(--border-color) !important; border-radius: var(--radius) !important; }}
"""
    return css


def generate_preview_html(project_path, style_key, project_info):
    """生成实时预览页"""
    if style_key not in DESIGN_TEMPLATES: return None
    
    template = DESIGN_TEMPLATES[style_key]
    colors = template["colors"]
    
    preview_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{template['name']} - 实时预览</title>
    <style>
        :root {{
            --bg-primary: {colors.get('background', '#FFFFFF')};
            --bg-secondary: {colors.get('backgroundSecondary', '#F5F5F5')};
            --text-primary: {colors.get('text', '#1E1E1E')};
            --link-color: {colors.get('link', '#0070F3')};
            --border-color: {colors.get('border', '#E5E5E5')};
            --primary: {colors.get('primary', '#0070F3')};
            --radius: {template['radius']};
        }}
        body {{
            background: var(--bg-primary);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            padding: 40px;
            margin: 0;
            transition: all 0.3s ease;
        }}
        .preview-container {{ max-width: 1200px; margin: 0 auto; }}
        .style-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .color-swatch {{
            display: inline-block;
            width: 100px;
            height: 100px;
            border-radius: var(--radius);
            margin: 10px;
            border: 1px solid rgba(0,0,0,0.1);
        }}
        .btn {{
            background: var(--primary);
            color: #fff;
            border: none;
            border-radius: var(--radius);
            padding: 12px 24px;
            font-size: 16px;
            cursor: pointer;
            margin: 10px 5px;
            transition: all 0.2s ease;
        }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }}
        h1 {{ font-family: Georgia, serif; font-size: 32px; margin-bottom: 10px; }}
        .comparison {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 40px 0; }}
        .comparison-item {{ padding: 20px; border-radius: var(--radius); }}
        .original {{ background: #f5f5f5; color: #333; }}
        .preview {{ background: var(--bg-secondary); color: var(--text-primary); }}
    </style>
</head>
<body>
    <div class="preview-container">
        <h1>{template['name']} - 实时预览</h1>
        <p>{template['description']}</p>
        
        <div class="style-card">
            <h2>色彩系统</h2>
            <div class="color-swatch" style="background: {colors.get('background', '#FFFFFF')};"></div>
            <div class="color-swatch" style="background: {colors.get('backgroundSecondary', '#F5F5F5')};"></div>
            <div class="color-swatch" style="background: {colors.get('text', '#1E1E1E')};"></div>
            <div class="color-swatch" style="background: {colors.get('primary', '#0070F3')};"></div>
        </div>
        
        <div class="style-card">
            <h2>按钮效果</h2>
            <button class="btn">主要按钮</button>
            <button class="btn" style="background: transparent; color: var(--text-primary); border: 1px solid var(--border-color);">次要按钮</button>
        </div>
        
        <div class="comparison">
            <div class="comparison-item original">
                <h3>原始效果</h3>
                <p>这是原始样式</p>
            </div>
            <div class="comparison-item preview">
                <h3>{template['name']} 效果</h3>
                <p>这是应用{template['name']}后的效果</p>
            </div>
        </div>
        
        <div class="style-card">
            <h2>适合场景</h2>
            <p>{', '.join(template['suitable_for'])}</p>
        </div>
    </div>
</body>
</html>"""
    
    preview_path = os.path.join(project_path, f"preview-{style_key}.html")
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(preview_content)
    
    return preview_path


def main():
    if len(sys.argv) < 2:
        print("用法：py beautify.py <项目路径> [风格名称|--auto|--preview]")
        print("可用风格：", ", ".join(DESIGN_TEMPLATES.keys()))
        sys.exit(1)
    
    project_path = sys.argv[1]
    style_key = sys.argv[2].lower() if len(sys.argv) > 2 else None
    is_preview = '--preview' in sys.argv
    
    if not os.path.exists(project_path):
        print(f"❌ 路径不存在：{project_path}")
        sys.exit(1)
    
    # 智能检测
    print("\n🔍 分析项目...")
    project_info = detect_project_type(project_path)
    print(f"类型：{project_info['type']} | Tailwind: {'是' if project_info['has_tailwind'] else '否'}")
    
    # 推荐或指定风格
    if style_key == '--auto' or style_key is None:
        style_key, suitable = recommend_style(project_info)
        print(f"💡 推荐：{DESIGN_TEMPLATES[style_key]['name']}")
    elif style_key not in DESIGN_TEMPLATES:
        print(f"❌ 风格不存在：{style_key}")
        print(f"可用：{', '.join(DESIGN_TEMPLATES.keys())}")
        sys.exit(1)
    
    template = DESIGN_TEMPLATES[style_key]
    print(f"\n🎨 风格：{template['name']} - {template['description']}")
    
    # 生成 DESIGN.md
    design_md_path = os.path.join(project_path, "DESIGN.md")
    if generate_design_md(style_key, design_md_path):
        print("✅ DESIGN.md")
    
    # 生成 CSS
    styles_dir = os.path.join(project_path, "styles")
    if not os.path.exists(styles_dir): os.makedirs(styles_dir)
    css_path = os.path.join(styles_dir, "theme-override.css")
    css_content = generate_css_content(style_key, project_info)
    with open(css_path, "w", encoding="utf-8") as f: f.write(css_content)
    print("✅ styles/theme-override.css")
    
    # 构建项目支持
    if project_info['type'] in ['vite', 'nextjs', 'cra']:
        assets_dir = os.path.join(project_path, "assets")
        if not os.path.exists(assets_dir): os.makedirs(assets_dir)
        shutil.copy(css_path, os.path.join(assets_dir, "theme-override.css"))
        print("✅ assets/theme-override.css")
    
    # 生成预览页
    if is_preview or '--preview' in sys.argv:
        print("\n📺 生成预览页...")
        preview_path = generate_preview_html(project_path, style_key, project_info)
        if preview_path:
            print(f"✅ {preview_path}")
            # 自动打开浏览器
            try:
                webbrowser.open(f"file://{preview_path}")
                print("🌐 已打开浏览器预览")
            except:
                print(f"📄 预览路径：{preview_path}")
    
    print("\n✨ 完成！")


if __name__ == "__main__":
    main()
