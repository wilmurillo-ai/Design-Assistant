# -*- coding: utf-8 -*-
"""
SM2/SM4 国密加密工具模块

兼容 Java 版本的加密加签逻辑：
- SM2：非对称加密，用于密钥交换和签名验签
- SM4：对称加密，ECB 模式，用于报文加解密
"""

import secrets
from typing import Optional

from sm_crypto import sm2
from gmssl import sm4


class CryptoError(Exception):
    """加密操作错误"""
    pass


class SM2Util:
    """SM2 非对称加密工具类"""
    
    @staticmethod
    def generate_key() -> str:
        """
        生成 SM2 私钥
        
        Returns:
            16 进制格式的私钥字符串（32 字节 = 64 字符）
        """
        private_key_bytes = secrets.token_bytes(32)
        return private_key_bytes.hex()
    
    @staticmethod
    def get_public_key_from_private(private_key_hex: str) -> str:
        """
        从私钥推导公钥
        
        使用 sm-crypto 库从私钥推导公钥。
        
        Args:
            private_key_hex: 16 进制格式的私钥
            
        Returns:
            16 进制格式的公钥字符串（去掉 04 前缀，64 字节 = 128 字符）
        """
        try:
            private_key = sm2.SM2PrivateKey(private_key_hex)
            public_key_obj = private_key.public_key()
            # 获取公钥坐标并拼接（x 和 y 已经是 16 进制字符串）
            x = public_key_obj.x
            y = public_key_obj.y
            return x + y
        except Exception as e:
            raise CryptoError(f"从私钥推导公钥失败: {e}")
    
    @staticmethod
    def en_code(public_key_hex: str, data: str, uid: Optional[str] = None) -> str:
        """
        SM2 加密（对应 Java SM2Util.enCode）
        
        使用 sm-crypto 库进行 SM2 加密。
        
        Args:
            public_key_hex: 公钥（16 进制字符串，可以带或不带 04 前缀）
            data: 待加密数据（UTF-8 字符串）
            uid: 用户 ID（可选）
            
        Returns:
            16 进制字符串格式的加密结果
        """
        try:
            # 解析公钥坐标（去掉 04 前缀后，前 64 字符是 x，后 64 字符是 y）
            if public_key_hex.startswith('04'):
                public_key_hex = public_key_hex[2:]
            x = public_key_hex[:64]
            y = public_key_hex[64:]
            
            # 创建公钥对象
            public_key = sm2.SM2PublicKey(x, y)
            
            # 加密数据
            data_bytes = data.encode('utf-8')
            enc_bytes = public_key.encrypt(data_bytes)
            
            # 返回 16 进制字符串
            return enc_bytes.hex()
        except Exception as e:
            raise CryptoError(f"SM2 加密失败: {e}")
    
    @staticmethod
    def de_code(private_key_hex: str, encrypted_data: str, uid: Optional[str] = None) -> str:
        """
        SM2 解密（对应 Java SM2Util.deCode）
        
        使用 sm-crypto 库进行 SM2 解密。
        
        Args:
            private_key_hex: 私钥（16 进制字符串）
            encrypted_data: 16 进制格式的加密数据
            uid: 用户 ID（可选）
            
        Returns:
            解密后的 UTF-8 字符串
        """
        try:
            # 创建私钥对象
            private_key = sm2.SM2PrivateKey(private_key_hex)
            
            # 16 进制解码得到加密字节
            enc_bytes = bytes.fromhex(encrypted_data)
            
            # 解密数据
            dec_bytes = private_key.decrypt(enc_bytes)
            
            # 解密为 UTF-8 字符串
            return dec_bytes.decode('utf-8')
        except Exception as e:
            raise CryptoError(f"SM2 解密失败: {e}")
    
    @staticmethod
    def sign(private_key_hex: str, data: str) -> str:
        """
        SM2 签名（对应 Java SM2Util.sign）
        
        使用 sm-crypto 库进行 SM2 签名。
        
        Args:
            private_key_hex: 私钥（16 进制字符串）
            data: 待签名数据
            
        Returns:
            16 进制字符串格式的签名结果
        """
        try:
            # 创建私钥对象
            private_key = sm2.SM2PrivateKey(private_key_hex)
            
            # 计算签名（返回 DER 编码的 ASN.1 格式）
            data_bytes = data.encode('utf-8')
            sign_bytes = private_key.sign(data_bytes)
            
            # 返回 16 进制字符串
            return sign_bytes.hex()
        except Exception as e:
            raise CryptoError(f"SM2 签名失败: {e}")
    
    @staticmethod
    def verify(public_key_hex: str, data: str, signature: str) -> bool:
        """
        SM2 验签（对应 Java SM2Util.verify）
        
        使用 sm-crypto 库进行 SM2 验签。
        
        Args:
            public_key_hex: 公钥（16 进制字符串）
            data: 原始数据
            signature: 16 进制字符串格式的签名（DER 编码）
            
        Returns:
            验签是否成功
        """
        try:
            # 解析公钥坐标（去掉 04 前缀后，前 64 字符是 x，后 64 字符是 y）
            if public_key_hex.startswith('04'):
                public_key_hex = public_key_hex[2:]
            x = public_key_hex[:64]
            y = public_key_hex[64:]
            
            # 创建公钥对象
            public_key = sm2.SM2PublicKey(x, y)
            
            # 16 进制解码签名
            sign_bytes = bytes.fromhex(signature)
            
            # 验签
            data_bytes = data.encode('utf-8')
            return public_key.verify(data_bytes, sign_bytes)
        except Exception as e:
            # 验签失败返回 False，不抛出异常
            return False


class SM4Util:
    """SM4 对称加密工具类"""
    
    # SM4 密钥长度（16 字节 = 128 位）
    KEY_LENGTH = 16
    
    @staticmethod
    def generate_key() -> str:
        """
        生成随机 SM4 密钥（对应 Java SM4Util.generatorSM4key）
        
        Returns:
            16 进制字符串格式的密钥
        """
        key_bytes = secrets.token_bytes(SM4Util.KEY_LENGTH)
        return key_bytes.hex()
    
    @staticmethod
    def encrypt_ecb(key_hex: str, data: str) -> str:
        """
        SM4 ECB 模式加密（对应 Java SM4Util.encrypt_ECB）
        
        Java 实现:
        - 密钥是 16 进制字符串
        - 返回 16 进制加密字符串
        
        Args:
            key_hex: 16 进制格式的密钥
            data: 待加密数据
            
        Returns:
            16 进制格式的加密结果
        """
        try:
            # 创建 SM4 加密对象
            crypt_sm4 = sm4.CryptSM4()
            crypt_sm4.set_key(bytes.fromhex(key_hex), sm4.SM4_ENCRYPT)
            
            # 加密数据（需要填充到 16 字节对齐）
            data_bytes = data.encode('utf-8')
            padded_data = SM4Util._pkcs7_padding(data_bytes)
            
            # 加密
            enc_bytes = crypt_sm4.crypt_ecb(padded_data)
            
            # 返回 16 进制字符串
            return enc_bytes.hex()
        except Exception as e:
            raise CryptoError(f"SM4 加密失败: {e}")
    
    @staticmethod
    def decrypt_ecb(key_hex: str, encrypted_data: str) -> str:
        """
        SM4 ECB 模式解密（对应 Java SM4Util.decrypt_ECB）
        
        Java 实现:
        - 密文是 16 进制字符串
        - 密钥是 16 进制字符串
        - 返回 UTF-8 字符串
        
        Args:
            key_hex: 16 进制格式的密钥
            encrypted_data: 16 进制格式的加密数据
            
        Returns:
            解密后的字符串
        """
        try:
            # 创建 SM4 解密对象
            crypt_sm4 = sm4.CryptSM4()
            crypt_sm4.set_key(bytes.fromhex(key_hex), sm4.SM4_DECRYPT)
            
            # 16 进制解码
            enc_bytes = bytes.fromhex(encrypted_data)
            
            # 解密
            dec_bytes = crypt_sm4.crypt_ecb(enc_bytes)
            
            # 去除填充
            unpadded_data = SM4Util._pkcs7_unpadding(dec_bytes)
            
            return unpadded_data.decode('utf-8')
        except Exception as e:
            raise CryptoError(f"SM4 解密失败: {e}")
    
    @staticmethod
    def _pkcs7_padding(data: bytes) -> bytes:
        """PKCS7 填充"""
        block_size = 16
        padding_len = block_size - (len(data) % block_size)
        padding = bytes([padding_len] * padding_len)
        return data + padding
    
    @staticmethod
    def _pkcs7_unpadding(data: bytes) -> bytes:
        """PKCS7 去填充"""
        padding_len = data[-1]
        return data[:-padding_len]
