import requests
import hmac
import hashlib
import time

# API配置
BASE_URL = "https://apigw.125339.com.cn"  # 生产环境
APP_ID = "your_app_id"
APP_KEY = "your_app_key"
USER_ID = "user_id"

def generate_auth_header(app_id, app_key, user_id):
    """生成Authorization头（HMAC-SHA256签名）"""
    expire_time = str(int(time.time()) + 3600)  # 1小时后过期
    nonce = "random_nonce_string"  # 32-64位随机字符串
    
    # 签名内容: appId:userId:expireTime:nonce
    sign_content = f"{app_id}:{user_id}:{expire_time}:{nonce}"
    signature = hmac.new(
        app_key.encode('utf-8'),
        sign_content.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return {
        "Authorization": f"{app_id}:{user_id}:{expire_time}:{nonce}:{signature}",
        "X-Token-Type": "LongTicket",
        "Content-Type": "application/json"
    }

def get_token():
    """获取Access Token"""
    url = f"{BASE_URL}/v2/usg/acs/auth/appauth"
    headers = generate_auth_header(APP_ID, APP_KEY, USER_ID)
    
    payload = {
        "clientType": 72,  # API调用类型
        # 其他参数...
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# 调用示例
if __name__ == "__main__":
    result = get_token()
    print(result)