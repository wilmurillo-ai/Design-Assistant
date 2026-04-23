#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZLPay Skill 主入口（Python API 层 + 命令行入口）

提供高层业务方法供 Python 代码直接调用，
同时作为 LLM 驱动模式的命令行入口。

Python 调用:
    from zlpay_skill import ZLPaySkill
    skill = ZLPaySkill()
    result = skill.query_balance(session_id="xxx")

命令行调用:
    python skill.py api_call method=GET endpoint=/skill/wallet/balance
"""

import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any

# 支持直接运行和作为包导入两种模式
try:
    # 尝试相对导入（作为包的一部分）
    from .config import Config
    from .context import SessionManager, StateStore, Memory
    from .business import WalletService, PaymentService
    from .log_manager import get_logger
except ImportError:
    # 直接运行时，添加父目录到路径并使用绝对导入
    _script_dir = Path(__file__).parent
    _package_root = _script_dir.parent
    if str(_package_root) not in sys.path:
        sys.path.insert(0, str(_package_root))
    from zlpay_skill.config import Config
    from zlpay_skill.context import SessionManager, StateStore, Memory
    from zlpay_skill.business import WalletService, PaymentService
    from zlpay_skill.log_manager import get_logger

logger = get_logger(__name__)



# ==================== API 策略注册表 ====================
# 策略模式：所有接口使用 interface_id 作为 key
# 支持策略分发和默认 HTTP 直连两种模式
# 方法路径支持点号分隔，如 "wallet_service.bind_sub_wallet"
API_STRATEGIES = {
    # 本地接口（L 开头）
    'L00001': {
        'method': 'wallet_service.query_wallet',
        'type': 'local'
    },
    'L00002': {
        'method': 'wallet_service.unbind_sub_wallet',
        'type': 'local'
    },
    # HTTP 接口（C 开头，已注册到策略）
    'C00003': {
        'method': 'wallet_service.bind_sub_wallet',
        'type': 'http',
        'endpoint': '/post/claw/bind-sub-wallet',
        'http_method': 'POST'
    },
    'C00004': {
        'method': 'payment_service.create_qr_code',
        'type': 'http',
        'endpoint': '/post/claw/create-qr-code',
        'http_method': 'POST'
    },
}


class ZLPaySkill:
    """ZLPay Skill 主类 - 统一管理所有服务"""
    
    def __init__(self, memory=None):
        # type: (Optional[Memory]) -> None
        """初始化 ZLPay Skill
        
        Args:
            memory: Memory 实例，用于从 state_store 读取配置
        """
        # 如果没有提供 memory，创建新的 Memory 实例
        if memory:
            self.memory = memory
        else:
            self.session_manager = SessionManager()
            self.state_store = StateStore(
                state_file_path=Config.STATE_FILE_PATH,
                retention_days=Config.STATE_RETENTION_DAYS
            )
            self.memory = Memory(self.session_manager, self.state_store)
        
        # 验证配置
        Config.validate()
        
        # 初始化业务服务
        self.wallet_service = WalletService(self, self.memory)
        self.payment_service = PaymentService(self, self.memory)
        # self.query_service = QueryService(self, self.memory)
        
        # 启动时校验策略配置
        self._validate_strategies()
    
    def _validate_strategies(self):
        """启动时校验 API_STRATEGIES 配置"""
        for interface_id, strategy in API_STRATEGIES.items():
            method_path = strategy.get('method')
            if not method_path:
                raise ValueError(f"接口 {interface_id} 缺少 method 配置")
            
            parts = method_path.split('.')
            if len(parts) != 2:
                raise ValueError(f"接口 {interface_id} method 格式错误: {method_path}")
            
            service_name, method_name = parts
            service = getattr(self, service_name, None)
            if not service:
                raise ValueError(f"接口 {interface_id} 服务不存在: {service_name}")
            
            handler = getattr(service, method_name, None)
            if not handler:
                raise ValueError(f"接口 {interface_id} 方法不存在: {method_path}")
            
            logger.debug(f"[Strategy] 校验通过: {interface_id} -> {method_path}")
    
    def api_call(self, method: str, endpoint: str, interface_id: str, params: dict = None, body: dict = None, timeout: int = 30) -> dict:
        """
        通用 API 调用（LLM 驱动模式入口 + 业务方法底层）
        
        支持任意 API 端点的调用，自动处理认证、签名和响应验证。
        
        Args:
            method: HTTP 方法（GET/POST）
            endpoint: API 端点路径（如 /skill/wallet/balance）
            interface_id: 接口编码（如 C00003、A00063）
            params: 查询参数（GET 请求）
            body: 请求体（POST 请求）
            timeout: 超时时间（秒），默认 30 秒
        
        Returns:
            API 响应数据字典
        """
        from .core.secure_client import SecureClient
        import json
        
        # 确保 body 不为 None
        if body is None:
            body = {}
        
        # 从环境变量获取 api_key（仅用于 SecureClient 初始化，不放入请求报文）
        from .config import Config
        api_key = Config.get_api_key(memory=self.memory)
        
        # 填充 sub_wallet_id（如果 body 中不存在且 memory 能获取到）
        if 'subWalletId' not in body:
            try:
                sub_wallet_id = self.memory.get_wallet()
                if sub_wallet_id:
                    body = body.copy()
                    body['subWalletId'] = sub_wallet_id
                    logger.debug(f"[API] 从 memory 获取并填充 sub_wallet_id")
            except Exception:
                # 未绑定钱包时跳过，由业务方法处理
                pass

        # 打印请求信息
        logger.info(f"[API Request] {method} {endpoint} interface_id={interface_id}")
        if params:
            logger.info(f"[API Request Params] {json.dumps(params, ensure_ascii=False)}")
        if body:
            # 屏蔽敏感字段
            safe_body = body.copy()
            for key in ['api_key', 'apiKey', 'password', 'token']:
                if key in safe_body:
                    safe_body[key] = '***'
            logger.info(f"[API Request Body] {json.dumps(safe_body, ensure_ascii=False)}")
        
        
            
        # 使用 SecureClient 执行安全请求（延迟初始化，使用已获取的 api_key）
        client = SecureClient(lazy_init=True)
        if api_key:
            client = client.with_api_key(api_key)
        
        result = client.secure_request(
            method=method,
            endpoint=endpoint,
            interface_id=interface_id,
            params=params,
            body=body,
            timeout=timeout
        )
        
        client.close()
        
        # 打印响应信息
        logger.info(f"[API Response] {json.dumps(result, ensure_ascii=False)[:500]}")
        
        return result
    
    def cleanup(self):
        """清理过期数据"""
        return self.memory.cleanup()


def _fill_common_params(body, memory):
    """
    统一填充公共参数
    
    Args:
        body: 请求体字典
        memory: Memory 实例
        
    Returns:
        填充后的请求体
    """
    if 'subWalletId' not in body:
        try:
            sub_wallet_id = Config.get_sub_wallet_id(memory)
            if sub_wallet_id:
                body = body.copy()
                body['subWalletId'] = sub_wallet_id
                logger.debug(f"[API] 自动填充 subWalletId: {sub_wallet_id}")
        except Exception:
            pass
    return body


def _get_handler(skill, method_path):
    """
    获取方法引用
    
    Args:
        skill: ZLPaySkill 实例
        method_path: 方法路径，如 "wallet_service.bind_sub_wallet"
        
    Returns:
        方法引用
        
    Raises:
        ValueError: 服务或方法不存在
    """
    parts = method_path.split('.')
    if len(parts) != 2:
        raise ValueError(f"method_path 格式错误: {method_path}")
    
    service_name, method_name = parts
    service = getattr(skill, service_name, None)
    if not service:
        raise ValueError(f"服务不存在: {service_name}")
    
    handler = getattr(service, method_name, None)
    if not handler:
        raise ValueError(f"方法不存在: {method_path}")
    
    return handler


# ==================== 命令行入口 ====================
def resolve_api_call(skill, interface_id, session_id=None, method=None, endpoint=None, 
                     params=None, body=None, timeout=30, **kwargs):
    """
    统一接口调用入口 - 策略分发 + 默认HTTP直连
    
    支持三种调用模式：
    1. 本地接口：已注册到策略，直接调用业务方法
    2. HTTP接口（已注册）：策略分发到业务方法
    3. HTTP接口（未注册）：默认直连 SecureClient
    
    Args:
        skill: ZLPaySkill 实例
        interface_id: 接口编码（如 L00001, C00003, 或自定义标识）
        session_id: 会话ID
        method: HTTP 方法（默认直连时需要）
        endpoint: HTTP 端点（默认直连时需要）
        params: URL/查询参数
        body: 请求体
        timeout: 超时时间（秒），默认 30
        **kwargs: 扩展参数
        
    Returns:
        接口响应结果
        
    Raises:
        ValueError: 接口不存在或参数缺失
    """
    import time
    
    # 参数校验
    if not skill:
        raise ValueError("skill 参数不能为空")
    
    if not interface_id:
        raise ValueError("interface_id 参数不能为空")
    
    start_time = time.time()
    body = body or {}
    
    # 1. 查找策略
    strategy = API_STRATEGIES.get(interface_id)
    
    if strategy:
        # ===== 策略匹配：走业务方法 =====
        logger.info(f"[API] {interface_id} 策略匹配，走业务方法")
        
        try:
            # 获取方法引用
            handler = _get_handler(skill, strategy['method'])
            
            # 统一填充公共参数
            body = _fill_common_params(body, skill.memory)
            
            # 调用业务方法
            if strategy.get('type') == 'http':
                result = handler(session_id=session_id, interface_id=interface_id, params=params, body=body, **kwargs)
            else:
                result = handler(session_id=session_id, interface_id=interface_id, params=params, body=body)
            
            duration = time.time() - start_time
            logger.info(f"[API] {interface_id} 完成，耗时 {duration:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"[API] {interface_id} 业务方法失败: {str(e)}, method={strategy['method']}, params={params}")
            raise RuntimeError(f"业务方法调用失败: {e}") from e
    
    else:
        # ===== 策略未匹配：走默认HTTP直连 =====
        logger.info(f"[API] {interface_id} 策略未匹配，走默认HTTP直连")
        
        # 校验必需参数
        if not method or not endpoint:
            raise ValueError(
                f"接口 {interface_id} 未注册到策略，"
                f"需要提供 method 和 endpoint 进行默认HTTP直连"
            )
        
        # 统一填充公共参数
        body = _fill_common_params(body, skill.memory)
        
        # 从环境变量获取 api_key 用于 SecureClient 初始化
        from .config import Config
        api_key = Config.get_api_key(memory=skill.memory)
        
        # 调用 SecureClient 直连（延迟初始化，使用已获取的 api_key）
        try:
            from .core.secure_client import SecureClient
            
            client = SecureClient(lazy_init=True)
            if api_key:
                client = client.with_api_key(api_key)
            
            result = client.secure_request(
                method=method,
                endpoint=endpoint,
                interface_id=interface_id,
                params=params,
                body=body,
                timeout=timeout
            )
            
            client.close()
            
            duration = time.time() - start_time
            logger.info(f"[API] {interface_id} 直连完成，耗时 {duration:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"[API] {interface_id} 直连失败: {str(e)}, endpoint={endpoint}, method={method}")
            raise RuntimeError(f"HTTP直连调用失败: {e}") from e


def check_environment():
    """检查环境是否完整"""
    # 尝试多个可能的虚拟环境位置
    current_file = Path(__file__)
    possible_venv_paths = [
        current_file.parent.parent / "venv",  # scripts/venv
        current_file.parent.parent.parent / "venv",  # 项目根目录/venv
        Path.cwd() / "venv",  # 当前工作目录/venv
    ]
    
    venv_exists = any(p.exists() for p in possible_venv_paths)
    
    if not venv_exists:
        print("❌ 错误: 虚拟环境未初始化", file=sys.stderr)
        print("\n请运行以下命令初始化环境:", file=sys.stderr)
        print("  pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)
    
    try:
        import requests
        from .core.secure_client import SecureClient
    except ImportError as e:
        print(f"❌ 错误: 缺少依赖 - {e}", file=sys.stderr)
        print("\n请运行以下命令安装依赖:", file=sys.stderr)
        print("  pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)


def _parse_value(value: str) -> str:
    """
    解析参数值，处理引号和 Unicode 转义
    
    Args:
        value: 原始参数字符串
        
    Returns:
        处理后的值
    """
    # 去除首尾空格
    value = value.strip()
    
    # 去除首尾引号（单引号或双引号）
    if len(value) >= 2:
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
    
    # 解码 Unicode 转义序列（如 \u9f99\u867e -> 龙虾）
    # 只有当值中包含 \u 转义序列时才解码
    if '\\u' in value:
        try:
            value = value.encode('utf-8').decode('unicode_escape')
        except (UnicodeDecodeError, UnicodeError):
            pass
    
    return value


def parse_args(args: list) -> tuple:
    """解析命令行参数
    
    参数格式：
    - 控制参数：-key=value (单横线，如 -interfaceId=C00003, -method=POST)
    - 数据参数：--key=value (双横线，如 --amount=100, --sub_wallet_id=xxx)
    
    Returns:
        tuple: (command, control_params, data_params)
            - command: 命令名称
            - control_params: 单横线控制参数字典
            - data_params: 双横线业务参数字典
    """
    if len(args) < 1:
        return None, {}, {}
    
    command = args[0]
    control_params = {}
    data_params = {}
    
    for arg in args[1:]:
        if arg.startswith('--') and '=' in arg:
            # --key=value 形式，数据参数
            key_value = arg[2:]  # 去掉开头的 --
            key, value = key_value.split('=', 1)
            data_params[key] = _parse_value(value)
        elif arg.startswith('-') and '=' in arg:
            # -key=value 形式，控制参数
            key_value = arg[1:]  # 去掉开头的 -
            key, value = key_value.split('=', 1)
            control_params[key] = _parse_value(value)
        else:
            logger.warning(f"忽略无效参数: {arg}")
    
    return command, control_params, data_params


def main():
    """命令行主函数"""
    check_environment()

    command, control_params, data_params = parse_args(sys.argv[1:])

    # 打印接收的参数
    logger.info(f"[CLI] 原始参数: {sys.argv[1:]}")
    logger.info(f"[CLI] 命令: {command}")
    logger.info(f"[CLI] 控制参数: {control_params}")
    logger.info(f"[CLI] 数据参数: {data_params}")
    
    if not command:
        print("用法: python skill.py call <参数>", file=sys.stderr)
        print("\n参数格式:", file=sys.stderr)
        print("  -interfaceId=xxx: 接口编码（如 L00001, C00003）", file=sys.stderr)
        print("  -api-key=xxx: API Key（可选，支持环境变量或交互式输入）", file=sys.stderr)
        print("  -method=POST: HTTP 方法（策略未匹配时需要）", file=sys.stderr)
        print("  -endpoint=/api: HTTP 端点（策略未匹配时需要）", file=sys.stderr)
        print("  -timeout=30: 超时时间（秒），默认 30", file=sys.stderr)
        print("  --amount=100: 业务参数（双横线，放入 body）", file=sys.stderr)
        print("\n示例:", file=sys.stderr)
        print('  python skill.py call -interfaceId=L00001', file=sys.stderr)
        print('  python skill.py call -interfaceId=C00003 -method=POST -endpoint=/post/claw/bind-sub-wallet', file=sys.stderr)
        sys.exit(1)
    
    # 统一使用 call 命令
    if command == 'call':
        try:
            # 从控制参数提取必需参数
            interface_id = control_params.get('interfaceId') or control_params.get('interface_id')
            if not interface_id:
                print("错误: 必须提供 interfaceId 参数", file=sys.stderr)
                sys.exit(1)
            
            # 从控制参数提取可选参数
            session_id = control_params.get('sessionId') or control_params.get('session_id')
            method = control_params.get('method')
            endpoint = control_params.get('endpoint')
            timeout = int(control_params.get('timeout', 30))
            
            # 从控制参数提取 API Key（支持 -api-key 或 --api_key）
            api_key = control_params.get('api-key') or control_params.get('api_key') or data_params.get('api_key')
            if api_key:
                Config.set_api_key(api_key)
                logger.info("API Key set from command line argument")
            
            # 组装 body 和 params
            call_params = {}
            call_body = {}
            
            for k, v in data_params.items():
                # POST 请求且非查询参数 -> 放入 body
                if method and method.upper() == 'POST' and k not in ['sub_wallet_id', 'phone', 'page', 'page_size']:
                    call_body[k] = v
                else:
                    call_params[k] = v
            
            # 初始化 Skill 并执行请求
            skill = ZLPaySkill()
            
            # 使用统一的 resolve_api_call 调用
            result = resolve_api_call(
                skill=skill,
                interface_id=interface_id,
                session_id=session_id,
                method=method,
                endpoint=endpoint,
                params=call_params if call_params else None,
                body=call_body if call_body else None,
                timeout=timeout
            )
            
            # 输出 JSON 结果
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(0 if result.get("success", True) else 1)
            
        except Exception as e:
            logger.error(f"调用失败: {e}")
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)
    
    print(f"错误: 未知的命令: {command}", file=sys.stderr)
    print("提示: 请使用 'call' 命令，如: python skill.py call -interfaceId=L00001", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
