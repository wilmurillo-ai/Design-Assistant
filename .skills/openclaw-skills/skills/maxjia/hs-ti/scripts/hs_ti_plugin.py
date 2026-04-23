import json
import urllib.request
import urllib.error
import urllib.parse
import os
import time
import logging
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, asdict, field
from datetime import datetime
from functools import wraps, lru_cache
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from collections import OrderedDict


class IOCType(Enum):
    """IOC类型枚举"""
    IP = "ip"
    DOMAIN = "domain"
    URL = "url"
    HASH = "hash"
    UNKNOWN = "unknown"


class QueryResult(Enum):
    """查询结果枚举"""
    MALICIOUS = "malicious"
    BENIGN = "benign"
    UNKNOWN = "unknown"


@dataclass
class PerformanceStats:
    """性能统计数据类"""
    avg_ms: float
    max_ms: int
    min_ms: int
    median_ms: int
    total_calls: int


@dataclass
class IOCQueryResult:
    """IOC查询结果数据类"""
    ioc: str
    ioc_type: str
    result: Dict[str, Any]
    response_time_ms: int
    success: bool
    error: Optional[str] = None


class YunzhanError(Exception):
    """云瞻威胁情报基础异常"""
    pass


class YunzhanConfigError(YunzhanError):
    """配置错误"""
    pass


class YunzhanAPIError(YunzhanError):
    """API错误"""
    def __init__(self, message: str, status_code: int = None, 
                 response_data: Dict = None):
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message)


class YunzhanNetworkError(YunzhanError):
    """网络错误"""
    pass


class YunzhanTimeoutError(YunzhanError):
    """超时错误"""
    pass


class IOCTypeDetector:
    """IOC类型自动检测器"""
    
    IPV4_PATTERN = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )
    
    IPV6_PATTERN = re.compile(
        r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|'
        r'^(?:(?:[0-9a-fA-F]{1,4}:){1,7}:|'
        r'(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|'
        r'(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|'
        r'(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|'
        r'(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|'
        r'(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|'
        r'[0-9a-fA-F]{1,4}:(?::[0-9a-fA-F]{1,4}){1,6}|'
        r':(?::[0-9a-fA-F]{1,4}){1,7}|'
        r':(?:[0-9a-fA-F]{1,4}:){1,7}|'
        r'fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|'
        r'::(?:ffff(?::0{1,4}){0,1}:){0,1}'
        r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|'
        r'(?:[0-9a-fA-F]{1,4}:){1,4}:'
        r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))$'
    )
    
    DOMAIN_PATTERN = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+'
        r'[a-zA-Z]{2,}$'
    )
    
    URL_PATTERN = re.compile(
        r'^https?://(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+'
        r'[a-zA-Z]{2,}(?:/[^\s]*)?$'
    )
    
    MD5_PATTERN = re.compile(r'^[a-fA-F0-9]{32}$')
    SHA1_PATTERN = re.compile(r'^[a-fA-F0-9]{40}$')
    SHA256_PATTERN = re.compile(r'^[a-fA-F0-9]{64}$')
    
    @classmethod
    @lru_cache(maxsize=1024)
    def detect(cls, ioc_value: str) -> Optional[str]:
        """自动检测IOC类型（带缓存）"""
        ioc_value = ioc_value.strip()
        
        if cls.IPV4_PATTERN.match(ioc_value) or cls.IPV6_PATTERN.match(ioc_value):
            return IOCType.IP.value
        elif cls.URL_PATTERN.match(ioc_value):
            return IOCType.URL.value
        elif cls.MD5_PATTERN.match(ioc_value):
            return IOCType.HASH.value
        elif cls.SHA1_PATTERN.match(ioc_value):
            return IOCType.HASH.value
        elif cls.SHA256_PATTERN.match(ioc_value):
            return IOCType.HASH.value
        elif cls.DOMAIN_PATTERN.match(ioc_value):
            return IOCType.DOMAIN.value
        
        return IOCType.UNKNOWN.value


class ConnectionPoolManager:
    """HTTP连接池管理器"""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.active_connections = 0
        self._connection_lock = Lock()
        self.logger = logging.getLogger('hs-ti-connection-pool')
    
    def acquire_connection(self) -> bool:
        """获取连接"""
        with self._connection_lock:
            if self.active_connections < self.max_connections:
                self.active_connections += 1
                self.logger.debug(f"获取连接成功，当前活跃连接: {self.active_connections}")
                return True
            self.logger.warning(f"连接池已满，当前活跃连接: {self.active_connections}")
            return False
    
    def release_connection(self) -> None:
        """释放连接"""
        with self._connection_lock:
            if self.active_connections > 0:
                self.active_connections -= 1
                self.logger.debug(f"释放连接成功，当前活跃连接: {self.active_connections}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        return {
            'active_connections': self.active_connections,
            'max_connections': self.max_connections,
            'available_connections': self.max_connections - self.active_connections
        }


class CircuitBreaker:
    """断路器模式实现"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'
        self._lock = Lock()
        self.logger = logging.getLogger('hs-ti-circuit-breaker')
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """通过断路器调用函数"""
        with self._lock:
            if self.state == 'open':
                if self._should_attempt_reset():
                    self.state = 'half-open'
                    self.logger.info("断路器状态从open切换到half-open")
                else:
                    raise Exception("断路器已打开，请求被拒绝")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置断路器"""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.timeout
    
    def _on_success(self) -> None:
        """成功回调"""
        with self._lock:
            self.failure_count = 0
            if self.state == 'half-open':
                self.state = 'closed'
                self.logger.info("断路器状态从half-open切换到closed")
    
    def _on_failure(self) -> None:
        """失败回调"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'open'
                self.logger.warning(f"断路器已打开，失败次数: {self.failure_count}")
    
    def get_state(self) -> Dict[str, Any]:
        """获取断路器状态"""
        return {
            'state': self.state,
            'failure_count': self.failure_count,
            'failure_threshold': self.failure_threshold,
            'last_failure_time': self.last_failure_time
        }


def exponential_backoff_retry(max_retries: int = 3, base_delay: int = 1, 
                            exceptions: tuple = (urllib.error.URLError,)) -> Callable:
    """指数退避重试装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


class YunzhanThreatIntel:
    """云瞻威胁情报查询插件 / Hillstone Threat Intelligence Plugin"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.api_key: Optional[str] = None
        self.api_url: str = "https://ti.hillstonenet.com.cn"
        self.response_times: List[int] = []
        self.language: str = "en"
        self.lang_config_path: Optional[str] = None
        self.cache_enabled: bool = True
        self.cache_ttl: int = 3600
        self.cache: OrderedDict = OrderedDict()
        self._cache_lock: Lock = Lock()
        self._response_times_lock: Lock = Lock()
        self.max_retries: int = 3
        self.retry_delay: int = 1
        self.timeout: int = 30
        self.max_workers: int = 5
        self.cache_stats = {'hits': 0, 'misses': 0}
        self.max_cache_size: int = 1000
        self.connection_pool = ConnectionPoolManager(max_connections=10)
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
        self.logger: logging.Logger = self._setup_logger()
        
        self.load_config(config_path)
        self.load_language_config()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('hs-ti')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            log_dir = Path.home() / '.openclaw' / 'logs'
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / 'hs_ti.log'
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def load_config(self, config_path: Optional[str] = None) -> None:
        """加载配置文件"""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.api_key = config.get('api_key') or os.environ.get('HILLSTONE_API_KEY')
                    if 'api_url' in config:
                        self.api_url = config['api_url'].rstrip('/')
                    if 'timeout' in config:
                        self.timeout = config['timeout']
                    if 'max_retries' in config:
                        self.max_retries = config['max_retries']
                    if 'retry_delay' in config:
                        self.retry_delay = config['retry_delay']
                    if 'cache_enabled' in config:
                        self.cache_enabled = config['cache_enabled']
                    if 'cache_ttl' in config:
                        self.cache_ttl = config['cache_ttl']
                    if 'max_workers' in config:
                        self.max_workers = config['max_workers']
                    if 'max_cache_size' in config:
                        self.max_cache_size = config['max_cache_size']
                    if 'max_connections' in config:
                        self.connection_pool = ConnectionPoolManager(max_connections=config['max_connections'])
                    if 'circuit_breaker_failure_threshold' in config:
                        self.circuit_breaker = CircuitBreaker(
                            failure_threshold=config['circuit_breaker_failure_threshold'],
                            timeout=config.get('circuit_breaker_timeout', 60)
                        )
                self.logger.info(f"配置文件加载成功: {config_path}")
            except Exception as e:
                self.logger.error(f"加载配置文件失败: {e}")
        else:
            self.api_key = os.environ.get('HILLSTONE_API_KEY')
            if self.api_key:
                self.logger.info("从环境变量加载API密钥")
            else:
                self.logger.warning(f"配置文件不存在: {config_path}")
    
    def load_language_config(self) -> None:
        """加载语言配置"""
        skill_dir = os.path.dirname(os.path.dirname(__file__))
        self.lang_config_path = os.path.join(skill_dir, "language.json")
        
        if os.path.exists(self.lang_config_path):
            try:
                with open(self.lang_config_path, 'r', encoding='utf-8') as f:
                    lang_config = json.load(f)
                    self.language = lang_config.get('language', 'en')
                self.logger.info(f"语言配置加载成功: {self.language}")
            except Exception as e:
                self.logger.error(f"加载语言配置失败: {e}")
                self.language = 'en'
    
    def save_language_config(self) -> None:
        """保存语言配置"""
        if self.lang_config_path:
            try:
                with open(self.lang_config_path, 'w', encoding='utf-8') as f:
                    json.dump({"language": self.language}, f, indent=2, ensure_ascii=False)
                self.logger.info(f"语言配置保存成功: {self.language}")
            except Exception as e:
                self.logger.error(f"保存语言配置失败: {e}")
    
    def set_language(self, lang: str) -> bool:
        """设置语言"""
        if lang in ['en', 'cn']:
            self.language = lang
            self.save_language_config()
            return True
        return False
    
    def _get_cache_key(self, ioc_value: str, ioc_type: str, advanced: bool) -> str:
        """生成缓存键"""
        data = f"{ioc_value}:{ioc_type}:{advanced}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """检查缓存是否有效"""
        return time.time() - cache_entry['timestamp'] < self.cache_ttl
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """从缓存获取数据（线程安全+LRU）"""
        with self._cache_lock:
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if self._is_cache_valid(cache_entry):
                    self.cache_stats['hits'] += 1
                    self._update_lru_order(cache_key)
                    return cache_entry['data']
                else:
                    del self.cache[cache_key]
            self.cache_stats['misses'] += 1
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict) -> None:
        """保存数据到缓存（线程安全+LRU）"""
        with self._cache_lock:
            self.cache[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }
            self._update_lru_order(cache_key)
            self._enforce_cache_size_limit()
    
    def _update_lru_order(self, cache_key: str) -> None:
        """更新LRU顺序"""
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            del self.cache[cache_key]
            self.cache[cache_key] = cache_entry
    
    def _enforce_cache_size_limit(self) -> None:
        """强制执行缓存大小限制"""
        while len(self.cache) > self.max_cache_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.logger.debug(f"缓存已满，移除最旧的条目: {oldest_key}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = 0
        if total_requests > 0:
            hit_rate = (self.cache_stats['hits'] / total_requests) * 100
        
        return {
            'total_entries': len(self.cache),
            'max_size': self.max_cache_size,
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'total_requests': total_requests,
            'hit_rate': f"{hit_rate:.2f}%",
            'cache_enabled': self.cache_enabled
        }
    
    def _add_response_time(self, response_time: int) -> None:
        """添加响应时间（线程安全）"""
        with self._response_times_lock:
            self.response_times.append(response_time)
    
    def _cleanup_expired_cache(self) -> int:
        """清理过期缓存"""
        with self._cache_lock:
            current_time = time.time()
            expired_keys = [
                key for key, value in self.cache.items()
                if current_time - value['timestamp'] >= self.cache_ttl
            ]
            for key in expired_keys:
                del self.cache[key]
            return len(expired_keys)
    
    def get_text(self, key: str) -> str:
        """获取当前语言的文本"""
        texts = {
            'en': {
                'api_key_not_configured': 'API key not configured',
                'config_hint': 'Please configure your API key in config.json:\n1. Edit config.json in the hs-ti skill directory\n2. Replace "your-api-key-here" with your actual API key\n3. Restart OpenClaw if needed',
                'request_failed': 'Request failed',
                'invalid_json': 'Invalid JSON response',
                'result_malicious': 'malicious',
                'result_benign': 'benign',
                'result_unknown': 'unknown',
                'language_switched': 'Language switched to',
                'language_switched_to_en': 'Language switched to English',
                'language_switched_to_cn': 'Language switched to Chinese',
                'current_language': 'Current language',
                'default_language': 'Default language: English',
                'switch_to_chinese': 'Switch to Chinese',
                'switch_to_english': 'Switch to English',
                'query_results': 'Query Results',
                'single_query': 'Single Query',
                'batch_query': 'Batch Query',
                'cumulative_stats': 'Cumulative Statistics',
                'response_time': 'Response Time',
                'avg': 'Average',
                'max': 'Maximum',
                'min': 'Minimum',
                'median': 'Median',
                'total_calls': 'Total Calls',
                'threat_type': 'Threat Type',
                'credibility': 'Credibility',
                'ip_address': 'IP Address',
                'domain': 'Domain',
                'url': 'URL',
                'file_hash': 'File Hash',
                'no_results': 'No results found',
                'query_completed': 'Query completed',
                'performance_stats': 'Performance Statistics',
                'current_call': 'Current Call',
                'batch_stats': 'Batch Statistics',
                'total_stats': 'Total Statistics',
                'unknown_ioc_type': 'Unknown IOC type',
                'auto_detected_type': 'Auto-detected type'
            },
            'cn': {
                'api_key_not_configured': 'API密钥未配置',
                'config_hint': '请在config.json中配置您的API密钥：\n1. 编辑hs-ti技能目录下的config.json文件\n2. 将 "your-api-key-here" 替换为您的实际API密钥\n3. 如需要请重启OpenClaw',
                'request_failed': '请求失败',
                'invalid_json': '无效的JSON响应',
                'result_malicious': '恶意',
                'result_benign': '良性',
                'result_unknown': '未知',
                'language_switched': '语言已切换到',
                'language_switched_to_en': '语言已切换到英文',
                'language_switched_to_cn': '语言已切换到中文',
                'current_language': '当前语言',
                'default_language': '默认语言：英文',
                'switch_to_chinese': '切换到中文',
                'switch_to_english': '切换到英文',
                'query_results': '查询结果',
                'single_query': '单次查询',
                'batch_query': '批量查询',
                'cumulative_stats': '累计统计',
                'response_time': '响应时间',
                'avg': '平均',
                'max': '最大',
                'min': '最小',
                'median': '中位数',
                'total_calls': '总调用次数',
                'threat_type': '威胁类型',
                'credibility': '可信度',
                'ip_address': 'IP地址',
                'domain': '域名',
                'url': 'URL',
                'file_hash': '文件哈希',
                'no_results': '未找到结果',
                'query_completed': '查询完成',
                'performance_stats': '性能统计',
                'current_call': '本次调用',
                'batch_stats': '批量统计',
                'total_stats': '累计统计',
                'unknown_ioc_type': '未知的IOC类型',
                'auto_detected_type': '自动识别类型'
            }
        }
        return texts.get(self.language, texts['en']).get(key, key)
    
    @exponential_backoff_retry(max_retries=3, base_delay=1, exceptions=(urllib.error.URLError,))
    def _make_api_request(self, url: str, headers: Dict[str, str], ioc_value: str) -> Dict[str, Any]:
        """执行API请求（带重试）"""
        start_time = time.time()
        
        if not self.connection_pool.acquire_connection():
            raise Exception("连接池已满，无法获取连接")
        
        try:
            url_with_params = f"{url}?key={urllib.parse.quote(ioc_value)}"
            request = urllib.request.Request(url_with_params, headers=headers)
            
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                response_time_ms = int((time.time() - start_time) * 1000)
                self._add_response_time(response_time_ms)
                
                data = response.read().decode('utf-8')
                result = json.loads(data)
                result['response_time_ms'] = response_time_ms
                
                masked_ioc = self._mask_sensitive_value(ioc_value)
                self.logger.info(f"查询成功: {masked_ioc}, 耗时: {response_time_ms}ms")
                return result
        finally:
            self.connection_pool.release_connection()
    
    def _mask_sensitive_value(self, value: str) -> str:
        """遮蔽敏感值，用于日志记录"""
        if not value:
            return ""
        if len(value) <= 4:
            return "*" * len(value)
        return value[:2] + "*" * (len(value) - 4) + value[-2:]
    
    def query_ioc(self, ioc_value: str, ioc_type: str = "domain", 
                  advanced: bool = False, use_cache: bool = True) -> Dict[str, Any]:
        """
        查询威胁情报
        
        Args:
            ioc_value: IOC值（域名、IP、URL、哈希等）
            ioc_type: IOC类型（domain/ip/url/hash）
            advanced: 是否使用高级接口
            use_cache: 是否使用缓存
        
        Returns:
            查询结果字典
        """
        if not self.api_key or self.api_key == "your-api-key-here":
            error_msg = self.get_text('api_key_not_configured')
            config_hint = f"\n\n{self.get_text('config_hint')}"
            self.logger.error("API密钥未配置")
            return {"error": error_msg + config_hint}
        
        if use_cache and self.cache_enabled:
            cache_key = self._get_cache_key(ioc_value, ioc_type, advanced)
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                masked_ioc = self._mask_sensitive_value(ioc_value)
                self.logger.info(f"使用缓存结果: {masked_ioc}")
                return cached_data
        
        masked_ioc = self._mask_sensitive_value(ioc_value)
        self.logger.info(f"查询IOC: {masked_ioc} (类型: {ioc_type}, 高级: {advanced})")
        
        headers = {
            "X-Auth-Token": self.api_key,
            "ACCEPT": "application/json",
            "X-API-Version": "1.0.0",
            "X-API-Language": self.language
        }
        
        type_mapping = {
            "ip": "ip",
            "domain": "domain", 
            "url": "url",
            "hash": "file",
            "md5": "file",
            "sha1": "file",
            "sha256": "file"
        }
        
        endpoint = type_mapping.get(ioc_type.lower(), "domain")
        
        if advanced:
            url = f"{self.api_url}/api/{endpoint}/detail"
        else:
            url = f"{self.api_url}/api/{endpoint}/reputation"
        
        start_time = time.time()
        
        try:
            result = self.circuit_breaker.call(
                self._make_api_request, url, headers, ioc_value
            )
            
            if use_cache and self.cache_enabled:
                cache_key = self._get_cache_key(ioc_value, ioc_type, advanced)
                self._save_to_cache(cache_key, result)
            
            return result
            
        except urllib.error.HTTPError as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            error_msg = f"{self.get_text('request_failed')}: HTTP {e.code} {e.reason}"
            
            try:
                error_body = e.read().decode('utf-8')
                self.logger.error(f"HTTP错误: {ioc_value}, 状态码: {e.code}, 原因: {e.reason}, 响应体: {error_body}")
            except:
                self.logger.error(f"HTTP错误: {ioc_value}, 状态码: {e.code}, 原因: {e.reason}")
            
            return {"error": error_msg, "response_time_ms": response_time_ms, "status_code": e.code}
        except urllib.error.URLError as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            if isinstance(e.reason, TimeoutError):
                error_msg = f"{self.get_text('request_failed')}: Timeout after {self.timeout}s"
                self.logger.error(f"超时错误: {ioc_value}, 超时时间: {self.timeout}s")
            else:
                error_msg = f"{self.get_text('request_failed')}: {str(e)}"
                self.logger.error(f"网络错误: {ioc_value}, 错误详情: {str(e)}")
            return {"error": error_msg, "response_time_ms": response_time_ms}
        except json.JSONDecodeError as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            self.logger.error(f"JSON解析失败: {ioc_value}, 错误: {str(e)}")
            return {"error": self.get_text('invalid_json'), "response_time_ms": response_time_ms}
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            error_msg = f"{self.get_text('request_failed')}: {type(e).__name__} - {str(e)}"
            self.logger.error(f"未知错误: {ioc_value}, 异常类型: {type(e).__name__}, 错误: {str(e)}")
            return {"error": error_msg, "response_time_ms": response_time_ms}
    
    def query_ioc_auto(self, ioc_value: str, advanced: bool = False, 
                      use_cache: bool = True) -> Dict[str, Any]:
        """
        自动识别IOC类型的查询
        
        Args:
            ioc_value: IOC值
            advanced: 是否使用高级接口
            use_cache: 是否使用缓存
        
        Returns:
            查询结果字典
        """
        detected_type = IOCTypeDetector.detect(ioc_value)
        
        if detected_type == IOCType.UNKNOWN.value:
            self.logger.warning(f"无法识别IOC类型: {ioc_value}")
            return {
                "error": f"{self.get_text('unknown_ioc_type')}: {ioc_value}",
                "detected_type": IOCType.UNKNOWN.value
            }
        
        self.logger.info(f"{self.get_text('auto_detected_type')}: {detected_type}")
        return self.query_ioc(ioc_value, detected_type, advanced, use_cache)
    
    def batch_query(self, iocs: List[Dict[str, str]], 
                    use_cache: bool = True, concurrent: bool = True,
                    progress_callback: Optional[Callable[[float, int, int], None]] = None) -> Dict[str, Any]:
        """
        批量查询威胁情报
        
        Args:
            iocs: IOC列表，每个元素为 {"value": "ioc_value", "type": "ioc_type"}
            use_cache: 是否使用缓存
            concurrent: 是否使用并发查询（默认True）
            progress_callback: 进度回调函数，参数为 (progress_percentage, current, total)
        
        Returns:
            包含结果和统计信息的字典
        """
        self.logger.info(f"开始批量查询，共 {len(iocs)} 个IOC，并发: {concurrent}")
        
        results: List[IOCQueryResult] = []
        batch_times: List[int] = []
        
        if concurrent and len(iocs) > 1:
            results = self._batch_query_concurrent(iocs, use_cache, progress_callback)
        else:
            results = self._batch_query_sequential(iocs, use_cache, progress_callback)
        
        batch_times = [r.response_time_ms for r in results]
        batch_stats = self._calculate_stats(batch_times)
        total_stats = self._calculate_stats(self.response_times)
        
        success_count = sum(1 for r in results if r.success)
        failure_count = sum(1 for r in results if not r.success)
        self.logger.info(f"批量查询完成，成功: {success_count}, 失败: {failure_count}")
        
        return {
            "results": [asdict(r) for r in results],
            "batch_stats": asdict(batch_stats),
            "total_stats": asdict(total_stats)
        }
    
    def _batch_query_sequential(self, iocs: List[Dict[str, str]], 
                               use_cache: bool,
                               progress_callback: Optional[Callable[[float, int, int], None]] = None) -> List[IOCQueryResult]:
        """顺序批量查询"""
        results: List[IOCQueryResult] = []
        total = len(iocs)
        
        for i, ioc in enumerate(iocs):
            ioc_value = ioc["value"]
            ioc_type = ioc.get("type", IOCTypeDetector.detect(ioc_value) or "domain")
            
            result = self.query_ioc(ioc_value, ioc_type, False, use_cache)
            response_time = result.get('response_time_ms', 0)
            
            query_result = IOCQueryResult(
                ioc=ioc_value,
                ioc_type=ioc_type,
                result=result,
                response_time_ms=response_time,
                success='error' not in result,
                error=result.get('error') if 'error' in result else None
            )
            results.append(query_result)
            
            if progress_callback:
                progress = (i + 1) / total * 100
                progress_callback(progress, i + 1, total)
        
        return results
    
    def _batch_query_concurrent(self, iocs: List[Dict[str, str]], 
                                use_cache: bool,
                                progress_callback: Optional[Callable[[float, int, int], None]] = None) -> List[IOCQueryResult]:
        """并发批量查询"""
        results: List[IOCQueryResult] = []
        completed_count = 0
        total = len(iocs)
        _results_lock = Lock()
        
        def query_single(ioc: Dict[str, str]) -> IOCQueryResult:
            ioc_value = ioc["value"]
            ioc_type = ioc.get("type", IOCTypeDetector.detect(ioc_value) or "domain")
            
            result = self.query_ioc(ioc_value, ioc_type, False, use_cache)
            response_time = result.get('response_time_ms', 0)
            
            return IOCQueryResult(
                ioc=ioc_value,
                ioc_type=ioc_type,
                result=result,
                response_time_ms=response_time,
                success='error' not in result,
                error=result.get('error') if 'error' in result else None
            )
        
        def on_complete(future):
            nonlocal completed_count
            try:
                result = future.result()
                with _results_lock:
                    results.append(result)
                    completed_count += 1
                    if progress_callback:
                        progress = completed_count / total * 100
                        progress_callback(progress, completed_count, total)
            except Exception as e:
                with _results_lock:
                    ioc = future_to_ioc[future]
                    self.logger.error(f"查询异常: {ioc['value']}, 错误: {str(e)}")
                    results.append(IOCQueryResult(
                        ioc=ioc['value'],
                        ioc_type=ioc.get('type', 'unknown'),
                        result={"error": str(e)},
                        response_time_ms=0,
                        success=False,
                        error=str(e)
                    ))
                    completed_count += 1
                    if progress_callback:
                        progress = completed_count / total * 100
                        progress_callback(progress, completed_count, total)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_ioc = {
                executor.submit(query_single, ioc): ioc 
                for ioc in iocs
            }
            
            for future in future_to_ioc:
                future.add_done_callback(on_complete)
        
        return results
    
    def _calculate_stats(self, times: List[int]) -> PerformanceStats:
        """计算统计数据"""
        if not times:
            return PerformanceStats(avg_ms=0, max_ms=0, min_ms=0, median_ms=0, total_calls=0)
        
        avg_ms = round(sum(times) / len(times), 2)
        max_ms = max(times)
        min_ms = min(times)
        sorted_times = sorted(times)
        median_ms = sorted_times[len(sorted_times) // 2]
        total_calls = len(times)
        
        return PerformanceStats(avg_ms=avg_ms, max_ms=max_ms, min_ms=min_ms, 
                              median_ms=median_ms, total_calls=total_calls)
    
    def import_iocs_from_file(self, file_path: str) -> List[Dict[str, str]]:
        """
        从文件导入IOC列表
        
        Args:
            file_path: 文件路径，支持CSV、TXT、JSON格式
        
        Returns:
            IOC列表，每个元素为 {"value": "ioc_value", "type": "ioc_type"}
        
        Raises:
            ValueError: 不支持的文件格式
            FileNotFoundError: 文件不存在
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        file_ext = file_path_obj.suffix.lower()
        
        if file_ext == '.csv':
            return self._import_from_csv(file_path)
        elif file_ext == '.txt':
            return self._import_from_txt(file_path)
        elif file_ext == '.json':
            return self._import_from_json(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}，仅支持CSV、TXT、JSON")
    
    def _import_from_csv(self, file_path: str) -> List[Dict[str, str]]:
        """从CSV文件导入IOC"""
        import csv
        
        iocs = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ioc_value = row.get('ioc') or row.get('value') or row.get('ioc_value', '')
                    ioc_type = row.get('type', 'auto')
                    
                    if ioc_value:
                        iocs.append({
                            'value': ioc_value.strip(),
                            'type': ioc_type.strip() if ioc_type != 'auto' else 'auto'
                        })
        except Exception as e:
            self.logger.error(f"CSV文件导入失败: {e}")
            raise
        
        self.logger.info(f"从CSV文件导入了 {len(iocs)} 个IOC")
        return iocs
    
    def _import_from_txt(self, file_path: str) -> List[Dict[str, str]]:
        """从TXT文件导入IOC"""
        iocs = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        iocs.append({
                            'value': line,
                            'type': 'auto'
                        })
        except Exception as e:
            self.logger.error(f"TXT文件导入失败: {e}")
            raise
        
        self.logger.info(f"从TXT文件导入了 {len(iocs)} 个IOC")
        return iocs
    
    def _import_from_json(self, file_path: str) -> List[Dict[str, str]]:
        """从JSON文件导入IOC"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            iocs = []
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        ioc_value = item.get('ioc') or item.get('value') or item.get('ioc_value', '')
                        ioc_type = item.get('type', 'auto')
                        
                        if ioc_value:
                            iocs.append({
                                'value': str(ioc_value).strip(),
                                'type': ioc_type.strip() if ioc_type != 'auto' else 'auto'
                            })
                    elif isinstance(item, str):
                        iocs.append({
                            'value': item.strip(),
                            'type': 'auto'
                        })
            elif isinstance(data, dict):
                if 'iocs' in data:
                    for item in data['iocs']:
                        if isinstance(item, dict):
                            ioc_value = item.get('ioc') or item.get('value') or item.get('ioc_value', '')
                            ioc_type = item.get('type', 'auto')
                            
                            if ioc_value:
                                iocs.append({
                                    'value': str(ioc_value).strip(),
                                    'type': ioc_type.strip() if ioc_type != 'auto' else 'auto'
                                })
                        elif isinstance(item, str):
                            iocs.append({
                                'value': item.strip(),
                                'type': 'auto'
                            })
            
            self.logger.info(f"从JSON文件导入了 {len(iocs)} 个IOC")
            return iocs
        except Exception as e:
            self.logger.error(f"JSON文件导入失败: {e}")
            raise
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        return {
            'cache_stats': self.get_cache_stats(),
            'connection_pool_stats': self.connection_pool.get_stats(),
            'circuit_breaker_stats': self.circuit_breaker.get_state()
        }
    
    def validate_api_key(self) -> bool:
        """验证API密钥是否有效配置"""
        return bool(self.api_key and self.api_key != "your-api-key-here")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.response_times:
            return {
                "total_queries": 0,
                "avg_response_time_ms": 0,
                "max_response_time_ms": 0,
                "min_response_time_ms": 0
            }
        
        return {
            "total_queries": len(self.response_times),
            "avg_response_time_ms": round(sum(self.response_times) / len(self.response_times), 2),
            "max_response_time_ms": max(self.response_times),
            "min_response_time_ms": min(self.response_times)
        }
    
    def clear_cache(self) -> None:
        """清空缓存"""
        with self._cache_lock:
            self.cache.clear()
        self.logger.info("缓存已清空")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._cache_lock:
            valid_entries = sum(1 for entry in self.cache.values() 
                              if self._is_cache_valid(entry))
            return {
                "total_entries": len(self.cache),
                "valid_entries": valid_entries,
                "expired_entries": len(self.cache) - valid_entries,
                "cache_enabled": self.cache_enabled,
                "cache_ttl": self.cache_ttl
            }
    
    def cleanup_cache(self) -> int:
        """清理过期缓存，返回清理的条目数"""
        expired_count = self._cleanup_expired_cache()
        if expired_count > 0:
            self.logger.info(f"清理了 {expired_count} 个过期缓存条目")
        return expired_count


yunzhan_intel = YunzhanThreatIntel()
