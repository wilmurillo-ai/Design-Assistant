"""
金融分析师团队 - AI 分析引擎 v4.0 (ThreadPool并行版)

修复：移除 asyncio，使用 ThreadPoolExecutor，避免嵌套事件循环问题
"""

from typing import Dict, Any, List, Tuple
import json
import urllib.request
import os
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed


class AnalysisEngine:
    """AI 分析引擎 v4.0 (ThreadPool并行版)"""
    
    SINGLE_CALL_TIMEOUT = 35  # 单次调用超时（适中）
    TOKEN_LIMITS = {"quick": 150, "standard": 800, "pro": 1500}
    REQUEST_DELAY = 0.5  # 请求间延迟
    MAX_RETRIES = 2  # 重试次数（快速失败）
    
    def __init__(self, model: str = None):
        self.model = model or "glm-4-flash"  # 使用智谱 GLM-4-flash
        self.api_base = "https://open.bigmodel.cn/api/paas/v4"  # 智谱 API
        self.api_key = os.environ.get("ZHIPU_API_KEY", "")
        self._cache: Dict[str, Dict] = {}
        self._cache_ttl = 300
        self._max_retries = 2
        self._shared_insights: Dict[str, str] = {}
    
    def _get_default_model(self) -> str:
        try:
            config_path = os.path.expanduser("~/.openclaw/openclaw.json")
            with open(config_path, "r") as f:
                config = json.load(f)
                primary = config.get("agents", {}).get("defaults", {}).get("model", {}).get("primary", "")
                if primary and "/" in primary:
                    return primary.split("/")[-1]
        except:
            pass
        return "glm-5"
    
    def analyze(self, analyst_name: str, task: str, context: Dict = None, 
                mode: str = "standard") -> Dict[str, Any]:
        """单分析师分析"""
        prompt = self._build_prompt(analyst_name, context, mode)
        if prompt is None:
            return {"skipped": True}
        
        max_tokens = self.TOKEN_LIMITS.get(mode, 800)
        
        for attempt in range(self._max_retries):
            try:
                print(f"  🤖 [{analyst_name}] 分析中...")
                response = self._call_ai_sync(prompt, max_tokens)
                result = self._parse_response(analyst_name, response)
                self._save_insight(analyst_name, result)
                return result
            except Exception as e:
                print(f"  ⚠️ [{analyst_name}] 失败: {e}")
                time.sleep(1)
        
        return self._fallback_analysis(analyst_name, str(e))
    
    def analyze_parallel(self, analysts: List[Tuple[str, str]], context: Dict, 
                         mode: str = "standard", verbose: bool = True) -> Dict[str, Dict]:
        """并行分析（ThreadPoolExecutor）"""
        results = {}
        
        def analyze_one(item: Tuple[str, str]) -> Tuple[str, Dict]:
            name, task = item
            prompt = self._build_prompt(name, context, mode)
            if prompt is None:
                return name, {"skipped": True}
            
            max_tokens = self.TOKEN_LIMITS.get(mode, 800)
            
            for attempt in range(self.MAX_RETRIES):
                try:
                    if verbose:
                        print(f"  🤖 [{name}] 开始分析...")
                    response = self._call_ai_sync(prompt, max_tokens)
                    result = self._parse_response(name, response)
                    self._save_insight(name, result)
                    if verbose:
                        print(f"  ✅ [{name}] 完成")
                    return name, result
                except Exception as e:
                    if verbose:
                        print(f"  ⚠️ [{name}] 失败: {e}")
                    time.sleep(1.5)  # 增加重试间隔
            
            return name, self._fallback_analysis(name, "重试耗尽")
        
        with ThreadPoolExecutor(max_workers=min(len(analysts), 6)) as executor:
            futures = {executor.submit(analyze_one, item): item[0] for item in analysts}
            for future in as_completed(futures, timeout=120):  # 更长的总超时
                try:
                    name, result = future.result(timeout=40)
                    results[name] = result
                    time.sleep(self.REQUEST_DELAY)
                except Exception as e:
                    name = futures[future]
                    results[name] = self._fallback_analysis(name, str(e))
        
        # 确保所有分析师都有结果
        for name, _ in analysts:
            if name not in results:
                results[name] = self._fallback_analysis(name, "超时未返回")
        
        return results
    
    def _call_ai_sync(self, prompt: str, max_tokens: int = 800) -> str:
        """同步 AI 调用"""
        url = f"{self.api_base}/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
        data = {"model": self.model, "messages": [{"role": "user", "content": prompt}], 
                "temperature": 0.7, "max_tokens": max_tokens}
        
        # 使用安全的 SSL 配置
        req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=self.SINGLE_CALL_TIMEOUT) as response:
            result = json.loads(response.read().decode())
            return result["choices"][0]["message"]["content"]
    
    def _save_insight(self, name: str, result: Dict):
        key_points = []
        if "核心逻辑" in result:
            key_points.append(f"逻辑: {str(result['核心逻辑'])[:50]}")
        if "估值判断" in result:
            key_points.append(f"估值: {result['估值判断']}")
        if key_points:
            self._shared_insights[name] = " | ".join(key_points)
    
    def _get_shared_insights(self) -> str:
        if not self._shared_insights:
            return ""
        return "\n".join([f"【{n}】{i}" for n, i in self._shared_insights.items()])
    
    def _build_prompt(self, name: str, context: Dict, mode: str) -> str:
        shared = self._get_shared_insights()
        shared_ctx = f"\n\n其他见解:\n{shared}" if shared else ""
        code = context.get('code', '') if context else ''
        stock_name = context.get('name', '') if context else ''
        
        if mode == "quick":
            prompts = {
                "产业分析师": f"{code} {stock_name}行业简评。仅返回JSON:{{\"行业\":\"\",\"景气度\":\"高/中/低\"}}",
                "估值分析师": f"{code} {stock_name}估值简评。仅返回JSON:{{\"PE\":0,\"判断\":\"低估/合理/高估\"}}",
                "风险分析师": f"{code} {stock_name}风险简评。仅返回JSON:{{\"等级\":\"高/中/低\"}}"
            }
        else:
            prompts = {
                "产业分析师": f"{code} {stock_name}产业分析。返回JSON:{{行业,景气度,地位,逻辑}}",
                "估值分析师": f"{code} {stock_name}估值分析。返回JSON:{{PE,PB,ROE,判断}}",
                "技术分析师": f"{code} {stock_name}技术分析。返回JSON:{{趋势,支撑,压力,建议}}",
                "风险分析师": f"{code} {stock_name}风险分析。返回JSON:{{等级,舆情,预警}}",
                "资金分析师": f"{code} {stock_name}资金分析。返回JSON:{{主力,北向,评价}}",
                "策略师": f"{code} {stock_name}策略建议。{shared_ctx}返回JSON:{{评分(0-100),建议,风险,操作}}"
            }
        return prompts.get(name)
    
    def _parse_response(self, name: str, response: str) -> Dict:
        try:
            if "```json" in response:
                return json.loads(response.split("```json")[1].split("```")[0].strip())
            elif "{" in response:
                return json.loads(response[response.index("{"):response.rindex("}")+1])
        except:
            pass
        return {"analyst": name, "analysis": response}
    
    def _fallback_analysis(self, name: str, error: str) -> Dict:
        defaults = {
            "产业分析师": {"行业": "未知", "景气度": "未知", "_error": error},
            "估值分析师": {"估值判断": "未知", "_error": error},
            "技术分析师": {"趋势": "未知", "_error": error},
            "风险分析师": {"风险等级": "未知", "_error": error},
            "资金分析师": {"资金评价": "未知", "_error": error},
            "策略师": {"综合评分": 50, "投资建议": "AI 不可用", "_error": error}
        }
        return defaults.get(name, {"_error": error})


def analyze_stock(code: str, name: str = None, price: float = None, 
                  mode: str = "standard", verbose: bool = True) -> Dict:
    """分析股票（ThreadPool并行版）"""
    engine = AnalysisEngine()
    mode_names = {"quick": "快速版", "standard": "标准版", "pro": "专业版"}
    
    start_time = time.time()
    context = {"code": code, "name": name or code, "price": price or 0}
    
    if verbose:
        print(f"\n📊 开始分析: {code} {context['name']} ({mode_names.get(mode, mode)})")
        print("=" * 50)
    
    result = {"code": code, "name": context["name"], "mode": mode, "price": context["price"]}
    
    if mode == "quick":
        analysts = [("产业分析师", ""), ("估值分析师", ""), ("风险分析师", "")]
        if verbose:
            print("\n🚀 并行分析（3个分析师）...")
        results = engine.analyze_parallel(analysts, context, mode, verbose)
        for n, r in results.items():
            result[n.replace("师", "")] = r
        result["final"] = {"综合评分": _quick_score(result), "投资建议": _quick_advice(result)}
    else:
        analysts = [("产业分析师", ""), ("估值分析师", ""), ("技术分析师", ""),
                   ("风险分析师", ""), ("资金分析师", "")]
        if verbose:
            print("\n🚀 并行分析（5个分析师）...")
        results = engine.analyze_parallel(analysts, context, mode, verbose)
        for n, r in results.items():
            result[n.replace("师", "")] = r
        if verbose:
            print("\n🎯 策略师综合...")
        result["final"] = engine.analyze("策略师", "", context, mode)
    
    elapsed = time.time() - start_time
    if verbose:
        print(f"\n✅ 完成！耗时: {elapsed:.1f}s")
    
    result["elapsed_seconds"] = elapsed
    return result


def _quick_score(result: Dict) -> int:
    score = 60
    if "产业" in result and result["产业"].get("景气度") in ["高", "中高"]:
        score += 10
    if "估值" in result and "低估" in str(result["估值"].get("估值判断", "")):
        score += 10
    if "风险" in result and result["风险"].get("风险等级") in ["低", "中低"]:
        score += 10
    return min(100, score)


def _quick_advice(result: Dict) -> str:
    score = _quick_score(result)
    if score >= 80:
        return "建议关注"
    elif score >= 60:
        return "可以观察"
    return "谨慎对待"


def print_report(result: Dict):
    """打印报告"""
    print(f"\n{'='*60}")
    print(f"📊 {result['code']} {result['name']} 分析报告")
    print(f"{'='*60}")
    final = result.get("final", {})
    print(f"\n🎯 综合评分: {final.get('综合评分', 'N/A')}")
    print(f"   投资建议: {final.get('投资建议', 'N/A')}")
    print(f"\n⏱️ 耗时: {result.get('elapsed_seconds', 0):.1f}s")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    print("🧪 ThreadPool v4.0 测试")
    result = analyze_stock("600519", "贵州茅台", 1550, mode="quick")
    print_report(result)