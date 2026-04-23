#!/usr/bin/env python3
"""
HSCIQ MCP Python Client
海关编码查询服务 - Python 客户端

功能:
- 搜索海关编码
- 获取编码详情（税率、申报要素、监管条件）
- 搜索归类实例
- 统一搜索（CIQ/危化品/港口）

使用示例:
    python hsciq_client.py search-code --keywords "塑料软管" --country CN
    python hsciq_client.py get-detail --code "3926909090"
    python hsciq_client.py search-instance --keywords "蓝牙耳机"
    python hsciq_client.py search-unified --keywords "食品" --type ciq
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from typing import Optional, Dict, Any

# 默认配置
DEFAULT_BASE_URL = "https://www.hsciq.com"
CONFIG_FILE = os.path.expanduser("~/.openclaw/workspace/hsciq-mcp-config.json")


class HSCIQClient:
    """HSCIQ MCP API 客户端"""
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        初始化客户端
        
        Args:
            base_url: API 基础 URL，默认 https://www.hsciq.com
            api_key: API 密钥，可从配置文件或环境变量读取
        """
        self.base_url = (base_url or os.getenv("HSCIQ_BASE_URL") or 
                        self._load_config().get("baseUrl", DEFAULT_BASE_URL))
        self.api_key = (api_key or os.getenv("HSCIQ_API_KEY") or 
                       self._load_config().get("apiKey", ""))
        self.auth_header = self._load_config().get("authHeader", "X-API-Key")
    
    def _load_config(self) -> Dict[str, str]:
        """从配置文件加载配置"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _request(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送 API 请求到统一端点 /mcp/tools/call
        
        Args:
            tool_name: 工具名称（search_code, get_code_detail, search_instance, search_unified）
            arguments: 工具参数
        
        Returns:
            API 响应结果
        """
        url = f"{self.base_url}/mcp/tools/call"
        
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.api_key:
            headers[self.auth_header] = self.api_key
        
        # 根据最新文档，请求体格式为：{"toolName": "...", "arguments": {...}}
        payload = {
            "toolName": tool_name,
            "arguments": arguments
        }
        
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ""
            raise Exception(f"API 请求失败 (HTTP {e.code}): {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"网络连接失败：{e.reason}")
        except json.JSONDecodeError as e:
            raise Exception(f"响应解析失败：{e}")
    
    def search_code(self, keywords: str, country: str = "CN", 
                    pageIndex: int = 1, pageSize: int = 10) -> Dict[str, Any]:
        """
        搜索海关编码
        
        Args:
            keywords: 搜索关键词（商品名称）
            country: 国家代码（CN/JP/US）
            pageIndex: 页码（从 1 开始）
            pageSize: 每页条数
        
        Returns:
            海关编码列表及税率信息
        """
        return self._request("search_code", {
            "keywords": keywords,
            "country": country,
            "pageIndex": pageIndex,
            "pageSize": pageSize
        })
    
    def get_code_detail(self, code: str, country: str = "CN") -> Dict[str, Any]:
        """
        获取海关编码详情
        
        Args:
            code: 海关编码
            country: 国家代码（CN/JP/US）
        
        Returns:
            编码详情（税率、申报要素、监管条件等）
        """
        return self._request("get_code_detail", {
            "code": code,
            "country": country
        })
    
    def search_instance(self, keywords: str, country: str = "CN",
                        pageIndex: int = 1, pageSize: int = 10) -> Dict[str, Any]:
        """
        搜索归类实例
        
        Args:
            keywords: 商品名称关键词
            country: 国家代码
            pageIndex: 页码
            pageSize: 每页条数
        
        Returns:
            历史归类案例
        """
        return self._request("search_instance", {
            "keywords": keywords,
            "country": country,
            "pageIndex": pageIndex,
            "pageSize": pageSize
        })
    
    def search_unified(self, keywords: str, search_type: str = "ciq",
                       pageIndex: int = 1, pageSize: int = 10) -> Dict[str, Any]:
        """
        统一搜索（CIQ/危化品/港口）
        
        Args:
            keywords: 搜索关键词
            search_type: 搜索类型（ciq/hazardous/port）
            pageIndex: 页码
            pageSize: 每页条数
        
        Returns:
            搜索结果
        """
        return self._request("search_unified", {
            "keywords": keywords,
            "unifiedType": search_type,
            "pageIndex": pageIndex,
            "pageSize": pageSize
        })
    
    def list_tools(self) -> Dict[str, Any]:
        """列出可用的 API 工具"""
        url = f"{self.base_url}/mcp/tools/list"
        
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.api_key:
            headers[self.auth_header] = self.api_key
        
        req = urllib.request.Request(url, data=b'{}', headers=headers, method='POST')
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else ""
            raise Exception(f"API 请求失败 (HTTP {e.code}): {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"网络连接失败：{e.reason}")
        except json.JSONDecodeError as e:
            raise Exception(f"响应解析失败：{e}")


def format_output(data: Dict[str, Any], indent: int = 2) -> str:
    """格式化输出结果"""
    return json.dumps(data, ensure_ascii=False, indent=indent)


def main():
    parser = argparse.ArgumentParser(
        description="HSCIQ MCP 海关编码查询服务",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s search-code --keywords "塑料软管" --country CN
  %(prog)s get-detail --code "3926909090"
  %(prog)s search-instance --keywords "蓝牙耳机"
  %(prog)s search-unified --keywords "食品" --type ciq
  %(prog)s list-tools
        """
    )
    
    parser.add_argument('--base-url', type=str, help='API 基础 URL')
    parser.add_argument('--api-key', type=str, help='API 密钥')
    parser.add_argument('--json', action='store_true', help='以 JSON 格式输出')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # search-code
    search_parser = subparsers.add_parser('search-code', help='搜索海关编码')
    search_parser.add_argument('--keywords', required=True, help='搜索关键词')
    search_parser.add_argument('--country', default='CN', help='国家代码 (CN/JP/US)')
    
    # get-detail
    detail_parser = subparsers.add_parser('get-detail', help='获取编码详情')
    detail_parser.add_argument('--code', required=True, help='海关编码')
    detail_parser.add_argument('--country', default='CN', help='国家代码')
    
    # search-instance
    instance_parser = subparsers.add_parser('search-instance', help='搜索归类实例')
    instance_parser.add_argument('--keywords', required=True, help='商品名称')
    instance_parser.add_argument('--country', default='CN', help='国家代码')
    
    # search-unified
    unified_parser = subparsers.add_parser('search-unified', help='统一搜索')
    unified_parser.add_argument('--keywords', required=True, help='搜索关键词')
    unified_parser.add_argument('--type', default='ciq', help='搜索类型 (ciq/chemical/port)')
    
    # list-tools
    subparsers.add_parser('list-tools', help='列出可用工具')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 初始化客户端
    client = HSCIQClient(base_url=args.base_url, api_key=args.api_key)
    
    try:
        result = None
        
        if args.command == 'search-code':
            result = client.search_code(args.keywords, args.country)
        elif args.command == 'get-detail':
            result = client.get_code_detail(args.code, args.country)
        elif args.command == 'search-instance':
            result = client.search_instance(args.keywords, args.country)
        elif args.command == 'search-unified':
            result = client.search_unified(args.keywords, args.type)
        elif args.command == 'list-tools':
            result = client.list_tools()
        
        # 输出结果
        if args.json:
            print(format_output(result))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    
    except Exception as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
