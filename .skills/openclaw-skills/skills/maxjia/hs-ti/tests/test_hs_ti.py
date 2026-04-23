#!/usr/bin/env python3
"""
云瞻威胁情报查询技能测试文件 - 增强版
"""

import unittest
import os
import sys
import json
import tempfile
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from hs_ti_plugin import (
    YunzhanThreatIntel,
    IOCTypeDetector,
    IOCType,
    QueryResult,
    PerformanceStats,
    IOCQueryResult,
    YunzhanError,
    YunzhanConfigError,
    YunzhanAPIError,
    YunzhanNetworkError,
    YunzhanTimeoutError
)
from result_formatter import ResultFormatter, ResultExporter


class TestIOCTypeDetector(unittest.TestCase):
    """IOC类型检测器测试"""
    
    def test_detect_ipv4(self):
        """测试IPv4地址检测"""
        self.assertEqual(IOCTypeDetector.detect("192.168.1.1"), IOCType.IP.value)
        self.assertEqual(IOCTypeDetector.detect("8.8.8.8"), IOCType.IP.value)
        self.assertEqual(IOCTypeDetector.detect("255.255.255.255"), IOCType.IP.value)
    
    def test_detect_ipv6(self):
        """测试IPv6地址检测"""
        self.assertEqual(IOCTypeDetector.detect("2001:0db8:85a3:0000:0000:8a2e:0370:7334"), 
                        IOCType.IP.value)
        self.assertEqual(IOCTypeDetector.detect("::1"), IOCType.IP.value)
        self.assertEqual(IOCTypeDetector.detect("fe80::1"), IOCType.IP.value)
    
    def test_detect_domain(self):
        """测试域名检测"""
        self.assertEqual(IOCTypeDetector.detect("example.com"), IOCType.DOMAIN.value)
        self.assertEqual(IOCTypeDetector.detect("www.example.com"), IOCType.DOMAIN.value)
        self.assertEqual(IOCTypeDetector.detect("sub.domain.example.com"), 
                        IOCType.DOMAIN.value)
    
    def test_detect_url(self):
        """测试URL检测"""
        self.assertEqual(IOCTypeDetector.detect("https://example.com"), IOCType.URL.value)
        self.assertEqual(IOCTypeDetector.detect("http://example.com/path"), 
                        IOCType.URL.value)
        self.assertEqual(IOCTypeDetector.detect("https://example.com/path?query=value"), 
                        IOCType.URL.value)
    
    def test_detect_hash_md5(self):
        """测试MD5哈希检测"""
        self.assertEqual(IOCTypeDetector.detect("d41d8cd98f00b204e9800998ecf8427e"), 
                        IOCType.HASH.value)
        self.assertEqual(IOCTypeDetector.detect("D41D8CD98F00B204E9800998ECF8427E"), 
                        IOCType.HASH.value)
    
    def test_detect_hash_sha1(self):
        """测试SHA1哈希检测"""
        self.assertEqual(IOCTypeDetector.detect("da39a3ee5e6b4b0d3255bfef95601890afd80709"), 
                        IOCType.HASH.value)
    
    def test_detect_hash_sha256(self):
        """测试SHA256哈希检测"""
        self.assertEqual(IOCTypeDetector.detect(
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ), IOCType.HASH.value)
    
    def test_detect_unknown(self):
        """测试未知类型检测"""
        self.assertEqual(IOCTypeDetector.detect("invalid-ioc"), 
                        IOCType.UNKNOWN.value)
        self.assertEqual(IOCTypeDetector.detect("not-a-valid-thing"), 
                        IOCType.UNKNOWN.value)


class TestYunzhanThreatIntel(unittest.TestCase):
    """云瞻威胁情报查询测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "config.json")
        self.lang_config_path = os.path.join(self.temp_dir, "language.json")
        
        test_config = {
            "api_key": "test-api-key",
            "api_url": "https://test.example.com",
            "timeout": 30,
            "max_retries": 3,
            "retry_delay": 1,
            "cache_enabled": True,
            "cache_ttl": 3600
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(test_config, f)
        
        with open(self.lang_config_path, 'w', encoding='utf-8') as f:
            json.dump({"language": "en"}, f)
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """测试初始化"""
        intel = YunzhanThreatIntel(self.config_path)
        self.assertIsNotNone(intel)
        self.assertEqual(intel.api_key, "test-api-key")
        self.assertEqual(intel.api_url, "https://test.example.com")
        self.assertEqual(intel.timeout, 30)
        self.assertEqual(intel.max_retries, 3)
        self.assertEqual(intel.cache_enabled, True)
        self.assertEqual(intel.cache_ttl, 3600)
    
    def test_load_config(self):
        """测试配置加载"""
        intel = YunzhanThreatIntel(self.config_path)
        intel.load_config(self.config_path)
        self.assertEqual(intel.api_key, "test-api-key")
        self.assertEqual(intel.api_url, "https://test.example.com")
    
    def test_load_config_missing_file(self):
        """测试配置文件不存在"""
        intel = YunzhanThreatIntel()
        intel.api_key = "fallback-key"
        intel.load_config("/nonexistent/config.json")
        self.assertIsNone(intel.api_key)
    
    def test_language_switching(self):
        """测试语言切换"""
        intel = YunzhanThreatIntel(self.config_path)
        
        self.assertTrue(intel.set_language('cn'))
        self.assertEqual(intel.language, 'cn')
        
        self.assertTrue(intel.set_language('en'))
        self.assertEqual(intel.language, 'en')
        
        self.assertFalse(intel.set_language('fr'))
        self.assertEqual(intel.language, 'en')
    
    def test_get_text(self):
        """测试文本获取"""
        intel = YunzhanThreatIntel(self.config_path)
        
        intel.set_language('en')
        self.assertEqual(intel.get_text('api_key_not_configured'), 
                        'API key not configured')
        
        intel.set_language('cn')
        self.assertEqual(intel.get_text('api_key_not_configured'), 
                        'API密钥未配置')
    
    @patch('urllib.request.urlopen')
    def test_query_ioc_success(self, mock_urlopen):
        """测试成功查询"""
        intel = YunzhanThreatIntel(self.config_path)
        
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            "data": {"result": "malicious", "threat_type": ["Scanner"], 
                    "credibility": 50},
            "response_code": 0,
            "response_msg": "OK"
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = intel.query_ioc("test.com", "domain")
        
        self.assertEqual(result['data']['result'], 'malicious')
        self.assertIn('response_time_ms', result)
        self.assertGreaterEqual(result['response_time_ms'], 0)
    
    def test_query_ioc_no_api_key(self):
        """测试API密钥未配置"""
        intel = YunzhanThreatIntel()
        intel.api_key = None
        
        result = intel.query_ioc("test.com", "domain")
        
        self.assertIn('error', result)
        self.assertIn('API key not configured', result['error'])
    
    @patch('urllib.request.urlopen')
    def test_query_ioc_http_error(self, mock_urlopen):
        """测试HTTP错误"""
        intel = YunzhanThreatIntel(self.config_path)
        
        from urllib.error import HTTPError
        mock_urlopen.side_effect = HTTPError(
            "http://test.com", 401, "Unauthorized", {}, None
        )
        
        result = intel.query_ioc("test.com", "domain")
        
        self.assertIn('error', result)
        self.assertIn('HTTP 401', result['error'])
    
    @patch('urllib.request.urlopen')
    def test_query_ioc_timeout(self, mock_urlopen):
        """测试超时错误"""
        intel = YunzhanThreatIntel(self.config_path)
        
        from urllib.error import URLError
        mock_urlopen.side_effect = URLError(TimeoutError("Timeout"))
        
        result = intel.query_ioc("test.com", "domain")
        
        self.assertIn('error', result)
        self.assertIn('Timeout', result['error'])
    
    @patch('urllib.request.urlopen')
    def test_query_ioc_json_error(self, mock_urlopen):
        """测试JSON解析错误"""
        intel = YunzhanThreatIntel(self.config_path)
        
        mock_response = Mock()
        mock_response.read.return_value = b"invalid json"
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = intel.query_ioc("test.com", "domain")
        
        self.assertIn('error', result)
        self.assertIn('Invalid JSON', result['error'])
    
    def test_query_ioc_auto(self):
        """测试自动识别IOC类型的查询"""
        intel = YunzhanThreatIntel(self.config_path)
        
        with patch.object(intel, 'query_ioc') as mock_query:
            mock_query.return_value = {"data": {"result": "benign"}}
            
            result = intel.query_ioc_auto("192.168.1.1")
            
            self.assertEqual(mock_query.call_args[0][0], "192.168.1.1")
            self.assertEqual(mock_query.call_args[0][1], "ip")
    
    def test_query_ioc_auto_unknown(self):
        """测试自动识别未知类型"""
        intel = YunzhanThreatIntel(self.config_path)
        
        result = intel.query_ioc_auto("invalid-ioc-type")
        
        self.assertIn('error', result)
        self.assertIn('Unknown IOC type', result['error'])
    
    @patch('urllib.request.urlopen')
    def test_batch_query(self, mock_urlopen):
        """测试批量查询"""
        intel = YunzhanThreatIntel(self.config_path)
        
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            "data": {"result": "benign", "threat_type": [], "credibility": 0},
            "response_code": 0,
            "response_msg": "OK"
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        iocs = [
            {"value": "test1.com", "type": "domain"},
            {"value": "test2.com", "type": "domain"}
        ]
        
        result = intel.batch_query(iocs)
        
        self.assertEqual(len(result['results']), 2)
        self.assertIn('batch_stats', result)
        self.assertIn('total_stats', result)
        self.assertEqual(result['batch_stats']['total_calls'], 2)
    
    def test_cache_mechanism(self):
        """测试缓存机制"""
        intel = YunzhanThreatIntel(self.config_path)
        
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = Mock()
            mock_response.read.return_value = json.dumps({
                "data": {"result": "benign", "threat_type": [], "credibility": 0},
                "response_code": 0,
                "response_msg": "OK"
            }).encode('utf-8')
            mock_urlopen.return_value.__enter__.return_value = mock_response
            
            intel.query_ioc("test.com", "domain", use_cache=True)
            intel.query_ioc("test.com", "domain", use_cache=True)
            
            self.assertEqual(mock_urlopen.call_count, 1)
    
    def test_cache_invalid(self):
        """测试缓存失效"""
        intel = YunzhanThreatIntel(self.config_path)
        intel.cache_ttl = 0
        
        with patch.object(intel, 'query_ioc') as mock_query:
            mock_query.return_value = {"data": {"result": "benign"}}
            
            intel.query_ioc("test.com", "domain", use_cache=True)
            intel.query_ioc("test.com", "domain", use_cache=True)
            
            self.assertEqual(mock_query.call_count, 2)
    
    def test_clear_cache(self):
        """测试清空缓存"""
        intel = YunzhanThreatIntel(self.config_path)
        
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = Mock()
            mock_response.read.return_value = json.dumps({
                "data": {"result": "benign", "threat_type": [], "credibility": 0},
                "response_code": 0,
                "response_msg": "OK"
            }).encode('utf-8')
            mock_urlopen.return_value.__enter__.return_value = mock_response
            
            intel.query_ioc("test.com", "domain", use_cache=True)
            
            with intel._cache_lock:
                cache_size = len(intel.cache)
            self.assertGreater(cache_size, 0)
            
            intel.clear_cache()
            
            with intel._cache_lock:
                cache_size_after = len(intel.cache)
            self.assertEqual(cache_size_after, 0)
    
    def test_get_cache_stats(self):
        """测试获取缓存统计"""
        intel = YunzhanThreatIntel(self.config_path)
        
        stats = intel.get_cache_stats()
        
        self.assertIn('total_entries', stats)
        self.assertIn('valid_entries', stats)
        self.assertIn('expired_entries', stats)
        self.assertIn('cache_enabled', stats)
        self.assertIn('cache_ttl', stats)
    
    def test_calculate_stats(self):
        """测试统计计算"""
        intel = YunzhanThreatIntel(self.config_path)
        
        times = [100, 200, 300, 400, 500]
        stats = intel._calculate_stats(times)
        
        self.assertEqual(stats.avg_ms, 300.0)
        self.assertEqual(stats.max_ms, 500)
        self.assertEqual(stats.min_ms, 100)
        self.assertEqual(stats.median_ms, 300)
        self.assertEqual(stats.total_calls, 5)
    
    def test_calculate_stats_empty(self):
        """测试空列表统计"""
        intel = YunzhanThreatIntel(self.config_path)
        
        stats = intel._calculate_stats([])
        
        self.assertEqual(stats.avg_ms, 0)
        self.assertEqual(stats.max_ms, 0)
        self.assertEqual(stats.min_ms, 0)
        self.assertEqual(stats.median_ms, 0)
        self.assertEqual(stats.total_calls, 0)


class TestDataClasses(unittest.TestCase):
    """数据类测试"""
    
    def test_performance_stats(self):
        """测试性能统计数据类"""
        stats = PerformanceStats(
            avg_ms=100.5,
            max_ms=200,
            min_ms=50,
            median_ms=100,
            total_calls=10
        )
        
        self.assertEqual(stats.avg_ms, 100.5)
        self.assertEqual(stats.max_ms, 200)
        self.assertEqual(stats.min_ms, 50)
        self.assertEqual(stats.median_ms, 100)
        self.assertEqual(stats.total_calls, 10)
    
    def test_ioc_query_result(self):
        """测试IOC查询结果数据类"""
        result = IOCQueryResult(
            ioc="test.com",
            ioc_type="domain",
            result={"data": {"result": "benign"}},
            response_time_ms=100,
            success=True
        )
        
        self.assertEqual(result.ioc, "test.com")
        self.assertEqual(result.ioc_type, "domain")
        self.assertEqual(result.response_time_ms, 100)
        self.assertTrue(result.success)
        self.assertIsNone(result.error)


class TestExceptions(unittest.TestCase):
    """异常类测试"""
    
    def test_yunzhan_error(self):
        """测试基础异常"""
        with self.assertRaises(YunzhanError):
            raise YunzhanError("Test error")
    
    def test_yunzhan_config_error(self):
        """测试配置错误"""
        with self.assertRaises(YunzhanConfigError):
            raise YunzhanConfigError("Config error")
    
    def test_yunzhan_api_error(self):
        """测试API错误"""
        exc = YunzhanAPIError("API error", status_code=401)
        self.assertEqual(exc.status_code, 401)
    
    def test_yunzhan_network_error(self):
        """测试网络错误"""
        with self.assertRaises(YunzhanNetworkError):
            raise YunzhanNetworkError("Network error")
    
    def test_yunzhan_timeout_error(self):
        """测试超时错误"""
        with self.assertRaises(YunzhanTimeoutError):
            raise YunzhanTimeoutError("Timeout error")


class TestResultFormatter(unittest.TestCase):
    """结果格式化器测试"""
    
    def test_format_text(self):
        """测试文本格式化"""
        result = {
            "data": {
                "result": "malicious",
                "threat_type": ["Scanner"],
                "credibility": 50
            },
            "response_time_ms": 100
        }
        
        text = ResultFormatter.format_text(result, 'en')
        self.assertIn('Malicious', text)
        self.assertIn('Scanner', text)
        self.assertIn('50', text)
        self.assertIn('100ms', text)
    
    def test_format_text_error(self):
        """测试错误文本格式化"""
        result = {"error": "Test error"}
        
        text = ResultFormatter.format_text(result, 'en')
        self.assertIn('Error', text)
        self.assertIn('Test error', text)
    
    def test_format_json(self):
        """测试JSON格式化"""
        result = {"data": {"result": "benign"}}
        
        json_str = ResultFormatter.format_json(result)
        parsed = json.loads(json_str)
        self.assertEqual(parsed['data']['result'], 'benign')
    
    def test_format_table(self):
        """测试表格格式化"""
        results = [
            {
                "ioc": "test.com",
                "ioc_type": "domain",
                "result": {"data": {"result": "benign", "threat_type": [], "credibility": 0}},
                "response_time_ms": 100
            }
        ]
        
        table = ResultFormatter.format_table(results, 'en')
        self.assertIn('test.com', table)
        self.assertIn('domain', table)
        self.assertIn('benign', table)
    
    def test_format_batch_results(self):
        """测试批量结果格式化"""
        batch_result = {
            "results": [
                {
                    "ioc": "test.com",
                    "ioc_type": "domain",
                    "result": {"data": {"result": "benign", "threat_type": [], "credibility": 0}},
                    "response_time_ms": 100
                }
            ],
            "batch_stats": {
                "batch_avg_ms": 100.0,
                "batch_max_ms": 100,
                "batch_min_ms": 100,
                "batch_median_ms": 100
            },
            "total_stats": {
                "total_calls": 1,
                "total_avg_ms": 100.0,
                "total_max_ms": 100,
                "total_min_ms": 100,
                "total_median_ms": 100
            }
        }
        
        formatted = ResultFormatter.format_batch_results(batch_result, 'en')
        self.assertIn('Query Results', formatted)
        self.assertIn('Batch Statistics', formatted)
        self.assertIn('Total Statistics', formatted)


class TestResultExporter(unittest.TestCase):
    """结果导出器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_export_csv(self):
        """测试CSV导出"""
        results = [
            {
                "ioc": "test.com",
                "ioc_type": "domain",
                "result": {"data": {"result": "benign", "threat_type": [], "credibility": 0}},
                "response_time_ms": 100,
                "success": True,
                "error": None
            }
        ]
        
        filename = os.path.join(self.temp_dir, "test.csv")
        ResultExporter.export_csv(results, filename, 'en')
        
        self.assertTrue(os.path.exists(filename))
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('test.com', content)
            self.assertIn('domain', content)
    
    def test_export_json(self):
        """测试JSON导出"""
        results = [
            {
                "ioc": "test.com",
                "ioc_type": "domain",
                "result": {"data": {"result": "benign"}},
                "response_time_ms": 100
            }
        ]
        
        filename = os.path.join(self.temp_dir, "test.json")
        ResultExporter.export_json(results, filename)
        
        self.assertTrue(os.path.exists(filename))
        
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn('results', data)
            self.assertIn('export_time', data)
    
    def test_export_html(self):
        """测试HTML导出"""
        results = [
            {
                "ioc": "test.com",
                "ioc_type": "domain",
                "result": {"data": {"result": "benign", "threat_type": [], "credibility": 0}},
                "response_time_ms": 100,
                "success": True,
                "error": None
            }
        ]
        
        filename = os.path.join(self.temp_dir, "test.html")
        ResultExporter.export_html(results, filename, 'en')
        
        self.assertTrue(os.path.exists(filename))
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('<!DOCTYPE html>', content)
            self.assertIn('test.com', content)
            self.assertIn('benign', content)
    
    def test_export_markdown(self):
        """测试Markdown导出"""
        results = [
            {
                "ioc": "test.com",
                "ioc_type": "domain",
                "result": {"data": {"result": "benign", "threat_type": [], "credibility": 0}},
                "response_time_ms": 100,
                "success": True,
                "error": None
            }
        ]
        
        filename = os.path.join(self.temp_dir, "test.md")
        ResultExporter.export_markdown(results, filename, 'en')
        
        self.assertTrue(os.path.exists(filename))
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('# Hillstone Threat Intelligence Report', content)
            self.assertIn('test.com', content)
            self.assertIn('benign', content)


if __name__ == '__main__':
    unittest.main()
