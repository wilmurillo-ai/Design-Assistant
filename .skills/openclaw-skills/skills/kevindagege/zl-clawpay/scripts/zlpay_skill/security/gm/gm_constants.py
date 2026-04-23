# -*- coding: utf-8 -*-
"""
国密 SM2/SM4 常量定义

集中管理国密策略相关的所有常量，避免魔法值分散在代码中。
"""


class GmConstants:
    """国密策略常量类"""
    
    # ==================== HTTP 请求头 ====================
    HEADER_CONTENT_TYPE = "Content-Type"
    HEADER_ENCRYPTION_TYPE = "X-Encryption-Type"
    
    # ==================== HTTP 头值 ====================
    CONTENT_TYPE_JSON = "application/json"
    ENCRYPTION_TYPE_SM = "SM2/SM4"
    
    # ==================== 请求/响应字段名 ====================
    FIELD_APP_ID = "appId"
    FIELD_VERSION = "version"
    FIELD_SEQ_ID = "seqId"
    FIELD_TIMESTAMP = "timeStamp"
    FIELD_INTERFACE_ID = "interfaceId"
    FIELD_SECRET = "secret"
    FIELD_DATA = "data"
    FIELD_SIGN = "sign"
    
    # ==================== 响应特定字段 ====================
    FIELD_RES_CODE = "resCode"
    
    # ==================== 默认值 ====================
    DEFAULT_EMPTY_STRING = ""
