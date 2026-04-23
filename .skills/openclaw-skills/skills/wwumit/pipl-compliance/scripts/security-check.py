#!/usr/bin/env python3
"""
简化的安全验证工具

功能：检查脚本安全性，验证无网络调用和危险操作
设计：轻量级检查，易于审查
使用：验证技能脚本的安全性
"""

import argparse
import os
import sys
from typing import List, Dict, Any


class SecurityVerifier:
    """安全性验证工具"""
    
    def __init__(self):
        self.dangerous_patterns = self._load_dangerous_patterns()
    
    def _load_dangerous_patterns(self) -> Dict[str, List[str]]:
        """加载危险模式"""
        return {
            "network_calls": [
                "requests.", "urllib.", "httplib.", "socket.",
                "http://", "https://", "urlopen(", "send(",
                "connect(", "listen(", "accept("
            ],
            "dangerous_operations": [
                "eval(", "exec(", "compile(", "os.system(",
                "subprocess.call(", "subprocess.Popen(",
                "execfile(", "popen(", "spawn("
            ],
            "suspicious_patterns": [
                "os.popen", "exec", "shell", "cmd",
                "powershell", "bash", "sh", "zsh"
            ]
        }
    
    def check_script_safety(self, file_path: str) -> Dict[str, Any]:
        """检查脚本安全性"""
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"文件不存在：{file_path}",
                    "security_level": "unknown"
                }
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = []
            warnings = []
            passed = []
            
            # 检查网络调用
            for pattern in self.dangerous_patterns["network_calls"]:
                if pattern in content:
                    issues.append(f"发现可能的网络调用：{pattern}")
            
            # 检查危险操作
            for pattern in self.dangerous_patterns["dangerous_operations"]:
                if pattern in content:
                    issues.append(f"发现可能的危险操作：{pattern}")
            
            # 检查可疑模式
            for pattern in self.dangerous_patterns["suspicious_patterns"]:
                if pattern in content:
                    warnings.append(f"发现可疑模式：{pattern}")
            
            # 检查导入
            import_lines = []
            for line in content.split('\n'):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    import_lines.append(line.strip())
                    # 基本检查是否只使用标准库
                    if line.strip().startswith('import ') and not line.strip().startswith('import argparse'):
                        warnings.append(f"非标准库导入：{line.strip()}")
            
            # 分析结果
            if len(issues) == 0:
                passed.append("未发现明显的安全风险")
                security_level = "low_risk"
            elif len(issues) <= 3:
                security_level = "medium_risk"
            else:
                security_level = "high_risk"
            
            # 检查文件大小（作为额外指标）
            file_size = os.path.getsize(file_path)
            file_size_ok = file_size < 50000  # 小于50KB
            
            if file_size_ok:
                passed.append(f"文件大小合适：{file_size}字节")
            else:
                warnings.append(f"文件较大：{file_size}字节（建议小于50KB）")
            
            return {
                "success": True,
                "file_name": os.path.basename(file_path),
                "file_path": file_path,
                "file_size": file_size,
                "security_level": security_level,
                "issues": issues,
                "warnings": warnings,
                "passed": passed,
                "recommendations": [
                    "建议在测试环境中验证脚本功能",
                    "如发现问题，建议咨询专业人员",
                    "重要数据操作前进行备份"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "security_level": "unknown"
            }
    
    def verify_skill_safety(self, skill_dir: str) -> Dict[str, Any]:
        """验证技能整体安全性"""
        try:
            scripts_dir = os.path.join(skill_dir, 'scripts')
            if not os.path.exists(scripts_dir):
                return {
                    "success": False,
                    "error": f"scripts目录不存在：{scripts_dir}"
                }
            
            results = []
            risk_files = []
            
            # 检查每个脚本文件
            for file_name in os.listdir(scripts_dir):
                if file_name.endswith('.py'):
                    file_path = os.path.join(scripts_dir, file_name)
                    result = self.check_script_safety(file_path)
                    results.append(result)
                    
                    if result.get("security_level") != "low_risk":
                        risk_files.append({
                            "file": file_name,
                            "issues": result.get("issues", []),
                            "warnings": result.get("warnings", [])
                        })
            
            # 总体评估
            total_issues = sum(len(r.get("issues", [])) for r in results)
            total_warnings = sum(len(r.get("warnings", [])) for r in results)
            
            if total_issues == 0 and total_warnings == 0:
 overall_status = "low_risk"
            elif total_issues <= 2:
 overall_status = "medium_risk"
            else:
 overall_status = "high_risk"
            
            return {
                "success": True,
                skill_directory": skill_dir,
                "overall_status": overall_status,
                "total_scripts": len(results),
                "total_issues": total_issues,
                "total_warnings": total_warnings,
                "detailed_results": results,
                "risk_files": risk_files if risk_files else None,
                "overall_assessment": "符合基本安全要求" if overall_status == "low_risk" else "存在中等风险，建议进一步验证" if overall_status == "medium_risk" else "存在高风险，建议暂停使用"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def print_report(self, result: Dict[str, Any], output_format: str = "text"):
        """打印验证报告"""
        if output_format == "json":
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
        
        print("\n" + "="*60)
        print("安全验证报告")
        print("="*60)
        
        if not result.get("success", False):
            print(f"❌ 验证失败：{result.get('error', '未知错误')}")
            return
        
        print(f"\n📄 验证范围：{result.get('skill_directory', '未知')}")
        print(f"📊 脚本总数：{result.get('total_scripts', 0)}")
        print(f"⚠️ 问题总数：{result.get('total_issues', 0)}")
        print(f"🔔 警告总数：{result.get('total_warnings', 0)}")
        print(f"🛡️ 总体安全等级：{result.get('overall_status', '未知')}")
        
        if result.get("overall_assessment"):
            print(f"📋 总体评价：{result['overall_assessment']}")
        
        # 如果有详细结果
        if result.get("detailed_results"):
            print("\n📝 详细结果:")
            for res in result["detailed_results"]:
                if res.get("success", False):
                    print(f"\n  🔍 {res['file_name']}: {res.get('security_level', '未知')}")
                    
                    issues = res.get("issues", [])
                    warnings = res.get("warnings", [])
                    passed = res.get("passed", [])
                    
                    if issues:
                        print("    ❌ 问题:")
                        for issue in issues:
                            print(f"      • {issue}")
                    
                    if warnings:
                        print("    ⚠️ 警告:")
                        for warning in warnings:
                            print(f"      • {warning}")
                    
                    if passed:
                        print("    ✅ 通过:")
                        for pass_item in passed:
                            print(f"      • {pass_item}")
        
        # 如果有风险文件
        if result.get("risk_files"):
            print(f"\n🚨 风险文件 (共 {len(result['risk_files'])} 个):")
            for risk in result["risk_files"]:
                print(f"  📄 {risk['file']}")
        
        print("\n" + "="*60)
        print("建议：")
        print("  1. 在测试环境中验证所有脚本功能")
        print("  2. 重要数据操作前进行备份")
        print("  3. 如有疑问，建议咨询专业人员")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(description="安全验证工具")
    
    parser.add_argument("--file", help="检查指定文件")
    parser.add_argument("--skill-dir", help="检查整个技能目录")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    
    args = parser.parse_args()
    
    verifier = SecurityVerifier()
    
    if args.file:
        result = verifier.check_script_safety(args.file)
    elif args.skill_dir:
        result = verifier.verify_skill_safety(args.skill_dir)
    else:
        print("❌ 请指定要检查的文件或目录")
        sys.exit(1)
    
    verifier.print_report(result, args.format)


if __name__ == "__main__":
    main()