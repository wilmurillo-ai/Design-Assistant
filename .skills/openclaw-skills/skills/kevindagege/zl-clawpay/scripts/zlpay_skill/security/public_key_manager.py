# -*- coding: utf-8 -*-
"""
Public key management module - fetch server public keys on demand without caching
"""

from typing import Optional, Dict, Any

from ..log_manager import get_logger

logger = get_logger(__name__)


class PublicKeyManager:
    """Public key manager - fetch server public keys on demand without local caching"""
    
    def __init__(self, http_client):
        # type: (Any) -> None
        """
        Initialize public key manager
        
        Args:
            http_client: HTTP client (for fetching public keys)
        """
        self.http_client = http_client
    
    def fetch_keys(self):
        # type: () -> Dict[str, Dict[str, Any]]
        """
        Fetch public keys from server (no caching)
        
        Returns:
            Dictionary of public keys, key is key_id, value is key info
        """
        try:
            response = self.http_client.get("/skill/public-keys")
            keys_list = response.get("keys", [])
            
            # Convert to dictionary format (key_id -> key_info)
            keys_cache = {}
            for key_info in keys_list:
                key_id = key_info.get("key_id")
                if key_id:
                    keys_cache[key_id] = key_info
            
            return keys_cache
        except Exception as e:
            raise ValueError(f"Failed to fetch public keys: {e}")
    
    def get_key(self, key_id):
        # type: (str) -> Optional[Dict[str, Any]]
        """
        Get public key for specified key_id
        
        Args:
            key_id: Key ID
            
        Returns:
            Key info or None
        """
        keys = self.fetch_keys()
        return keys.get(key_id)
    
    def get_latest_key(self):
        # type: () -> Optional[Dict[str, Any]]
        """
        Get latest public key (sorted by created_at)
        
        Returns:
            Latest key info or None
        """
        keys = self.fetch_keys()
        if not keys:
            return None
        
        # Sort by created_at, return latest
        sorted_keys = sorted(
            keys.values(),
            key=lambda k: k.get("created_at", ""),
            reverse=True
        )
        
        return sorted_keys[0] if sorted_keys else None
    
    def get_public_key_pem(self, key_id):
        # type: (str) -> Optional[str]
        """
        Get PEM format public key for specified key_id
        
        Args:
            key_id: Key ID
            
        Returns:
            PEM format public key string or None
        """
        key_info = self.get_key(key_id)
        if key_info:
            return key_info.get("public_key")
        return None
