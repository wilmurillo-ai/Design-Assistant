#!/usr/bin/env python3
"""
问道云 API 客户端
"""

import json
import os
import requests
from typing import Dict, List, Optional, Any

class WendaoYunClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化客户端
        :param api_key: API Key，如果不提供则从配置文件或环境变量读取
        :param base_url: API 基础URL，如果不提供使用默认值
        """
        self.base_url = base_url or "https://h5.wintaocloud.com/prod-api/api/invoke"
        self.api_key = api_key or self._load_api_key()
        if not self.api_key:
            raise ValueError("API Key 未配置，请参考 references/config.md 进行配置")
    
    def _load_api_key(self) -> Optional[str]:
        """从配置文件加载API Key"""
        config_paths = [
            os.path.expanduser("~/.config/wendao-yun/config.json"),
            "wendao-yun-config.json"
        ]
        
        for path in config_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 支持 api_key 或 apiKey 两种格式
                    return config.get("api_key") or config.get("apiKey")
        
        # 尝试从环境变量读取
        return os.environ.get("WENDAOYUN_API_KEY")
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def call_api(self, endpoint: str, params: Dict[str, Any] = None, method: str = "GET") -> Dict[str, Any]:
        """
        调用API
        :param endpoint: 接口路径
        :param params: 请求参数
        :param method: 请求方法 GET/POST
        :return: 响应JSON
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        params = params or {}
        headers = self._get_headers()
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers)
            else: # POST
                response = requests.post(url, json=params, headers=headers)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "code": -1,
                "message": f"请求失败: {str(e)}",
                "data": None
            }
    
    def fuzzy_search_org(self, search_key: str, page_num: int = 1) -> Dict[str, Any]:
        """
        模糊搜索企业
        :param search_key: 搜索关键词
        :param page_num: 分页页码
        :return: 搜索结果
        """
        if len(search_key) < 2:
            return {
                "code": -1,
                "message": "搜索关键词最少需要2个字符",
                "data": None
            }
        
        params = {
            "searchKey": search_key,
            "pageNum": page_num
        }
        
        return self.call_api("fuzzy-search-org", params, method="GET")
    
    def get_punishments(self, searchKey: str, page_num: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        查询企业行政处罚
        :param search_key: 企业全称名字orgName
    :param page_num: 分页页码
    :param page_size: 每页大小
        :return: 行政处罚列表
        """
        params = {
            "searchKey": searchKey,
            "pageNum": page_num,
            "pageSize": page_size
        }
        
        return self.call_api("get-punishments", params, method="GET")

    def get_abnormal(self, searchKey: str) -> Dict[str, Any]:
        """
        查询企业经营异常信息
        :param searchKey: 企业全称（orgName）
        :return: 经营异常列表
        """
        params = {
            "searchKey": searchKey
        }
        return self.call_api("get-abnormal", params, method="GET")

    def get_equity_pledge(self, searchKey: str, page_num: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        查询企业股权质押信息
        :param searchKey: 企业全称（orgName）
        :param page_num: 分页页码，默认1
        :param page_size: 每页大小，默认10，最大20
        :return: 股权质押列表
        """
        params = {
            "searchKey": searchKey,
            "pageNum": page_num,
            "pageSize": page_size
        }
        return self.call_api("get-equity-pledge", params, method="GET")

    def get_environmental_penalties(self, searchKey: str, page_num: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        查询企业环保处罚信息
        :param searchKey: 企业全称（orgName）
        :param page_num: 分页页码，默认1
        :param page_size: 每页大小，默认10，最大20
        :return: 环保处罚列表
        """
        params = {
            "searchKey": searchKey,
            "pageNum": page_num,
            "pageSize": page_size
        }
        return self.call_api("get-environmental-penalties", params, method="GET")

    def get_tax_notice(self, searchKey: str, page_num: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        查询企业欠税公告信息
        :param searchKey: 企业全称（orgName）
        :param page_num: 分页页码，默认1
        :param page_size: 每页大小，默认10，最大20
        :return: 欠税公告列表
        """
        params = {
            "searchKey": searchKey,
            "pageNum": page_num,
            "pageSize": page_size
        }
        return self.call_api("get-tax-notice", params, method="GET")

    def get_simple_cancel(self, searchKey: str, page_num: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        查询企业简易注销信息
        :param searchKey: 企业全称（orgName）
        :param page_num: 分页页码，默认1
        :param page_size: 每页大小，默认10，最大20
        :return: 简易注销列表
        """
        params = {
            "searchKey": searchKey,
            "pageNum": page_num,
            "pageSize": page_size
        }
        return self.call_api("get-simple-cancel", params, method="GET")

    def get_land_mortgage(self, searchKey: str, page_num: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        查询企业土地抵押信息
        :param searchKey: 企业全称（orgName）
        :param page_num: 分页页码，默认1
        :param page_size: 每页大小，默认10，最大20
        :return: 土地抵押列表
        """
        params = {
            "searchKey": searchKey,
            "pageNum": page_num,
            "pageSize": page_size
        }
        return self.call_api("get-land-mortgage", params, method="GET")

    def get_clear_info(self, searchKey: str) -> Dict[str, Any]:
        """
        查询企业清算信息
        :param searchKey: 企业全称（orgName）
        :return: 清算信息
        """
        params = {
            "searchKey": searchKey
        }
        return self.call_api("get-clear-info", params, method="GET")

    def get_public_inform(self, searchKey: str, page_num: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        查询企业公示催告信息
        :param searchKey: 企业全称（orgName）
        :param page_num: 分页页码，默认1
        :param page_size: 每页大小，默认10，最大20
        :return: 公示催告列表
        """
        params = {
            "searchKey": searchKey,
            "pageNum": page_num,
            "pageSize": page_size
        }
        return self.call_api("get-public-inform", params, method="GET")

    def get_labour_arb(self, searchKey: str, page_num: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        查询企业劳动仲裁送达报告信息
        :param searchKey: 企业全称（orgName）
        :param page_num: 分页页码，默认1
        :param page_size: 每页大小，默认10，最大20
        :return: 劳动仲裁列表
        """
        params = {
            "searchKey": searchKey,
            "pageNum": page_num,
            "pageSize": page_size
        }
        return self.call_api("get-labour-arb", params, method="GET")

    def get_gua_info(self, searchKey: str, page_num: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        查询企业担保信息
        :param searchKey: 企业全称（orgName）
        :param page_num: 分页页码，默认1
        :param page_size: 每页大小，默认10，最大20
        :return: 担保信息列表
        """
        params = {
            "searchKey": searchKey,
            "pageNum": page_num,
            "pageSize": page_size
        }
        return self.call_api("get-gua-info", params, method="GET")

    def get_open_court_arb(self, searchKey: str, page_num: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        查询企业开庭公告（劳动仲裁）信息
        :param searchKey: 企业全称（orgName）
        :param page_num: 分页页码，默认1
        :param page_size: 每页大小，默认10，最大20
        :return: 开庭公告列表
        """
        params = {
            "searchKey": searchKey,
            "pageNum": page_num,
            "pageSize": page_size
        }
        return self.call_api("get-open-court-arb", params, method="GET")

def main():
    """简单的命令行测试入口"""
    import argparse
    parser = argparse.ArgumentParser(description='问道云API客户端测试')
    parser.add_argument('--api-key', help='API Key')
    parser.add_argument('--search', help='企业名称搜索关键词')
    parser.add_argument('--page', type=int, default=1, help='页码')
    parser.add_argument('--punishments', help='查询行政处罚，指定企业ID')
    parser.add_argument('--abnormal', help='查询经营异常，指定企业全称')
    parser.add_argument('--equity-pledge', help='查询股权质押，指定企业全称')
    parser.add_argument('--environmental-penalties', help='查询环保处罚，指定企业全称')
    parser.add_argument('--tax-notice', help='查询欠税公告，指定企业全称')
    parser.add_argument('--simple-cancel', help='查询简易注销，指定企业全称')
    parser.add_argument('--land-mortgage', help='查询土地抵押，指定企业全称')
    parser.add_argument('--clear-info', help='查询清算信息，指定企业全称')
    parser.add_argument('--public-inform', help='查询公示催告，指定企业全称')
    parser.add_argument('--labour-arb', help='查询劳动仲裁，指定企业全称')
    parser.add_argument('--gua-info', help='查询担保信息，指定企业全称')
    parser.add_argument('--open-court-arb', help='查询开庭公告，指定企业全称')
    args = parser.parse_args()
    
    client = WendaoYunClient(api_key=args.api_key)
    
    if args.search:
        result = client.fuzzy_search_org(args.search, args.page)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.punishments:
        result = client.get_punishments(args.punishments)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.abnormal:
        result = client.get_abnormal(args.abnormal)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.equity_pledge:
        result = client.get_equity_pledge(args.equity_pledge)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.environmental_penalties:
        result = client.get_environmental_penalties(args.environmental_penalties)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.tax_notice:
        result = client.get_tax_notice(args.tax_notice)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.simple_cancel:
        result = client.get_simple_cancel(args.simple_cancel)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.land_mortgage:
        result = client.get_land_mortgage(args.land_mortgage)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.clear_info:
        result = client.get_clear_info(args.clear_info)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.public_inform:
        result = client.get_public_inform(args.public_inform)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.labour_arb:
        result = client.get_labour_arb(args.labour_arb)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.gua_info:
        result = client.get_gua_info(args.gua_info)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.open_court_arb:
        result = client.get_open_court_arb(args.open_court_arb)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("请指定 --search 关键词 或 --punishments orgId")

if __name__ == "__main__":
    main()
