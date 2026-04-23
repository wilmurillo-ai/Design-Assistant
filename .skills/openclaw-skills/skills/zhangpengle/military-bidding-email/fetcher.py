#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
军工采购商机邮件发送工具

自动抓取招标信息并发送邮件报告
"""

import sys
import os
import subprocess
import json
import pandas as pd
from pathlib import Path


def load_env_config():
    """从.env文件加载邮件配置"""
    env_path = Path(__file__).parent / '.env'
    config = {'to': [], 'cc': [], 'smtp': {}}

    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if line.startswith('TO_RECIPIENTS='):
                        to_str = line.split('=', 1)[1].strip()
                        config['to'] = [e.strip() for e in to_str.split(',') if e.strip()]
                    elif line.startswith('CC_RECIPIENTS='):
                        cc_str = line.split('=', 1)[1].strip()
                        config['cc'] = [e.strip() for e in cc_str.split(',') if e.strip()]
                    elif line.startswith('SMTP_HOST='):
                        config['smtp']['host'] = line.split('=', 1)[1].strip()
                    elif line.startswith('SMTP_PORT='):
                        config['smtp']['port'] = line.split('=', 1)[1].strip()
                    elif line.startswith('SMTP_USER='):
                        config['smtp']['user'] = line.split('=', 1)[1].strip()
                    elif line.startswith('SMTP_PASSWORD='):
                        config['smtp']['password'] = line.split('=', 1)[1].strip()

    # 确保有默认值
    if not config['to']:
        config['to'] = ['zhangpengle@formulas.cc']
    if not config['cc']:
        config['cc'] = ['wangzilong@formulas.cc', 'fuyan@formulas.cc']

    return config


def _import_fetcher():
    """延迟导入避免循环依赖"""
    sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/skills/military-bidding-fetcher')
    from fetcher import fetch_all_bidding, DEFAULT_CORE_KW
    return fetch_all_bidding, DEFAULT_CORE_KW


def get_high_recommend_items(df_weain, df_military, df_nudt):
    """获取各渠道高推荐项目"""
    result = {
        'weain': [],
        'military': [],
        'nudt': []
    }
    
    # 全军武器装备采购信息网
    if len(df_weain) > 0:
        high = df_weain[df_weain['推荐等级'] == '高']
        for _, row in high.iterrows():
            result['weain'].append({
                'title': row['项目名称'][:50],
                'type': row['公告类型'],
                'deadline': row.get('截止日期', '')
            })
    
    # 军队采购网
    if len(df_military) > 0:
        high = df_military[df_military['推荐等级'] == '高']
        for _, row in high.iterrows():
            result['military'].append({
                'title': row['项目名称'][:50],
                'type': row['采购方式'],
                'region': row.get('地区', '')
            })
    
    # 国防科大采购信息网
    if len(df_nudt) > 0:
        high = df_nudt[df_nudt['推荐等级'] == '高']
        for _, row in high.iterrows():
            result['nudt'].append({
                'title': row['项目名称'][:50],
                'type': row['公告类型']
            })
    
    return result


def send_email(date_str, df_weain, df_military, df_nudt, dates_info):
    """发送邮件"""
    # 获取高推荐项目
    high_items = get_high_recommend_items(df_weain, df_military, df_nudt)

    # 构建邮件正文
    body = f"""鹏乐总，您好！

今日军工采购商机采集已完成，汇总如下：

【全军武器装备采购信息网】{len(df_weain)}条（更新日期: {dates_info.get('weain', date_str)}）

高推荐项目：
"""

    for i, item in enumerate(high_items['weain'], 1):
        deadline = f" | 截止{item['deadline']}" if item.get('deadline') else ""
        body += f"{i}. {item['title']}... | {item['type']}{deadline}\n"

    body += f"""
【军队采购网】{len(df_military)}条（更新日期: {dates_info.get('military', date_str)}）

高推荐项目：
"""

    for i, item in enumerate(high_items['military'], 1):
        region = f" | {item['region']}" if item.get('region') else ""
        body += f"{i}. {item['title']}... | {item['type']}{region}\n"

    body += f"""
【国防科大采购信息网】{len(df_nudt)}条（更新日期: {dates_info.get('nudt', date_str)}）

高推荐项目：
"""

    for i, item in enumerate(high_items['nudt'], 1):
        body += f"{i}. {item['title']}... | {item['type']}\n"

    body += """
详情请见附件Excel。

方小程"""

    # 获取Excel文件路径
    excel_path = f"/home/ubuntu/.openclaw/workspace/military-bidding/商机信息汇总_{date_str}.xlsx"

    # 从环境变量加载收件人/抄送人配置
    env_config = load_env_config()
    to_list = env_config['to']
    cc_list = env_config['cc']

    # 构建 MML 格式邮件
    mml_content = build_mml_message(date_str, body, excel_path, to_list, cc_list)

    # 发送邮件
    try:
        send_email_via_himalaya(mml_content, to_list, cc_list)
        print("[SUCCESS] 邮件发送成功")
        return True
    except Exception as e:
        print(f"[ERROR] 邮件发送失败: {e}")
        return False


def build_mml_message(date_str, body, excel_path, to_list, cc_list):
    """构建 MML 格式邮件"""
    # 构建 MML
    msg = f"""From: formulas@formulas.cc
To: {', '.join(to_list)}
Cc: {', '.join(cc_list)}
Subject: 【每日商机采集报告】{date_str}

<#multipart type=mixed>
<#part type=text/plain>
{body}
"""

    # 添加附件
    if excel_path and os.path.exists(excel_path):
        msg += f"<#part filename={excel_path} name={os.path.basename(excel_path)}><#/part>\n"

    msg += "<#/multipart>\n"
    return msg


def send_email_via_himalaya(mml_content, to_list, cc_list):
    """使用 SMTP 发送邮件（凭据从.env加载）"""
    import smtplib
    import re
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.application import MIMEApplication
    from email.header import Header
    from email.utils import formatdate

    # 从环境变量加载SMTP配置
    env_config = load_env_config()
    smtp_config = env_config.get('smtp', {})

    smtp_host = smtp_config.get('host', 'smtp.exmail.qq.com')
    smtp_port = int(smtp_config.get('port', '465'))
    smtp_user = smtp_config.get('user', 'formulas@formulas.cc')
    smtp_password = smtp_config.get('password', '')

    # 解析 MML 内容获取必要信息
    lines = mml_content.split('\n')
    subject = ''
    body = ''
    in_body = False
    attachments = []
    for line in lines:
        if line.startswith('Subject:'):
            subject = line.replace('Subject:', '').strip()
        elif line.startswith('<#part filename='):
            # 解析附件: <#part filename=... name=...>
            match = re.search(r'filename=(\S+)', line)
            name_match = re.search(r'name=([^>/\s]+)', line)
            if match:
                filepath = match.group(1)
                filename = name_match.group(1) if name_match else os.path.basename(filepath)
                attachments.append({'path': filepath, 'name': filename})
        elif line.startswith('<#multipart') or line.startswith('<#part type='):
            in_body = True
        elif line == '<#/multipart>':
            break
        elif in_body and not line.startswith('<#'):
            body += line + '\n'

    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = ', '.join(to_list)
    msg['Cc'] = ', '.join(cc_list)
    msg['Subject'] = subject
    msg['Date'] = formatdate()

    # 添加正文
    msg.attach(MIMEText(body.strip(), 'plain', 'utf-8'))

    # 添加附件
    for att in attachments:
        att_path = att['path']
        att_name = att['name']
        if os.path.exists(att_path):
            with open(att_path, 'rb') as f:
                # 使用 MIMEApplication，正确设置 xlsx 类型
                part = MIMEApplication(f.read(), _subtype='xlsx')
            # 正确编码中文文件名
            filename_encoded = Header(att_name, 'utf-8').encode()
            part.add_header('Content-Disposition', 'attachment',
                            filename=filename_encoded)
            msg.attach(part)
            print(f"[INFO] 已添加附件: {att_name}")
        else:
            print(f"[WARNING] 附件不存在: {att_path}")

    # 发送邮件
    smtp = smtplib.SMTP_SSL(smtp_host, smtp_port)
    smtp.login(smtp_user, smtp_password)
    smtp.send_message(msg)
    smtp.quit()
    return True


def send_bidding_report(date=None, keywords=None, regions=None, yesterday=True):
    """
    发送商机报告邮件
    
    Args:
        date: 日期，格式 YYYY-MM-DD，默认自动获取各渠道最新日期
        keywords: 关键词列表
        regions: 地区字典
        yesterday: 是否统一获取昨日数据（默认True，解决军队采购网白天更新的问题）
    """
    from datetime import datetime, timedelta
    
    # 记录是否为昨日模式
    is_yesterday = yesterday
    
    # 如果没有指定日期，则根据 yesterday 参数决定
    if date is None:
        if yesterday:
            # 获取昨日日期（统一日期，解决军队采购网白天更新的问题）
            yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            date = yesterday_date
            print(f"[INFO] 统一获取昨日商机: {date}")
        else:
            # 原有逻辑：自动获取各渠道最新日期
            date = None
    
    # 如果没有指定日期，则自动获取最新日期
    auto_latest = (date is None)
    
    print(f"[INFO] 开始抓取商机信息 - 自动获取最新日期: {auto_latest}")
    
    # 延迟导入
    fetch_all_bidding, _ = _import_fetcher()
    
    # 抓取数据（不传date，这样会自动获取最新日期）
    result = fetch_all_bidding(date=date, auto_latest=auto_latest)
    
    if len(result) == 4:
        df_weain, df_military, df_nudt, dates_info = result
        # 使用实际查询日期作为文件名（如果是昨日模式则用昨日，否则用今天）
        if is_yesterday:
            file_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            file_date = datetime.now().strftime('%Y-%m-%d')
    else:
        df_weain, df_military, df_nudt = result
        dates_info = {'weain': date, 'military': date, 'nudt': date}
        file_date = date if date else datetime.now().strftime('%Y-%m-%d')
    
    print(f"[INFO] 采集完成: 全军{len(df_weain)}条, 军队{len(df_military)}条, 国防科大{len(df_nudt)}条")
    
    # 发送邮件
    send_email(file_date, df_weain, df_military, df_nudt, dates_info)
    
    return df_weain, df_military, df_nudt


# CLI入口
if __name__ == '__main__':
    import argparse
    import fcntl
    import time
    
    # 锁文件路径
    LOCK_FILE = '/tmp/bidding_email.lock'
    
    # 检查并获取锁
    try:
        lock_fd = open(LOCK_FILE, 'w')
        # 非阻塞模式尝试获取锁，如果失败说明已有进程在运行
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (IOError, OSError):
        print("[INFO] 已有任务在运行，跳过本次执行")
        sys.exit(0)
    
    parser = argparse.ArgumentParser(description='军工采购商机邮件发送工具')
    parser.add_argument('--date', type=str, help='日期，格式 YYYY-MM-DD')
    parser.add_argument('--keywords', type=str, help='关键词，逗号分隔')
    parser.add_argument('--no-yesterday', action='store_true', help='禁用昨日模式，获取各渠道最新日期（默认启用昨日模式）')
    
    args = parser.parse_args()
    
    # 解析关键词
    keywords = None
    if args.keywords:
        keywords = args.keywords.split(',')
    
    # 发送报告（默认获取昨日数据）
    try:
        send_bidding_report(date=args.date, keywords=keywords, yesterday=not args.no_yesterday)
    finally:
        # 释放锁
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()
        try:
            os.remove(LOCK_FILE)
        except:
            pass
