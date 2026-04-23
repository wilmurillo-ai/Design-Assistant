#!/usr/bin/env python3
"""
WizNote API Core Module
认证 + API 核心封装，包含重试机制和错误处理

Author: OpenClaw Worker
Date: 2026-03-26
"""

import os
import sys
import time
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

try:
    import requests
    from requests.exceptions import RequestException, ConnectionError, Timeout, HTTPError
except ImportError:
    print("❌ 缺少依赖: requests")
    print("请运行: pip install requests")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('wiznote.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WizNoteAPIError(Exception):
    """WizNote API 自定义异常"""
    pass


class WizNoteAPI:
    """
    WizNote API 客户端
    
    支持功能：
    - 密码登录获取 token
    - 统一的 API 请求封装
    - 自动重试机制（指数退避）
    - 完整的错误处理
    """
    
    # 重试配置
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # 秒
    RETRY_BACKOFF = 2  # 延迟倍数
    REQUEST_TIMEOUT = 30  # 秒
    
    # 可重试的 HTTP 状态码
    RETRYABLE_STATUS_CODES = {500, 502, 503, 504, 408, 429}
    
    def __init__(self):
        """初始化 API 客户端"""
        # 加载环境变量
        self.endpoint = os.getenv('WIZ_ENDPOINT', 'http://127.0.0.1:80')
        self.user = os.getenv('WIZ_USER')
        self.token = os.getenv('WIZ_TOKEN')
        
        # 验证必需的环境变量
        self._validate_config()
        
        # 初始化 session
        self.session = requests.Session()
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # 如果已有 token，添加到 header
        if self.token:
            self.headers['X-Wiz-Token'] = self.token
        
        logger.info(f"WizNote API 客户端初始化完成，endpoint: {self.endpoint}")
    
    def _validate_config(self):
        """验证配置是否完整"""
        if not self.user:
            error_msg = "❌ 缺少必需的环境变量: WIZ_USER"
            logger.error(error_msg)
            raise WizNoteAPIError(error_msg)
        
        logger.info(f"配置验证通过，用户: {self.user}")
    
    def login(self, password: str) -> str:
        """
        通过密码登录获取 token
        
        Args:
            password: 用户密码
            
        Returns:
            str: 认证 token
            
        Raises:
            WizNoteAPIError: 登录失败
        """
        logger.info(f"尝试登录，用户: {self.user}")
        
        # 私有化部署 API 路径：/as/user/login
        url = f"{self.endpoint}/as/user/login"
        payload = {
            "userId": self.user,
            "password": password
        }
        
        try:
            response = self.session.post(
                url, 
                json=payload, 
                headers={'Content-Type': 'application/json'},
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            
            # 检查返回码
            if data.get('returnCode') != 200:
                error_msg = data.get('returnMessage', '未知错误')
                logger.error(f"登录失败: {error_msg}")
                raise WizNoteAPIError(f"登录失败: {error_msg}")
            
            # 提取 token 和 kbGuid
            result = data.get('result', {})
            self.token = result.get('token')
            self.kb_guid = result.get('kbGuid')
            
            if not self.token:
                logger.error("登录响应中未找到 token")
                raise WizNoteAPIError("登录失败: 响应中未包含 token")
            
            # 更新 header
            self.headers['X-Wiz-Token'] = self.token
            
            # 保存 kbGuid 到环境变量
            if self.kb_guid:
                os.environ['WIZ_KB_GUID'] = self.kb_guid
            
            logger.info(f"✅ 登录成功，token 已获取，kbGuid: {self.kb_guid}")
            
            return self.token
            
        except HTTPError as e:
            if response.status_code == 401:
                logger.error("认证失败: 用户名或密码错误")
                raise WizNoteAPIError("认证失败: 用户名或密码错误")
            else:
                logger.error(f"HTTP 错误: {e}")
                raise WizNoteAPIError(f"登录失败: HTTP {response.status_code}")
                
        except ConnectionError:
            error_msg = f"无法连接到为知笔记服务器: {self.endpoint}"
            logger.error(error_msg)
            raise WizNoteAPIError(error_msg)
            
        except Timeout:
            logger.error("连接超时")
            raise WizNoteAPIError("登录失败: 连接超时")
            
        except Exception as e:
            logger.error(f"登录时发生未知错误: {e}")
            raise WizNoteAPIError(f"登录失败: {e}")
    
    def _request(self, method: str, api: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        统一请求封装，包含重试机制
        
        Args:
            method: HTTP 方法 (GET, POST, PUT, DELETE)
            api: API 路径（如 /api/note/list）
            data: 请求数据（字典）
            
        Returns:
            Dict: API 响应数据
            
        Raises:
            WizNoteAPIError: 请求失败
        """
        url = f"{self.endpoint}{api}"
        
        # 检查 token
        if not self.token:
            logger.error("未设置 token，请先登录或设置 WIZ_TOKEN 环境变量")
            raise WizNoteAPIError("未认证: 请先登录或设置 WIZ_TOKEN")
        
        # 重试逻辑
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.debug(f"请求: {method} {url} (尝试 {attempt + 1}/{self.MAX_RETRIES})")
                
                response = self.session.request(
                    method=method.upper(),
                    url=url,
                    json=data,
                    headers=self.headers,
                    timeout=self.REQUEST_TIMEOUT
                )
                
                # 检查 HTTP 状态码
                if response.status_code in self.RETRYABLE_STATUS_CODES:
                    if attempt < self.MAX_RETRIES - 1:
                        delay = self.RETRY_DELAY * (self.RETRY_BACKOFF ** attempt)
                        logger.warning(f"服务器错误 {response.status_code}，{delay}秒后重试...")
                        time.sleep(delay)
                        continue
                    else:
                        raise HTTPError(f"服务器错误: {response.status_code}")
                
                response.raise_for_status()
                
                # 解析 JSON
                result = response.json()
                
                # 检查业务返回码
                if isinstance(result, dict) and result.get('return_code') not in [200, None]:
                    error_msg = result.get('return_message', '未知业务错误')
                    logger.error(f"API 业务错误: {error_msg}")
                    raise WizNoteAPIError(f"API 错误: {error_msg}")
                
                logger.debug(f"请求成功: {method} {url}")
                return result
                
            except ConnectionError as e:
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAY * (self.RETRY_BACKOFF ** attempt)
                    logger.warning(f"连接失败，{delay}秒后重试...")
                    time.sleep(delay)
                    continue
                else:
                    error_msg = f"API 不可达: {self.endpoint}"
                    logger.error(error_msg)
                    self._log_error_to_file(f"ConnectionError: {url}")
                    raise WizNoteAPIError(error_msg)
                    
            except Timeout as e:
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAY * (self.RETRY_BACKOFF ** attempt)
                    logger.warning(f"请求超时，{delay}秒后重试...")
                    time.sleep(delay)
                    continue
                else:
                    logger.error("请求超时，已达最大重试次数")
                    raise WizNoteAPIError("请求超时")
                    
            except HTTPError as e:
                # 认证失败不重试
                if response.status_code == 401:
                    logger.error("认证失败: Token 无效或已过期")
                    raise WizNoteAPIError("认证失败: Token 无效或已过期，请重新登录")
                # 权限不足不重试
                elif response.status_code == 403:
                    logger.error("权限不足")
                    raise WizNoteAPIError("权限不足: 无权访问此资源")
                # 资源不存在不重试
                elif response.status_code == 404:
                    logger.error("资源不存在")
                    raise WizNoteAPIError("资源不存在: 请检查 ID 是否正确")
                # 其他 HTTP 错误
                else:
                    logger.error(f"HTTP 错误: {e}")
                    raise WizNoteAPIError(f"HTTP 错误: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"请求时发生未知错误: {e}")
                raise WizNoteAPIError(f"请求失败: {e}")
        
        # 理论上不会执行到这里
        raise WizNoteAPIError("请求失败: 超过最大重试次数")
    
    def _log_error_to_file(self, error_msg: str):
        """记录错误到单独的错误日志文件"""
        error_log_file = 'wiznote_error.log'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(error_log_file, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} ERROR {error_msg}\n")
    
    def get(self, api: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET 请求"""
        return self._request('GET', api, params)
    
    def post(self, api: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """POST 请求"""
        return self._request('POST', api, data)
    
    def put(self, api: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """PUT 请求"""
        return self._request('PUT', api, data)
    
    def delete(self, api: str) -> Dict[str, Any]:
        """DELETE 请求"""
        return self._request('DELETE', api)
    
    def check_connection(self) -> bool:
        """
        检查与服务器的连接
        
        Returns:
            bool: 连接成功返回 True，否则返回 False
        """
        try:
            # 尝试访问一个简单的 API
            response = self.session.get(
                f"{self.endpoint}/api/user/info",
                headers=self.headers,
                timeout=5
            )
            return response.status_code in [200, 401]  # 401 表示服务器可达，只是未认证
        except Exception:
            return False


def main():
    """测试入口"""
    import getpass
    
    print("=" * 60)
    print("WizNote API 测试")
    print("=" * 60)
    
    # 检查环境变量
    if not os.getenv('WIZ_USER'):
        print("❌ 请设置环境变量 WIZ_USER")
        print("示例: export WIZ_USER='your_username'")
        return
    
    # 初始化 API
    try:
        api = WizNoteAPI()
    except WizNoteAPIError as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    # 测试连接
    print(f"\n测试连接: {api.endpoint}")
    if api.check_connection():
        print("✅ 服务器可达")
    else:
        print("❌ 无法连接到服务器")
        return
    
    # 如果没有 token，尝试登录
    if not api.token:
        password = getpass.getpass(f"请输入用户 {api.user} 的密码: ")
        try:
            token = api.login(password)
            print(f"✅ 登录成功")
            print(f"Token: {token[:20]}...")
        except WizNoteAPIError as e:
            print(f"❌ 登录失败: {e}")
            return
    
    print("\n✅ API 客户端测试通过")


if __name__ == '__main__':
    main()
