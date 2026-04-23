#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AiTaxs 综合税务计算工具
面向个体工商户 / 小微企业主

用法:
  python tax_calculator.py --type salary --income 20000 --deductions 3000
  python tax_calculator.py --type business --annual-profit 200000
  python tax_calculator.py --type vat --sales 280000 --type-flag small
  python tax_calculator.py --type corp --profit 1500000
"""

import argparse
import sys


# ──────────────────────────────────────────────
# 工资薪金个税（月度预扣预缴）
# ──────────────────────────────────────────────
SALARY_BRACKETS = [
    (36000,    0.03,    0),
    (144000,   0.10,    2520),
    (300000,   0.20,    16920),
    (420000,   0.25,    31920),
    (660000,   0.30,    52920),
    (960000,   0.35,    85920),
    (float('inf'), 0.45, 181920),
]

def calc_salary_tax(monthly_income: float, special_deductions: float = 0) -> dict:
    """
    计算月度工资个税（预扣预缴方式，按单月估算，不含全年累计）
    :param monthly_income: 税前月收入
    :param special_deductions: 专项附加扣除合计（月度）
    :return: 计算明细字典
    """
    THRESHOLD = 5000  # 免征额
    SOCIAL_INSURANCE_RATE = 0.105  # 社保公积金估算比例（仅供参考，各地不同）

    social_deduction = monthly_income * SOCIAL_INSURANCE_RATE
    taxable = monthly_income - THRESHOLD - social_deduction - special_deductions
    taxable = max(taxable, 0)

    # 换算为年度累计预扣预缴所得额（按单月×12估算）
    annual_taxable = taxable * 12
    tax_rate, quick_deduction = 0, 0
    for limit, rate, deduction in SALARY_BRACKETS:
        if annual_taxable <= limit:
            tax_rate = rate
            quick_deduction = deduction
            break

    annual_tax = annual_taxable * tax_rate - quick_deduction
    monthly_tax = annual_tax / 12

    return {
        "计算类型": "工资薪金个人所得税（月度估算）",
        "税前月收入": f"{monthly_income:,.2f} 元",
        "减：免征额": f"{THRESHOLD:,.2f} 元",
        "减：社保公积金估算": f"{social_deduction:,.2f} 元",
        "减：专项附加扣除": f"{special_deductions:,.2f} 元",
        "月度应纳税所得额": f"{taxable:,.2f} 元",
        "适用税率": f"{tax_rate*100:.0f}%",
        "预计月度应缴个税": f"{monthly_tax:,.2f} 元",
        "税后月收入（估算）": f"{monthly_income - social_deduction - monthly_tax:,.2f} 元",
        "注意": "社保公积金比例按10.5%估算，实际以当地标准为准；专项附加扣除需据实填报"
    }


# ──────────────────────────────────────────────
# 经营所得个税（个体工商户年度）
# ──────────────────────────────────────────────
BUSINESS_BRACKETS = [
    (30000,      0.05,  0),
    (90000,      0.10,  1500),
    (300000,     0.20,  10500),
    (500000,     0.30,  40500),
    (float('inf'), 0.35, 65500),
]

def calc_business_tax(annual_profit: float) -> dict:
    """
    计算个体工商户经营所得个人所得税（年度）
    :param annual_profit: 全年应纳税所得额（已扣除成本费用后）
    """
    tax_rate, quick_deduction = 0, 0
    for limit, rate, deduction in BUSINESS_BRACKETS:
        if annual_profit <= limit:
            tax_rate = rate
            quick_deduction = deduction
            break

    tax = annual_profit * tax_rate - quick_deduction

    return {
        "计算类型": "经营所得个人所得税（个体工商户年度）",
        "全年应纳税所得额": f"{annual_profit:,.2f} 元",
        "适用税率": f"{tax_rate*100:.0f}%",
        "速算扣除数": f"{quick_deduction:,.2f} 元",
        "全年应缴个税": f"{tax:,.2f} 元",
        "综合税负率": f"{tax/annual_profit*100:.2f}%" if annual_profit > 0 else "0%",
        "注意": "应纳税所得额 = 收入总额 - 成本 - 费用 - 税金 - 损失；核定征收请以税务机关核定为准"
    }


# ──────────────────────────────────────────────
# 增值税计算
# ──────────────────────────────────────────────
def calc_vat(sales: float, taxpayer_type: str = "small", rate: float = None,
             input_tax: float = 0) -> dict:
    """
    计算增值税
    :param sales: 含税销售额
    :param taxpayer_type: 'small'=小规模纳税人, 'general'=一般纳税人
    :param rate: 一般纳税人适用税率（如 0.13/0.09/0.06）
    :param input_tax: 进项税额（仅一般纳税人适用）
    """
    if taxpayer_type == "small":
        征收率 = 0.01  # 当前优惠征收率1%
        EXEMPT_THRESHOLD_QUARTERLY = 300000  # 季度免税门槛

        # 换算为不含税销售额
        tax_exclusive_sales = sales / (1 +征收率)
        vat = tax_exclusive_sales * 0.01

        quarterly_sales_approx = sales  # 此处按单次销售额视为季度

        if quarterly_sales_approx <= EXEMPT_THRESHOLD_QUARTERLY:
            result = {
                "计算类型": "增值税（小规模纳税人）",
                "含税销售额": f"{sales:,.2f} 元",
                "季度销售额是否超30万": "未超过",
                "应缴增值税": "0 元（免征）",
                "依据": "季度销售额 ≤ 30万元，小规模纳税人免征增值税",
            }
        else:
            result = {
                "计算类型": "增值税（小规模纳税人）",
                "含税销售额": f"{sales:,.2f} 元",
                "征收率": "1%（2023年优惠政策）",
                "不含税销售额": f"{tax_exclusive_sales:,.2f} 元",
                "应缴增值税": f"{vat:,.2f} 元",
                "附：城建税+教育附加（市区，约12%）": f"{vat * 0.12:,.2f} 元",
                "合计税款": f"{vat * 1.12:,.2f} 元",
            }
    else:
        if rate is None:
            return {"错误": "一般纳税人需指定税率，如 --vat-rate 0.13"}
        tax_exclusive_sales = sales / (1 + rate)
        output_tax = tax_exclusive_sales * rate
        vat_payable = max(output_tax - input_tax, 0)
        result = {
            "计算类型": "增值税（一般纳税人）",
            "含税销售额": f"{sales:,.2f} 元",
            "适用税率": f"{rate*100:.0f}%",
            "不含税销售额": f"{tax_exclusive_sales:,.2f} 元",
            "销项税额": f"{output_tax:,.2f} 元",
            "进项税额": f"{input_tax:,.2f} 元",
            "应缴增值税（销项-进项）": f"{vat_payable:,.2f} 元",
            "附：城建税+教育附加（市区，约12%）": f"{vat_payable * 0.12:,.2f} 元",
        }
    return result


# ──────────────────────────────────────────────
# 企业所得税（小微企业优惠）
# ──────────────────────────────────────────────
def calc_corp_tax(annual_profit: float) -> dict:
    """
    计算企业所得税（含小微企业优惠税率）
    :param annual_profit: 年度应纳税所得额
    """
    if annual_profit <= 1_000_000:
        effective_rate = 0.05
        tax = annual_profit * 0.05
        policy = "小微企业优惠：应纳税所得额≤100万，实际税率5%（25%×20%）"
    elif annual_profit <= 3_000_000:
        tax1 = 1_000_000 * 0.05
        tax2 = (annual_profit - 1_000_000) * 0.10
        tax = tax1 + tax2
        effective_rate = tax / annual_profit
        policy = "小微企业优惠：100万~300万部分，实际税率10%（25%×40%）"
    else:
        tax = annual_profit * 0.25
        effective_rate = 0.25
        policy = "标准税率25%（超过小微企业认定标准或应纳税所得额>300万）"

    return {
        "计算类型": "企业所得税",
        "年度应纳税所得额": f"{annual_profit:,.2f} 元",
        "适用政策": policy,
        "应缴企业所得税": f"{tax:,.2f} 元",
        "综合税负率": f"{effective_rate*100:.2f}%",
        "注意": "小微企业认定须同时满足：从业人数≤300人、资产总额≤5000万元"
    }


# ──────────────────────────────────────────────
# 主程序
# ──────────────────────────────────────────────
def print_result(result: dict):
    print("\n" + "=" * 50)
    for k, v in result.items():
        print(f"  {k}: {v}")
    print("=" * 50 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="AiTaxs 综合税务计算工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 计算月薪2万、专项附加扣除3000元的个税
  python tax_calculator.py --type salary --income 20000 --deductions 3000

  # 计算个体工商户全年经营利润20万的个税
  python tax_calculator.py --type business --annual-profit 200000

  # 计算小规模纳税人季度含税销售额28万的增值税
  python tax_calculator.py --type vat --sales 280000

  # 计算一般纳税人含税销售额100万（税率13%）、进项税5万的增值税
  python tax_calculator.py --type vat --sales 1000000 --taxpayer general --vat-rate 0.13 --input-tax 50000

  # 计算小微企业年度应纳税所得额150万的企业所得税
  python tax_calculator.py --type corp --profit 1500000
        """
    )

    parser.add_argument("--type", required=True,
                        choices=["salary", "business", "vat", "corp"],
                        help="计算类型: salary=工资个税, business=经营所得个税, vat=增值税, corp=企业所得税")
    parser.add_argument("--income", type=float, help="税前月收入（salary模式）")
    parser.add_argument("--deductions", type=float, default=0, help="专项附加扣除合计/月（salary模式）")
    parser.add_argument("--annual-profit", type=float, help="全年应纳税所得额（business模式）")
    parser.add_argument("--sales", type=float, help="含税销售额（vat模式）")
    parser.add_argument("--taxpayer", choices=["small", "general"], default="small",
                        help="纳税人类型: small=小规模, general=一般（vat模式）")
    parser.add_argument("--vat-rate", type=float, help="增值税税率，如0.13（general模式）")
    parser.add_argument("--input-tax", type=float, default=0, help="进项税额（general模式）")
    parser.add_argument("--profit", type=float, help="年度应纳税所得额（corp模式）")

    args = parser.parse_args()

    if args.type == "salary":
        if args.income is None:
            print("错误：salary 模式需要 --income 参数")
            sys.exit(1)
        result = calc_salary_tax(args.income, args.deductions)

    elif args.type == "business":
        if args.annual_profit is None:
            print("错误：business 模式需要 --annual-profit 参数")
            sys.exit(1)
        result = calc_business_tax(args.annual_profit)

    elif args.type == "vat":
        if args.sales is None:
            print("错误：vat 模式需要 --sales 参数")
            sys.exit(1)
        result = calc_vat(args.sales, args.taxpayer, args.vat_rate, args.input_tax)

    elif args.type == "corp":
        if args.profit is None:
            print("错误：corp 模式需要 --profit 参数")
            sys.exit(1)
        result = calc_corp_tax(args.profit)

    print_result(result)


if __name__ == "__main__":
    main()
