#鉴权与接口约定

##接口约定
1. 所有接口遵循RESTful风格
2. 除获取Access Token外，所有请求需添加Header：Colipu-Token: {access_token}
3. 所有返回为JSON格式

##通用响应
|参数|必须|描述|
|success|是|true/false|
|errorcode|是|错误码，0表示成功|
|errormsg|否|错误描述|
|requestId|是|请求编号|
|result|否|返回结果数据|

##获取Access Token(3.1)
GET /api/restful/auth2/access_token
参数: timestamp(string,yyyyMMdd), username, sign(MD5(username+password+timestamp+password)小写)
返回: access_token, expires_at, refresh_token, refresh_expires_at
Token默认12小时有效。

##刷新Refresh Token(3.2)
GET /api/restful/auth2/refresh_token?refresh_token={}

##错误码
5000=系统异常, 5001=Token过期, 5002=Token解析出错, 5003=RefreshToken过期
5004=没有数据, 5005=参数验证失败
2060=订单重复, 2061=订单不存在, 2062=订单已被确认, 2063=订单已被取消
2064=没有配置支付类型, 2065=提交订单过快
