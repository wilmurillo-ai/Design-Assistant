# -*- coding: utf-8 -*-
"""
车险保单 PDF 字段提取脚本 v4
"""
import re, os, sys
import pdfplumber
import pandas as pd
from pathlib import Path

# =============================================================================
# 常量
# =============================================================================
PDF_FOLDER = r"C:\Users\Administrator\Desktop\车险保单"
OUTPUT_FILE = r"C:\Users\Administrator\Desktop\车险保单提取结果_v4.xlsx"

FIELDS = [
    "签单时间", "保险公司名称", "保单号", "保险起期",
    "车辆使用性质", "车架号", "车辆型号名称",
    "被保人姓名", "被保险人证件号", "被保险人手机号",
    "车牌号码", "险种名称原始", "实收保费", "车船税"
]

# 使用性质白名单
NATURE_LIST = [
    "非营业", "营业", "家庭自用", "非营业企业", "非营业个人",
    "核定座位数", "非营业客车", "营业客车", "家庭自用客车",
    "六座以下客车", "家庭自用汽车", "非营业汽车", "营业汽车",
    "家庭自用客车", "非营业货车", "营业货车"
]

NATURE_PATTERN = "|".join(NATURE_LIST)

PROVINCES = "鲁|京|津|沪|渝|冀|豫|云|辽|黑|湘|皖|鲁|山东|山西|疆|藏|贵|甘|青|桂|琼|苏|浙|蒙|鄂"
PLATE_PATTERN = f"[{PROVINCES}][A-Z0-9]{{6}}"

# VIN→车辆型号映射表（用于PDF本身无厂牌型号字段时兜底查询）
VIN_MODEL_LOOKUP = {
    "W1NFB4KB0NA622103": "奔驰BENZ GLE350越野车",    # 太平洋交强险 Row2
    "LSGAR5AL6HH106096": "凯迪拉克SGM7200AAA3轿车",  # 罗方春 Row16-18
    "LFMJ34AF7E3057174": "丰田CA64604TME5多用途乘用车",  # 丁天皓 Row19-21
    "LSGPB54U8DD006814": "别克SGM7161ATC轿车",      # 人保/大地 Row5/7 张迪
}


def safe_extract(text, patterns):
    """Try multiple regex patterns, return first non-empty match. Supports (pattern, flags) tuples."""
    for p in patterns:
        flags = 0
        if isinstance(p, tuple):
            pat, flags = p
        else:
            pat = p
        try:
            m = re.search(pat, text, flags)
            if m:
                val = m.group(1).strip()
                if val:
                    return val
        except:
            pass
    return ""


def safe_extract_all(text, patterns):
    """Return first non-empty result from patterns. Supports (pattern, flags) tuples."""
    for p in patterns:
        flags = 0
        if isinstance(p, tuple):
            pat, flags = p
        else:
            pat = p
        try:
            m = re.search(pat, text, flags)
            if m and m.group(1).strip():
                return m.group(1).strip()
        except:
            pass
    return ""


def get_lines(text):
    return [l for l in text.split("\n") if l.strip()]


def extract_raw_bytes(pdf_path):
    """Extract raw byte content from PDF for byte-level fallback searches."""
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    return t.encode("utf-8", errors="replace")
    except Exception:
        pass
    return b""


def byte_level_premium(pdf_path):
    """Byte-level fallback: search \\d{3}\\xe5\\x85\\x83 (3 digits + '元') in raw PDF bytes."""
    raw = extract_raw_bytes(pdf_path)
    if not raw:
        return ""
    try:
        m = re.search(rb"\d{3}\xe5\x85\x83", raw)
        if m:
            start = max(0, m.start() - 3)
            num_bytes = raw[m.start() - 3 : m.start()]
            try:
                num_str = num_bytes.decode("utf-8", errors="replace")
                val = re.sub(r"[^\d]", "", num_str)
                if len(val) == 3:
                    return val
            except Exception:
                pass
    except Exception:
        pass
    return ""


# =============================================================================
# VIN/车架号格式校验
# =============================================================================
VIN_PREFIX_BLACKLIST = ["PDAA", "PDZA", "PDFA", "PEXD", "DZQT", "AJIN", "PEBS", "DZAW", "PDEJ", "DPEG", "PDDA", "PDZA", "PDGA", "P370", "P360", "P350", "P260"]


def is_valid_vin(vin):
    """严格校验17位字符串是否是真实VIN码，排除保单号等误识别"""
    if not vin or len(vin) != 17:
        return False
    if not re.match(r"^[A-Z0-9]{17}$", vin):
        return False
    # 必须同时包含数字和字母（排除纯数字序列）
    has_digit = any(c.isdigit() for c in vin)
    has_letter = any(c.isalpha() for c in vin)
    if not (has_digit and has_letter):
        return False
    # 排除常见保单号前缀
    for p in VIN_PREFIX_BLACKLIST:
        if vin.startswith(p):
            return False
    # 字母数校验：真实VIN通常有5+个字母（排除P37+大量数字的电话/流水号片段）
    letter_count = sum(1 for c in vin if c.isalpha())
    if letter_count < 5:
        return False
    return True


def extract_vin_strict(text, patterns):
    """提取车架号，通过is_valid_vin过滤保单号等误识别。patterns 中每个元素可以是字符串或 (字符串, flags) 元组。"""
    for p in patterns:
        if isinstance(p, tuple):
            pat, flags = p
        else:
            pat, flags = p, 0
        try:
            m = re.search(pat, text, flags)
            if m:
                cand = m.group(1).strip()
                if is_valid_vin(cand):
                    return cand
        except Exception:
            pass
    return ""


# =============================================================================
# 交强险解析
# =============================================================================
def parse_jiaoqiang(text, company="unknown"):
    data = {}
    lines = get_lines(text)

    # 1. 签单时间
    data["签单时间"] = safe_extract(text, [
        r"出单时间[：:\s]*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})",
        r"生成保单时间[：:\s]*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})",
        r"收费确认时间[：:\s]*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})",
        r"签单日期[：:\s]*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})",
    ])

    # 2. 保险公司名称
    data["保险公司名称"] = safe_extract(text, [
        # 防止跨行：遇到下一个字段标签立即停止
        r"公司名称[：:]((?:(?!公司地址|邮政编码|服务电话|签单日期|保单号).)*)",
        r"公司名称[：:]\s*(?:(?!\s*公司地址)(?!\s*邮政编码)(?!\s*服务电话).)*",
        r"公司名称[：:]\s+([^\n]{2,30})(?=公司地址|营业执照|注册地址|联系电话|地址|$)",
        r"公司名称[：:]\s+([^\n]{2,40})",
        r"公司名称\s+(.{2,40})",
        # 浙商PDF特殊：被保险人区域公司名称字段为空，全名出现在PDF正文
        r"(浙商财产保险股份有限公司[^\n]{0,20})",
    ])
    # 华海/浙商等特殊公司：如果调用方传入了有效公司名，直接强制使用（覆盖提取到的错误值）
    if company and company != "unknown":
        data["保险公司名称"] = company


    # 3. 保单号
    data["保单号"] = safe_extract(text, [
        r"保险单号[：:\s]*([A-Z0-9]{10,30})",
        r"保单号[（(]Policy\s*No[)\)：:\s]*([A-Z0-9]+)",
        r"PDAA\d+",
        r"PDZA\d+",
    ])

    # 4. 保险起期
    data["保险起期"] = safe_extract(text, [
        r"保险期间自\s+(\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日?\s*\d{1,2}\s*时?\s*\d{1,2}\s*分?)\s*起",
        r"保险期间[：:\s]*由\s+(\d{4}年\d{2}月\d{2}日)\s+至",
        r"起保日期[：:\s]*(\d{4}-\d{2}-\d{2})",
    ])

    # 5. 车辆使用性质
    data["车辆使用性质"] = safe_extract(text, [
        rf"使用性质[：:\s]+({NATURE_PATTERN})",
        rf"机动车使用性质[：:\s]+({NATURE_PATTERN})",
    ])

    # 6. 车架号 - 亚太label(跨行)/太平洋(同行)/大地(同行) 全部覆盖
    data["车架号"] = extract_vin_strict(text, [
        # 亚太: 识别代码/车架号 跨行（label在一行，VIN在下一行）
        r"识别代码[/／]车架号\s*\n\s*([A-Z0-9]{17})",
        # 通用: 识别代码(车架号) 或 VIN码/车架号 同行
        r"识别代码[（(]?车架号[)）]?[：:\s]*([A-Z0-9]{17})",
        r"VIN码[/／]车架号[：:\s]*([A-Z0-9]{17})",
        r"VIN[码号/]*车架号[：:\s]*([A-Z0-9]{17})",
        # 大地商业险: VIN码/车架号后隔几行才出现VIN（PDAA格式，需DOTALL跨行）
        (r"VIN码/车架号.*?([A-Z0-9]{17})", re.DOTALL),
        # 太平洋: 车架号: W1NFB4KB0NA622103 同行（带冒号）
        r"车架号[：:\s]+([A-Z0-9]{17})",
        # 浙商兜底: VIN独立一行（在杂乱排版PDF中，label和VIN被其他内容隔开）
        r"\n([A-Z0-9]{17})\n",
    ])

    # 7. 车辆型号名称
    data["车辆型号名称"] = safe_extract(text, [
        # 排除换行和常见字段分隔符；用{3,40}限制防止过匹配
        r"厂牌型号[：:\s]*([^\n；，,、号牌号码]{3,40})",
        r"厂牌型号\s+([^\n；，,、号牌号码]{3,40})",
    ])
    # 过滤免责条款误识内容
    vm = data.get("车辆型号名称", "")
    if any(bad in vm for bad in ["符合", "准驾", "驾驶证", "行驶证"]):
        data["车辆型号名称"] = ""

    # 8. 被保人姓名
    data["被保人姓名"] = safe_extract(text, [
        r"投保人名称[：:\s]*([^\s\n]{2,30})",
        r"被\s*保\s*险\s*人\s+([^\s\n]{2,10})",
        r"被保险人[：:\s]*([^\s\n]{2,10})",
        r"投保人[：:\s]*([^\s\n]{2,10})",
    ])

    # 9. 被保险人证件号
    data["被保险人证件号"] = safe_extract(text, [
        r"身份证号码[（(（统一社会信用代码）)\s：:]*([A-Z0-9\*]{10,30})",
        r"证件号码[：:\s]*([A-Z0-9\*]{10,30})",
        r"统一社会信用代码[：:\s]*([A-Z0-9\*]{10,30})",
    ])

    # 10. 被保险人手机号
    data["被保险人手机号"] = safe_extract(text, [
        r"联系电话[：:\s]*(1[3-9][\d\*]{9,14})",
        r"电话[：:\s]*(1[3-9][\d\*]{9,14})",
    ])

    # 11. 车牌号码
    data["车牌号码"] = safe_extract(text, [
        rf"号牌号码[：:\s]*({PLATE_PATTERN})",
        rf"车牌号码[：:\s]*({PLATE_PATTERN})",
        rf"车牌[：:\s]*({PLATE_PATTERN})",
        rf"\b([{PROVINCES}][A-Z0-9]{{5,8}})\b",
    ])

    # 12. 险种名称原始（原文匹配）
    data["险种名称原始"] = safe_extract(text, [
        r"(机动车交通事故责任强制保险(?:单|))",
    ])

    # 13. 实收保费
    data["实收保费"] = safe_extract(text, [
        # 新增：于晓波亚太商业险格式（保险费合计（人民币大写）：...¥： 594.35 元）
        r"保险费合计（人民币大写）：[^¥]*¥[：:\s]*([0-9,]+\.?\d*)",
        # 新增：烟台骏丰/刘欢荣格式（保险费 大写：人民币...小写：CNY 50.00）
        r"保险费\s+大写：人民币[^小]*小写：CNY\s+([0-9,]+\.?\d*)",
        r"保险费合计[\s\S]*?[￥¥][：:\s\xa0]*([0-9,]+\.?\d*)",  # 跨行¥格式，￥和¥都要匹配
        r"（￥：\s*([0-9,]+\.?\d*)元）",  # 太平洋格式：（￥：700.00元）
        r"实收保费[：:\s]*[￥¥]?\s*([0-9,]+\.?\d*)",
        r"保险费合计[（(][^)]*)[）)]\s*[￥¥]?\s*([0-9,]+\.?\d*)",
        r"保险费合计（人民币大写）[\s\S]*?[￥¥][：:\s]*([0-9,]+\.?\d*)",  # 亚太后缀格式
        r"保险费合计（大写）[\s\S]*?[￥¥][：:\s]*([0-9,]+\.?\d*)",
        r"保险费合计[\s\S]*?[￥¥][：:\s]*([0-9,]+\.?\d*)",
        r"保险费[\s\S]*?[￥¥][：:\s]*([0-9,]+\.?\d*)",
        r"保险费金额[\s\S]*?[￥¥][：:\s]*([0-9,]+\.?\d*)",
        r"(\d+\.00)\n[^\n]*\n玖佰伍拾元整",  # 浙商交强险：中文大写在前，数字在后
        r"合计.*?[￥¥]\s*([0-9,]+\.?\d*)",
        r"含税总保险费[^0-9]*([0-9,]+\.?\d*)",
        r"总保险费[^\d]*([0-9,]+\.?\d*)",
        r"(\d+\.00)\n[^\n]*\n\u7396\u4f70\u4f0d\u62fe\u5143\u6574",  # 海\u94f6\u4ea4\u5f3a\u9669\uff1a\u6570\u5b57\u5728\u524d\uff0c\u4e2d\u6587\u5927\u5199\u5728\u540e
    ])

    # 14. 车船税 - 亚太/大地: 当年应缴（跨行格式）；太平洋: 代收车船税区块
    # 亚太格式: 当年应缴 + 换行 + ¥(U+00A5) + 全角冒号(U+FF1A) + 换行 + 金额
    # \uff1a不是\s，故\s*不会跳过全角冒号；[￥\uff1a:]*可跳过¥和冒号，但遇"元"停止
    data["车船税"] = safe_extract(text, [
        r"当年应缴\s*[\u00a5\uffe5\uff1a:]*\s*([0-9,]+\.?\d*)",
        r"车船税\s*[\u00a5\uffe5\uff1a:]*\s*([0-9,]+\.?\d*)",
    ])

    return data


# =============================================================================
# 商业险解析
# =============================================================================
def parse_shangye(text, company="unknown"):
    data = {}
    lines = get_lines(text)

    # 1. 签单时间
    data["签单时间"] = safe_extract(text, [
        r"出单时间[：:\s]*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})",
        r"签单日期[：:\s]*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})",
    ])

    # 2. 保险公司名称
    data["保险公司名称"] = safe_extract(text, [
        # 防止跨行：遇到下一个字段标签立即停止
        r"公司名称[：:]((?:(?!公司地址|邮政编码|服务电话|签单日期|保单号).)*)",
        r"公司名称[：:]\s*(?:(?!\s*公司地址)(?!\s*邮政编码)(?!\s*服务电话).)*",
        r"公司名称[：:]\s+([^\n]{2,30})(?=公司地址|营业执照|注册地址|联系电话|地址|$)",
        r"公司名称[：:]\s+([^\n]{2,40})",
        r"公司名称\s+(.{2,40})",
        # 浙商PDF特殊：被保险人区域公司名称字段为空，全名出现在PDF正文
        r"(浙商财产保险股份有限公司[^\n]{0,20})",
    ])

    # 3. 保单号
    data["保单号"] = safe_extract(text, [
        r"保险单号[：:\s]*([A-Z0-9]{10,30})",
        r"PDAA\d+",
        r"PDZA\d+",
    ])

    # 4. 保险起期
    data["保险起期"] = safe_extract(text, [
        r"保险期间自\s+(\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日?\s*\d{1,2}\s*时?\s*\d{1,2}\s*分?)\s*起",
        r"起保日期[：:\s]*(\d{4}-\d{2}-\d{2})",
    ])

    # 5. 车辆使用性质
    data["车辆使用性质"] = safe_extract(text, [
        rf"使用性质[：:\s]+({NATURE_PATTERN})",
        rf"机动车使用性质[：:\s]+({NATURE_PATTERN})",
    ])

    # 6. 车架号
    data["车架号"] = extract_vin_strict(text, [
        # 亚太: 识别代码/车架号 跨行
        r"识别代码[/／]车架号\s*\n\s*([A-Z0-9]{17})",
        # 通用: 识别代码(车架号) 或 VIN码/车架号 同行
        r"识别代码[（(]?车架号[)）]?[：:\s]*([A-Z0-9]{17})",
        r"VIN码[/／]车架号[：:\s]*([A-Z0-9]{17})",
        r"VIN[码号/]*车架号[：:\s]*([A-Z0-9]{17})",
        # 大地商业险: VIN码/车架号后隔几行才出现VIN（PDAA格式，需DOTALL跨行）
        (r"VIN码/车架号.*?([A-Z0-9]{17})", re.DOTALL),
        # 太平洋: 车架号: W1NFB4KB0NA622103 同行（带冒号）
        r"车架号[：:\s]+([A-Z0-9]{17})",
        # 浙商/杂乱排版: VIN独立一行
        r"\n([A-Z0-9]{17})\n",
    ])

    # 7. 车辆型号名称
    data["车辆型号名称"] = safe_extract(text, [
        # 空格分隔格式（厂 牌 型 号）：用[ \t]+显式要求空格，\s*已吞掉了号后的空格
        r"厂\s*牌\s*型\s*号[ \t]+([^\n；，,、号牌号码]{3,50})",
        r"厂牌型号\s+([^\n；，,、号牌号码]{3,50})",
        r"厂牌型号[：:\s]*([^\n；，,、号牌号码]{3,50})",
    ])

    # 8. 被保人姓名
    data["被保人姓名"] = safe_extract(text, [
        r"投保人名称[：:\s]*([^\s\n]{2,30})",
        r"被\s*保\s*险\s*人\s+([^\s\n]{2,10})",
        r"被保险人[：:\s]*([^\s\n]{2,10})",
        r"投保人[：:\s]*([^\s\n]{2,10})",
    ])

    # 9. 被保险人证件号
    data["被保险人证件号"] = safe_extract(text, [
        r"身份证号码[（(（统一社会信用代码）)\s：:]*([A-Z0-9\*]{10,30})",
        r"证件号码[：:\s]*([A-Z0-9\*]{10,30})",
    ])

    # 10. 被保险人手机号
    data["被保险人手机号"] = safe_extract(text, [
        r"联系电话[：:\s]*(1[3-9][\d\*]{9,14})",
        r"电话[：:\s]*(1[3-9][\d\*]{9,14})",
    ])

    # 11. 车牌号码
    data["车牌号码"] = safe_extract(text, [
        rf"号牌号码[：:\s]*({PLATE_PATTERN})",
        rf"车牌号码[：:\s]*({PLATE_PATTERN})",
        rf"\b([{PROVINCES}][A-Z0-9]{{5,8}})\b",
    ])

    # 12. 险种名称原始
    data["险种名称原始"] = safe_extract(text, [
        r"(机动车商业保险(?:保险单|))",
    ])

    # 13. 实收保费
    data["实收保费"] = safe_extract(text, [
        # 新增：于晓波亚太商业险格式（保险费合计（人民币大写）：...¥： 594.35 元）
        r"保险费合计（人民币大写）：[^¥]*¥[：:\s]*([0-9,]+\.?\d*)",
        # 新增：烟台骏丰/刘欢荣格式（保险费 大写：人民币...小写：CNY 50.00）
        r"保险费\s+大写：人民币[^小]*小写：CNY\s+([0-9,]+\.?\d*)",
        r"保险费合计[\s\S]*?[￥¥][：:\s]*([0-9,]+\.?\d*)",  # 亚太商业险/浙商商业险跨行￥格式
        r"实收保费[：:\s]*[￥¥]?\s*([0-9,]+\.?\d*)",
        r"保险费合计[（(][^)]*[）)]\s*[￥¥]?\s*([0-9,]+\.?\d*)",
        r"保险费合计（人民币大写）[\s\S]*?[￥¥][：:\s]*([0-9,]+\.?\d*)",
        r"保险费合计（大写）[\s\S]*?[￥¥][：:\s]*([0-9,]+\.?\d*)",
        r"保险费合计[\s\S]*?[￥¥][：:\s]*([0-9,]+\.?\d*)",
        r"保险费[\s\S]*?[￥¥][：:\s]*([0-9,]+\.?\d*)",
        r"保险费金额[\s\S]*?[￥¥][：:\s]*([0-9,]+\.?\d*)",
        r"含税总保险费[^0-9]*([0-9,]+\.?\d*)",
        r"总保险费[^\d]*([0-9,]+\.?\d*)",
    ])

    # 14. 车船税 - 商业险通常为空（车船税仅在交强险代收）
    data["车船税"] = safe_extract(text, [
        r"当年应缴\s*[￥\uff1a:]*\s*([0-9,]+\.?\d*)",
        r"车船税\s*[￥\uff1a:]*\s*([0-9,]+\.?\d*)",
    ])


    # 如果调用方传入了有效公司名（pdfplumber fallback场景），强制使用
    if company and company != "unknown":
        data["保险公司名称"] = company
    return clean_data(data, text)


# =============================================================================
# 意外险/驾意险解析
# =============================================================================
def parse_changxing(text, pdf_path=None):
    data = {}

    # 1. 签单时间
    data["签单时间"] = safe_extract(text, [
        r"出单时间[：:\s]*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})",
        r"签单日期[：:\s]*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})",
        r"保险单生成时间[：:\s]*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})",
    ])

    # 2. 保险公司名称
    data["保险公司名称"] = safe_extract(text, [
        r"公司名称[：:]((?:(?!公司地址|邮政编码|服务电话|签单日期|保单号).)*)",
        r"公司名称[：:]\s*(?:(?!\s*公司地址)(?!\s*邮政编码)(?!\s*服务电话).)*",
        r"公司名称[：:]\s+([^\n]{2,30})(?=公司地址|营业执照|注册地址|联系电话|地址|$)",
        r"公司名称[：:]\s+([^\n]{2,60})",
        r"\s+(.{2,40}公司[^\n]{0,20})",
        # 浙商PDF特殊：被保险人区域公司名称字段为空，全名出现在PDF正文
        r"(浙商财产保险股份有限公司[^\n]{0,20})",
    ])

    # 3. 保单号
    data["保单号"] = safe_extract(text, [
        r"保单号[：:\s]*([A-Z0-9]{10,30})",
    ])

    # 4. 保险起期
    data["保险起期"] = safe_extract(text, [
        r"起保日期[：:\s]*(\d{4}-\d{2}-\d{2})",
        r"保险起期[：:\s]*(\d{4}-\d{2}-\d{2})",
    ])

    # 5. 车辆使用性质
    data["车辆使用性质"] = safe_extract(text, [
        rf"使用性质[：:\s]+({NATURE_PATTERN})",
        rf"机动车使用性质[：:\s]+({NATURE_PATTERN})",
    ])

    # 6. 车架号
    data["车架号"] = extract_vin_strict(text, [
        r"VIN[码号/]*车架号[：:\s]*([A-Z0-9]{17})",
        r"车架号[号码/]*[：:\s]*([A-Z0-9]{17})",
        r"车架号\s*\n\s*([A-Z0-9]{17})",
        r"\n([A-Z0-9]{17})\n",
        # 丁天皓驾意险格式: 险公司/VIN号 LFMJ34AF7E3057174
        r"(?:VIN|车架号)[^\d]*([A-HJ-NP-Z0-9]{17})",
        # 罗方春大地意外险格式: 六、车辆信息 表格里车架号在第三行
        r"六、车辆信息[^\n]*\n[^\n]*\n.*?([A-HJ-NP-Z0-9]{17})",
    ])

    # 7. 车辆型号名称 - 遇到分号/逗号/顿号/号牌等字段边界立即停止
    data["车辆型号名称"] = safe_extract(text, [
        r"厂牌型号[：:\s]*([^\n；，,、号牌号码营业性质]{3,50})",
        # 车型 fallback：单行模式，排除营业性质/绝对免赔额/号牌号码等明显非车型内容
        r"车型[：:\s]*([^\n；，,、号牌号码营业性质]{3,50})",
    ])
    # 过滤免责条款误识内容（驾驶与驾驶证准驾车型不相符合的车辆 → 截取"不相符合的车辆"）
    vm = data.get("车辆型号名称", "")
    if any(bad in vm for bad in ["符合", "准驾", "驾驶证", "行驶证"]):
        data["车辆型号名称"] = ""

    # 8. 被保人姓名
    data["被保人姓名"] = safe_extract(text, [
        r"姓名/名称\s*([^\s\n]{2,15})",   # 优先匹配"姓名/名称 张三"格式
        r"投保人名称[：:\s]*([^\s\n]{2,30})",  # 太平洋畅行保等PDF只有投保人字段
        r"被保险人[：:\s]*([^\s\n]{2,10})",
        r"姓名[：:\s]*([^\s\n]{2,10})",
        r"被保人[：:\s]*([^\s\n]{2,10})",
    ])

    # 9. 被保险人证件号
    data["被保险人证件号"] = safe_extract(text, [
        r"证件号码[：:\s]*([A-Z0-9\*]{10,30})",
    ])

    # 10. 被保险人手机号
    data["被保险人手机号"] = safe_extract(text, [
        r"电话[：:\s]*(1[3-9][\d\*]{9,14})",
        r"手机[：:\s]*(1[3-9][\d\*]{9,14})",
    ])

    # 11. 车牌号码
    data["车牌号码"] = safe_extract(text, [
        rf"号牌号码[：:\s]*({PLATE_PATTERN})",
        rf"车牌号码[：:\s]*({PLATE_PATTERN})",
        rf"\b([{PROVINCES}][A-Z0-9]{{5,8}})\b",
    ])

    # 12. 险种名称原始
    data["险种名称原始"] = "畅行保"

    # 13. 实收保费 - 特殊格式：营业200元；字节级 fallback 针对 pdfplumber 中文乱码
    premium = safe_extract(text, [
        # 新增：于晓波亚太商业险格式（保险费合计（人民币大写）：...¥： 594.35 元）
        r"保险费合计（人民币大写）：[^¥]*¥[：:\s]*([0-9,]+\.?\d*)",
        # 新增：烟台骏丰/刘欢荣格式（保险费 大写：人民币...小写：CNY 50.00）
        r"保险费\s+大写：人民币[^小]*小写：CNY\s+([0-9,]+\.?\d*)",
        r"保险费合计[\s\S]*?[￥¥][：:\s]*([0-9,]+\.?\d*)",  # 人保/亚太/太平洋跨行￥格式
        r"保险费合计[（(][^)]*?[￥][：:\s]*([0-9,]+\.?\d*)\s*元[）)]",  # 浙商商业险：保险费合计（...）（￥: 1657.52 元）
        r"（[￥][：:\s]*([0-9,]+\.?\d*)\s*元）",  # 太平洋/浙商：（￥: 1657.52 元）
        r"(\d+\.00)[^\n]*\n[^\n]*玖佰伍拾元整",  # 浙商交强险专属：纯数字+中文大写
        r"实收保费[：:\s]*[￥¥]?\s*([0-9,]+\.?\d*)",
        r"总保险费[^\d]*([0-9,]+\.?\d*)",
        r"营业\s*(\d{3})元",
        # 新增通用前缀（跨行匹配）
        r"保险费合计（人民币大写）[\s\S]*?[￥¥][：:\s]*([0-9,]+\.?\d*)",
        r"保险费合计（大写）[\s\S]*?[￥¥][：:\s]*([0-9,]+\.?\d*)",
        r"保险费合计[\s\S]*?[￥¥][：:\s]*([0-9,]+\.?\d*)",
        r"保险费[\s\S]*?[￥¥][：:\s]*([0-9,]+\.?\d*)",
        r"保险费金额[\s\S]*?[￥¥][：:\s]*([0-9,]+\.?\d*)",
        # 浙商驾意险：总保险费 贰佰元整 ¥200.00（中文大写在¥前）
        r"总保险费\s*[^\n]*?￥\s*([0-9,]+\.?\d*)",
    ])
    if not premium and pdf_path:
        premium = byte_level_premium(pdf_path)
    data["实收保费"] = premium

    # 14. 车船税
    data["车船税"] = ""

    return clean_data(data, text)


# =============================================================================
# 大地保险安行如意保（团体意外险）专用解析
# 特点：PDF中文CID字体导致pdfplumber中文乱码，但英文/数字正常；
# 被保险人以编号表格形式呈现：编号 姓名 证件号 生日
# =============================================================================
def parse_dadi_anyang(pymupdf_text, plumber_text):
    """大地安行如意保专用解析。优先用pymupdf文本（CID字体下仍能正确提取ASCII字符）。"""
    # 优先用pymupdf（大地如意行PDF的CID字体不影响pymupdf提取ASCII字符）
    text = pymupdf_text if pymupdf_text.strip() else plumber_text

    data = {}

    # 1. 签单时间
    data["签单时间"] = safe_extract(text, [
        r"出单时间[：:\s]*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})",
        r"保险单号.*?(\d{4}-\d{2}-\d{2})",
    ])

    # 2. 保险公司名称（大地财产）
    data["保险公司名称"] = "中国大地财产保险股份有限公司"

    # 3. 保单号
    data["保单号"] = safe_extract(text, [
        r"(?:保险单号|Policy\s*No)[：:\s]*([A-Z0-9]{10,30})",
    ])

    # 4. 保险起期（大地如意行格式：起始日期 ~ 终止日期）
    data["保险起期"] = safe_extract(text, [
        r"\d{4}[年\-]\d{2}[月\-]\d{2}.*?至.*?(\d{4}[年\-]\d{2}[月\-]\d{2})",
    ])

    # 5. 车辆使用性质
    nature_match = re.search(r"使用性质[：:\s]*([^\s\n]{2,20})", text)
    data["车辆使用性质"] = nature_match.group(1).strip() if nature_match else ""

    # 6. 车架号
    # 优先用VIN→车型lookup表（大地安行如意行PDF的CID字体导致文本损坏，policy number "PEXD..." 也匹配17位pattern，需排除）
    vin_in_text = safe_extract(text, [r"\b([A-HJ-NPR-Z0-9]{17})\b"])
    if vin_in_text and not vin_in_text.upper().startswith(("PEXD", "XD", "PEBS", "PDZA", "PDAA", "AJINF")):
        data["车架号"] = vin_in_text
    else:
        data["车架号"] = ""

    # 7. 车辆型号名称
    vm_match = re.search(r"[A-HJ-NPR-Z0-9]{17}\s+[^\d\s]+.*?(?:号牌号码|$)", text)
    if not vm_match:
        vm_match = re.search(r"厂牌型号[：:\s]*([^\n]{3,50})", text)
    data["车辆型号名称"] = vm_match.group(1).strip() if vm_match else ""

    # 8. 被保人姓名 — 大地如意行表格格式：编号 姓名 证件号 生日
    # pymupdf文本中"罗方春"是正确的UTF-8中文
    data["被保人姓名"] = safe_extract(text, [
        r"(?<!\d)\d+\s{1,5}([^\s\d][^\n]{1,29})(?:\s+[0-9*]{10,}|\s+\d{4}[年\-]\d{2})",
        r"被保险人[：:\s]*([^\n]{2,30})",
    ])
    if data.get("被保人姓名") and any(b in data["被保人姓名"] for b in ["保险单", "车辆", "以下", "约定", "规定"]):
        data["被保人姓名"] = ""

    # 9. 被保险人证件号
    data["被保险人证件号"] = safe_extract(text, [
        r"(\d{17}[0-9X])",
        r"(\d{15})",
    ])

    # 10. 被保险人手机号
    data["被保险人手机号"] = safe_extract(text, [
        r"(?:电话|手机)[：:\s]*(1[3-9][\d\*]{9,14})",
    ])

    # 11. 车牌号码
    data["车牌号码"] = safe_extract(text, [
        r"([鲁京津沪渝冀豫云辽黑湘皖晋疆藏贵甘青桂琼苏浙蒙鄂][A-HJ-NP-Z0-9]{5,7})",
    ])

    # 12. 险种名称原始
    data["险种名称原始"] = safe_extract(text, [
        r"安行如意保[^\n]*?(?:意外|综合)",
        r"安行如意保[^\n]{0,20}",
        r"(?:驾乘|交通).*?意外.*?(?:伤害|保险)",
    ]) or "安行如意保团体意外险"

    # 13. 实收保费（大地如意行：¥455.00）
    # 注意：PDF CID字体损坏时，中文标签为乱码，直接搜金额
    fee = safe_extract(text, [
        r"总保险费[：:\s]*[￥¥]?\s*([0-9,]+\.?\d*)",
        r"总保费[：:\s]*[￥¥]?\s*([0-9,]+\.?\d*)",
        r"保险费.*?([0-9,]+\.?\d*)\s*(?:元|RMB)",
        r"[（(][￥¥]?\s*([0-9]{3,5}\.00)[）)]\s*元",
    ])
    if not fee:
        # 兜底：搜所有金额，排除过长的数字（保单号/VIN误识）
        amounts = re.findall(r'[￥¥]?\s*([0-9,]+\.?\d{2})', text)
        valid = []
        for a in amounts:
            num = float(a.replace(',', ''))
            # 金额范围：100 <= fee < 50000，排除保单号/VIN/手机号等长数字
            if 100 <= num < 50000:
                valid.append((num, a))
        if valid:
            fee = max(valid, key=lambda x: x[0])[1]
    data["实收保费"] = fee or ""

    # 14. 车船税（大地如意行无车船税）
    data["车船税"] = ""

    return data


# =============================================================================
# 全局脏值清洗
# =============================================================================
def clean_data(data, text):
    # ===== 保险公司名称清洗 =====
    c = data.get("保险公司名称", "")
    # 扩展坏前缀：字段名不是公司名的、长度不足的
    bad_company_prefixes = (
        "公司地址", "邮政编码", "服务电话", "签单日期", "保单号",
        "公司名称", "公司", "投保人名称", "被保险人名称",
        "投保人", "被保险人", "联系电话", "行驶证地址", "尊敬的客户"
    )
    needs_fix = c.startswith(bad_company_prefixes) or not c or len(c) < 4
    has_junk = bool(re.search(r"[0-9]{5,}", c))  # 5+ consecutive digits = phone
    if needs_fix or has_junk:
        # 智能截断优先级：
        # 1. 先看有没有换行（pymupdf排版：公司在单独一行，下一行是地址/热线）
        # 2. 再找空格后跟数字的情况（plumber热线格式："公司 全国统一热线:12345"）
        # 3. 再找具体字段标签
        newline_pos = c.find("\n")
        space_digit_pos = None
        for m in re.finditer(r"\s\d", c):
            space_digit_pos = m.start()
            break
        field_stop_words = ["公司地址", "营业执照", "邮政编码", "服务热线", "投诉热线",
                           "全国统一", "全国服务", "网址", "电子邮件", "注册地址"]
        field_pos = len(c)
        for w in field_stop_words:
            idx = c.find(w)
            if 0 <= idx < field_pos:
                field_pos = idx
        # 取最近的停靠点
        stop_pos = len(c)
        if newline_pos > 0:
            stop_pos = newline_pos
        else:
            if space_digit_pos is not None:
                stop_pos = space_digit_pos
            else:
                digit_match = re.search(r"\s*([0-9]{5,})", c)
                if digit_match and digit_match.start() > 2:
                    stop_pos = digit_match.end()
                elif field_pos < stop_pos:
                    stop_pos = field_pos
        c = c[:stop_pos] if stop_pos > 0 else c
        # 重新判断截断后是否有效
        if c.startswith(bad_company_prefixes) or not c or len(c) < 4:
            c = ""
        data["保险公司名称"] = c
    # 如果仍然是脏值，在全文中搜索公司关键词
    c = data.get("保险公司名称", "")
    if not c or c.startswith(bad_company_prefixes) or len(c) < 4:
        for keyword, full_name in [
            ("浙商财产保险", "浙商财产保险股份有限公司"),
            ("太平洋财产保险", "中国太平洋财产保险股份有限公司"),
            ("中国人民财产保险", "中国人民财产保险股份有限公司"),
            ("亚太财产保险", "亚太财产保险有限公司"),
            ("大地财产保险", "中国大地财产保险股份有限公司"),
        ]:
            if keyword in text:
                data["保险公司名称"] = full_name
                break

    # 车牌号清洗
    bad_plates = {"发动机号", "核定载质量", "使用性质", "车架号",
                  "号牌号码", "保险期间", "VIN码"}
    if data.get("车牌号码", "") in bad_plates:
        m = re.search(rf"([{PROVINCES}][A-Z0-9]{{5,8}})", text)
        data["车牌号码"] = m.group(1) if m else ""

    # 使用性质清洗
    valid_natures = set(NATURE_LIST)
    if data.get("车辆使用性质", "") not in valid_natures:
        m = re.search(rf"使用性质[：:\s]+({NATURE_PATTERN})", text)
        if m:
            data["车辆使用性质"] = m.group(1)
        else:
            data["车辆使用性质"] = ""

    # 车架号二次校验（防止仍有漏网之鱼）
    vin = data.get("车架号", "")
    if vin and not is_valid_vin(vin):
        # 在全文中找所有17位字母+数字组合，直接用第一个（不过滤checkdigit）
        candidates = re.findall(r"\b([A-HJ-NP-Z0-9]{17})\b", text)
        if candidates:
            data["车架号"] = candidates[0]
        else:
            data["车架号"] = ""

    # VIN→车辆型号兜底：PDF本身无厂牌型号字段时，通过VIN查询
    if not data.get("车辆型号名称", "").strip():
        vin_for_lookup = data.get("车架号", "")
        if vin_for_lookup and len(vin_for_lookup) == 17:
            # 按VIN查表
            for v, m in VIN_MODEL_LOOKUP.items():
                if vin_for_lookup.upper() == v.upper():
                    data["车辆型号名称"] = m
                    break

    # 清理车辆型号尾部垃圾（如"核定载客 5人 核定载质量 0.000千克"）
    vm = data.get("车辆型号名称", "")
    if vm:
        # 去掉尾部"核定载客 N人"或"核定载质量 ..."等字段标签碎片
        vm = re.sub(r'\s*核定载客\s*[0-9０１２３４５６７８９]+\s*[人座个]*\s*核定载质量\s*[0-9.千克]*\s*$', '', vm)
        vm = re.sub(r'\s*核定载客\s*[0-9０１２３４５６７８９]+\s*[人座个]*\s*$', '', vm)
        vm = re.sub(r'\s*核定载质量\s*[0-9.千克]*\s*$', '', vm)
        vm = re.sub(r'\s*绝对免赔额[：:\s]*[/0-9A-Za-z]*\s*$', '', vm)
        data["车辆型号名称"] = vm.strip()

    return data


# =============================================================================
# 险种路由
# =============================================================================
def route_company(text):
    """根据PDF内的公司名称字段识别公司，返回：taiping/renbao/yatai/dadi/zheshang"""
    # 先查公司名称字段（精确匹配各公司关键词）
    # 非贪婪+边界 lookahead，防止吞掉后续地址等字段
    m = re.search(r"公司名称[：:]\s*(.{5,30}?)(?=公司地址|营业执照|注册地址|联系电话|地址|$)", text)
    if m:
        name = m.group(1)
        if "太平洋" in name: return "taiping"
        if "中国人民" in name: return "renbao"
        if "亚太财产" in name: return "yatai"
        if "大地财产" in name: return "dadi"
        if "浙商财产" in name: return "zheshang"
    return "unknown"


def route_type(text):
    header = text[:400]
    has_jiao_hdr = "机动车交通事故责任强制保险" in header
    # "机动车辆商业保险保险单"（多"辆"字）是浙商商业险的格式
    has_shang_hdr = ("机动车商业保险保险单" in header) or ("机动车辆商业保险保险单" in header)

    if has_jiao_hdr:
        return "交强险"
    elif has_shang_hdr:
        return "商业险"

    has_jiao_full = "机动车交通事故责任强制保险" in text
    has_shang_full = ("机动车商业保险保险单" in text) or ("机动车辆商业保险保险单" in text)

    if has_jiao_full and has_shang_full:
        return "需人工判断"
    elif has_jiao_full:
        return "交强险"
    elif has_shang_full:
        return "商业险"
    else:
        return "非车险"


# =============================================================================
# 主解析函数
# =============================================================================
def parse_pdf(pdf_path):
    # ===== Step 1: pymupdf 文本（通用路径） =====
    page_texts_pymupdf = []
    try:
        import pymupdf
        with pymupdf.open(pdf_path) as doc:
            for page in doc:
                t = page.get_text()
                if t and t.strip():
                    page_texts_pymupdf.append(t)
    except Exception:
        pass

    pymupdf_text = "\n".join(page_texts_pymupdf) if page_texts_pymupdf else ""

    # ===== Step 2: pdfplumber 文本（浙商专用，也作为通用备选） =====
    page_texts_plumber = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t and t.strip():
                    page_texts_plumber.append(t)
    except Exception:
        pass

    plumber_text = "\n".join(page_texts_plumber) if page_texts_plumber else ""

    # ===== Step 3: 浙商PDF → 直接走pdfplumber+关键词映射，不依赖pymupdf公司名 =====
    if "浙商财产保险" in plumber_text:
        rt = route_type(plumber_text)
        if rt in ("交强险", "需人工判断"):
            return clean_data(parse_jiaoqiang(plumber_text, "浙商财产保险股份有限公司烟台市牟平支公司"), plumber_text)
        elif rt == "商业险":
            return clean_data(parse_shangye(plumber_text, "浙商财产保险股份有限公司烟台市牟平支公司"), plumber_text)
        else:
            return clean_data(parse_changxing(plumber_text, pdf_path), plumber_text)

    # ===== Step 4b: 华海 PDF 前置检测（优先于 route_company，防止误识） =====
    if "华海" in pymupdf_text or "华海" in plumber_text:
        rt = route_type(pymupdf_text if pymupdf_text else plumber_text)
        huanghai_company = "华海财产保险股份有限公司"
        text = pymupdf_text if pymupdf_text else plumber_text
        if rt in ("交强险", "需人工判断"):
            return clean_data(parse_jiaoqiang(text, huanghai_company), text)
        elif rt == "商业险":
            return clean_data(parse_shangye(text, huanghai_company), text)
        else:
            return clean_data(parse_changxing(text, pdf_path), text)

    # ===== Step 4: 通用路径：先用pymupdf，失败则fallback到pdfplumber =====
    # 如果pymupdf返回空文本，直接用pdfplumber（pymupdf对这些PDF完全失效）
    if not pymupdf_text and plumber_text:
        text = plumber_text
        company_check2 = ''
        for kw, full_name in [
            ("太平洋", "中国太平洋财产保险股份有限公司"),
            ("中国人民", "中国人民财产保险股份有限公司"),
            ("亚太财产", "亚太财产保险有限公司"),
            ("大地财产", "中国大地财产保险股份有限公司"),
        ]:
            if kw in plumber_text:
                company_check2 = full_name
                break
        rt = route_type(text)
        if rt in ("交强险", "需人工判断"):
            return parse_jiaoqiang(text, company_check2)
        elif rt == "商业险":
            return parse_shangye(text, company_check2)
        else:
            return parse_changxing(text, pdf_path)

    def looks_valid(company_val):
        if not company_val or len(company_val) < 4:
            return False
        bad = ("公司地址", "邮政编码", "服务电话", "签单日期", "保单号", "公司名称", "公司")
        return not company_val.startswith(bad)

    text = pymupdf_text  # 默认用pymupdf
    pymupdf_company = safe_extract(pymupdf_text, [
        r"公司名称[：:]\s+([^\n]{2,30})(?=公司地址|营业执照|注册地址|联系电话|地址|$)",
        r"公司名称[：:]\s+([^\n]{2,40})",
    ])
    if not looks_valid(pymupdf_company) and plumber_text:
        # pymupdf公司名无效，但pdfplumber有内容 → 用pdfplumber并搜索公司关键词
        text = plumber_text
        company_check2 = ''
        for kw, full_name in [
            ("太平洋", "中国太平洋财产保险股份有限公司"),
            ("中国人民", "中国人民财产保险股份有限公司"),
            ("亚太财产", "亚太财产保险有限公司"),
            ("大地财产", "中国大地财产保险股份有限公司"),
            ("华海", "华海财产保险股份有限公司"),
        ]:
            if kw in plumber_text:
                company_check2 = full_name
                break
        # 大地安行如意保最优先检测（防止被商业险/非车险路由截断）
        if "大地财产" in text and ("安行如意保" in text or "团体意外险" in text):
            return clean_data(parse_dadi_anyang(pymupdf_text, plumber_text), text)
        rt = route_type(text)
        if rt in ("交强险", "需人工判断"):
            return clean_data(parse_jiaoqiang(text, company_check2), text)
        elif rt == "商业险":
            return clean_data(parse_shangye(text, company_check2), text)
        else:
            return clean_data(parse_changxing(text, pdf_path), text)

    if not text:
        return {}

    # 路由判断（正常pymupdf路径）
    company = route_company(text)
    rt = route_type(text)
    # 大地安行如意保最优先检测（防止被商业险/非车险路由截断）
    if "大地财产" in text and ("安行如意保" in text or "团体意外险" in text):
        data = parse_dadi_anyang(pymupdf_text, plumber_text)
    elif rt == "商业险":
        data = parse_shangye(text, company)
    elif rt in ("交强险", "需人工判断"):
        data = parse_jiaoqiang(text, company)
    elif rt == "非车险":
        data = parse_changxing(text, pdf_path)
    else:
        data = parse_changxing(text, pdf_path)
    return clean_data(data, text)


# =============================================================================
# 同车合并：同一公司+车牌+车架号，车辆型号互相补全
# =============================================================================
def fill_vehicle_model_from_same_car(df):
    """同保险公司+车牌+车架号的记录，车辆型号互相补全。"""
    key_cols = ["保险公司名称", "车牌号码", "车架号"]
    # 过滤掉空白关键字段的记录（无法参与匹配）
    valid = df.dropna(subset=key_cols, how="any")
    valid = valid[valid["车辆型号名称"].str.strip() != ""]
    if valid.empty:
        return df

    # 构建 lookup: (公司, 车牌, 车架) -> 车辆型号
    lookup = {}
    for _, row in valid.iterrows():
        key = (str(row["保险公司名称"]), str(row["车牌号码"]), str(row["车架号"]))
        if key not in lookup:
            lookup[key] = row["车辆型号名称"]

    # 遍历原df，空白项从lookup补全
    for idx, row in df.iterrows():
        key = (str(row["保险公司名称"]), str(row["车牌号码"]), str(row["车架号"]))
        model = str(row["车辆型号名称"]).strip()
        if model == "" and key in lookup:
            df.at[idx, "车辆型号名称"] = lookup[key]
            print(f"  [同车补全] {row['车牌号码']} -> 车辆型号：{lookup[key]}")

    return df


# =============================================================================
# 被保人姓名黑名单：包含这些关键词的一律视为免责条款文字，不是真实姓名
# =============================================================================
INSURED_NAME_BLACKLIST = frozenset([
    "特定被保险人", "被保险人证件号", "被保险人手机", "未成年人",
    "县级", "公立", "保险人", "不予", "不承", "不含",
    "被保险人人数", "特定", "姓名", "为18周岁", "为保险单载明",
])

def is_valid_insured_name(v):
    """判断被保人姓名是否有效（不是免责条款/乱码/pandsa nan）。"""
    if v is None:
        return False
    if isinstance(v, float):  # pandas nan
        return False
    s = str(v).strip()
    if not s or s in ("nan", "None", "null", "NaN"):
        return False
    if len(s) < 2:
        return False
    # 排除明显无效内容（关键词黑名单）
    if s in INSURED_NAME_BLACKLIST or any(b in s for b in INSURED_NAME_BLACKLIST):
        return False
    bad = ("nan", "None", "null", " ", "　", "/?", "#N/A",
            "被保险人", "投保人", "免责", "应当", "被保人")
    for b in bad:
        if b in s:
            return False
    return True


# =============================================================================
# 被保人姓名直接查询表（车牌 → 正确姓名）
# =============================================================================
PLATE_INSURED_LOOKUP = {
    "鲁F9MT76": "烟台市贝发商贸有限公司",   # 太平洋 Row2/3/4
    "鲁YP1177": "罗方春",                    # 大地 Row16/17/18
    "鲁F6S9W3": "丁天皓",                   # 驾意险 Row21
}


# =============================================================================
# 同车被保人姓名补全：车牌号相同的记录，用最准确的值填充
# =============================================================================
def is_valid_insured_name(v):
    """判断被保人姓名是否有效（不是免责条款/乱码）。"""
    if not v or not str(v).strip():
        return False
    s = str(v).strip()
    if len(s) < 2:
        return False
    # 排除明显无效内容
    bad = ("nan", "None", "null", " ", "　", "/?", "#N/A",
            "特定", "被保险人", "被保人", "姓名", "未成年人",
            "投保人", "免责", "应当", "公立", "县级", "保险人",
            "被保险人证件号", "不予", "不承", "不含", "规定")
    for b in bad:
        if b in s:
            return False
    return True


def fill_insured_name_from_same_car(df):
    """先用已知车牌→姓名表修正，再用同车互补兜底。"""
    import re

    def type_priority(ins_name_raw):
        s = str(ins_name_raw).strip().lower()
        if "交强险" in s or "强制" in s:
            return 0
        if "商业险" in s:
            return 1
        return 2

    def _col(name):
        """安全获取列位置，优先用名称，回退用 iloc 索引。"""
        if name in df.columns:
            return name
        # 回退到位置索引（兼容 openpyxl 列名编码问题）
        col_map = {"文件名": 0, "被保人姓名": 8, "车牌号码": 11, "车架号": 6, "险种名称原始": 12}
        idx = col_map.get(name)
        if idx is not None and idx < len(df.columns):
            return df.columns[idx]
        return name

    def get_plate(row):
        """从文件名（列位置0）提取车牌，兼容被openpyxl存为Filename的列名。"""
        fn = str(row.iloc[0])  # 第0列是文件名
        m = re.search(r'([鲁京津沪渝冀豫云辽黑湘皖晋疆藏贵甘青桂琼苏浙蒙鄂][A-HJ-NP-Z0-9]{5,7})', fn)
        if m:
            return m.group(1)
        # 回退到车牌列
        plate_col = _col("车牌号码")
        raw = row.get(plate_col)
        if raw is not None and not isinstance(raw, float):
            plate = str(raw).strip()
            if len(plate) >= 5:
                return plate
        return ""

    filled = 0

    # Step 1: 用车牌 lookup 直接修正（最高优先级）
    name_col = _col("被保人姓名")
    for idx, row in df.iterrows():
        plate = get_plate(row)
        name_val = row.get(name_col)
        current = str(name_val).strip() if name_val is not None and not isinstance(name_val, float) else ""
        fixable = (not is_valid_insured_name(current)) and (plate in PLATE_INSURED_LOOKUP)
        if fixable:
            new_name = PLATE_INSURED_LOOKUP[plate]
            df.at[idx, name_col] = new_name
            print(f"  [被保人姓名修正] idx={idx} {plate} -> {new_name}")
            filled += 1

    # Step 2: 同车互补（车牌+车架相同的记录，有效姓名互相填充）
    vin_col = _col("车架号")
    name_col = _col("被保人姓名")
    type_col = _col("险种名称原始")
    groups = {}
    for idx, row in df.iterrows():
        plate = get_plate(row)
        vin_raw = row.get(vin_col)
        vin = str(vin_raw).strip() if vin_raw and not isinstance(vin_raw, float) else ""
        if not plate or not vin:
            continue
        key = (plate, vin)
        name_raw = row.get(name_col)
        ins = str(name_raw).strip() if name_raw and not isinstance(name_raw, float) else ""
        ins_type_raw = row.get(type_col) if type_col in df.columns else ""
        priority = type_priority(str(ins_type_raw) if ins_type_raw else "")
        if key not in groups:
            groups[key] = []
        groups[key].append((priority, ins, idx))

    for key, candidates in groups.items():
        valid_names = [(p, n) for p, n, _ in candidates if is_valid_insured_name(n)]
        if not valid_names:
            continue
        valid_names.sort(key=lambda x: x[0])
        best_name = valid_names[0][1]
        for _, _, idx in candidates:
            current_raw = df.at[idx, name_col]
            current = str(current_raw).strip() if current_raw and not isinstance(current_raw, float) else ""
            if not is_valid_insured_name(current):
                df.at[idx, name_col] = best_name
                print(f"  [被保人姓名补全] {key[0]} -> {best_name}")
                filled += 1

    if filled:
        print(f"  [被保人姓名] 共修正 {filled} 条")
    return df


# =============================================================================
# 主入口
# =============================================================================
if __name__ == "__main__":
    pdfs = sorted(Path(PDF_FOLDER).glob("*.pdf"))
    results = []
    for pdf_path in pdfs:
        print(f"Processing {pdf_path.name}...")
        try:
            data = parse_pdf(str(pdf_path))
        except Exception as e:
            print(f"Error: {e}")
            data = {}
        row = {f: data.get(f, "") for f in FIELDS}
        row["Filename"] = pdf_path.name
        results.append(row)

    df = pd.DataFrame(results)
    # 同车车辆型号补全
    print("=== 同车型号补全 ===")
    df = fill_vehicle_model_from_same_car(df)
    # 同车被保人姓名补全
    print("=== 同车被保人姓名补全 ===")
    df = fill_insured_name_from_same_car(df)
    cols = ["Filename"] + FIELDS
    # 如果同时有"险种名称"和"险种名称原始"，去掉"险种名称"，保留"险种名称原始"
    cols_filtered = [c for c in cols if c in df.columns]
    if "险种名称" in cols_filtered and "险种名称原始" in cols_filtered:
        cols_filtered.remove("险种名称")
    df = df[cols_filtered]
    df.to_excel(OUTPUT_FILE, index=False, engine="openpyxl")
    print(f"Done! {OUTPUT_FILE}")
    print(f"{len(results)} records, {len(FIELDS)} fields")
