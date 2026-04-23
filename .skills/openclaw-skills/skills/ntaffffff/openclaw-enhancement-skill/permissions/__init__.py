#!/usr/bin/env python3
"""
权限验证增强模块

6层权限模型 + 细粒度控制
参考 Claude Code 的权限系统
"""

import os
import re
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib

try:
    from colorama import Fore, init
    init(autoreset=True)
except ImportError:
    class Fore:
        CYAN = GREEN = RED = YELLOW = BLUE = ""


class PermissionLevel(Enum):
    """权限级别"""
    NONE = 0      # 无权限
    READ = 1      # 只读
    WRITE = 2     # 写入
    EXECUTE = 3   # 执行
    ADMIN = 4     # 管理


@dataclass
class Permission:
    """权限定义"""
    name: str
    description: str
    level: PermissionLevel
    patterns: List[str] = field(default_factory=list)  # 路径匹配模式
    conditions: Dict[str, Any] = field(default_factory=dict)  # 执行条件


@dataclass
class Role:
    """角色"""
    name: str
    description: str
    permissions: Set[str] = field(default_factory=set)
    inherits_from: List[str] = field(default_factory=list)


@dataclass
class User:
    """用户"""
    id: str
    name: str
    roles: Set[str] = field(default_factory=set)
    permissions: Set[str] = field(default_factory=set)  # 直接权限
    restrictions: Dict[str, Any] = field(default_factory=dict)  # 限制


@dataclass
class PermissionRequest:
    """权限请求"""
    id: str
    user_id: str
    permission: str
    resource: str
    action: str
    timestamp: datetime = field(default_factory=datetime.now)
    granted: bool = False
    reason: Optional[str] = None


class PermissionChecker:
    """权限检查器"""
    
    # 危险操作模式
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf",           # 递归强制删除
        r"chmod\s+777",        # 过度开放权限
        r">\s*/etc/",          # 写入系统目录
        r"curl.*\|\s*bash",    # 远程脚本执行
        r"wget.*\|\s*bash",    # 远程脚本执行
        r"format",             # 格式化
        r"mkfs",               # 创建文件系统
    ]
    
    # 关键路径
    PROTECTED_PATHS = [
        "/etc/passwd",
        "/etc/shadow",
        "/etc/sudoers",
        "/root",
        "/sys",
        "/proc",
        "/boot",
        "/dev",
    ]
    
    def __init__(self):
        self.permissions: Dict[str, Permission] = {}
        self.roles: Dict[str, Role] = {}
        self.users: Dict[str, User] = {}
        self.request_history: List[PermissionRequest] = []
        self.denied_count = 0
        
        self._init_default_permissions()
    
    def _init_default_permissions(self):
        """初始化默认权限"""
        # 文件权限
        self.register_permission(Permission(
            name="fs:read",
            description="读取文件系统",
            level=PermissionLevel.READ,
            patterns=["*"]
        ))
        
        self.register_permission(Permission(
            name="fs:write",
            description="写入文件系统",
            level=PermissionLevel.WRITE,
            patterns=["~/", "/tmp/"]
        ))
        
        self.register_permission(Permission(
            name="fs:delete",
            description="删除文件",
            level=PermissionLevel.WRITE,
            patterns=["~/", "/tmp/"],
            conditions={"confirm": True}
        ))
        
        # 网络权限
        self.register_permission(Permission(
            name="network:http",
            description="HTTP 请求",
            level=PermissionLevel.READ,
            patterns=["http://*", "https://*"]
        ))
        
        self.register_permission(Permission(
            name="network:ssh",
            description="SSH 连接",
            level=PermissionLevel.EXECUTE,
            patterns=["*"]
        ))
        
        # 执行权限
        self.register_permission(Permission(
            name="exec:shell",
            description="执行 Shell 命令",
            level=PermissionLevel.EXECUTE,
            patterns=["*"],
            conditions={"timeout": 30}
        ))
        
        # 角色
        self.register_role(Role(
            name="admin",
            description="管理员",
            permissions={"*"}  # 所有权限
        ))
        
        self.register_role(Role(
            name="developer",
            description="开发者",
            permissions={"fs:read", "fs:write", "network:http", "exec:shell"}
        ))
        
        self.register_role(Role(
            name="user",
            description="普通用户",
            permissions={"fs:read", "network:http"}
        ))
    
    def register_permission(self, permission: Permission):
        """注册权限"""
        self.permissions[permission.name] = permission
    
    def register_role(self, role: Role):
        """注册角色"""
        # 处理继承
        for parent_name in role.inherits_from:
            parent = self.roles.get(parent_name)
            if parent:
                role.permissions.update(parent.permissions)
        
        self.roles[role.name] = role
    
    def register_user(self, user: User):
        """注册用户"""
        self.users[user.id] = user
    
    def check_permission(
        self,
        user_id: str,
        permission: str,
        resource: str = None,
        action: str = None
    ) -> bool:
        """检查权限（6层检查）"""
        
        # 第1层：用户是否存在
        user = self.users.get(user_id)
        if not user:
            self.denied_count += 1
            self._log_request(user_id, permission, resource, action, False, "用户不存在")
            return False
        
        # 第2层：直接权限检查
        if permission in user.permissions:
            return True
        
        # 第3层：角色权限检查
        for role_name in user.roles:
            role = self.roles.get(role_name)
            if role and ("*" in role.permissions or permission in role.permissions):
                return True
        
        # 第4层：资源路径检查
        if resource:
            perm = self.permissions.get(permission)
            if perm and not self._check_path_pattern(resource, perm.patterns):
                self._log_request(user_id, permission, resource, action, False, "路径不匹配")
                return False
            
            # 第5层：危险操作检查
            if self._is_dangerous(resource, action):
                self.denied_count += 1
                self._log_request(user_id, permission, resource, action, False, "危险操作")
                return False
            
            # 第6层：受保护路径检查
            if self._is_protected(resource):
                self.denied_count += 1
                self._log_request(user_id, permission, resource, action, False, "受保护路径")
                return False
        
        self.denied_count += 1
        self._log_request(user_id, permission, resource, action, False, "权限不足")
        return False
    
    def _check_path_pattern(self, path: str, patterns: List[str]) -> bool:
        """检查路径模式"""
        for pattern in patterns:
            if pattern == "*":
                return True
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                if path.startswith(prefix):
                    return True
            elif pattern in path:
                return True
        return False
    
    def _is_dangerous(self, resource: str, action: str = None) -> bool:
        """检查危险操作"""
        combined = f"{resource} {action or ''}"
        
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, combined, re.IGNORECASE):
                return True
        
        return False
    
    def _is_protected(self, path: str) -> bool:
        """检查受保护路径"""
        path = os.path.abspath(path)
        
        for protected in self.PROTECTED_PATHS:
            if path.startswith(protected):
                return True
        
        return False
    
    def _log_request(self, user_id: str, permission: str, resource: str, action: str, granted: bool, reason: str):
        """记录权限请求"""
        request = PermissionRequest(
            id=hashlib.md5(f"{user_id}{permission}{datetime.now()}".encode()).hexdigest()[:12],
            user_id=user_id,
            permission=permission,
            resource=resource or "",
            action=action or "",
            granted=granted,
            reason=reason
        )
        
        self.request_history.append(request)
        
        # 只保留最近1000条
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]
    
    def request_permission(
        self,
        user_id: str,
        permission: str,
        resource: str = None,
        action: str = None
    ) -> PermissionRequest:
        """请求权限"""
        granted = self.check_permission(user_id, permission, resource, action)
        
        # 找到最近的请求记录
        request = self.request_history[-1] if self.request_history else None
        return request
    
    def get_user_permissions(self, user_id: str) -> Set[str]:
        """获取用户所有权限"""
        user = self.users.get(user_id)
        if not user:
            return set()
        
        all_perms = set(user.permissions)
        
        for role_name in user.roles:
            role = self.roles.get(role_name)
            if role:
                all_perms.update(role.permissions)
        
        return all_perms
    
    def get_stats(self) -> Dict[str, Any]:
        """获取权限统计"""
        total = len(self.request_history)
        granted = sum(1 for r in self.request_history if r.granted)
        denied = total - granted
        
        return {
            "total_requests": total,
            "granted": granted,
            "denied": denied,
            "deny_rate": denied / total if total > 0 else 0,
            "users": len(self.users),
            "roles": len(self.roles),
            "permissions": len(self.permissions)
        }


# ============ 使用示例 ============

def example():
    """示例"""
    print(f"{Fore.CYAN}=== 权限验证增强示例 ==={Fore.RESET}\n")
    
    # 创建权限系统
    checker = PermissionChecker()
    
    # 创建用户
    checker.register_user(User(
        id="user1",
        name="Alice",
        roles={"developer"}
    ))
    
    checker.register_user(User(
        id="user2", 
        name="Bob",
        roles={"user"}
    ))
    
    checker.register_user(User(
        id="admin1",
        name="Admin",
        roles={"admin"}
    ))
    
    # 测试权限
    print("1. 权限检查:")
    print(f"   Alice 读取文件: {checker.check_permission('user1', 'fs:read', '~/project/main.py')}")
    print(f"   Alice 删除文件: {checker.check_permission('user1', 'fs:delete', '~/project/main.py')}")
    print(f"   Bob 读取文件: {checker.check_permission('user2', 'fs:read', '~/project/main.py')}")
    print(f"   Bob 删除文件: {checker.check_permission('user2', 'fs:delete', '~/project/main.py')}")
    print(f"   Admin 删除文件: {checker.check_permission('admin1', 'fs:delete', '~/project/main.py')}")
    
    # 危险操作检查
    print("\n2. 危险操作检测:")
    print(f"   尝试删除根目录: {checker.check_permission('user1', 'fs:delete', '/etc/passwd')}")
    print(f"   尝试执行危险命令: {checker.check_permission('user1', 'exec:shell', 'rm -rf /')}")
    
    # 获取权限
    print("\n3. 用户权限:")
    for perm in checker.get_user_permissions("user1"):
        print(f"   - {perm}")
    
    # 统计
    print("\n4. 权限统计:")
    stats = checker.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print(f"\n{Fore.GREEN}✓ 权限验证增强示例完成!{Fore.RESET}")


if __name__ == "__main__":
    example()