const crypto = require('crypto');
const axios = require('axios');

// API配置
const BASE_URL = 'https://apigw.125339.com.cn';  // 生产环境
const APP_ID = 'your_app_id';
const APP_KEY = 'your_app_key';
const USER_ID = 'user_id';

function generateAuthHeader(appId, appKey, userId) {
    const expireTime = Math.floor(Date.now() / 1000) + 3600;  // 1小时后过期
    const nonce = 'random_nonce_string';  // 32-64位随机字符串
    
    // 签名内容: appId:userId:expireTime:nonce
    const signContent = `${appId}:${userId}:${expireTime}:${nonce}`;
    const signature = crypto
        .createHmac('sha256', appKey)
        .update(signContent)
        .digest('hex');
    
    return {
        'Authorization': `${appId}:${userId}:${expireTime}:${nonce}:${signature}`,
        'X-Token-Type': 'LongTicket',
        'Content-Type': 'application/json'
    };
}

async function getToken() {
    const url = `${BASE_URL}/v2/usg/acs/auth/appauth`;
    const headers = generateAuthHeader(APP_ID, APP_KEY, USER_ID);
    
    const payload = {
        clientType: 72,  // API调用类型
        // 其他参数...
    };
    
    const response = await axios.post(url, payload, { headers });
    return response.data;
}

// 调用示例
getToken().then(console.log).catch(console.error);