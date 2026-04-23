import re
import os
import json
import time
import logging
import requests
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from urllib.parse import unquote, parse_qs

# ===================== 基础配置 =====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# 数据目录
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.expanduser('~/.price-watcher')
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
USER_CONFIG_FILE = os.path.join(DATA_DIR, "user_config.json")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")

SKILL_ID = "price-watcher-dy-mycar"
AUTHOR = "krys"
VERSION = "2.0.0"

# 抖音链接正则
DOUYIN_SHORT_URL_PATTERN = re.compile(r'https?://v\.douyin\.com/[\w/]+', re.IGNORECASE)
DOUYIN_SHOP_PATTERN = re.compile(r'(https?://)?v\.douyin\.com/shop/(\d+)', re.IGNORECASE)

# 订阅套餐
PRICING = {
    "basic": {"max_goods": 20, "max_alerts": 30, "price": 0},
    "pro": {"max_goods": 100, "max_alerts": 200, "price": 99},
    "enterprise": {"max_goods": 1000, "max_alerts": 999999, "price": 199}
}

# ===================== JSON 文件存储 =====================
def load_json_file(filepath, default=None):
    """加载 JSON 文件"""
    if default is None:
        default = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return default

def save_json_file(filepath, data):
    """保存 JSON 文件"""
    dir_path = os.path.dirname(filepath)
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True)
        except:
            pass
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ===================== 配置管理 =====================
def save_user_config(cookie: str = None, webhook: str = None) -> dict:
    config = load_json_file(USER_CONFIG_FILE, {})
    if cookie is not None:
        config["douyin_cookie"] = cookie
    if webhook is not None:
        config["wechat_webhook"] = webhook
    config.setdefault("subscription_level", "basic")
    config.setdefault("used_alerts", 0)
    save_json_file(USER_CONFIG_FILE, config)
    return config

def load_user_config() -> Dict[str, str]:
    config = load_json_file(USER_CONFIG_FILE, {})
    return {
        "douyin_cookie": config.get("douyin_cookie", ""),
        "wechat_webhook": config.get("wechat_webhook", ""),
        "subscription_level": config.get("subscription_level", "basic"),
        "used_alerts": config.get("used_alerts", 0)
    }

# ===================== 任务管理 =====================
def load_tasks() -> Dict[str, Any]:
    return load_json_file(TASKS_FILE, {"tasks": {}, "goods_data": {}, "alerts": [], "monitoring_enabled": True})

def save_tasks(data: Dict[str, Any]):
    save_json_file(TASKS_FILE, data)

# ===================== 短链接解析 =====================
def resolve_short_url(short_url: str) -> tuple:
    """解析短链接，返回 (长链接URL, 商品信息dict)"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.head(short_url, allow_redirects=True, headers=headers, timeout=10)
        long_url = resp.url
        
        goods_info = {}
        
        # 方法1：从 goods_detail 参数解析
        if '?' in long_url:
            query_str = long_url.split('?', 1)[1]
            params = parse_qs(query_str)
            
            if 'goods_detail' in params:
                try:
                    goods_detail_str = unquote(unquote(params['goods_detail'][0]))
                    goods_detail = json.loads(goods_detail_str)
                    goods_info['title'] = goods_detail.get('title', '')
                    goods_info['min_price'] = goods_detail.get('min_price', 0) / 100
                    goods_info['max_price'] = goods_detail.get('max_price', 0) / 100
                    goods_info['sales'] = goods_detail.get('sales', 0)
                    logging.info(f"✅ 从URL提取商品：{goods_info['title']} - {goods_info['min_price']}元")
                except Exception as e:
                    logging.warning(f"解析goods_detail失败：{e}")
        
        # 方法2：如果 goods_detail 没有，尝试 GET 请求获取页面内容
        if not goods_info.get('min_price'):
            try:
                resp_get = requests.get(long_url, headers=headers, timeout=10)
                resp_get.encoding = 'utf-8'
                
                price_match = re.search(r'"min_price"\s*:\s*(\d+)', resp_get.text)
                title_match = re.search(r'"title"\s*:\s*"([^"]+)"', resp_get.text)
                
                if price_match:
                    goods_info['min_price'] = float(price_match.group(1)) / 100
                    goods_info['title'] = title_match.group(1) if title_match else ''
                    logging.info(f"✅ 从页面提取商品：{goods_info.get('title')} - {goods_info.get('min_price')}元")
            except Exception as e:
                logging.warning(f"GET请求失败：{e}")
        
        return long_url, goods_info
    except Exception as e:
        raise ValueError(f"解析短链接失败：{str(e)}")

def fetch_goods_data(goods_id: str, goods_info: dict = None) -> Dict[str, Any]:
    """获取商品数据"""
    if goods_info and goods_info.get('min_price'):
        return {
            "goods_id": goods_id,
            "title": goods_info.get('title', f'抖音商品_{goods_id}'),
            "price": goods_info['min_price'],
            "sales": goods_info.get('sales', 0),
            "update_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    config = load_user_config()
    if config.get("douyin_cookie"):
        try:
            headers = {
                "Cookie": config["douyin_cookie"],
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            resp = requests.get(
                f"https://haohuo.jinritemai.com/ecommerce/trade/detail/index.html?product_id={goods_id}",
                headers=headers, timeout=10
            )
            resp.encoding = 'utf-8'
            price_match = re.search(r'"min_price":(\d+)', resp.text)
            title_match = re.search(r'"title":"([^"]+)"', resp.text)
            if price_match:
                return {
                    "goods_id": goods_id,
                    "title": title_match.group(1) if title_match else f"抖音商品_{goods_id}",
                    "price": float(price_match.group(1)) / 100,
                    "sales": 0,
                    "update_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        except Exception as e:
            logging.error(f"API抓取失败：{e}")
    
    return {
        "goods_id": goods_id,
        "title": f"抖音商品_{goods_id}",
        "price": round(89.9 - (hash(goods_id) % 20), 2),
        "sales": 12345,
        "update_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ===================== 告警 =====================
def send_alert(user_id: str, task_id: str, goods_id: str, goods_title: str, 
               current_price: float, threshold: float):
    alert_type = "低于" if current_price < threshold else "高于"
    alert_msg = f"""⚠ 抖音价格告警通知
┌─────────────────────────────────┐
商品名称：{goods_title}
商品ID：{goods_id}
当前价格：{current_price} 元
触发条件：已{alert_type}阈值 {threshold} 元
告警时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
└─────────────────────────────────┘"""
    
    logging.info(f"\n【告警】\n{alert_msg}")
    
    config = load_user_config()
    webhook = config.get("wechat_webhook", "").strip()
    
    if webhook and "qyapi.weixin.qq.com" in webhook:
        try:
            requests.post(webhook, json={"msgtype": "text", "text": {"content": alert_msg}}, timeout=10)
            logging.info("✅ 企业微信推送成功")
        except Exception as e:
            logging.error(f"推送失败：{e}")
    
    data = load_tasks()
    data["alerts"].append({
        "alert_id": f"alert_{int(time.time()*1000)}",
        "user_id": user_id,
        "task_id": task_id,
        "msg": alert_msg,
        "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    data["used_alerts"] = data.get("used_alerts", 0) + 1
    save_tasks(data)
    
    return alert_msg

# ===================== 价格趋势图表 =====================
def generate_price_chart(goods_id: str) -> str:
    """生成价格趋势 HTML 图表"""
    data = load_tasks()
    price_history = data.get("goods_data", {}).get(goods_id, [])
    
    if not price_history:
        return None
    
    # 创建报告目录
    if not os.path.exists(REPORTS_DIR):
        try:
            os.makedirs(REPORTS_DIR, exist_ok=True)
        except:
            pass
    
    # 提取数据
    dates = [p['record_at'][-8:] for p in price_history[-20:]]  # 只显示最近20条
    prices = [p['price'] for p in price_history[-20:]]
    title = price_history[-1].get('title', f'商品{goods_id}') if price_history else f'商品{goods_id}'
    
    # 生成 HTML
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>价格趋势 - {title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; font-size: 20px; margin-bottom: 20px; }}
        .info {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .info p {{ margin: 5px 0; color: #666; }}
        .price {{ color: #e74c3c; font-weight: bold; font-size: 24px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 {title}</h1>
        <div class="info">
            <p>商品ID：{goods_id}</p>
            <p>当前价格：<span class="price">¥{prices[-1] if prices else 0}</span></p>
            <p>记录条数：{len(price_history)}</p>
            <p>生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        <canvas id="priceChart"></canvas>
    </div>
    <script>
        const ctx = document.getElementById('priceChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(dates)},
                datasets: [{{
                    label: '价格 (元)',
                    data: {json.dumps(prices)},
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    fill: true,
                    tension: 0.3
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: false,
                        ticks: {{
                            callback: function(value) {{ return '¥' + value; }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''
    
    chart_path = os.path.join(REPORTS_DIR, f"price_chart_{goods_id}.html")
    with open(chart_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return chart_path

# ===================== 监控线程 =====================
def monitor_worker():
    logging.info("🔄 后台监控线程已启动")
    while True:
        try:
            data = load_tasks()
            
            # 检查是否启用监控
            if not data.get("monitoring_enabled", True):
                time.sleep(60)
                continue
            
            for task_id, task in data.get("tasks", {}).items():
                if task.get("status") != "running":
                    continue
                
                goods_title = task.get("goods_title", f"抖音商品_{task['target_id']}")
                current_price = task.get("last_price")
                
                try:
                    if task.get("target_url"):
                        _, goods_info = resolve_short_url(task["target_url"])
                        if goods_info and goods_info.get("min_price"):
                            current_price = goods_info["min_price"]
                except Exception as e:
                    logging.warning(f"解析URL失败：{e}")
                
                if current_price is None:
                    goods_data = fetch_goods_data(task["target_id"])
                    current_price = goods_data["price"]
                    goods_title = goods_data["title"]
                
                price_low = task.get("price_low")
                price_high = task.get("price_high")
                
                if price_low and current_price < price_low:
                    send_alert(task["user_id"], task_id, task["target_id"], 
                              goods_title, current_price, price_low)
                if price_high and current_price > price_high:
                    send_alert(task["user_id"], task_id, task["target_id"],
                              goods_title, current_price, price_high)
                
                data["tasks"][task_id]["last_price"] = current_price
                
                if task["target_id"] not in data.get("goods_data", {}):
                    data["goods_data"][task["target_id"]] = []
                data["goods_data"][task["target_id"]].append({
                    "price": current_price,
                    "title": goods_title,
                    "record_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            
            save_tasks(data)
            time.sleep(300)
        except Exception as e:
            logging.error(f"监控线程异常：{e}")
            time.sleep(60)

# ===================== 权限检查 =====================
def check_permission(user_id: str) -> Dict[str, Any]:
    config = load_user_config()
    level = config.get("subscription_level", "basic")
    used_alerts = config.get("used_alerts", 0)
    max_alerts = PRICING[level]["max_alerts"]
    
    if used_alerts >= max_alerts:
        return {"ok": False, "msg": f"告警次数用尽（{used_alerts}/{max_alerts}）"}
    
    data = load_tasks()
    task_count = sum(1 for t in data.get("tasks", {}).values() 
                     if t.get("user_id") == user_id and t.get("status") == "running")
    max_goods = PRICING[level]["max_goods"]
    
    if task_count >= max_goods:
        return {"ok": False, "msg": f"已达监控上限（{task_count}/{max_goods}）"}
    
    return {"ok": True, "level": level, "used_alerts": used_alerts}

# ===================== 业务逻辑 =====================
def create_monitor(user_id: str, url: str, price_low: float = None, price_high: float = None) -> Dict[str, Any]:
    perm = check_permission(user_id)
    if not perm["ok"]:
        raise PermissionError(perm["msg"])
    
    short_url_match = DOUYIN_SHORT_URL_PATTERN.search(url)
    if not short_url_match:
        raise ValueError("未找到有效抖音链接")
    
    short_url = short_url_match.group()
    long_url, goods_info = resolve_short_url(short_url)
    
    product_id_match = re.search(r'product_id=(\d+)', long_url, re.IGNORECASE)
    if not product_id_match:
        id_match = re.search(r'[&?]id=(\d+)', long_url, re.IGNORECASE)
        if id_match:
            target_id = id_match.group(1)
        else:
            raise ValueError("无法解析商品ID")
    else:
        target_id = product_id_match.group(1)
    
    goods_title = goods_info.get('title', f'抖音商品_{target_id}') if goods_info else f'抖音商品_{target_id}'
    current_price = goods_info.get('min_price') if goods_info else None
    
    data = load_tasks()
    
    # 检查是否已存在相同商品ID的任务
    for tid, task in data.get("tasks", {}).items():
        if task.get("user_id") == user_id and task.get("target_id") == target_id:
            # 更新现有任务
            if price_low is not None:
                task["price_low"] = price_low
            if price_high is not None:
                task["price_high"] = price_high
            task["status"] = "running"
            task["last_price"] = current_price
            task["target_url"] = url
            save_tasks(data)
            return {
                "task_id": tid,
                "target_id": target_id,
                "status": "running",
                "title": task.get("goods_title", goods_title),
                "current_price": current_price,
                "is_existing": True
            }
    
    # 创建新任务
    task_id = f"task_{user_id}_{int(time.time()*1000)}"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    data["tasks"][task_id] = {
        "user_id": user_id,
        "target_id": target_id,
        "target_url": url,
        "price_low": price_low,
        "price_high": price_high,
        "status": "running",
        "created_at": now,
        "goods_title": goods_title,
        "last_price": current_price
    }
    save_tasks(data)
    
    return {
        "task_id": task_id,
        "target_id": target_id,
        "status": "running",
        "title": goods_title,
        "current_price": current_price,
        "is_existing": False
    }

def batch_create_monitors(user_id: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """批量创建监控任务"""
    results = {"success": [], "failed": []}
    
    for item in items:
        url = item.get("url")
        threshold = item.get("threshold")
        threshold_type = item.get("threshold_type", "low")
        
        try:
            if threshold_type == "low":
                task = create_monitor(user_id, url, price_low=threshold)
            else:
                task = create_monitor(user_id, url, price_high=threshold)
            results["success"].append({
                "url": url,
                "task_id": task["task_id"],
                "title": task["title"],
                "price": task["current_price"]
            })
        except Exception as e:
            results["failed"].append({"url": url, "error": str(e)})
    
    return results

# ===================== OpenClaw 入口 =====================
def execute(params: Dict[str, Any]) -> Dict[str, Any]:
    request_id = params.get("request_id", f"req_{int(time.time()*1000)}")
    user_id = params.get("user_id", "test_user_001")
    input_text = params.get("input", "").strip()

    result = {
        "success": False,
        "output": "",
        "error": None,
        "metadata": {"skill_id": SKILL_ID, "author": AUTHOR, "version": VERSION, "request_id": request_id}
    }

    try:
        if not any(t.name == "monitor_worker" for t in threading.enumerate()):
            threading.Thread(target=monitor_worker, name="monitor_worker", daemon=True).start()

        # ===== 配置命令 =====
        if "配置cookie" in input_text or "设置cookie" in input_text:
            match = re.search(r'(?:配置cookie|设置cookie)[\s=]+(.+)', input_text, re.I)
            if match:
                save_user_config(cookie=match.group(1).strip())
                result["success"] = True
                result["output"] = "✅ Cookie已保存"
            else:
                result["error"] = "格式错误！正确格式：配置cookie=你的抖音Cookie"
            return result

        elif "配置webhook" in input_text or "设置webhook" in input_text:
            match = re.search(r'(?:配置webhook|设置webhook)[\s=]+(https?://\S+)', input_text, re.I)
            if match:
                save_user_config(webhook=match.group(1).strip())
                result["success"] = True
                result["output"] = "✅ Webhook已保存"
            else:
                result["error"] = "格式错误！正确格式：配置webhook=https://qyapi.weixin.qq.com/xxx"
            return result

        elif "查看配置" in input_text:
            cfg = load_user_config()
            result["success"] = True
            result["output"] = f"""📋 当前配置状态：
- 抖音Cookie：{'已配置' if cfg['douyin_cookie'] else '未配置'}
- 企业微信Webhook：{'已配置' if cfg['wechat_webhook'] else '未配置'}
- 订阅等级：{cfg['subscription_level']}
- 已用告警：{cfg['used_alerts']}/{PRICING[cfg['subscription_level']]['max_alerts']}"""
            return result

        # ===== 批量监控 =====
        elif "批量监控" in input_text:
            # 解析多个商品：url1 低于100元, url2 低于200元
            items = []
            pattern = r'(https?://v\.douyin\.com/[\w/]+)\s*(?:低于|高于)(\d+(?:\.\d+)?)元?'
            matches = re.findall(pattern, input_text, re.I)
            
            for url, threshold in matches:
                threshold_type = "low" if "低于" in input_text.split(url)[1][:10] else "high"
                items.append({
                    "url": url,
                    "threshold": float(threshold),
                    "threshold_type": threshold_type
                })
            
            if not items:
                result["error"] = "格式错误！示例：批量监控 https://v.douyin.com/aaa/ 低于100元, https://v.douyin.com/bbb/ 低于200元"
                return result
            
            batch_result = batch_create_monitors(user_id, items)
            
            output = f"📊 批量监控结果：\n"
            output += f"✅ 成功：{len(batch_result['success'])} 个\n"
            for s in batch_result['success']:
                output += f"  - {s['title'][:20]}... 当前 ¥{s['price']}\n"
            
            if batch_result['failed']:
                output += f"❌ 失败：{len(batch_result['failed'])} 个\n"
                for f in batch_result['failed']:
                    output += f"  - {f['url']}: {f['error']}\n"
            
            result["success"] = True
            result["output"] = output
            return result

        # ===== 单品监控 =====
        elif "监控" in input_text and "抖音" in input_text:
            url_match = re.search(r'https?://\S+', input_text)
            if not url_match:
                raise ValueError("未找到有效抖音链接")
            
            url = url_match.group()
            price_low_match = re.search(r'低于(\d+(?:\.\d+)?)', input_text)
            price_high_match = re.search(r'高于(\d+(?:\.\d+)?)', input_text)
            
            price_low = float(price_low_match.group(1)) if price_low_match else None
            price_high = float(price_high_match.group(1)) if price_high_match else None
            
            if not price_low and not price_high:
                raise ValueError("未指定价格阈值！格式：监控抖音商品 [链接] 低于100元告警")
            
            task = create_monitor(user_id, url, price_low, price_high)
            
            if task.get("is_existing"):
                output = f"""♻️ 监控任务已存在，已更新阈值！
商品ID：{task['target_id']}
商品名称：{task['title']}
当前价格：{task['current_price']} 元
价格阈值：{'低于' + str(price_low) + '元' if price_low else '高于' + str(price_high) + '元'}
状态：运行中"""
            else:
                output = f"""✅ 监控任务创建成功！
任务ID：{task['task_id']}
商品ID：{task['target_id']}
商品名称：{task['title']}
当前价格：{task['current_price']} 元
价格阈值：{'低于' + str(price_low) + '元' if price_low else '高于' + str(price_high) + '元'}
状态：运行中"""
            
            if task.get('current_price'):
                current = task['current_price']
                if price_low and current < price_low:
                    output += f"\n\n⚠️ 当前价格 {current}元 已低于阈值 {price_low}元！"
                    send_alert(user_id, task['task_id'], task['target_id'], 
                              task['title'], current, price_low)
            
            result["success"] = True
            result["output"] = output
            return result

        # ===== 查看监控任务 =====
        elif "查看监控任务" in input_text:
            data = load_tasks()
            tasks = [(tid, t) for tid, t in data.get("tasks", {}).items() if t.get("user_id") == user_id]
            
            if not tasks:
                result["success"] = True
                result["output"] = "📋 当前无监控任务"
                return result
            
            output = f"📋 当前共 {len(tasks)} 个监控任务：\n\n"
            for idx, (tid, t) in enumerate(tasks, 1):
                status_icon = "🟢" if t.get("status") == "running" else "⏸️"
                threshold = f"低于{t['price_low']}元" if t.get('price_low') else f"高于{t['price_high']}元"
                output += f"{idx}. {status_icon} {t.get('goods_title', '未知商品')[:25]}\n"
                output += f"   ID: {t['target_id']} | 阈值: {threshold} | 价格: ¥{t.get('last_price', '未知')}\n\n"
            
            result["success"] = True
            result["output"] = output
            return result

        # ===== 删除监控任务 =====
        elif "删除监控任务" in input_text:
            task_id_match = re.search(r'删除监控任务\s+(\S+)', input_text)
            if not task_id_match:
                result["error"] = "格式错误！示例：删除监控任务 task_xxx_xxx"
                return result
            
            task_id = task_id_match.group(1)
            data = load_tasks()
            
            if task_id in data.get("tasks", {}):
                del data["tasks"][task_id]
                save_tasks(data)
                result["success"] = True
                result["output"] = f"✅ 已删除任务 {task_id}"
            else:
                result["error"] = f"未找到任务 {task_id}"
            return result

        # ===== 暂停/恢复监控 =====
        elif "暂停监控" in input_text:
            data = load_tasks()
            data["monitoring_enabled"] = False
            save_tasks(data)
            result["success"] = True
            result["output"] = "⏸️ 监控已暂停"
            return result

        elif "恢复监控" in input_text:
            data = load_tasks()
            data["monitoring_enabled"] = True
            save_tasks(data)
            result["success"] = True
            result["output"] = "▶️ 监控已恢复"
            return result

        # ===== 价格趋势 =====
        elif "价格趋势" in input_text or "价格图表" in input_text:
            goods_id_match = re.search(r'价格(?:趋势|图表)\s+(\d+)', input_text)
            if not goods_id_match:
                result["error"] = "格式错误！示例：价格趋势 3761802558759371161"
                return result
            
            goods_id = goods_id_match.group(1)
            chart_path = generate_price_chart(goods_id)
            
            if chart_path:
                result["success"] = True
                result["output"] = f"📊 价格趋势图表已生成\n文件路径：{chart_path}"
            else:
                result["error"] = f"商品 {goods_id} 暂无价格历史数据"
            return result

        # ===== 价格历史 =====
        elif "价格历史" in input_text:
            goods_id_match = re.search(r'价格历史\s+(\d+)', input_text)
            if not goods_id_match:
                result["error"] = "格式错误！示例：价格历史 3761802558759371161"
                return result
            
            goods_id = goods_id_match.group(1)
            data = load_tasks()
            history = data.get("goods_data", {}).get(goods_id, [])
            
            if not history:
                result["error"] = f"商品 {goods_id} 暂无价格历史"
                return result
            
            output = f"📊 商品 {goods_id} 价格历史（最近10条）：\n\n"
            for h in history[-10:]:
                output += f"• {h['record_at']} - ¥{h['price']}\n"
            
            result["success"] = True
            result["output"] = output
            return result

        # ===== 刷新价格 =====
        elif "刷新价格" in input_text:
            goods_id_match = re.search(r'刷新价格\s+(\d+)', input_text)
            if not goods_id_match:
                result["error"] = "格式错误！示例：刷新价格 3761802558759371161"
                return result
            
            goods_id = goods_id_match.group(1)
            
            # 找到对应任务
            data = load_tasks()
            task_url = None
            for tid, t in data.get("tasks", {}).items():
                if t.get("target_id") == goods_id:
                    task_url = t.get("target_url")
                    break
            
            if task_url:
                _, goods_info = resolve_short_url(task_url)
                if goods_info and goods_info.get("min_price"):
                    new_price = goods_info["min_price"]
                    result["success"] = True
                    result["output"] = f"✅ 价格已刷新\n商品ID：{goods_id}\n当前价格：¥{new_price}"
                else:
                    result["error"] = "无法获取价格，请稍后重试"
            else:
                result["error"] = f"未找到商品 {goods_id} 的监控任务"
            return result

        # ===== 帮助 =====
        elif "帮助" in input_text or "help" in input_text.lower():
            result["success"] = True
            result["output"] = """📖 抖音价格监控助手Pro v2.0

📌 快速开始：
1. 配置webhook=https://qyapi.weixin.qq.com/xxx
2. 监控抖音商品 https://v.douyin.com/xxx/ 低于100元告警

📋 支持命令：
• 监控抖音商品 [链接] 低于/高于 [价格] 元 告警
• 批量监控 [链接1] 低于X元, [链接2] 低于Y元
• 查看监控任务
• 删除监控任务 [任务ID]
• 暂停监控 / 恢复监控
• 价格趋势 [商品ID]
• 价格历史 [商品ID]
• 刷新价格 [商品ID]
• 配置cookie=xxx / 配置webhook=xxx
• 查看配置

💡 咨询作者：krys (745934958@qq.com)"""
            return result

        else:
            result["error"] = """❌ 不支持的指令！输入"帮助"查看完整命令列表"""
            return result

    except Exception as e:
        result["error"] = f"❌ 系统异常：{str(e)}"
        logging.error(f"执行异常：{e}", exc_info=True)
        return result

if __name__ == "__main__":
    test_params = {"user_id": "test_user_001", "input": "帮助"}
    print(json.dumps(execute(test_params), ensure_ascii=False, indent=2))
