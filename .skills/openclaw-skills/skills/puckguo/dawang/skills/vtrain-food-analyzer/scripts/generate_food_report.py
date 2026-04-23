import requests
import json
import re
import sys
from datetime import datetime, timedelta

BASE_URL = "https://puckg.fun"

def fetch_user_data(email, password):
    """使用邮箱和密码获取用户基本信息"""
    response = requests.post(
        f"{BASE_URL}/api/agent/user-data",
        headers={"Content-Type": "application/json"},
        json={"email": email, "password": password}
    )
    return response.json()

def fetch_food_data(user_id, start_date=None, end_date=None, meal_type=None):
    """获取用户食物数据"""
    payload = {"userId": user_id}
    if start_date:
        payload["startDate"] = start_date
    if end_date:
        payload["endDate"] = end_date
    if meal_type:
        payload["mealType"] = meal_type

    response = requests.post(
        f"{BASE_URL}/api/food/analysis/by-date-range",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    return response.json()

def generate_food_report(food_data, user_email, date_range, output_file, template_path='assets/food_report_template.html'):
    """生成食物数据HTML报告"""
    # 读取模板
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # 替换数据
    food_data_json = json.dumps(food_data, ensure_ascii=False, indent=4)

    # 使用正则替换 FOOD_DATA
    pattern = r'const FOOD_DATA = \{[\s\S]*?\};'
    replacement = f'const FOOD_DATA = {food_data_json};'
    template = re.sub(pattern, replacement, template)

    # 替换用户信息
    template = template.replace(
        'const USER_EMAIL = "user@example.com";',
        f'const USER_EMAIL = "{user_email}";'
    )

    # 替换日期范围
    template = template.replace(
        'const DATE_RANGE = {\n            start: "2026-01-01",\n            end: "2026-01-31"\n        };',
        f'const DATE_RANGE = {{\n            start: "{date_range[0]}",\n            end: "{date_range[1]}"\n        }};'
    )

    # 保存报告
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(template)

    print(f'✅ 报告已生成: {output_file}')

def main():
    if len(sys.argv) < 3:
        print("用法: python generate_food_report.py <邮箱> <密码> [开始日期] [结束日期]")
        print("示例: python generate_food_report.py user@example.com password123")
        print("      python generate_food_report.py user@example.com password123 2026-03-01 2026-03-31")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    # 日期范围
    if len(sys.argv) >= 5:
        start_date = sys.argv[3]
        end_date = sys.argv[4]
    else:
        # 默认本月
        now = datetime.now()
        start_date = now.replace(day=1).strftime('%Y-%m-%d')
        end_date = (now.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        end_date = end_date.strftime('%Y-%m-%d')

    print(f"📧 邮箱: {email}")
    print(f"📅 日期范围: {start_date} 至 {end_date}")
    print("-" * 50)

    # 1. 获取用户数据
    print("🔐 正在登录...")
    user_result = fetch_user_data(email, password)

    if not user_result.get('success'):
        print(f"❌ 登录失败: {user_result.get('message')}")
        sys.exit(1)

    user_id = user_result['data']['user']['id']
    print(f"✅ 登录成功，用户ID: {user_id}")

    # 2. 获取食物数据
    print(f"\n📊 正在获取饮食数据...")
    food_result = fetch_food_data(user_id, start_date, end_date)

    if not food_result.get('success') or not food_result.get('data'):
        print(f"❌ 获取数据失败: {food_result.get('message')}")
        sys.exit(1)

    data = food_result['data']

    # 打印摘要
    print(f"\n{'='*60}")
    print(f"📊 饮食数据摘要")
    print(f"{'='*60}")
    print(f"总记录数: {data['totalCount']}")
    print(f"总热量: {data['totalCalories']} kcal")

    if data.get('stats'):
        print(f"\n{'='*60}")
        print(f"🍽️ 按餐型统计")
        print(f"{'='*60}")
        for meal_type, stat in data['stats'].items():
            print(f"{meal_type}: {stat['count']} 餐, {stat['totalCalories']} kcal")

    # 3. 生成HTML报告
    month_str = start_date[:7]  # 2026-03
    output_file = f'food_report_{month_str}.html'

    # 获取脚本所在目录的绝对路径
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)
    template_path = os.path.join(skill_dir, 'assets', 'food_report_template.html')

    generate_food_report(data, email, (start_date, end_date), output_file, template_path)

    # 4. 保存JSON数据
    json_file = f'food_data_{month_str}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 数据已保存: {json_file}")

    print(f"\n🎉 完成！生成的文件:")
    print(f"   📄 {output_file}")
    print(f"   📄 {json_file}")

if __name__ == '__main__':
    main()
