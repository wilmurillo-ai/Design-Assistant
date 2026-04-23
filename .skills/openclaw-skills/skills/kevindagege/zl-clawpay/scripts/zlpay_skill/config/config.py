# -*- coding: utf-8 -*-
"""
Configuration module
"""

import os
from pathlib import Path
from typing import Any, Optional

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
    load_dotenv()
except ImportError:
    DOTENV_AVAILABLE = False


class ConfigError(Exception):
    """Configuration error"""
    pass


class Config:
    """Config class - fast fail principle"""
    
    # Response code config
    SUCCESS_CODE_PREFIX = "S"
    HTTP_OK = 200
    
    # Timeout config
    REQUEST_TIMEOUT = 30
    
    # Retry config
    MAX_RETRIES = 3
    RETRY_DELAY = 1
    
    # Pagination config
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Session config
    SESSION_TIMEOUT = 1800
    
    # State storage config
    STATE_FILE_PATH = os.path.expanduser("~/.zlpay/state.json")
    STATE_RETENTION_DAYS = 90
    
    # Log config
    LOG_DIR = os.path.expanduser("~/.zlpay/logs")
    _LOG_LEVEL = None
    
    # Security strategy config
    SECURITY_STRATEGY = "gm"
    VERSION = "1.0"
    GM_TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"
    _GM_ENABLE_ENCRYPTION = None
    
    @classmethod
    def _read_from_env_file(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        """Read value directly from config/.env file without using environment variables"""
        env_file = Path("config/.env")
        if not env_file.exists():
            return default
        
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"\'')
                        if k == key:
                            return v
        except Exception:
            pass
        return default
    
    @classmethod
    def get_log_level(cls) -> str:
        """Get log level from config/.env file (not environment variables)"""
        if cls._LOG_LEVEL is None:
            cls._LOG_LEVEL = cls._read_from_env_file("ZLPAY_LOG_LEVEL", "INFO")
        return cls._LOG_LEVEL
    
    @classmethod
    def get_api_url(cls) -> str:
        """Get API URL from config/.env file (required, not from environment variables)"""
        api_url = cls._read_from_env_file("ZLPAY_API_URL")
        if api_url:
            return api_url
        
        raise ConfigError("ZLPAY_API_URL is required in config/.env")
    
    @classmethod
    def is_encryption_enabled(cls) -> bool:
        """Check if GM encryption is enabled - read from config/.env file (not environment variables)"""
        if cls._GM_ENABLE_ENCRYPTION is None:
            value = cls._read_from_env_file("ZLPAY_GM_ENABLE_ENCRYPTION", "true")
            cls._GM_ENABLE_ENCRYPTION = value.lower() != "false"
        return cls._GM_ENABLE_ENCRYPTION
    
    # API Key storage (for runtime user input)
    _API_KEY = None
    
    @classmethod
    def set_api_key(cls, api_key: str) -> None:
        """Set API Key from user input (runtime)"""
        cls._API_KEY = api_key
    
    @classmethod
    def get_api_key(cls, memory: Any = None, required: bool = True) -> Optional[str]:
        """
        Get API Key from multiple sources (in priority order):
        1. Memory (recall_api_key)
        2. Runtime set value (via set_api_key)
        3. Environment variables
        4. None (if not required)
        
        Args:
            memory: Memory instance to recall api_key
            required: If True and no API Key found, raises ConfigError
            
        Returns:
            API Key string or None if not required and not found
        """
        # Priority 1: Memory
        if memory:
            try:
                api_key = memory.recall_api_key()
                if api_key:
                    return api_key
            except Exception:
                pass
        
        # Priority 2: Runtime set value
        if cls._API_KEY is not None:
            return cls._API_KEY
        
        # Priority 3: Environment variables
        api_key = os.getenv("ZLPAY_API_KEY")
        if api_key:
            return api_key
        
        # Not found
        if required:
            raise ConfigError(
                "ZLPAY_API_KEY is required. "
                "Set via: 1) bind wallet, 2) --api-key argument, 3) environment variable"
            )
        return None
    
    @classmethod
    def clear_api_key(cls) -> None:
        """Clear runtime API Key"""
        cls._API_KEY = None
    
    @classmethod
    def get_sub_wallet_id(cls, memory: Any) -> str:
        """Get Wallet ID from memory"""
        if not memory:
            raise ConfigError("Memory instance required")
        
        sub_wallet_id = memory.recall_wallet()
        if not sub_wallet_id:
            raise ConfigError("sub_wallet_id not found. Please bind wallet first.")
        
        return sub_wallet_id
    
    @classmethod
    def validate(cls) -> None:
        """Validate config - fast fail (API Key checked at runtime)"""
        api_url = cls.get_api_url()
        if not (api_url.startswith("https://") or api_url.startswith("http://")):
            raise ConfigError("ZLPAY_API_URL must use HTTP or HTTPS protocol")
    
    @classmethod
    def is_sm2_enabled(cls) -> bool:
        """Check if SM2 signing is enabled"""
        value = os.getenv("ZLPAY_SM2_ENABLED", "false")
        return value.lower() == "true"
    
    @classmethod
    def get_sm2_private_key_path(cls) -> str:
        """Get SM2 private key path from environment"""
        private_key_path = os.getenv("ZLPAY_SM2_PRIVATE_KEY_PATH")
        # if not private_key_path:
            # raise ConfigError("ZLPAY_SM2_PRIVATE_KEY_PATH is required in environment variables")
        return private_key_path
    
    @classmethod
    def get_sm2_public_key_path(cls) -> str:
        """Get SM2 public key path from environment"""
        public_key_path = os.getenv("ZLPAY_SM2_PUBLIC_KEY_PATH")
        # if not public_key_path:
            # raise ConfigError("ZLPAY_SM2_PUBLIC_KEY_PATH is required in environment variables")
        return public_key_path
    
    @classmethod
    def _read_key_from_file(cls, key_path: str) -> str:
        """Read key content from file"""
        try:
            file_stat = os.stat(key_path)
            file_mode = file_stat.st_mode & 0o777
            
            if file_mode != 0o600:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Key file {key_path} has permissions {file_mode:o}, "
                    f"recommend 600 (owner read/write only)"
                )
            
            with open(key_path, "r", encoding="utf-8") as f:
                key_content = f.read().strip()
                if key_content.startswith("-----"):
                    lines = key_content.split("\n")
                    key_lines = [line for line in lines if not line.startswith("-----")]
                    key_content = "".join(key_lines)
                return key_content
        except FileNotFoundError:
            raise ConfigError(f"Key file not found: {key_path}")
        except PermissionError:
            raise ConfigError(f"Permission denied reading key file: {key_path}")
        except Exception as e:
            raise ConfigError(f"Failed to read key file: {e}")
    
    @classmethod
    def _validate_sm2_key_format(cls, key_hex: str, key_type: str = "private") -> None:
        """Validate SM2 key format"""
        if not key_hex:
            raise ConfigError(f"SM2 {key_type} key cannot be empty")
        
        try:
            int(key_hex, 16)
        except ValueError:
            raise ConfigError(f"SM2 {key_type} key must be valid hex string")
        
        if key_type == "private" and len(key_hex) != 64:
            raise ConfigError(f"SM2 private key must be 64 chars (32 bytes), got {len(key_hex)}")
        elif key_type == "public" and len(key_hex) not in [128, 130]:
            raise ConfigError(f"SM2 public key must be 128 or 130 chars, got {len(key_hex)}")
    
    @classmethod
    def get_gm_client_private_key(cls) -> str:
        """Get GM client private key from environment or file"""
        private_key = os.getenv("ZLPAY_GM_CLIENT_PRIVATE_KEY")
        if private_key:
            cls._validate_sm2_key_format(private_key, "private")
            return private_key
        
        key_path = os.getenv("ZLPAY_GM_CLIENT_PRIVATE_KEY_PATH")
        if key_path:
            private_key = cls._read_key_from_file(key_path)
            cls._validate_sm2_key_format(private_key, "private")
            return private_key
        
        return None
    
    @classmethod
    def get_gm_server_public_key(cls) -> Optional[str]:
        """Get GM server public key from environment or file (optional)"""
        public_key = os.getenv("ZLPAY_GM_SERVER_PUBLIC_KEY")
        if public_key:
            cls._validate_sm2_key_format(public_key, "public")
            return public_key

        key_path = os.getenv("ZLPAY_GM_SERVER_PUBLIC_KEY_PATH")
        if key_path:
            public_key = cls._read_key_from_file(key_path)
            cls._validate_sm2_key_format(public_key, "public")
            return public_key

        return None
    
    @classmethod
    def get_app_id(cls) -> str:
        """Get App ID from config/.env file (required, not from environment variables)"""
        app_id = cls._read_from_env_file("ZLPAY_APP_ID")
        if app_id:
            return app_id
        
        raise ConfigError("ZLPAY_APP_ID is required in config/.env")
