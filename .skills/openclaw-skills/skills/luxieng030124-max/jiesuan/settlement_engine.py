#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI智能结算引擎
支持：达标瓜分、排名赛、混合不互斥、权重分配
"""

import csv
import json
import re
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SettlementMode(Enum):
    """结算模式"""
    GUARANTEED = "guaranteed"      # 达标瓜分
    RANKING = "ranking"            # 排名赛
    HYBRID = "hybrid"              # 混合不互斥
    WEIGHTED = "weighted"          # 权重分配


@dataclass
class AwardPool:
    """奖池配置"""
    name: str                      # 奖池名称
    amount: float                  # 奖池金额
    mode: SettlementMode           # 结算模式
    condition: Optional[Dict] = None   # 达标条件
    ranking_rules: Optional[List[Dict]] = None  # 排名规则
    weight_field: Optional[str] = None  # 权重字段


@dataclass
class SettlementResult:
    """结算结果"""
    author_id: str
    author_name: str
    videos: int
    total_plays: int
    total_likes: int
    awards: Dict[str, float]       # 各奖池奖金
    total_amount: float            # 总奖金


class SettlementEngine:
    """结算引擎"""
    
    def __init__(self, pools: List[AwardPool]):
        self.pools = pools
        self.authors = defaultdict(lambda: {
            'name': '',
            'videos': 0,
            'total_plays': 0,
            'total_likes': 0
        })
    
    def load_data(self, file_path: str) -> None:
        """加载数据文件"""
        if file_path.endswith('.csv'):
            self._load_csv(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_path}")
    
    def _load_csv(self, file_path: str) -> None:
        """加载CSV数据"""
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                author_id = row.get('作者ID', row.get('用户ID', ''))
                author_name = row.get('作者名称（最新）', row.get('作者名称', ''))
                
                plays = self._parse_number(row.get('视频累计外显播放次数', '0'))
                likes = self._parse_number(row.get('视频累计外显点赞次数', '0'))
                
                self.authors[author_id]['name'] = author_name or self.authors[author_id]['name']
                self.authors[author_id]['videos'] += 1
                self.authors[author_id]['total_plays'] += plays
                self.authors[author_id]['total_likes'] += likes
    
    def _parse_number(self, value: str) -> int:
        """解析数字"""
        if not value:
            return 0
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0
    
    def process(self) -> List[SettlementResult]:
        """执行结算"""
        results = []
        
        for author_id, data in self.authors.items():
            result = SettlementResult(
                author_id=author_id,
                author_name=data['name'],
                videos=data['videos'],
                total_plays=data['total_plays'],
                total_likes=data['total_likes'],
                awards={},
                total_amount=0.0
            )
            
            # 遍历所有奖池计算奖金
            for pool in self.pools:
                award = self._calculate_award(pool, result)
                if award > 0:
                    result.awards[pool.name] = award
                    result.total_amount += award
            
            if result.total_amount > 0 or any(p.mode == SettlementMode.GUARANTEED for p in self.pools):
                results.append(result)
        
        # 按总奖金降序排列
        results.sort(key=lambda x: x.total_amount, reverse=True)
        return results
    
    def _calculate_award(self, pool: AwardPool, author: SettlementResult) -> float:
        """计算单个奖池的奖金"""
        if pool.mode == SettlementMode.GUARANTEED:
            return self._calc_guaranteed(pool, author)
        elif pool.mode == SettlementMode.RANKING:
            # 排名赛需要整体数据，延后计算
            return 0
        elif pool.mode == SettlementMode.WEIGHTED:
            # 权重分配需要整体数据，延后计算
            return 0
        return 0
    
    def _calc_guaranteed(self, pool: AwardPool, author: SettlementResult) -> float:
        """计算达标瓜分奖金（先标记达标，后续统一分配）"""
        if not pool.condition:
            return 0
        
        # 检查条件
        field = pool.condition.get('field', '')
        op = pool.condition.get('op', '>=')
        value = pool.condition.get('value', 0)
        
        # 获取字段值
        field_value = getattr(author, self._field_mapping(field), 0)
        
        # 判断条件
        if op == '>=' and field_value >= value:
            return -1  # 标记达标，后续分配
        elif op == '>' and field_value > value:
            return -1
        elif op == '<=' and field_value <= value:
            return -1
        elif op == '<' and field_value < value:
            return -1
        elif op == '==' and field_value == value:
            return -1
        
        return 0
    
    def _field_mapping(self, field: str) -> str:
        """字段映射"""
        mapping = {
            '播放量': 'total_plays',
            '播放': 'total_plays',
            '获赞': 'total_likes',
            '点赞': 'total_likes',
            '作品数': 'videos',
            '作品': 'videos',
        }
        return mapping.get(field, 'total_plays')


class RuleParser:
    """规则解析器（简化版，实际可由AI完成）"""
    
    @staticmethod
    def parse(rule_text: str) -> List[AwardPool]:
        """
        解析自然语言规则
        简化实现：支持达标瓜分模式的解析
        """
        pools = []
        
        # 匹配达标瓜分模式
        # 示例："总奖金2万元，发布作品≥5条且播放量≥3万的作者等额瓜分"
        guaranteed_pattern = r'总奖金(\d+)万.*?作品[数量]?[≥>=](\d+).*?播放[量]?[≥>=](d+)'
        
        # 提取奖池金额
        amount_match = re.search(r'总奖金(\d+)万', rule_text)
        if amount_match:
            amount = float(amount_match.group(1)) * 10000
            
            # 提取作品数条件
            videos_match = re.search(r'作品[数量]?[≥>=](\d+)', rule_text)
            videos_condition = int(videos_match.group(1)) if videos_match else 5
            
            # 提取播放量条件
            plays_match = re.search(r'播放[量]?[≥>=](\d+)万', rule_text)
            if plays_match:
                plays_condition = int(plays_match.group(1)) * 10000
            else:
                plays_match = re.search(r'播放[量]?[≥>=](\d+)', rule_text)
                plays_condition = int(plays_match.group(1)) if plays_match else 30000
            
            # 创建奖池
            pool = AwardPool(
                name="达标瓜分奖池",
                amount=amount,
                mode=SettlementMode.GUARANTEED,
                condition={
                    'field': '播放量',
                    'op': '>=',
                    'value': plays_condition
                }
            )
            pools.append(pool)
        
        return pools


def process_settlement(file_path: str, rule_text: str) -> Tuple[List[SettlementResult], Dict]:
    """
    执行结算
    
    Args:
        file_path: 数据文件路径
        rule_text: 规则描述
    
    Returns:
        (结算结果列表, 统计信息)
    """
    # 解析规则
    pools = RuleParser.parse(rule_text)
    
    if not pools:
        raise ValueError("无法解析规则，请检查描述格式")
    
    # 创建引擎
    engine = SettlementEngine(pools)
    
    # 加载数据
    engine.load_data(file_path)
    
    # 执行结算
    results = engine.process()
    
    # 计算达标瓜分（需要知道达标人数）
    for pool in pools:
        if pool.mode == SettlementMode.GUARANTEED:
            qualified = [r for r in results if pool.name in r.awards]
            if qualified:
                per_person = pool.amount / len(qualified)
                for r in qualified:
                    r.awards[pool.name] = per_person
                    # 重新计算总奖金
                    r.total_amount = sum(r.awards.values())
    
    # 重新排序
    results.sort(key=lambda x: x.total_amount, reverse=True)
    
    # 生成统计
    stats = {
        'total_authors': len(engine.authors),
        'qualified_authors': len(results),
        'total_videos': sum(r.videos for r in results),
        'total_plays': sum(r.total_plays for r in results),
        'total_likes': sum(r.total_likes for r in results),
        'total_award': sum(r.total_amount for r in results),
        'pools': [{'name': p.name, 'amount': p.amount, 'mode': p.mode.value} for p in pools]
    }
    
    return results, stats


def export_to_csv(results: List[SettlementResult], output_path: str, stats: Dict) -> None:
    """导出到CSV"""
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        
        # 写入标题
        writer.writerow(['序号', '作者ID', '作者名称', '发布作品数', '累计播放量', '累计获赞', '瓜分奖金(元)'])
        
        # 写入数据
        for idx, r in enumerate(results, 1):
            writer.writerow([
                idx,
                r.author_id,
                r.author_name,
                r.videos,
                r.total_plays,
                r.total_likes,
                f"{r.total_amount:.2f}"
            ])
        
        # 写入汇总
        writer.writerow([
            '汇总', '', '', 
            stats['total_videos'],
            stats['total_plays'],
            stats['total_likes'],
            f"{stats['total_award']:.2f}"
        ])


def print_summary(results: List[SettlementResult], stats: Dict) -> None:
    """打印结算摘要"""
    print("=" * 80)
    print("结算结果摘要")
    print("=" * 80)
    
    print(f"\n奖池配置：")
    for pool in stats.get('pools', []):
        print(f"  - {pool['name']}: {pool['amount']:,.0f}元 ({pool['mode']})")
    
    print(f"\n统计信息：")
    print(f"  - 参与作者总数：{stats['total_authors']} 人")
    print(f"  - 获奖作者数：{stats['qualified_authors']} 人")
    print(f"  - 累计发布作品：{stats['total_videos']} 条")
    print(f"  - 累计播放量：{stats['total_plays']:,} 次")
    print(f"  - 累计获赞：{stats['total_likes']:,} 次")
    print(f"  - 总奖金发放：{stats['total_award']:,.2f} 元")
    
    if results:
        avg_award = stats['total_award'] / len(results)
        print(f"  - 人均奖金：{avg_award:,.2f} 元")
    
    print("\n" + "=" * 80)
    print(f"\n获奖作者前10名：")
    print(f"{'序号':<6}{'作者ID':<16}{'作者名称':<20}{'作品数':<10}{'播放量':<12}{'奖金(元)':<12}")
    print("-" * 80)
    for r in results[:10]:
        print(f"{0:<6}{r.author_id:<16}{r.author_name:<20}{r.videos:<10}{r.total_plays:<12}{r.total_amount:<12.2f}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("用法: python settlement_engine.py <数据文件> <规则描述>")
        print("示例: python settlement_engine.py data.csv '总奖金2万，播放量≥3万作者瓜分'")
        sys.exit(1)
    
    file_path = sys.argv[1]
    rule_text = sys.argv[2]
    
    try:
        results, stats = process_settlement(file_path, rule_text)
        print_summary(results, stats)
        
        # 导出结果
        output_path = file_path.rsplit('.', 1)[0] + '_结算结果.csv'
        export_to_csv(results, output_path, stats)
        print(f"\n✓ 结算结果已保存至: {output_path}")
        
    except Exception as e:
        print(f"❌ 结算失败: {e}")
        import traceback
        traceback.print_exc()
