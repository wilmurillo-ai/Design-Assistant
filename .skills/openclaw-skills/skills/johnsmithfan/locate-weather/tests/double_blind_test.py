#!/usr/bin/env python3
"""
Locate-Weather 双盲对照测试框架
测试时间因素对定位策略的影响
"""

import json
import random
import subprocess
import sys
import os
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import statistics

@dataclass
class TestCondition:
    """测试条件：时间场景"""
    name: str
    hour: int  # 0-23
    season: str  # spring, summer, autumn, winter
    description: str
    expected_priority: List[str]  # 期望的定位方法优先级

@dataclass
class TestResult:
    """单次测试结果"""
    condition: str
    subject_group: str  # A组或B组
    subject_id: int
    method_used: str
    accuracy: float
    confidence: float
    success: bool
    response_time_ms: float
    timestamp: str

# 预定义测试场景（时间因素）
TEST_CONDITIONS = [
    TestCondition("深夜室内", 2, "winter", "凌晨2点，用户在室内，GPS信号弱", 
                  ["ip", "wifi", "system", "gps"]),
    TestCondition("清晨通勤", 7, "spring", "早上7点，用户通勤中，多源可用",
                  ["gps", "wifi", "system", "ip"]),
    TestCondition("正午户外", 12, "summer", "中午12点，户外强光，GPS可用",
                  ["gps", "system", "wifi", "ip"]),
    TestCondition("黄昏室内", 18, "autumn", "傍晚6点，室内，WiFi优先",
                  ["wifi", "ip", "system", "gps"]),
    TestCondition("夜间移动", 22, "winter", "晚上10点，移动中，GPS+IP混合",
                  ["gps", "ip", "system", "wifi"]),
]

class TestSubject:
    """受测者 Agent"""
    def __init__(self, group: str, subject_id: int, strategy: str):
        self.group = group  # "A" 或 "B"
        self.subject_id = subject_id
        self.strategy = strategy  # "time_aware" 或 "baseline"
        self.results: List[TestResult] = []
    
    def run_test(self, condition: TestCondition) -> TestResult:
        """执行单次测试"""
        start_time = datetime.now(timezone.utc)
        
        # 根据策略和时间条件选择方法
        if self.strategy == "time_aware":
            methods = self._time_aware_methods(condition)
        else:
            methods = ["system", "ip", "gps", "wifi"]  # 基线策略
        
        # 调用 locate-weather
        try:
            cmd = [sys.executable, "scripts/locate_weather.py", 
                   "--methods", ",".join(methods),
                   "--format", "json"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            elapsed_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                loc = data.get("location", {})
                
                # 评估是否匹配期望优先级
                actual_method = loc.get("method", "unknown")
                success = actual_method in condition.expected_priority[:2]
                
                return TestResult(
                    condition=condition.name,
                    subject_group=self.group,
                    subject_id=self.subject_id,
                    method_used=actual_method,
                    accuracy=loc.get("accuracy_meters", 99999),
                    confidence=loc.get("confidence", 0),
                    success=success,
                    response_time_ms=elapsed_ms,
                    timestamp=start_time.isoformat()
                )
            else:
                return TestResult(
                    condition=condition.name,
                    subject_group=self.group,
                    subject_id=self.subject_id,
                    method_used="error",
                    accuracy=99999,
                    confidence=0,
                    success=False,
                    response_time_ms=elapsed_ms,
                    timestamp=start_time.isoformat()
                )
                
        except Exception as e:
            elapsed_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            return TestResult(
                condition=condition.name,
                subject_group=self.group,
                subject_id=self.subject_id,
                method_used=f"exception: {e}",
                accuracy=99999,
                confidence=0,
                success=False,
                response_time_ms=elapsed_ms,
                timestamp=start_time.isoformat()
            )
    
    def _time_aware_methods(self, condition: TestCondition) -> List[str]:
        """根据时间条件选择最优方法序列"""
        hour = condition.hour
        
        # 夜间 (0-5): IP优先，GPS信号弱
        if 0 <= hour < 6:
            return ["ip", "wifi", "system", "gps"]
        # 清晨/傍晚 (6-9, 17-20): 系统定位优先
        elif (6 <= hour < 10) or (17 <= hour < 21):
            return ["system", "gps", "wifi", "ip"]
        # 白天 (10-16): GPS优先
        elif 10 <= hour < 17:
            return ["gps", "system", "wifi", "ip"]
        # 夜间 (21-23): 混合策略
        else:
            return ["gps", "ip", "system", "wifi"]


class DoubleBlindTester:
    """双盲测试控制器"""
    def __init__(self):
        self.subjects: List[TestSubject] = []
        self.results: List[TestResult] = []
        self.round = 0
    
    def create_subjects(self, n_per_group: int = 3):
        """创建受测者"""
        # A组：时间感知策略
        for i in range(n_per_group):
            self.subjects.append(TestSubject("A", i+1, "time_aware"))
        
        # B组：基线策略（对照组）
        for i in range(n_per_group):
            self.subjects.append(TestSubject("B", i+1, "baseline"))
        
        print(f"✓ 创建 {len(self.subjects)} 名受测者")
        print(f"  - A组（时间感知）: {n_per_group} 人")
        print(f"  - B组（基线对照）: {n_per_group} 人")
    
    def run_round(self, round_num: int):
        """执行一轮测试"""
        self.round = round_num
        print(f"\n{'='*60}")
        print(f"第 {round_num} 轮双盲测试")
        print(f"{'='*60}")
        
        # 随机打乱测试顺序（双盲）
        test_sequence = []
        for condition in TEST_CONDITIONS:
            for subject in self.subjects:
                test_sequence.append((condition, subject))
        
        random.shuffle(test_sequence)
        
        # 执行测试
        for idx, (condition, subject) in enumerate(test_sequence, 1):
            print(f"\n[{idx}/{len(test_sequence)}] {condition.name} | "
                  f"受测者 {subject.group}-{subject.subject_id} ({subject.strategy})")
            
            result = subject.run_test(condition)
            self.results.append(result)
            
            status = "✓" if result.success else "✗"
            print(f"  {status} 方法: {result.method_used}, "
                  f"精度: {result.accuracy:.0f}m, "
                  f"置信度: {result.confidence:.2f}, "
                  f"耗时: {result.response_time_ms:.0f}ms")
    
    def analyze_results(self) -> Dict[str, Any]:
        """分析测试结果"""
        print(f"\n{'='*60}")
        print("测试结果分析")
        print(f"{'='*60}")
        
        # 按组统计
        group_stats = {"A": [], "B": []}
        for r in self.results:
            group_stats[r.subject_group].append(r)
        
        analysis = {
            "round": self.round,
            "total_tests": len(self.results),
            "group_comparison": {}
        }
        
        for group, results in group_stats.items():
            successes = [r for r in results if r.success]
            accuracies = [r.accuracy for r in results if r.accuracy < 99999]
            confidences = [r.confidence for r in results]
            times = [r.response_time_ms for r in results]
            
            stats = {
                "strategy": "time_aware" if group == "A" else "baseline",
                "total": len(results),
                "success_rate": len(successes) / len(results) if results else 0,
                "avg_accuracy": statistics.mean(accuracies) if accuracies else 0,
                "avg_confidence": statistics.mean(confidences) if confidences else 0,
                "avg_response_ms": statistics.mean(times) if times else 0,
                "median_accuracy": statistics.median(accuracies) if accuracies else 0,
            }
            
            analysis["group_comparison"][group] = stats
            
            print(f"\n【{group}组 - {stats['strategy']}】")
            print(f"  成功率: {stats['success_rate']*100:.1f}%")
            print(f"  平均精度: {stats['avg_accuracy']:.0f}m")
            print(f"  平均置信度: {stats['avg_confidence']:.2f}")
            print(f"  平均响应: {stats['avg_response_ms']:.0f}ms")
        
        # 计算提升
        a_stats = analysis["group_comparison"]["A"]
        b_stats = analysis["group_comparison"]["B"]
        
        if b_stats["avg_accuracy"] > 0:
            accuracy_improvement = (b_stats["avg_accuracy"] - a_stats["avg_accuracy"]) / b_stats["avg_accuracy"]
            print(f"\n【A组 vs B组 提升】")
            print(f"  精度提升: {accuracy_improvement*100:.1f}%")
            print(f"  置信度提升: {(a_stats['avg_confidence'] - b_stats['avg_confidence']):.2f}")
        
        return analysis
    
    def export_report(self, filename: str = None):
        """导出测试报告"""
        if filename is None:
            filename = f"test_report_round{self.round}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "test_framework": "double_blind_time_aware",
            "round": self.round,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "conditions": [asdict(c) for c in TEST_CONDITIONS],
            "results": [asdict(r) for r in self.results],
            "analysis": self.analyze_results()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ 测试报告已保存: {filename}")
        return filename


def main():
    """主入口"""
    print("="*60)
    print("Locate-Weather 时间因素双盲对照测试")
    print("="*60)
    
    tester = DoubleBlindTester()
    tester.create_subjects(n_per_group=3)
    
    # 执行三轮测试
    for round_num in range(1, 4):
        tester.run_round(round_num)
        tester.export_report(f"test_report_round{round_num}.json")
    
    print("\n" + "="*60)
    print("三轮双盲测试完成")
    print("="*60)


if __name__ == "__main__":
    main()
