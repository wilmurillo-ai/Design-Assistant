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

# ============================================================
# 环境检测
# ============================================================

# 检测 akshare 是否可用
try:
    import akshare as ak
    HAS_AKSHARE = True
except ImportError:
    HAS_AKSHARE = False

# 检测 browserless 是否可用
BROWSERLESS_URL = os.environ.get("BROWSERLESS_URL", "")
HAS_BROWSERLESS = False
try:
    import urllib.request
    req = urllib.request.Request(f"{BROWSERLESS_URL}/json/version", method="GET")
    with urllib.request.urlopen(req, timeout=5) as response:
        if "Browser" in response.read().decode():
            HAS_BROWSERLESS = True
except:
    HAS_BROWSERLESS = False

def get_environment_status() -> Dict[str, Any]:
    """获取环境状态"""
    return {
        "akshare": HAS_AKSHARE,
        "browserless": HAS_BROWSERLESS,
        "browserless_url": BROWSERLESS_URL if HAS_BROWSERLESS else None,
        "mode": "完整模式" if (HAS_AKSHARE and HAS_BROWSERLESS) else ("标准模式" if HAS_AKSHARE else "纯AI模式")
    }


class AnalysisEngine:
    """AI 分析引擎 v4.1 (自动适配客户 API)"""
    
    SINGLE_CALL_TIMEOUT = 45  # 增加超时
    TOKEN_LIMITS = {"quick": 150, "standard": 800, "pro": 1500}
    REQUEST_DELAY = 1.0  # 增加请求间隔
    MAX_RETRIES = 2
    
    def __init__(self, model: str = None):
        # 自动从 OpenClaw 配置读取模型和 API
        self.model, self.api_base, self.api_key = self._get_openclaw_config()
        
        # 如果手动指定模型，覆盖默认值
        if model:
            self.model = model
        
        self._cache: Dict[str, Dict] = {}
        self._cache_ttl = 300
        self._max_retries = 2
        self._shared_insights: Dict[str, str] = {}
    
    def _get_openclaw_config(self) -> Tuple[str, str, str]:
        """
        从 OpenClaw 配置自动读取模型和 API
        
        Returns:
            (model, api_base, api_key)
        """
        try:
            config_path = os.path.expanduser("~/.openclaw/openclaw.json")
            with open(config_path, "r") as f:
                config = json.load(f)
            
            # 获取默认模型
            primary = config.get("agents", {}).get("defaults", {}).get("model", {}).get("primary", "")
            
            if not primary:
                # 默认使用智谱API（更稳定）
                return self._get_zhipu_config(config)
            
            # 解析 provider 和 model
            if "/" in primary:
                provider_name, model_name = primary.split("/", 1)
            else:
                provider_name, model_name = "zhipu", primary
            
            # 获取 provider 配置
            providers = config.get("models", {}).get("providers", {})
            provider = providers.get(provider_name, {})
            
            api_base = provider.get("baseUrl", "")
            api_key = provider.get("apiKey", "")
            
            # 如果是bailian，检查是否有智谱备用
            if provider_name == "bailian":
                # bailian不稳定，优先使用智谱
                zhipu_provider = providers.get("zhipu", {})
                if zhipu_provider.get("apiKey"):
                    return ("glm-4-flash", 
                            zhipu_provider.get("baseUrl", "https://open.bigmodel.cn/api/paas/v4"),
                            zhipu_provider.get("apiKey", ""))
            
            return (model_name, api_base, api_key)
            
        except Exception as e:
            # 降级：使用智谱作为默认
            print(f"⚠️ 无法读取 OpenClaw 配置: {e}")
            return ("glm-4-flash", "https://open.bigmodel.cn/api/paas/v4",
                    os.environ.get("ZHIPU_API_KEY", ""))
    
    def _get_zhipu_config(self, config: Dict) -> Tuple[str, str, str]:
        """获取智谱API配置"""
        providers = config.get("models", {}).get("providers", {})
        zhipu = providers.get("zhipu", {})
        return ("glm-4-flash", 
                zhipu.get("baseUrl", "https://open.bigmodel.cn/api/paas/v4"),
                zhipu.get("apiKey", os.environ.get("ZHIPU_API_KEY", "")))
    
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
                last_error = str(e)
                print(f"  ⚠️ [{analyst_name}] 失败: {e}")
                time.sleep(1)
        
        return self._fallback_analysis(analyst_name, last_error if 'last_error' in dir() else "重试耗尽")
    
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
        """构建 prompt（带真实数据支撑）"""
        shared = self._get_shared_insights()
        shared_ctx = f"\n\n其他见解:\n{shared}" if shared else ""
        code = context.get('code', '') if context else ''
        stock_name = context.get('name', '') if context else ''
        
        # 提取真实数据
        price = context.get('price', 0)
        change_pct = context.get('change_pct', 0)
        volume = context.get('volume', 0)
        high = context.get('high', 0)
        low = context.get('low', 0)
        
        # 数据摘要
        data_summary = f"当前价:{price}元,涨跌:{change_pct:+.2f}%,成交量:{volume:,},最高:{high},最低:{low}"
        
        if mode == "quick":
            prompts = {
                "产业分析师": f"""【数据】{data_summary}
分析{stock_name}行业。返回JSON:
{{"行业":"名称","景气度":"高/中/低","分析过程":"1.数据引用 2.原因分析 3.判断依据","结论":"总结"}}""",
                
                "估值分析师": f"""【数据】{data_summary}
分析{stock_name}估值。返回JSON:
{{"PE":"估算","判断":"低估/合理/高估","分析过程":"1.当前价格分析 2.估值对比 3.判断理由","结论":"总结"}}""",
                
                "风险分析师": f"""【数据】{data_summary}
分析{stock_name}风险。返回JSON:
{{"等级":"高/中/低","分析过程":"1.跌幅{change_pct:+.2f}%含义 2.成交量信号 3.等级依据","结论":"总结"}}"""
            }
        else:
            prompts = {
                "产业分析师": f"""【数据】{data_summary}
分析{stock_name}产业。返回JSON，分析过程必须写具体内容：
{{"行业":"具体行业名称","景气度":"高/中/低","分析过程":"第一步：分析当前行业现状，包括...；第二步：分析公司在行业中的地位，...；第三步：给出景气度判断依据，...","结论":"综合判断结论"}}""",
                
                "估值分析师": f"""【数据】{data_summary}
【财务数据】PE: {context.get('financial', {}).get('pe', '无')} | PB: {context.get('financial', {}).get('pb', '无')} | ROE: {context.get('financial', {}).get('roe', '无')}
分析{stock_name}估值。返回JSON，分析过程必须写具体内容：
{{"PE":"{context.get('financial', {}).get('pe', '估算')}","PB":"{context.get('financial', {}).get('pb', '估算')}","判断":"低估/合理/高估","分析过程":"第一步：分析当前价格{price}元和PE/PB数据的估值含义；第二步：对比同行业估值水平；第三步：给出估值判断理由","结论":"估值判断结论"}}""",
                
                "技术分析师": f"""【数据】{data_summary}
分析{stock_name}技术面。返回JSON，分析过程必须写具体内容：
{{"趋势":"上涨/下跌/震荡","支撑":"具体价位{low}元","压力":"具体价位{high}元","分析过程":"第一步：分析涨跌幅{change_pct:+.2f}%的技术含义；第二步：分析高低点{high}/{low}的意义；第三步：给出支撑压力位判断依据","建议":"具体操作建议","结论":"技术面判断结论"}}""",
                
                "风险分析师": f"""【数据】{data_summary}
分析{stock_name}风险。返回JSON，分析过程必须写具体内容：
{{"等级":"高/中/低","分析过程":"第一步：分析跌幅{change_pct:+.2f}%的风险含义；第二步：分析波动风险；第三步：给出风险等级依据","预警":"具体风险点","结论":"风险判断结论"}}""",
                
                "资金分析师": f"""【数据】{data_summary}
分析{stock_name}资金面。返回JSON，分析过程必须写具体内容：
{{"主力":"流入/流出/观望","北向":"流入/流出/观望","分析过程":"第一步：分析成交量{volume:,}的含义；第二步：分析资金流向；第三步：给出影响判断","评价":"资金面评价","结论":"资金面判断结论"}}""",
                
                "策略师": f"""【数据】{data_summary}
综合分析{stock_name}。返回JSON，评分必须是0-100的具体数字：
{{"评分":"60-90之间的具体数字","分析过程":"第一步：产业分析结论；第二步：估值分析结论；第三步：技术分析结论；第四步：风险分析结论；第五步：给出评分依据","建议":"买入/持有/卖出","风险":"主要风险点","操作":"具体操作建议","结论":"综合判断结论"}}"""
            }
        return prompts.get(name)
    
    def _parse_response(self, name: str, response: str) -> Dict:
        try:
            # 方式1: 提取 ```json 代码块
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                # 清理控制字符
                json_str = ''.join(char for char in json_str if ord(char) >= 32 or char in '\n\r\t')
                return json.loads(json_str)
            # 方式2: 直接提取 JSON 对象
            elif "{" in response:
                start = response.index("{")
                end = response.rindex("}") + 1
                json_str = response[start:end]
                # 清理控制字符
                json_str = ''.join(char for char in json_str if ord(char) >= 32 or char in '\n\r\t')
                return json.loads(json_str)
        except Exception as e:
            pass
        # 解析失败，返回原始文本
        return {"analyst": name, "analysis": response, "_parse_failed": True}
    
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


def _try_akshare_tx(code: str) -> Dict:
    """尝试使用 akshare 腾讯源获取数据"""
    try:
        import akshare as ak
        market = "sh" if code.startswith("6") else "sz"
        symbol = f"{market}{code}"
        df = ak.stock_zh_a_hist_tx(symbol=symbol)
        
        if len(df) >= 2:
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            change_pct = round((latest['close'] - prev['close']) / prev['close'] * 100, 2)
            return {
                "code": code,
                "name": code,
                "price": float(latest['close']),
                "change_pct": change_pct,
                "volume": int(latest['amount']),
                "high": float(latest['high']),
                "low": float(latest['low']),
                "open": float(latest['open']),
                "prev_close": float(prev['close']),
                "source": "akshare-腾讯",
            }
    except Exception as e:
        pass
    return {"error": str(e)}


def _try_akshare_em(code: str) -> Dict:
    """尝试使用 akshare 东财源获取数据"""
    try:
        import akshare as ak
        df = ak.stock_zh_a_spot_em()
        row = df[df['代码'] == code]
        if len(row) > 0:
            r = row.iloc[0]
            return {
                "code": code,
                "name": r['名称'],
                "price": float(r['最新价']),
                "change_pct": float(r['涨跌幅']),
                "volume": int(r['成交量']),
                "high": float(r['最高']),
                "low": float(r['最低']),
                "source": "akshare-东财",
            }
    except Exception as e:
        pass
    return {"error": str(e)}


def _try_data_fetcher(code: str) -> Dict:
    """尝试使用 data_fetcher 获取数据"""
    try:
        from data_fetcher import get_stock_price
        return get_stock_price(code)
    except Exception as e:
        return {"error": str(e)}


def _get_financial_data(code: str, verbose: bool = False) -> Dict:
    """
    获取股票财务数据（PE/PB/ROE等）
    
    优先级：
    1. 东财 push2 API（直接curl）
    2. akshare 东财实时行情
    3. browser 访问东方财富页面
    
    Returns:
        Dict: {pe, pb, roe, 毛利率, 净利率, source}
    """
    result = {"pe": None, "pb": None, "roe": None, "毛利率": None, "净利率": None, "source": "无"}
    
    # 方法1: 东财push2 API（优先）
    try:
        import urllib.request
        import json
        
        secid = f"1.{code}" if code.startswith("6") else f"0.{code}"
        url = f"https://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f162,f167,f173,f187,f105"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as response:
            output = response.read().decode()
        
        if output:
            data = json.loads(output)
            if data.get("data"):
                d = data["data"]
                pe_raw = d.get("f162")
                pb_raw = d.get("f167")
                roe_raw = d.get("f173")
                
                result["pe"] = pe_raw / 100 if pe_raw and pe_raw > 0 else None
                result["pb"] = pb_raw / 100 if pb_raw and pb_raw > 0 else None
                result["roe"] = roe_raw / 100 if roe_raw and roe_raw > 0 else None
                result["source"] = "eastmoney-api"
                
                if verbose:
                    print(f"  📊 财务数据: PE={result['pe']}, PB={result['pb']} (来源: {result['source']})")
                return result
    except Exception as e:
        if verbose:
            print(f"  ⚠️ 东财API获取失败: {e}")
    
    # 方法2: akshare东财实时行情（降级）
    try:
        import akshare as ak
        df = ak.stock_zh_a_spot_em()
        row = df[df['代码'] == code]
        if len(row) > 0:
            r = row.iloc[0]
            cols = list(r.index)
            pe_col = [c for c in cols if '盈' in c and '动' in c]
            pb_col = [c for c in cols if '净' in c and '率' in c]
            
            if pe_col:
                result["pe"] = r[pe_col[0]]
            if pb_col:
                result["pb"] = r[pb_col[0]]
            
            result["source"] = "akshare-东财"
            if verbose:
                print(f"  📊 财务数据: PE={result['pe']}, PB={result['pb']} (来源: {result['source']})")
            return result
    except Exception as e:
        if verbose:
            print(f"  ⚠️ akshare获取财务数据失败: {e}")
    
    # 方法3: browser访问东方财富页面（最终降级）
    try:
        # 使用 urllib 获取页面
        import urllib.request
        import json
        import re
        
        market = "sh" if code.startswith("6") else "sz"
        url = f"https://quote.eastmoney.com/{market}{code}.html"
        
        # 使用 urllib 替代 curl
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode()
        
        if html:
            
            # 从页面HTML提取数据 - 查找财务指标表格
            # PE(动) 通常在表格中
            pe_patterns = [
                r'市盈\(动\)[^>]*>[\s\S]*?>(\d+\.?\d*)',
                r'PE\(动\)[^>]*>[\s\S]*?>(\d+\.?\d*)',
                r'市盈率[^>]*>[\s\S]*?(\d+\.\d+)',
            ]
            
            pb_patterns = [
                r'市净[^>]*>[\s\S]*?>(\d+\.?\d*)',
                r'市净率[^>]*>[\s\S]*?(\d+\.\d+)',
            ]
            
            for pattern in pe_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    try:
                        result["pe"] = float(match.group(1))
                        break
                    except:
                        pass
            
            for pattern in pb_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    try:
                        result["pb"] = float(match.group(1))
                        break
                    except:
                        pass
            
            if result["pe"] or result["pb"]:
                result["source"] = "browser-eastmoney"
                if verbose:
                    print(f"  📊 财务数据: PE={result['pe']}, PB={result['pb']} (来源: {result['source']})")
                return result
        
    except Exception as e:
        if verbose:
            print(f"  ⚠️ browser获取财务数据失败: {e}")
    
    result["source"] = "无法获取"
    return result


def _get_fund_data(fund_code: str, verbose: bool = False) -> Dict:
    """
    获取基金数据（净值、持仓、基金经理等）
    
    Args:
        fund_code: 基金代码（如 "000001"）
        verbose: 是否打印详细信息
    
    Returns:
        Dict: {净值, 累计净值, 日增长率, 基金类型, 基金经理, 基金公司, source}
    """
    result = {
        "净值": None,
        "累计净值": None,
        "日增长率": None,
        "基金类型": None,
        "基金经理": None,
        "基金公司": None,
        "成立时间": None,
        "基金规模": None,
        "source": "无"
    }
    
    try:
        import akshare as ak
        
        # 方法1: 获取基金基本信息
        try:
            df_info = ak.fund_individual_basic_info_xq(symbol=fund_code)
            if df_info is not None and len(df_info) > 0:
                info_dict = dict(zip(df_info['item'], df_info['value']))
                result["基金类型"] = info_dict.get("基金类型", "未知")
                result["基金经理"] = info_dict.get("基金经理", "未知")
                result["基金公司"] = info_dict.get("基金公司", "未知")
                result["成立时间"] = info_dict.get("成立时间", "未知")
                result["基金规模"] = info_dict.get("最新规模", "未知")
                result["source"] = "akshare-雪球"
        except Exception as e:
            if verbose:
                print(f"  ⚠️ 基金基本信息获取失败: {e}")
        
        # 方法2: 获取基金净值数据
        try:
            df_nav = ak.fund_open_fund_daily_em()
            row = df_nav[df_nav['基金代码'] == fund_code]
            if len(row) > 0:
                r = row.iloc[0]
                # 获取净值字段
                cols = list(r.index)
                nav_col = [c for c in cols if '单位净值' in c]
                acc_col = [c for c in cols if '累计净值' in c]
                
                if nav_col:
                    result["净值"] = r[nav_col[0]]
                if acc_col:
                    result["累计净值"] = r[acc_col[0]]
                result["日增长率"] = r.get("日增长率", None)
                result["source"] = "akshare-东财"
                
        except Exception as e:
            if verbose:
                print(f"  ⚠️ 基金净值获取失败: {e}")
        
        if verbose:
            print(f"  📊 基金数据: {result.get('基金类型', 'N/A')} | 净值: {result.get('净值', 'N/A')} (来源: {result['source']})")
        
    except Exception as e:
        if verbose:
            print(f"  ⚠️ 基金数据获取失败: {e}")
        result["source"] = "无法获取"
    
    return result


def analyze_stock(code: str, name: str = None, price: float = None, 
                  mode: str = "standard", verbose: bool = True) -> Dict:
    """
    分析股票（ThreadPool并行版）- 带真实数据支撑
    
    数据获取优先级：
    1. akshare 腾讯源 (stock_zh_a_hist_tx) - 最稳定
    2. akshare 东财源 (stock_zh_a_spot_em)
    3. data_fetcher 模块
    4. 用户手动提供的参数
    """
    engine = AnalysisEngine()
    mode_names = {"quick": "快速版", "standard": "标准版", "pro": "专业版"}
    
    start_time = time.time()
    
    # ========== 第一步：按优先级获取真实数据 ==========
    real_data = {}
    data_source = "未知"
    
    if verbose:
        print(f"\n📡 获取 {code} 实时数据...")
    
    # 优先级1: akshare 腾讯源（最稳定）
    real_data = _try_akshare_tx(code)
    if "error" not in real_data:
        data_source = "akshare-腾讯"
        name = real_data.get("name", name or code)
        price = real_data.get("price", price or 0)
        if verbose:
            print(f"  ✅ {name}: ¥{price} ({real_data.get('change_pct', 0):+.2f}%)")
            print(f"  📊 数据源: {data_source}")
    
    # 优先级2: akshare 东财源
    if "error" in real_data:
        real_data = _try_akshare_em(code)
        if "error" not in real_data:
            data_source = "akshare-东财"
            name = real_data.get("name", name or code)
            price = real_data.get("price", price or 0)
            if verbose:
                print(f"  ✅ {name}: ¥{price}")
                print(f"  📊 数据源: {data_source}")
    
    # 优先级3: data_fetcher
    if "error" in real_data:
        real_data = _try_data_fetcher(code)
        if "error" not in real_data:
            data_source = real_data.get("source", "data_fetcher")
            name = real_data.get("name", name or code)
            price = real_data.get("price", price or 0)
            if verbose:
                print(f"  ✅ {name}: ¥{price}")
                print(f"  📊 数据源: {data_source}")
    
    # 优先级4: 使用用户参数
    if "error" in real_data:
        if price is not None:
            real_data = {
                "code": code,
                "name": name or code,
                "price": price,
                "change_pct": 0,
                "volume": 0,
                "high": price,
                "low": price,
                "source": "用户参数",
            }
            data_source = "用户参数"
            if verbose:
                print(f"  ℹ️ 使用用户参数: {name} ¥{price}")
        else:
            if verbose:
                print(f"  ⚠️ 无法获取数据，且用户未提供参数")
            real_data = {"error": "无数据源可用", "code": code}
    
    # 构建上下文（包含真实数据）
    context = {
        "code": code,
        "name": name or code,
        "price": real_data.get("price", price or 0),
        "change_pct": real_data.get("change_pct", 0),
        "volume": real_data.get("volume", 0),
        "high": real_data.get("high", 0),
        "low": real_data.get("low", 0),
        "open": real_data.get("open", 0),
        "prev_close": real_data.get("prev_close", 0),
    }
    
    # 获取财务数据（PE/PB/ROE）
    if verbose:
        print(f"  📊 获取财务数据...")
    financial_data = _get_financial_data(code, verbose)
    context["financial"] = financial_data
    
    if verbose:
        print(f"\n📊 开始分析: {code} {context['name']} ({mode_names.get(mode, mode)})")
        print(f"💰 数据来源: {data_source}")
        if financial_data.get("pe"):
            print(f"📊 PE: {financial_data.get('pe')} | PB: {financial_data.get('pb')}")
        print("=" * 50)
    
    result = {
        "code": code, 
        "name": context["name"], 
        "mode": mode, 
        "price": context["price"],
        "data_source": data_source,
        "real_data": real_data  # 保存原始数据
    }
    
    if mode == "quick":
        analysts = [("产业分析师", ""), ("估值分析师", ""), ("风险分析师", "")]
        if verbose:
            print("\n🚀 并行分析（3个分析师）...")
        results = engine.analyze_parallel(analysts, context, mode, verbose)
        name_map = {
            "产业分析师": "产业",
            "估值分析师": "估值", 
            "技术分析师": "技术",
            "风险分析师": "风险",
            "资金分析师": "资金"
        }
        for n, r in results.items():
            key = name_map.get(n, n)
            result[key] = r
        result["final"] = {"综合评分": _quick_score(result), "投资建议": _quick_advice(result)}
    
    elif mode == "standard":
        analysts = [("产业分析师", ""), ("估值分析师", ""), ("技术分析师", ""),
                   ("风险分析师", ""), ("资金分析师", "")]
        if verbose:
            print("\n🚀 并行分析（5个分析师）...")
        results = engine.analyze_parallel(analysts, context, mode, verbose)
        name_map = {
            "产业分析师": "产业",
            "估值分析师": "估值",
            "技术分析师": "技术",
            "风险分析师": "风险",
            "资金分析师": "资金"
        }
        for n, r in results.items():
            key = name_map.get(n, n)
            result[key] = r
        if verbose:
            print("\n🎯 策略师综合...")
        result["final"] = engine.analyze("策略师", "", context, mode)
    
    elif mode == "pro":
        # ========== 专业版迭代分析 ==========
        analysts = [("产业分析师", ""), ("估值分析师", ""), ("技术分析师", ""),
                   ("风险分析师", ""), ("资金分析师", "")]
        name_map = {
            "产业分析师": "产业",
            "估值分析师": "估值",
            "技术分析师": "技术",
            "风险分析师": "风险",
            "资金分析师": "资金"
        }
        
        # 保存迭代过程
        iteration_log = {
            "rounds": 3,
            "round1_results": {},
            "round2_results": {},
            "changes": {}
        }
        
        # Round 1: 分析师独立分析
        if verbose:
            print("\n🔄 Round 1: 分析师独立分析...")
        results_round1 = engine.analyze_parallel(analysts, context, mode, verbose)
        
        # 保存Round 1结果
        for name, r in results_round1.items():
            key = name_map.get(name, name)
            if isinstance(r, dict):
                iteration_log["round1_results"][key] = {
                    "结论": r.get("结论", ""),
                    "判断": r.get("判断", r.get("景气度", r.get("等级", "")))
                }
        
        # 构建共享意见
        shared_insights = {}
        for name, r in results_round1.items():
            if isinstance(r, dict) and "结论" in r:
                shared_insights[name] = r["结论"]
        
        # Round 2: 分析师交换意见
        if verbose:
            print("\n🔄 Round 2: 分析师交换意见...")
        results_round2 = {}
        for name, _ in analysts:
            other_insights = {k: v for k, v in shared_insights.items() if k != name}
            insight_context = context.copy()
            insight_context["其他分析师意见"] = other_insights
            
            r = engine.analyze(name, "", insight_context, mode)
            results_round2[name] = r
            
            # 记录变化
            key = name_map.get(name, name)
            r1_conclusion = iteration_log["round1_results"].get(key, {}).get("结论", "")
            r2_conclusion = r.get("结论", "") if isinstance(r, dict) else ""
            
            if r1_conclusion != r2_conclusion:
                iteration_log["changes"][key] = {
                    "初始结论": r1_conclusion[:100] + "..." if len(r1_conclusion) > 100 else r1_conclusion,
                    "修正结论": r2_conclusion[:100] + "..." if len(r2_conclusion) > 100 else r2_conclusion,
                    "参考意见": "参考了其他分析师的观点"
                }
            
            if verbose:
                print(f"  ✅ [{name}] 修正完成")
        
        # 保存Round 2结果
        for name, r in results_round2.items():
            key = name_map.get(name, name)
            if isinstance(r, dict):
                iteration_log["round2_results"][key] = {
                    "结论": r.get("结论", ""),
                    "判断": r.get("判断", r.get("景气度", r.get("等级", "")))
                }
        
        # Round 3: 策略师综合讨论
        if verbose:
            print("\n🔄 Round 3: 策略师综合讨论...")
        
        all_conclusions = {}
        for name, r in results_round2.items():
            key = name_map.get(name, name)
            result[key] = r
            if isinstance(r, dict) and "结论" in r:
                all_conclusions[key] = r["结论"]
        
        strategist_context = context.copy()
        strategist_context["分析师共识"] = all_conclusions
        
        final = engine.analyze("策略师", "", strategist_context, mode)
        result["final"] = final
        
        # 添加完整迭代日志
        result["iteration"] = iteration_log
        
        if verbose:
            print(f"\n✅ 专业版迭代完成！共3轮迭代")
    
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


def analyze_fund(fund_code: str, fund_name: str = None, mode: str = "standard", verbose: bool = False) -> Dict:
    """
    分析基金（股票型/混合型/债券型/QDII）
    
    Args:
        fund_code: 基金代码（如 "000001"）
        fund_name: 基金名称（可选）
        mode: 分析模式 (quick/standard/pro)
        verbose: 是否打印详细信息
    
    Returns:
        Dict: 基金分析结果
    """
    start_time = time.time()
    mode_names = {"quick": "快速版", "standard": "标准版", "pro": "专业版"}
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"📊 开始分析基金: {fund_code} ({mode_names.get(mode, mode)})")
        print(f"{'='*60}")
    
    # 获取基金数据
    if verbose:
        print(f"\n📡 获取基金数据...")
    
    fund_data = _get_fund_data(fund_code, verbose)
    
    # 构建上下文
    context = {
        "code": fund_code,
        "name": fund_name or fund_data.get("基金公司", fund_code),
        "净值": fund_data.get("净值", "N/A"),
        "累计净值": fund_data.get("累计净值", "N/A"),
        "日增长率": fund_data.get("日增长率", "N/A"),
        "基金类型": fund_data.get("基金类型", "未知"),
        "基金经理": fund_data.get("基金经理", "未知"),
        "基金公司": fund_data.get("基金公司", "未知"),
        "基金规模": fund_data.get("基金规模", "未知"),
        "成立时间": fund_data.get("成立时间", "未知"),
        "source": fund_data.get("source", "无")
    }
    
    if verbose:
        print(f"\n📊 基金信息:")
        print(f"  名称: {context['name']}")
        print(f"  类型: {context['基金类型']}")
        print(f"  净值: {context['净值']} ({context['日增长率']}%)")
        print(f"  经理: {context['基金经理']}")
        print(f"  公司: {context['基金公司']}")
    
    # 创建分析引擎
    engine = AnalysisEngine()
    
    result = {
        "code": fund_code,
        "name": context["name"],
        "mode": mode,
        "fund_data": fund_data,
        "asset_type": "fund"
    }
    
    # 构建数据摘要
    data_summary = f"""基金代码: {fund_code}
基金名称: {context['name']}
基金类型: {context['基金类型']}
单位净值: {context['净值']}
累计净值: {context['累计净值']}
日增长率: {context['日增长率']}%
基金经理: {context['基金经理']}
基金公司: {context['基金公司']}
基金规模: {context['基金规模']}"""
    
    # 根据模式选择分析师
    if mode == "quick":
        analysts = [("基金类型分析师", ""), ("基金经理分析师", ""), ("风险评估师", "")]
    else:
        analysts = [
            ("基金类型分析师", ""),
            ("基金经理分析师", ""),
            ("持仓结构分析师", ""),
            ("业绩表现分析师", ""),
            ("风险评估师", "")
        ]
    
    # 定义分析师 Prompt（参考股票报告标准版格式）
    prompts = {
        "基金类型分析师": f"""【数据】{data_summary}
分析该基金的类型定位。返回JSON，分析过程必须写具体内容：
{{"基金类型":"{context['基金类型']}","投资风格":"成长/价值/平衡","风险等级":"高/中/低","分析过程":"第一步：分析基金类型特点，混合型偏股意味着...；第二步：分析投资风格，该基金投资于成长型股票...；第三步：评估风险等级，基于...判断","结论":"类型定位综合结论"}}""",
        
        "基金经理分析师": f"""【数据】{data_summary}
分析基金经理能力。返回JSON，分析过程必须写具体内容：
{{"基金经理":"{context['基金经理']}","任职年限":"估算或说明","历史业绩":"优秀/良好/一般","分析过程":"第一步：分析基金经理背景，{context['基金经理']}的管理经验...；第二步：评估历史业绩，该基金近期表现...；第三步：给出能力评价","结论":"基金经理能力综合评价"}}""",
        
        "持仓结构分析师": f"""【数据】{data_summary}
分析基金持仓结构。返回JSON，分析过程必须写具体内容：
{{"股票仓位":"高/中/低","行业配置":"集中/分散","重仓股":"分析前十大持仓特点","分析过程":"第一步：分析仓位配置，该基金作为混合型基金...；第二步：分析行业分布，重点配置...行业；第三步：评估持仓风险","结论":"持仓结构综合评价"}}""",
        
        "业绩表现分析师": f"""【数据】{data_summary}
分析基金业绩表现。返回JSON，分析过程必须写具体内容：
{{"近1月收益":"根据日增长率估算","近1年收益":"估算或说明","同类排名":"前1/4/前1/2/后1/2","分析过程":"第一步：分析短期业绩，日增长率{context['日增长率']}%意味着...；第二步：分析长期业绩，累计净值{context['累计净值']}说明...；第三步：对比同类排名","结论":"业绩表现综合评价"}}""",
        
        "风险评估师": f"""【数据】{data_summary}
分析基金风险。返回JSON，分析过程必须写具体内容：
{{"风险等级":"高/中/低","最大回撤":"估算或说明","波动率":"高/中/低","分析过程":"第一步：分析波动风险，净值{context['净值']}的波动...；第二步：分析回撤风险，历史最大回撤约...；第三步：综合风险评估","预警":"具体风险点提示","结论":"风险综合评价结论"}}"""
    }
    
    # 执行分析
    if verbose:
        print(f"\n🚀 并行分析（{len(analysts)}个分析师）...")
    
    results = {}
    name_map = {
        "基金类型分析师": "类型",
        "基金经理分析师": "经理",
        "持仓结构分析师": "持仓",
        "业绩表现分析师": "业绩",
        "风险评估师": "风险"
    }
    
    for analyst_name, _ in analysts:
        if verbose:
            print(f"  🤖 [{analyst_name}] 分析中...")
        
        prompt = prompts.get(analyst_name, "")
        if prompt:
            # 直接调用AI，不通过 _build_prompt
            try:
                max_tokens = engine.TOKEN_LIMITS.get(mode, 800)
                response = engine._call_ai_sync(prompt, max_tokens)
                r = engine._parse_response(analyst_name, response)
                key = name_map.get(analyst_name, analyst_name)
                results[key] = r
                result[key] = r
                if verbose:
                    print(f"  ✅ [{analyst_name}] 完成")
            except Exception as e:
                if verbose:
                    print(f"  ⚠️ [{analyst_name}] 失败: {e}")
                key = name_map.get(analyst_name, analyst_name)
                result[key] = {"skipped": True, "error": str(e)}
    
    # 策略师综合
    if verbose:
        print(f"\n🎯 策略师综合...")
    
    # 收集所有结论
    all_conclusions = {}
    for key, r in results.items():
        if isinstance(r, dict) and "结论" in r:
            all_conclusions[key] = r["结论"]
    
    strategist_prompt = f"""【基金数据】{data_summary}
【分析师结论】
{json.dumps(all_conclusions, ensure_ascii=False, indent=2)}

综合分析该基金，返回JSON:
{{"评分":"60-90之间的具体数字","分析过程":"第一步：类型分析；第二步：经理分析；第三步：业绩分析；第四步：风险分析；第五步：给出评分依据","建议":"买入/持有/观望/赎回","风险":"主要风险点","结论":"综合判断结论"}}"""
    
    final = engine.analyze("策略师", "", context, mode)
    result["final"] = final
    
    elapsed = time.time() - start_time
    if verbose:
        print(f"\n✅ 完成！耗时: {elapsed:.1f}s")
    
    result["elapsed_seconds"] = elapsed
    return result


def print_fund_report(result: Dict):
    """打印基金报告"""
    print(f"\n{'='*60}")
    print(f"📊 {result['code']} {result.get('name', '基金')} 分析报告")
    print(f"{'='*60}")
    
    fund_data = result.get("fund_data", {})
    print(f"\n📋 基本信息:")
    print(f"   基金类型: {fund_data.get('基金类型', 'N/A')}")
    print(f"   基金经理: {fund_data.get('基金经理', 'N/A')}")
    print(f"   基金公司: {fund_data.get('基金公司', 'N/A')}")
    print(f"   单位净值: {fund_data.get('净值', 'N/A')}")
    print(f"   日增长率: {fund_data.get('日增长率', 'N/A')}%")
    
    final = result.get("final", {})
    print(f"\n🎯 综合评分: {final.get('评分', 'N/A')}")
    print(f"   投资建议: {final.get('建议', 'N/A')}")
    print(f"   主要风险: {final.get('风险', 'N/A')}")
    print(f"\n⏱️ 耗时: {result.get('elapsed_seconds', 0):.1f}s")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    print("🧪 ThreadPool v4.0 测试")
    # result = analyze_stock("600519", "贵州茅台", 1550, mode="quick")
    # print_report(result)
    
    # 测试基金分析
    print("\n📊 测试基金分析:")
    result = analyze_fund("000001", "华夏成长混合", mode="standard", verbose=True)
    print_fund_report(result)