"""
数据获取模块 - 多数据源支持

设计原则：
1. 优先使用 HTTP API（无需安装依赖）
2. 提供 Akshare 作为增强选项
3. 自动降级：主数据源失败 → 备用数据源
4. 用户可选择数据源
"""

from typing import Dict, Any, List, Optional
import json
import urllib.request
import urllib.error
from datetime import datetime


class DataSource:
    """数据源基类"""
    
    name: str = "base"
    requires_install: bool = False
    dependencies: List[str] = []
    
    def is_available(self) -> bool:
        """检查数据源是否可用"""
        return True
    
    def get_stock_price(self, code: str) -> Dict:
        """获取股票价格"""
        raise NotImplementedError
    
    def get_stock_info(self, code: str) -> Dict:
        """获取股票信息"""
        raise NotImplementedError


# ============================================================
# 数据源 1: 东方财富 API（HTTP 直接调用，无需安装）
# ============================================================

class EastMoneySource(DataSource):
    """东方财富数据源 - HTTP API 直接调用"""
    
    name = "东方财富"
    requires_install = False
    dependencies = []
    
    def is_available(self) -> bool:
        """检查 API 是否可用"""
        try:
            url = "http://push2.eastmoney.com/api/qt/stock/get"
            params = "?secid=1.000001&fields=f43,f44,f45,f46,f47"
            urllib.request.urlopen(url + params, timeout=5)
            return True
        except:
            return False
    
    def get_stock_price(self, code: str) -> Dict:
        """获取股票实时价格
        
        Args:
            code: 股票代码，如 "600821"
        
        Returns:
            {
                "code": "600821",
                "name": "金开新能",
                "price": 5.85,
                "change": 0.05,
                "change_pct": 0.86,
                "volume": 1234567,
                "amount": 72345678.90,
                "time": "2026-03-21 13:00:00"
            }
        """
        # 判断市场：6 开头是上海，0/3 开头是深圳
        market = "1" if code.startswith("6") else "0"
        secid = f"{market}.{code}"
        
        url = f"http://push2.eastmoney.com/api/qt/stock/get"
        params = f"?secid={secid}&fields=f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f55,f57,f58"
        
        try:
            with urllib.request.urlopen(url + params, timeout=10) as response:
                data = json.loads(response.read().decode())
                
            if data.get("data"):
                d = data["data"]
                return {
                    "code": code,
                    "name": d.get("f58", ""),
                    "price": d.get("f43", 0) / 100 if d.get("f43") else 0,
                    "change": d.get("f44", 0) / 100 if d.get("f44") else 0,
                    "change_pct": d.get("f45", 0) / 100 if d.get("f45") else 0,
                    "volume": d.get("f47", 0),
                    "amount": d.get("f48", 0),
                    "high": d.get("f46", 0) / 100 if d.get("f46") else 0,
                    "low": d.get("f51", 0) / 100 if d.get("f51") else 0,
                    "open": d.get("f50", 0) / 100 if d.get("f50") else 0,
                    "prev_close": d.get("f55", 0) / 100 if d.get("f55") else 0,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": self.name,
                }
        except Exception as e:
            return {"error": str(e), "source": self.name}
        
        return {"error": "No data", "source": self.name}
    
    def get_stock_info(self, code: str) -> Dict:
        """获取股票基本信息"""
        return self.get_stock_price(code)


# ============================================================
# 数据源 2: 新浪财经 API（HTTP 直接调用，无需安装）
# ============================================================

class SinaFinanceSource(DataSource):
    """新浪财经数据源 - HTTP API 直接调用"""
    
    name = "新浪财经"
    requires_install = False
    dependencies = []
    
    def is_available(self) -> bool:
        """检查 API 是否可用"""
        try:
            url = "http://hq.sinajs.cn/list=sh600000"
            urllib.request.urlopen(url, timeout=5)
            return True
        except:
            return False
    
    def get_stock_price(self, code: str) -> Dict:
        """获取股票实时价格"""
        prefix = "sh" if code.startswith("6") else "sz"
        symbol = f"{prefix}{code}"
        
        url = f"http://hq.sinajs.cn/list={symbol}"
        
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = response.read().decode("gbk")
            
            if '="' in data:
                content = data.split('="')[1].split('"')[0]
                if content:
                    parts = content.split(",")
                    if len(parts) >= 32:
                        return {
                            "code": code,
                            "name": parts[0],
                            "open": float(parts[1]),
                            "prev_close": float(parts[2]),
                            "price": float(parts[3]),
                            "high": float(parts[4]),
                            "low": float(parts[5]),
                            "volume": int(parts[8]),
                            "amount": float(parts[9]),
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "source": self.name,
                        }
        except Exception as e:
            return {"error": str(e), "source": self.name}
        
        return {"error": "No data", "source": self.name}


# ============================================================
# 数据源 3: Akshare（需要安装，功能更强）
# ============================================================

class AkshareSource(DataSource):
    """Akshare 数据源 - 需要安装 akshare"""
    
    name = "Akshare"
    requires_install = True
    dependencies = ["akshare"]
    
    def __init__(self):
        self._akshare = None
        self._available = None
    
    def is_available(self) -> bool:
        """检查 Akshare 是否安装"""
        if self._available is None:
            try:
                import akshare
                self._akshare = akshare
                self._available = True
            except ImportError:
                self._available = False
        return self._available
    
    def get_stock_price(self, code: str) -> Dict:
        """获取股票实时价格"""
        if not self.is_available():
            return {"error": "Akshare not installed", "source": self.name}
        
        try:
            df = self._akshare.stock_zh_a_spot_em()
            row = df[df["代码"] == code]
            if not row.empty:
                r = row.iloc[0]
                return {
                    "code": code,
                    "name": r["名称"],
                    "price": float(r["最新价"]),
                    "change": float(r["涨跌额"]),
                    "change_pct": float(r["涨跌幅"]),
                    "volume": int(r["成交量"]),
                    "amount": float(r["成交额"]),
                    "high": float(r["最高"]),
                    "low": float(r["最低"]),
                    "open": float(r["今开"]),
                    "prev_close": float(r["昨收"]),
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": self.name,
                }
        except Exception as e:
            return {"error": str(e), "source": self.name}
        
        return {"error": "No data", "source": self.name}


# ============================================================
# 数据源管理器
# ============================================================

class DataSourceManager:
    """数据源管理器 - 自动选择可用数据源"""
    
    def __init__(self, preferred_source: str = None):
        """
        初始化数据源管理器
        
        Args:
            preferred_source: 首选数据源 ("eastmoney" | "sina" | "akshare")
        """
        self.sources = {
            "akshare": AkshareSource(),  # Akshare 优先（更稳定）
            "eastmoney": EastMoneySource(),
            "sina": SinaFinanceSource(),
        }
        
        self.preferred = preferred_source or "akshare"  # 默认使用 Akshare
        self.priority = ["akshare", "eastmoney", "sina"]  # Akshare 优先
    
    def list_sources(self) -> List[Dict]:
        """列出所有数据源及其状态"""
        result = []
        for name, source in self.sources.items():
            result.append({
                "name": source.name,
                "key": name,
                "available": source.is_available(),
                "requires_install": source.requires_install,
                "dependencies": source.dependencies,
            })
        return result
    
    def get_available_sources(self) -> List[str]:
        """获取所有可用的数据源"""
        return [name for name, source in self.sources.items() if source.is_available()]
    
    def get_stock_price(self, code: str, source: str = None) -> Dict:
        """
        获取股票价格
        
        自动降级：如果指定的数据源失败，尝试下一个可用数据源
        """
        if source and source in self.sources:
            result = self.sources[source].get_stock_price(code)
            if "error" not in result:
                return result
        
        for name in self.priority:
            if self.sources[name].is_available():
                result = self.sources[name].get_stock_price(code)
                if "error" not in result:
                    return result
        
        return {"error": "No available data source", "code": code}


# ============================================================
# 便捷函数
# ============================================================

_data_manager = None

def get_data_manager() -> DataSourceManager:
    """获取全局数据源管理器"""
    global _data_manager
    if _data_manager is None:
        _data_manager = DataSourceManager()
    return _data_manager

def get_stock_price(code: str, source: str = None) -> Dict:
    """
    获取股票价格（便捷函数）
    
    Args:
        code: 股票代码，如 "600821"
        source: 数据源（可选）"eastmoney" | "sina" | "akshare"
    
    Returns:
        股票价格数据
    
    Example:
        >>> get_stock_price("600821")
        {"code": "600821", "name": "金开新能", "price": 5.85, ...}
    """
    return get_data_manager().get_stock_price(code, source)

def check_data_sources() -> List[Dict]:
    """检查所有数据源状态"""
    return get_data_manager().list_sources()


__all__ = [
    "DataSourceManager",
    "EastMoneySource",
    "SinaFinanceSource", 
    "AkshareSource",
    "get_stock_price",
    "check_data_sources",
]