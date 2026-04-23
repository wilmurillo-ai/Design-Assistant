# PalmAI Standard (KYC Standard - 基础核身版本) API/SDK及硬件接口对接文档

刷掌服务平台
PalmAI Standard_刷掌业务平台
_API 对接文档_V1.8
文档版本：V1.8
发布日期：2026-03-13
腾讯云计算（北京）有限责任公司
文档版本 v1.8 密级：公开 i
版权声明
本文档著作权归腾讯云计算（北京）有限责任公司（以下简称“腾讯云”）单独所有，未经
腾讯云事先书面许可，任何主体不得以任何方式或理由使用本文档，包括但不限于复制、修
改、传播、公开、剽窃全部或部分本文档内容。
本文档及其所含内容均属腾讯云内部资料，并且仅供腾讯云指定的主体查看。如果您非经腾
讯云授权而获得本文档的全部或部分内容，敬请予以删除，切勿以复制、披露、传播等任何
方式使用本文档或其任何内容，亦请切勿依本文档或其任何内容而采取任何行动。
商标声明
“腾讯”、“腾讯云”及其它腾讯云服务相关的商标、标识等均为腾讯云及其关联公司各自
所有。若本文档涉及第三方主体的商标，则应依法由其权利人所有。
免责声明
本文档旨在向客户介绍本文档撰写时，腾讯云相关产品、服务的当时的整体概况，部分产品
或服务在后续可能因技术调整或项目设计等任何原因，导致其服务内容、标准等有所调整。
因此，本文档仅供参考，腾讯云不对其准确性、适用性或完整性等做任何保证。您所购买、
使用的腾讯云产品、服务的种类、内容、服务标准等，应以您和腾讯云之间签署的合同约定
为准，除非双方另有约定，否则，腾讯云对本文档内容不做任何明示或默示的承诺或保证。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
目录
文档版本 v1.8 密级：公开 ii
目录
目录 .................................................................................................................................... ii
前言 ................................................................................................................................... iii
1 文档说明 .........................................................................................................................1
2 服务端接口说明 .............................................................................................................. 4
3 设备端接口说明 ..........................................................................................................114
4 移动端接口说明 ..........................................................................................................125
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
前言
文档版本 v1.8 密级：公开 iii
前言
文档目的
本文档用于帮助用户掌握云产品的操作方法与注意事项。
目标读者
本文档主要适用于如下对象群体：
● 客户
● 交付 PM
● 交付技术架构师
● 交付工程师
● 产品交付架构师
● 研发工程师
● 运维工程师
符号约定
本文档中可能采用的符号约定如下：
符号 说明
表示是正文的附加信息，是对正文的强调和
补充。
表示有低度的潜在风险，主要是用户必读或
较关键信息，若用户忽略注意消息，可能会
因误操作而带来一定的不良后果或者无法成
功操作。
表示有中度的潜在风险，例如用户应注意的
高危操作，如果忽视这些文本，可能导致设
备损坏、数据丢失、设备性能降低或不可预
知的结果。
表示有高度潜在危险，例如用户应注意的禁
用操作，如果不能避免，会导致系统崩溃、
数据丢失且无法修复等严重问
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
前言
文档版本 v1.8 密级：公开 iv
题。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
文档说明
文档版本 v1.8 密级：公开 1
1 文档说明
版本说明
编号 修改日期 修改人 更新内容
V1.0 2025-06-03 davinliu、
celinacchen、
marxwang、
yanceyyang、
krisding
初次发布
提供产品介绍、服务
端/设备端/移动端接
口说明
V1.1 2025-07-14 davinliu、krisding 新增获取访问凭证接
口用于鉴权
新增开放平台网关
V1.1.1 2025-08-27 celinacchen 补充设备端整机系统
支持的厂商及对接开
发时的具体差异
V1.1.2 2025-08-28 marxwang 更新 alignment 参
数说明，3 点变为 6
点
v1.1.3 2025-09-01 gavinxqguo 设备端 SDK：1. 增
加设备状态
kDeviceStatusRead
y；
删除错误码：-2,-7,-9
新增错误码：
10002,-101,-200,-
201
增加错误处理流程
增加接口调用注意
v1.4 2025-10-23 hooray、haixinchen
cassliu、
整合移动端、设备端
和服务端 v1.4 内容
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
文档说明
文档版本 v1.8 密级：公开 2
yanceyyang、
krisding
形成完整的刷掌业务
平台 API 对接文档
V1.5 2025-11-11 hooray、haixinchen
cassliu、
paradixche、
yanceyyang
设备端接口更新：新
增上位机与设备间切
换模式及查询模式指
令，优化异常反馈和
界面提示，调整
CPL 环境显示，修
复了录掌模式和设置
按钮相关问题。服务
端和移动端没有更新
V1.6 2025-12-15 hooray、haixinchen
cassliu、
paradixche、
yanceyyang
服务端新增设备管
理、场景管理相关接
口；设备端无更新；
移动端实现了注册、
核验和识别三种完整
模式支持
V1.7 2026-01-05 haixinchen、
celinacchen
cassliu、
paradixche、
yanceyyang
服务端新增用户标签
管理功能；移动端内
部逻辑优化
v1.8.0 2026-03-05 stevenbwang PalmAI Standard
产品版本适配
场景管理新增
DescribeScene（查
询场景详情）接口
设备管理新增
DescribeDevice
（查询设备详情）接
口
CreateScene 接口
新增 SceneId（可
选）和
ScenarioStrategy
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
文档说明
文档版本 v1.8 密级：公开 3
产品概述
PalmAI Standard 是基于全球领先的"掌纹+掌静脉"识别技术，打造的刷掌业务平台服务。
平台不仅提供刷掌设备接入、掌库管理与授权、手掌检索比对服务等算法能力，还提供面向
会员核身、门禁通行等场景的身份核验、人员管理、设备管理、考勤管理等完整的应用能力。
PalmAI Standard 支持 5W 掌库，主要配合 M3/M4 整机使用，适用门禁/核身中小规模
封闭场景。移动端空中开掌能力为增值选配服务。
平台包含刷掌设备端软件、移动端 APP 和后台管理软件，提供 API 支持客户对接自有业务
系统。
（必填）参数
ModifyScene 接口
新增
ScenarioStrategy
（必填）参数
新增
ScenarioStrategy、
RegisterType、
PalmDirection 枚举
类型
新增 5 个业务错误
码（InvalidUserId、
RegisterTypeNotAll
owed、Member 相
关错误码）
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 4
2 服务端接口说明
版本更新记录
版本
号
发布日
期 更新内容
v1.8.0 2026-
03-06
• 场景管理新增 DescribeScene（查询场景详情）接口
• 设备管理新增 DescribeDevice（查询设备详情）接口
• CreateScene 接口新增 SceneId（可选）和 ScenarioStrategy（必
填）参数
• ModifyScene 接口新增 ScenarioStrategy（必填）参数
• 新增 ScenarioStrategy、RegisterType、PalmDirection 枚举类型
• 新增 5 个业务错误码（InvalidUserId、RegisterTypeNotAllowed、
Member 相关错误码）
v1.7.1 2026-
01-20
• CreateVerifyRule 接口 EnableWebhookRule 参数改为可选，不传
默认为 true
v1.7.0 2026-
01-05
• 新增用户标签管理功能（4 个接口：CreateUserTag、
ModifyUserTag、DeleteUserTag、DescribeUserTag）
• 用户管理接口支持标签绑定和部分失败机制（CreateUser、
ModifyUser 支持 UserTagIdList 和 PartialFailure 参数）
• 新增部分失败机制完整文档说明
• 统一接口命名规范（接口表格使用 Action 名称）
• 新增 14 个业务错误码（用户标签、分页、会话、租户相关）
• 优化 4 个错误码格式，移除 39 个已废弃错误码
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 5
API 概览
PalmSaaS API 遵循腾讯云 API3.0 规范，提供用户、用户手掌、设备、场景、核验记录、
核验规则、扫码录掌等管理能力。
功能分类
● 鉴权管理相关接口
● 用户管理相关接口
● 用户标签管理相关接口
● 用户手掌管理相关接口
● 设备管理相关接口
● 场景管理相关接口
● 核验记录相关接口
● 核验规则相关接口
● 扫码录掌相关接口
鉴权管理相关接口
用户管理相关接口
用户标签管理相关接口
接口名称 接口功能 频率限制(次/秒/AppId)
CreateAccessToken 获取访问凭证 20
DescribePalmLicense 查询授权信息 20
接口名称 接口功能 频率限制(次/秒/AppId)
CreateUser 创建用户 20
ModifyUser 修改用户 20
DeleteUser 删除用户 20
DescribeUser 查询用户 20
接口名称 接口功能 频率限制(次/秒/AppId)
CreateUserTag 创建用户标签 20
ModifyUserTag 修改用户标签 20
DeleteUserTag 删除用户标签 20
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 6
用户手掌管理相关接口
设备管理相关接口
场景管理相关接口
核验记录相关接口
核验规则相关接口
DescribeUserTag 查询用户标签 20
接口名称 接口功能 频率限制(次/秒/AppId)
DeleteUserPalm 删除用户手掌信息 20
DescribeUserPalm 查询用户手掌信息 20
接口名称 接口功能 频率限制(次/秒/AppId)
CreateDevice 创建设备 20
ModifyDevice 修改设备 20
DeleteDevice 删除设备 20
DescribeDevice 查询设备详情 20
接口名称 接口功能 频率限制(次/秒/AppId)
CreateScene 创建场景 20
ModifyScene 修改场景 20
DeleteScene 删除场景 20
DescribeScene 查询场景详情 20
CreateSceneGroup 创建场景组 20
ModifySceneGroup 修改场景组 20
DeleteSceneGroup 删除场景组 20
接口名称 接口功能 频率限制(次/秒/AppId)
CreateVerificationRecord 创建核验记录 20
DescribeVerificationRecordList 查询核验记录列表 20
DescribeVerificationRecord 查询核验记录（推送专用） 20
接口名称 接口功能 频率限制(次/秒/AppId)
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 7
扫码录掌相关接口
CreateVerifyRule 创建核验规则 20
ModifyVerifyRule 修改核验规则 20
DeleteVerifyRule 删除核验规则 20
DescribeVerifyRule 查询核验规则 20
CheckAccessPermission 校验访问权限（回调专用） 20
接口名称 接口功能 频率限制(次/秒/AppId)
NotifyQrCodeScanEvent 用户扫码事件通知 20
BindQrCodeScanPalm 扫码绑定掌纹 20
DescribeQrCodeScanUser 查询扫码录掌用户信息 20
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 8
---
调用方式
请求结构
Palm API 的请求结构如下：
1. 服务地址
API 支持就近地域接入，推荐使用如下域名：
● 默认接入域名（推荐）：open.intl.palm.tencent.com（仅为示例，实际接入域名请以分
配为准，支持私有化部署场景）
● 指定地域接入（如有多地域部署，可扩展）：如 open.intl.palm.tencent.com（仅为示
例，实际接入域名请以分配为准）
注意：域名是 API 的接入点，并不代表产品或接口实际提供服务的地域。后续如有多地域
部署，将在文档中补充。
2. 通信协议
Palm API 所有接口均通过 HTTPS 进行通信，提供高安全性的通信通道。
3. 请求方法
● 推荐使用 POST 方法。
● 支持的 Content-Type 类型：
● application/json（推荐，必须使用签名方法 v3/TC3-HMAC-SHA256）
● POST 方法使用签名方法 v3 时，支持最大 10MB 的请求包。
4. 字符编码
所有请求和响应均使用 UTF-8 编码。
参考：腾讯云 API 请求结构官方文档（当前仅有中文版，需自行翻译）
公共参数
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 9
公共参数用于标识用户身份、接口签名和请求上下文。使用签名方法 v3（TC3-HMAC-
SHA256）时，所有公共参数需放在 HTTP Header 请求头部。
参数名称 类型 必
选 描述
X-TC-Action String 是 操作的接口名称。例如：CreateUser。
X-TC-
Timestamp
Integer 是 当前 UNIX 时间戳，单位为秒。例如：1704067200。与服
务器时间相差超过 5 分钟会引起签名过期错误。
X-TC-Version String 是 API 版本号，目前固定为：2025-07-15。
Authorization String 是 签名信息，格式：TC3-HMAC-SHA256
Credential=AKIDxxx/Date/service/tc3_request,
SignedHeaders=content-type;host;x-tc-action,
Signature=xxx。详见签名方法章节。
X-TC-Nonce String 是 随机字符串，一般用于防重放使用，建议每次请求都生成新
的唯一的随机字符串。
Content-Type String 是 请求内容类型，推荐 application/json; charset=utf-8。
Host String 是 服务地址，固定为 open.intl.palm.tencent.com。
X-Palm-
AppId
String 是 应用 ID，申请安全凭证时获得。</br>客户需向腾讯申请
AppId、SecretId 和 SecretKey。</br>请妥善保管以上信
息，并根据业务需要在接口请求中传递
X-Palm-
Openapi-
Token
String 是 临时安全凭证 Token。调用腾讯接口前，需首先通过【获取
访问凭证】接口（Action: CreateAccessToken）获取访问
凭证。请注意，访问凭证具有时效性，过期后需重新申请。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 10
请求头示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: CreateUser
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
参考：腾讯云 API 公共参数官方文档（当前仅有中文版，需自行翻译）
签名方法
Palm API 采用腾讯云 API3.0 签名方法 v3（TC3-HMAC-SHA256）进行身份鉴权。
注意：
签名方法由刷掌算法平台提供。本文档仅作简要说明，详细内容请参阅刷掌算法平台开放
API 文档。
为什么要进行签名
● 验证请求者身份，确保请求来自持有有效密钥的用户。
● 保护传输中的数据，防止请求被篡改。
申请安全凭证
● 客户需向腾讯申请 AppId、SecretId 和 SecretKey。
● SecretId 用于标识身份，SecretKey 用于签名和加密。
● 请妥善保管密钥，避免泄露。
签名过程（v3）
1. 拼接规范请求串（CanonicalRequest）
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 11
CanonicalRequest =
HTTPRequestMethod + '\n' +
CanonicalURI + '\n' +
CanonicalQueryString + '\n' +
CanonicalHeaders + '\n' +
SignedHeaders + '\n' +
HashedRequestPayload
● HTTPRequestMethod：如 POST
● CanonicalURI：固定为 /
● CanonicalQueryString：GET 请求时为 URL 查询串，POST 通常为空
● CanonicalHeaders：如 content-type:application/json; charset=utf-
8\nhost:open.intl.palm.tencent.com\nx-tc-action:createuser\n
● SignedHeaders：如 "content-type;host;x-palm-appid;x-tc-nonce;x-tc-timestamp"
● HashedRequestPayload：请求体的 SHA256 哈希值（小写十六进制字符串）
2. 拼接待签名字符串（StringToSign）
StringToSign =
Algorithm + '\n' +
RequestTimestamp + '\n' +
CredentialScope + '\n' +
HashedCanonicalRequest
● Algorithm：TC3-HMAC-SHA256
● RequestTimestamp：如 1704067200
● CredentialScope：如 2025-07-15/palm/tc3_request
● HashedCanonicalRequest：上一步结果的 SHA256 哈希值
3. 计算签名（Signature）
依次对 SecretKey、日期、服务名、tc3_request 进行 HMAC-SHA256 运算，最后对
StringToSign 进行 HMAC-SHA256 运算，得到签名。
4. 拼接 Authorization
Authorization: TC3-HMAC-SHA256 Credential=SecretId/CredentialScope,
SignedHeaders=SignedHeaders, Signature=Signature
签名示例
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 12
curl -X POST https://open.intl.palm.tencent.com/CreateUser \
-H "Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx"
\
-H "Content-Type: application/json; charset=utf-8" \
-H "Host: open.intl.palm.tencent.com" \
-H "X-TC-Action: CreateUser" \
-H "X-TC-Timestamp: 1704067200" \
-H "X-TC-Version: 2025-07-15" \
-H "X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1" \
-H "X-Palm-AppId: 223" \
-H "X-Palm-Openapi-Token: **************************************" \
-d '{
"UserId": "user123456",
"UserName": "张三"
}'
签名失败常见错误码
错误码 错误描述
AuthFailure.SignatureExpire 签名过期。Timestamp 与服务器接收到请求的时间相差
不得超过五分钟。
AuthFailure.SecretIdNotFound 密钥不存在。请到控制台查看密钥是否被禁用，是否少复
制了字符或者多了字符。
AuthFailure.SignatureFailure 签名错误。可能是签名计算错误，或者签名与实际发送的
内容不相符合，也有可能是密钥 SecretKey 错误导致
的。
AuthFailure.TokenFailure 临时凭证 Token 错误。
AuthFailure.InvalidSecretId 密钥非法（不是云 API 密钥类型）。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 13
详细签名过程和多语言示例请参考：腾讯云 API 签名方法 v3 官方文档（当前仅有中文版，
需自行翻译）
返回结果
云 API 3.0 接口默认返回 JSON 数据，返回非 JSON 格式的接口会在文档中做出说明。
返回 JSON 数据时最大限制为 50
MB，如果返回的数据超过最大限制，请求会失败并返回内部错误。建议根据接口文档中的过
滤或分页功能，控制返回数据不要过大。
注意：只要请求被服务端正常处理，响应的 HTTP 状态码均为 200。例如签名失败等错误，
HTTP 状态码也是 200，具体错误信息在返回体中体现。
正确返回结果
以用户查询接口为例，调用成功时返回如下：
{
"Response": {
"UserId": "user123456",
"UserName": "张三",
"PhoneNo": "(+86)13800138000",
"PhysicalCardNo": "CARD001",
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
● Response 及其内部的 RequestId 是固定字段，无论请求成功与否都会返回。
● RequestId 用于唯一标识一次 API 请求，便于问题排查。
● 其余字段为具体接口定义的业务字段。
错误返回结果
调用失败时返回如下：
{
"Response": {
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 14
"Error": {
"Code": "AuthFailure.SignatureFailure",
"Message": "The provided credentials could not be validated. Please check
your signature is correct."
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
● Error 字段出现代表请求失败，包含 Code（错误码）和 Message（错误信息）。
● RequestId 依然会返回，用于问题排查。
● 错误码请参考接口文档"公共错误码"章节。
公共错误码
返回结果中如果存在 Error 字段，则表示调用 API 接口失败。Error.Code 字段为错误码，
所有业务都可能出现的错误码为公共错误码。完整错误码列表请参考本产品"API
文档"目录下的"错误码"页面。
参考：腾讯云 API 返回结果官方文档（当前仅有中文版，需自行翻译）
参数类型
Palm API 3.0 输入参数和输出参数支持如下数据类型：
类型 说明 示例
String 字符串 "user123456"
Integer 整型，上限为无符号 64 位整数。不同语
言建议用最大整型定义。
123456
Boolean 布尔型，true/false true
Float 浮点型 3.14
Double 双精度浮点型 3.1415926535
Date 字符串，日期格式 "2022-01-01"
Timestamp 字符串，时间格式 "2022-01-01 00:00:00"
Timestamp
RFC3339
字符串，时间格式，RFC3339 标准时间格
式，建议用标准库解析
"2022-01-
01T00:00:20.021Z"
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 15
参考：腾讯云 API 参数类型官方文档（当前仅有中文版，需自行翻译）
部分失败
部分失败（Partial Failure）是一种特殊的处理机制，允许在批量操作中即使部分操作失败，
成功的操作仍然会被执行。这种机制可以提高批量操作的容错性和效率。
什么是部分失败
在批量操作（如批量绑定用户标签等）中，如果不使用部分失败机制：
● 任何一项操作失败，整个请求都会失败
● 所有操作都会回滚，即使其中大部分操作是有效的
启用部分失败机制后：
● 有效的操作会成功执行
● 失败的操作会在响应中返回详细的错误信息
● 可以根据返回的错误信息重试失败的操作
如何使用部分失败
支持部分失败的接口会提供 PartialFailure 参数：
请求参数：
响应字段：
当启用部分失败且存在失败项时，响应中会包含 PartialFailureError 字段，详细说明失败的
原因：
Binary 二进制内容，需以特定协议请求和解析 -
参数名称 必
选 类型 描述
PartialFailure 否 Boolean 是否允许部分失败。设置为 true 时启用部分失败机制，
默认为 false。
参数名称 类型 描述
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 16
PartialFailureError Object 部分失败错误信息，包含失败项的详细信息。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 17
示例场景
场景一：创建用户并批量绑定标签
请求示例：
{
"UserId": "user001",
"UserName": "张三",
"UserTagIdList": ["tag001", "tag002", "tag003"],
"PartialFailure": true
}
成功响应（无失败项）：
{
"Response": {
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
部分失败响应（存在失败项）：
{
"Response": {
"PartialFailureError": {
"NotExistUserTagIdList": ["tag003"]
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
在上述示例中：
● 用户 user001 创建成功
● tag001 和 tag002 绑定成功
● tag003 不存在，绑定失败
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 18
重试说明:如需重试,修正 tag003 后必须传入完整的标签列表 ["tag001", "tag002",
"tag003"],而非仅传入 ["tag003"],因为用户标签绑定是覆盖式操作。
最佳实践
1. 批量操作时启用部分失败
● 在批量创建、修改等操作中，建议设置 PartialFailure=true
● 这样可以确保有效数据被处理，无效数据被记录
2. 检查响应中的 PartialFailureError 字段
● 即使正确返回结果，也要检查 PartialFailureError 字段
● PartialFailureError 存在表示有部分操作失败，需要根据返回信息进行处理
3. 记录并重试失败项
● 记录 PartialFailureError 中返回的失败项信息
● 修正失败原因后重新发起请求
● 注意:对于批量绑定用户标签等覆盖式操作,重试时必须传入完整的标签列表(包括之前成
功的项),而非仅重试失败的项
4. 幂等性设计
● 确保操作具有幂等性，以便安全地重试失败的操作
● 批量绑定操作必须使用完整数据重试(覆盖式更新)
支持部分失败的接口
以下接口支持部分失败机制：
● 创建用户：支持批量绑定用户标签时的部分失败
● 修改用户：支持批量绑定用户标签时的部分失败
注意：并非所有接口都支持部分失败机制。具体支持情况请参考各接口的参数说明。
---
鉴权管理相关接口
获取访问凭证
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 19
接口说明：用于获取访问凭证（AccessToken），如下调用方式仅限普通服务端调用刷掌业
务平台开放接口的场景。
注意：
本接口仅需签名（Authorization），无需传递 X-Palm-OpenAPI-Token。
在接入刷掌业务平台服务前，客户需向腾讯申请 AppId、SecretId 和 SecretKey。请妥
善保管以上信息，并根据业务需要在接口请求中传递。
该接口由刷掌算法平台提供。本文档仅作简要说明，详细说明请参阅刷掌算法平台开放
API 文档。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必
选 类型 描述
AppId 是 int 系统分配的产品 ID
SecretId 是 string 客户的密钥 ID
SecretKeyHash 是 string 客户的密钥 hash，计算规则为：
hex.EncodeToString(sha256.Sum256(secretKey))
GrantType 是 string 授权类型。<br>调用刷掌业务平台开放接口时，**必须使用
client_credential**。<br><br>取值枚举：<br>-
client_credential_user：适用于第三方平台接入空中开掌
SDK 场景，即：<br>a. 移动端使用 SDK 发起注册或获取
活体视频上传地址流程；<br>b. 第三方服务端需根据指定
用户申请访问凭证，供 SDK 使用；<br>c. 此时必须同时
传入 UserId 字段。<br><br>- client_credential：适用于
普通服务端调用开放接口场景，即：<br>a. 此类型下不绑
定具体用户，仅使用应用级密钥获取访问凭证；<br>b.
UserId 字段无需传入。
UserId 否 string 用户的身份 id，grant_type 为"client_credential_user"
时，必须传递 UserId 字段
参数名称 类型 描述
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 20
AccessToken string 访问凭证，后续可以根据该凭证访问其他接口
ExpiresIn int AccessToken 的有效期，单位为秒，过期后 token 无效
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 21
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: CreateAccessToken
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"AppId": 223,
"SecretId": "this is secretId",
"SecretKeyHash": "this is secretKey hash",
"GrantType": "client_credential"
}
输出示例
{
"Response": {
"AccessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
"ExpiresIn": 7200,
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
查询授权信息
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 22
接口说明：用于查询服务端授权信息，包括掌库容量、使用量及过期时间。
注意：
该接口由刷掌算法平台提供。本文档仅作简要说明，详细说明请参阅刷掌算法平台开放
API 文档。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：DescribePalmLicense。
Version 是 String 公共参数，本接口取值：2025-07-15。
AppId 是 int 系统分配的产品 ID
参数名称 类型 描述
PalmCapacity int 掌库容量上限，表示当前授权允许注册的最大掌纹数量
PalmUsage int 当前掌库使用量，表示已注册的掌纹数量
ExpireTime int License 过期时间，UTC 时间戳，单位：秒。过期后将无法继续
使用服务
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 23
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: DescribePalmLicense
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"AppId": 223
}
输出示例
{
"Response": {
"PalmCapacity": 50000,
"PalmUsage": 5680,
"ExpireTime": 1767225600,
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "InvalidParameter",
"Message": "参数错误"
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 24
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
用户管理相关接口
创建用户
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于创建新用户，支持设置用户基本信息。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必
选 类型 描述
Action 是 String 公共参数，本接口取值：CreateUser。
Version 是 String 公共参数，本接口取值：2025-07-15。
UserId 是 String 用户唯一标识。
UserName 是 String 用户名称。
PhoneNo 否 String 手机号（带区号），如“(+86)13530612342”，如
未填写地区号，则默认“(+86)”。
PhysicalCardNo 否 String 实体卡号，数字英文组合。
UserTagIdList 否 Array of
String
用户标签 ID 列表。
PartialFailure 否 Boolean 是否允许部分失败。
参数名称 类型 描述
PartialFailureEr CreateUserResponsePartialFailur 部分失败结果，参见
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 25
ror eError CreateUserResponsePartialFailur
eError 结构。
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 26
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: CreateUser
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"UserId": "user123456",
"UserName": "张三",
"PhoneNo": "(+86)13530612342",
"PhysicalCardNo": "CARD001",
"UserTagIdList": ["tag001", "tag002"],
"PartialFailure": true
}
输出示例
{
"Response": {
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
部分失败输出示例
{
"Response": {
"PartialFailureError": {
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 27
"NotExistUserTagIdList": [
"tag003"
]
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "InvalidParameterValue.UserNameEmpty",
"Message": "用户名称为空"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
修改用户
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于修改用户信息，支持更新用户的基本信息。
注意：
此接口为全量更新，需要传入用户的所有字段信息。
未传入的可选字段将被清空，建议先调用 DescribeUser 获取当前用户信息后再修改。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 28
3. 输出参数
参数名称 必
选 类型 描述
Action 是 String 公共参数，本接口取值：ModifyUser。
Version 是 String 公共参数，本接口取值：2025-07-15。
UserId 是 String 用户唯一标识。
UserName 是 String 用户名称。
PhoneNo 否 String 手机号（带区号），如“(+86)13530612342”，如
未填写地区号，则默认“(+86)”。
PhysicalCardNo 否 String 实体卡号，数字英文组合。
UserTagIdList 否 Array of
String
用户标签 ID 列表。
PartialFailure 否 Boolean 是否允许部分失败。
参数名称 类型 描述
PartialFailureEr
ror
ModifyUserResponsePartialFailur
eError
部分失败结果，参见
ModifyUserResponsePartialFailur
eError 结构。
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 29
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: ModifyUser
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"UserId": "user001",
"UserName": "张三",
"PhoneNo": "(+86)13800138000",
"UserTagIdList": ["tag001", "tag002"],
"PartialFailure": true
}
输出示例
{
"Response": {
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
部分失败输出示例
{
"Response": {
"PartialFailureError": {
"NotExistUserTagIdList": [
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 30
"tag003"
]
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "FailedOperation.UserNotExist",
"Message": "用户不存在或已被删除。"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
删除用户
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于删除指定用户，删除后用户数据将无法恢复。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：DeleteUser。
Version 是 String 公共参数，本接口取值：2025-07-15。
UserId 是 String 用户唯一标识。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 31
3. 输出参数
参数名称 类型 描述
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 32
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: DeleteUser
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"UserId": "user001"
}
输出示例
{
"Response": {
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "FailedOperation.UserNotExist",
"Message": "用户不存在或已被删除。"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 33
}
---
查询用户
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于查询指定用户的详细信息，包括基本信息和录掌状态。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：DescribeUser。
Version 是 String 公共参数，本接口取值：2025-07-15。
UserId 是 String 用户唯一标识。
参数名称 类型 描述
UserId String 用户唯一标识。
UserName String 用户名称。
PhoneNo String 手机号（带区号），如“(+86)13530612342”，如未填
写地区号，则默认“(+86)”。
PhysicalCardNo String 实体卡号，数字英文组合。
UserTagList Array of
Object
用户标签列表，参见 UserTag 结构。
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 34
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: DescribeUser
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"UserId": "user001"
}
输出示例
{
"Response": {
"UserId": "user001",
"UserName": "张三",
"PhoneNo": "(+86)13800138000",
"PhysicalCardNo": "CARD2024A001",
"UserTagList": [
{
"UserTagId": "tag001",
"UserTagName": "研发中心"
},
{
"UserTagId": "tag002",
"UserTagName": "产品中心"
}
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 35
],
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "FailedOperation.UserNotExist",
"Message": "未找到该用户信息。"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
用户标签管理相关接口
创建用户标签
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于创建新的用户标签。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：CreateUserTag。
Version 是 String 公共参数，本接口取值：2025-07-15。
UserTagName 是 String 用户标签名称。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 36
3. 输出参数
参数名称 类型 描述
UserTagId String 用户标签唯一标识。
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 37
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: CreateUserTag
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"UserTagName": "研发中心"
}
输出示例
{
"Response": {
"UserTagId": "tag001",
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "InvalidParameterValue.UserTagNameEmpty",
"Message": "用户标签名称为空"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 38
}
}
---
修改用户标签
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于修改用户标签信息。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：ModifyUserTag。
Version 是 String 公共参数，本接口取值：2025-07-15。
UserTagId 是 String 用户标签唯一标识。
UserTagName 是 String 用户标签名称。
参数名称 类型 描述
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 39
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: ModifyUserTag
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"UserTagId": "tag001",
"UserTagName": "产品中心"
}
输出示例
{
"Response": {
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "FailedOperation.UserTagNotExist",
"Message": "用户标签不存在或已被删除。"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 40
}
}
---
删除用户标签
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于删除指定用户标签，删除后用户标签数据将无法恢复。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：DeleteUserTag。
Version 是 String 公共参数，本接口取值：2025-07-15。
UserTagId 是 String 用户标签唯一标识。
参数名称 类型 描述
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 41
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: DeleteUserTag
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"UserTagId": "tag001"
}
输出示例
{
"Response": {
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "FailedOperation.UserTagNotExist",
"Message": "用户标签不存在或已被删除。"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 42
}
---
查询用户标签
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于查询指定用户标签的详细信息。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：DescribeUserTag。
Version 是 String 公共参数，本接口取值：2025-07-15。
UserTagId 是 String 用户标签唯一标识。
参数名称 类型 描述
UserTagId String 用户标签唯一标识。
UserTagName String 用户标签名称。
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 43
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: DescribeUserTag
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"UserTagId": "tag001"
}
输出示例
{
"Response": {
"UserTagId": "tag001",
"UserTagName": "研发中心",
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "FailedOperation.UserTagNotExist",
"Message": "未找到该用户标签信息。"
},
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 44
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
用户手掌管理相关接口
删除用户手掌信息
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于删除指定用户的手掌信息，删除后需要重新录掌。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：DeleteUserPalm。
Version 是 String 公共参数，本接口取值：2025-07-15。
UserId 是 String 用户唯一标识。
参数名称 类型 描述
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 45
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: DeleteUserPalm
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"UserId": "user001"
}
输出示例
{
"Response": {
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "FailedOperation.UserNotExist",
"Message": "用户手掌信息不存在或已被删除。"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 46
}
---
查询用户手掌信息
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于查询指定用户的掌纹信息及录掌状态。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：DescribeUserPalm。
Version 是 String 公共参数，本接口取值：2025-07-15。
UserId 是 String 用户唯一标识。
参数名称 类型 描述
UserId String 用户唯一标识。
PalmState PalmState 录掌状态。
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 47
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: DescribeUserPalm
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"UserId": "user001"
}
输出示例
{
"Response": {
"UserId": "user001",
"PalmState": "registered",
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "FailedOperation.UserNotExist",
"Message": "未找到该用户手掌信息。"
},
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 48
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
设备管理相关接口
创建设备
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于创建新设备，支持设置设备基本信息。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：CreateDevice。
Version 是 String 公共参数，本接口取值：2025-07-15。
DeviceSn 是 String 设备序列号。
DeviceName 是 String 设备名称。
参数名称 类型 描述
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 49
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: CreateDevice
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"DeviceSn": "device001",
"DeviceName": "深圳南山门禁 1 号"
}
输出示例
{
"Response": {
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "InvalidParameterValue.DeviceSnEmpty",
"Message": "设备 SN 为空"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 50
}
}
---
修改设备
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于修改设备信息，支持更新设备的基本信息。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：ModifyDevice。
Version 是 String 公共参数，本接口取值：2025-07-15。
DeviceSn 是 String 设备序列号。
DeviceName 是 String 设备名称。
参数名称 类型 描述
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 51
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: ModifyDevice
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"DeviceSn": "device001",
"DeviceName": "深圳南山门禁 1 号（已更新）"
}
输出示例
{
"Response": {
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "FailedOperation.DeviceNotExist",
"Message": "设备不存在或已被删除。"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 52
}
}
---
删除设备
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于删除指定设备，删除后设备数据将无法恢复。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：DeleteDevice。
Version 是 String 公共参数，本接口取值：2025-07-15。
DeviceSn 是 String 设备序列号。
参数名称 类型 描述
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 53
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: DeleteDevice
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"DeviceSn": "device001"
}
输出示例
{
"Response": {
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "FailedOperation.DeviceNotExist",
"Message": "设备不存在或已被删除。"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 54
}
---
查询设备详情
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于查询指定设备的详细信息。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：DescribeDevice。
Version 是 String 公共参数，本接口取值：2025-07-15。
DeviceSn 是 String 设备序列号。
参数名称 类型 描述
DeviceSn String 设备 SN。
DeviceName String 关联设备名。
DeviceType String 设备类型。
ModuleType String 模组类型。
ModuleExpireTime Timestamp 模组有效期，RFC3339 字符串格式。
AppVersion String 应用版本。
ModuleVersion String 模组版本。
SystemVersion String 系统版本。
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 55
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: DescribeDevice
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"DeviceSn": "device001"
}
输出示例
{
"Response": {
"DeviceSn": "device001",
"DeviceName": "深圳南山门禁设备",
"DeviceType": "palm_device_v1",
"ModuleType": "palm_module_v1",
"ModuleExpireTime": "2027-07-03T09:30:15.500Z",
"AppVersion": "1.0.0",
"ModuleVersion": "2.0.0",
"SystemVersion": "3.0.0",
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 56
{
"Response": {
"Error": {
"Code": "FailedOperation.DeviceNotExist",
"Message": "设备不存在或已被删除。"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
场景管理相关接口
创建场景
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于创建新场景，支持设置场景基本信息、绑定设备和核验规则。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：CreateScene。
Version 是 String 公共参数，本接口取值：2025-07-15。
SceneName 是 String 场景名称。
SceneGroupId 是 String 场景组 Id。
DeviceSn 否 String 设备序列号。
VerifyRuleIdList 否 Array 核验规则 Id 列表。
SceneId 否 String 场景 ID（可选，不传则自动生成）。
ScenarioStrategy 是 ScenarioStrategy 场景策略，见 ScenarioStrategy 枚举。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 57
3. 输出参数
参数名称 类型 描述
SceneId String 场景唯一标识。
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 58
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: CreateScene
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"SceneName": "深圳南山门禁 1 号",
"SceneGroupId": "scenegroup001",
"DeviceSn": "device001",
"VerifyRuleIdList": ["verifyrule001", "verifyrule002"],
"ScenarioStrategy": "AccessOnDeviceRecognition50k"
}
输出示例
{
"Response": {
"SceneId": "scene001",
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 59
"Code": "InvalidParameterValue.SceneNameEmpty",
"Message": "场景名称不能为空。"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
修改场景
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于修改场景信息，支持更新场景的基本信息、绑定设备和核验规则。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：ModifyScene。
Version 是 String 公共参数，本接口取值：2025-07-15。
SceneId 是 String 场景 Id。
SceneName 是 String 场景名称。
DeviceSn 否 String 设备序列号。
VerifyRuleIdList 否 Array 核验规则 Id 列表。
ScenarioStrategy 是 ScenarioStrategy 场景策略，见 ScenarioStrategy 枚举。
参数名称 类型 描述
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 60
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: ModifyScene
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"SceneId": "scene001",
"SceneName": "深圳南山门禁 1 号（已更新）",
"DeviceSn": "device002",
"VerifyRuleIdList": ["verifyrule001"],
"ScenarioStrategy": "AccessOnDeviceRecognition50k"
}
输出示例
{
"Response": {
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "FailedOperation.SceneNotExist",
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 61
"Message": "场景不存在或已被删除。"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
删除场景
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于删除指定场景，删除后场景数据将无法恢复。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：DeleteScene。
Version 是 String 公共参数，本接口取值：2025-07-15。
SceneId 是 String 场景 Id。
参数名称 类型 描述
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 62
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: DeleteScene
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"SceneId": "scene001"
}
输出示例
{
"Response": {
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "FailedOperation.SceneNotExist",
"Message": "场景不存在或已被删除。"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 63
}
---
查询场景详情
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于查询指定场景的详细信息。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：DescribeScene。
Version 是 String 公共参数，本接口取值：2025-07-15。
SceneId 是 String 场景 Id。
参数名称 类型 描述
SceneId String 场景 ID。
SceneName String 场景名称。
SceneGroupId String 场景组 ID。
SceneGroupName String 场景组名称。
DeviceSn String 关联设备 SN。
DeviceName String 关联设备名。
ScenarioStrategy ScenarioStrategy 场景策略，见 ScenarioStrategy 枚举。
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 64
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: DescribeScene
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"SceneId": "scene001"
}
输出示例
{
"Response": {
"SceneId": "scene001",
"SceneName": "深圳南山门禁 1 号",
"SceneGroupId": "scenegroup001",
"SceneGroupName": "深圳南山区域",
"DeviceSn": "device001",
"DeviceName": "深圳南山门禁设备",
"ScenarioStrategy": "AccessOnDeviceRecognition50k",
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 65
"Response": {
"Error": {
"Code": "FailedOperation.SceneNotExist",
"Message": "场景不存在或已被删除。"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
创建场景组
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于创建新场景组，支持设置场景组基本信息和父场景组。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：CreateSceneGroup。
Version 是 String 公共参数，本接口取值：2025-07-15。
SceneGroupName 是 String 场景组名称。
ParentSceneGroupId 是 String 父场景组 Id。
参数名称 类型 描述
SceneGroupId String 场景组唯一标识。
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 66
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: CreateSceneGroup
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"SceneGroupName": "深圳南山区域",
"ParentSceneGroupId": "scene_group_root"
}
输出示例
{
"Response": {
"SceneGroupId": "scenegroup001",
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "InvalidParameterValue.SceneGroupNameEmpty",
"Message": "场景组名称不能为空。"
},
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 67
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
修改场景组
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于修改场景组信息，支持更新场景组的基本信息。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：ModifySceneGroup。
Version 是 String 公共参数，本接口取值：2025-07-15。
SceneGroupId 是 String 场景组 Id。
SceneGroupName 是 String 场景组名称。
参数名称 类型 描述
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 68
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: ModifySceneGroup
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"SceneGroupId": "scenegroup001",
"SceneGroupName": "深圳南山区域（已更新）"
}
输出示例
{
"Response": {
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "FailedOperation.SceneGroupNotExist",
"Message": "场景组不存在或已被删除。"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 69
}
}
---
删除场景组
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于删除指定场景组，删除后场景组数据将无法恢复。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：DeleteSceneGroup。
Version 是 String 公共参数，本接口取值：2025-07-15。
SceneGroupId 是 String 场景组 Id。
参数名称 类型 描述
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 70
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: DeleteSceneGroup
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"SceneGroupId": "scenegroup001"
}
输出示例
{
"Response": {
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "FailedOperation.SceneGroupNotExist",
"Message": "场景组不存在或已被删除。"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 71
}
---
核验记录相关接口
创建核验记录
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于创建核验记录。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必
选 类型 描述
Action 是 String 公共参数，本接口取值：
CreateVerificationRecord。
Version 是 String 公共参数，本接口取值：2025-07-15。
UserId 是 String 用户 ID。
VerificationTime 是 String 核验时间，RFC3339 格式。
VerificationMedium 是 VerificationMedium 核验介质。
DeviceSn 是 String 设备 SN。
VerifierId 否 String 核验人 ID。
VerifierName 否 String 核验人名。
参数名称 类型 描述
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 72
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: CreateVerificationRecord
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"UserId": "user001",
"VerificationTime": "2024-07-15T09:30:15.500Z",
"VerificationMedium": "palm",
"DeviceSn": "device001",
"VerifierId": "verifier001",
"VerifierName": "李四"
}
输出示例
{
"Response": {
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 73
"Code": "InvalidParameterValue.UserIdEmpty",
"Message": "用户 ID 不能为空。"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
查询核验记录列表
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于查询核验记录列表，支持多条件过滤、分页。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
参数名称 必
选 类型 描述
Action 是 String 公共参数，本接口取值：
DescribeVerificationRecordList。
Version 是 String 公共参数，本接口取值：2025-07-15。
UserId 否 String 用户 ID。
UserName 否 String 用户名。
VerificationMedium 否 VerificationMedium 核验介质。
DeviceSn 否 String 设备 SN。
SceneId 否 String 场景 ID。
StartTime 否 String 核验开始时间，RFC3339 格式。
EndTime 否 String 核验结束时间，RFC3339 格式。
Offset 否 Integer 偏移量，默认 0。
Limit 否 Integer 返回数量，默认 20，最大 100。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 74
3. 输出参数
VerificationRecord 结构说明：
参数名称 类型 描述
TotalCount Integer 符合条件的核验记录数量。
VerificationRecordList Array 核验记录列表，见下表。
RequestId String 唯一请求 ID，每次请求都会返回。
字段名 类型 描述
UserId String 用户 ID
UserName String 用户名
VerificationTime String 核验时间，RFC3339 格式
VerificationMedium VerificationMedium 核验介质
DeviceSn String 设备 SN
SceneId String 场景 ID
SceneName String 场景名称
VerifierId String 核验人 ID
VerifierName String 核验人名
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 75
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: DescribeVerificationRecordList
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"UserId": "user001",
"UserName": "张三",
"VerificationMedium": "palm",
"DeviceSn": "device001",
"StartTime": "2024-06-01T00:00:00+08:00",
"EndTime": "2024-06-30T23:59:59+08:00",
"Offset": 0,
"Limit": 10
}
输出示例
{
"Response": {
"TotalCount": 2,
"VerificationRecordList": [
{
"UserId": "user001",
"UserName": "张三",
"VerificationTime": "2024-06-10T09:15:00+08:00",
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 76
"VerificationMedium": "palm",
"DeviceSn": "device001",
"SceneId": "scene001",
"SceneName": "深圳南山门禁 1 号",
"VerifierId": "verifier001",
"VerifierName": "李四"
},
{
"UserId": "user001",
"UserName": "张三",
"VerificationTime": "2024-06-11T18:30:00+08:00",
"VerificationMedium": "palm",
"DeviceSn": "device002",
"SceneId": "scene002",
"SceneName": "深圳南山门禁 2 号",
"VerifierId": "verifier002",
"VerifierName": "王五"
}
],
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
错误输出示例
{
"Response": {
"Error": {
"Code": "InvalidParameterValue.FiltersLimitExceed",
"Message": "过滤器个数超过限制"
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 77
查询核验记录推送专用
1. 接口描述
接口推送域名：由客户提供给平台，平台主动推送
接口说明：用于接收开放平台推送的核验记录信息。该接口只支持推送，不支持主动拉取。
推送内容即为核验记录详情（见下表），客户收到推送后返回 HTTP 200 OK 即可。
2. 推送内容（参数结构）
参数名称 类型 描述
UserId String 用户 ID
UserName String 用户名
VerificationTime String 核验时间，RFC3339 格式
VerificationMedium VerificationMedium 核验介质
DeviceSn String 设备 SN
SceneId String 场景 ID
SceneName String 场景名称
VerifierId String 核验人 ID
VerifierName String 核验人名
RequestId String 唯一请求 ID
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 78
3. 推送示例
POST / HTTP/1.1
Host: <客户推送地址域名>
Content-Type: application/json; charset=utf-8
X-TC-Action: CreateVerificationRecord
{
"UserId": "user001",
"UserName": "张三",
"VerificationTime": "2024-07-15T09:30:15.500Z",
"VerificationMedium": "palm",
"DeviceSn": "device001",
"SceneId": "scene001",
"SceneName": "深圳南山门禁 1 号",
"VerifierId": "verifier001",
"VerifierName": "李四",
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
客户收到推送后返回 HTTP 200 OK 即可，无需返回业务数据。
---
核验规则相关接口
创建核验规则
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于创建核验规则，支持配置时间规则、用户规则，并可绑定多个场景。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 79
3. 输出参数
参数名称 必
选 类型 描述
Action 是 String 公共参数，本接口取值：CreateVerifyRule。
Version 是 String 公共参数，本接口取值：2025-07-15。
VerifyRuleName 是 String 核验规则名称。
EnableTimeRule 是 Boolean 是否启用时间规则，false 表示不启用，true 表
示启用。
TimeRule 否 TimeRule 时间规则，启用时间规则时需配置。
EnableUserRule 是 Boolean 是否启用用户规则，false 表示所有用户，true
表示指定用户。
UserRule 否 UserRule 用户规则，启用用户规则时需配置。
EnableWebhookRule 否 Boolean 是否启用 Webhook 规则，可选，不传默认为
true。
BindSceneIdList 否 Array 绑定场景 ID 列表，可绑定多个场景。
参数名称 类型 描述
VerifyRuleId String 核验规则 ID。
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 80
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: CreateVerifyRule
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"VerifyRuleName": "工作日早晚高峰",
"EnableTimeRule": true,
"TimeRule": {
"AllowDateRange": {
"StartDate": {"Year": 2025, "Month": 1, "Day": 1},
"EndDate": {"Year": 2025, "Month": 12, "Day": 31}
},
"AllowDayOfWeekList": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY",
"FRIDAY"],
"AllowTimePeriodList": [
{
"StartTime": {"Hours": 7, "Minutes": 30, "Seconds": 0},
"EndTime": {"Hours": 9, "Minutes": 30, "Seconds": 0},
"MaxVerificationCount": 0
},
{
"StartTime": {"Hours": 17, "Minutes": 30, "Seconds": 0},
"EndTime": {"Hours": 20, "Minutes": 0, "Seconds": 0},
"MaxVerificationCount": 0
}
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 81
]
},
"EnableUserRule": true,
"UserRule": {
"UserTags": [
{"UserTagId": "tag001", "UserTagName": "研发中心"}
],
"UserInfos": [
{"UserId": "user001", "UserName": "张三"}
]
},
"EnableWebhookRule": false,
"BindSceneIdList": ["scene001", "scene002"]
}
输出示例
{
"Response": {
"VerifyRuleId": "vr_20250715001",
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
修改核验规则
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于修改已有的核验规则信息。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 82
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：ModifyVerifyRule。
Version 是 String 公共参数，本接口取值：2025-07-15。
VerifyRuleId 是 String 核验规则全局唯一 ID。
VerifyRuleName 是 String 核验规则名称。
EnableTimeRule 是 Boolean 是否启用时间规则。
TimeRule 否 TimeRule 时间规则。
EnableUserRule 是 Boolean 是否启用用户规则。
UserRule 否 UserRule 用户规则。
EnableWebhookRule 是 Boolean 是否启用 Webhook 规则。
BindSceneIdList 否 Array 绑定场景 ID 列表。
参数名称 类型 描述
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 83
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: ModifyVerifyRule
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"VerifyRuleId": "vr_20250715001",
"VerifyRuleName": "工作日高峰与中午",
"EnableTimeRule": true,
"TimeRule": {
"AllowDayOfWeekList": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY",
"FRIDAY"],
"AllowTimePeriodList": [
{"StartTime": {"Hours": 7, "Minutes": 30, "Seconds": 0}, "EndTime": {"Hours": 9,
"Minutes": 30, "Seconds": 0}},
{"StartTime": {"Hours": 12, "Minutes": 0, "Seconds": 0}, "EndTime": {"Hours": 13,
"Minutes": 30, "Seconds": 0}},
{"StartTime": {"Hours": 17, "Minutes": 30, "Seconds": 0}, "EndTime": {"Hours":
20, "Minutes": 0, "Seconds": 0}}
]
},
"EnableUserRule": false,
"EnableWebhookRule": true,
"BindSceneIdList": ["scene001"]
}
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 84
输出示例
{
"Response": {
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
删除核验规则
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于删除指定的核验规则。
默认接口请求频率限制：20 次/秒/AppId。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：DeleteVerifyRule。
Version 是 String 公共参数，本接口取值：2025-07-15。
VerifyRuleId 是 String 核验规则 ID。
参数名称 类型 描述
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 85
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: DeleteVerifyRule
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"VerifyRuleId": "vr_20250715001"
}
输出示例
{
"Response": {
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
查询核验规则
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于查询指定核验规则的详细配置。
默认接口请求频率限制：20 次/秒/AppId。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 86
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
Action 是 String 公共参数，本接口取值：DescribeVerifyRule。
Version 是 String 公共参数，本接口取值：2025-07-15。
VerifyRuleId 是 String 核验规则 ID。
参数名称 类型 描述
VerifyRuleId String 核验规则 ID。
VerifyRuleName String 核验规则名称。
EnableTimeRule Boolean 是否启用时间规则。
TimeRule TimeRule 时间规则。
EnableUserRule Boolean 是否启用用户规则。
UserRule UserRule 用户规则。
EnableWebhookRule Boolean 是否启用 Webhook 规则。
BindSceneIdList Array 绑定场景 ID 列表。
RequestId String 唯一请求 ID，每次请求都会返回。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 87
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: DescribeVerifyRule
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: 223
X-Palm-Openapi-Token: **************************************
Authorization: TC3-HMAC-SHA256 Credential=AKIDxxx/2025-07-
15/palm/tc3_request, SignedHeaders=content-type;host;x-tc-action, Signature=xxx
{
"VerifyRuleId": "vr_20250715001"
}
输出示例
{
"Response": {
"VerifyRuleId": "vr_20250715001",
"VerifyRuleName": "工作日早晚高峰",
"EnableTimeRule": true,
"TimeRule": {
"AllowDateRange": {
"StartDate": {
"Year": 2025,
"Month": 1,
"Day": 1
},
"EndDate": {
"Year": 2025,
"Month": 12,
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 88
"Day": 31
}
},
"DisallowDateList": [
{
"Year": 2025,
"Month": 5,
"Day": 1
}
],
"AllowDayOfWeekList": [
"MONDAY",
"TUESDAY",
"WEDNESDAY",
"THURSDAY",
"FRIDAY"
],
"AllowTimePeriodList": [
{
"StartTime": {
"Hours": 7,
"Minutes": 30,
"Seconds": 0
},
"EndTime": {
"Hours": 9,
"Minutes": 30,
"Seconds": 0
},
"MaxVerificationCount": 0
},
{
"StartTime": {
"Hours": 17,
"Minutes": 30,
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 89
"Seconds": 0
},
"EndTime": {
"Hours": 20,
"Minutes": 0,
"Seconds": 0
},
"MaxVerificationCount": 0
}
]
},
"EnableUserRule": true,
"UserRule": {
"UserTags": [
{
"UserTagId": "tag001",
"UserTagName": "研发中心"
}
],
"UserInfos": [
{
"UserId": "user001",
"UserName": "张三"
}
]
},
"EnableWebhookRule": false,
"BindSceneIdList": [
"scene001",
"scene002"
],
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 90
---
校验访问权限
1. 接口描述
接口回调域名：由客户提供给平台，平台主动调用
接口说明：用于检查用户的访问权限。该接口只支持回调，不支持主动拉取
，需提前将回调地址提供给平台，由平台主动调用。平台发送访问权限校验请求，客户根据
自有规则判断后返回是否允许通行及原因。
2. 输入参数
3. 输出参数
参数名称 类型 描述
UserId String 用户 ID
UserName String 用户名
VerificationTime String 核验时间，RFC3339 字符串格式，如"2025-
07-03T09:30:15.500Z"
VerificationMedium VerificationMedium 核验介质
DeviceSn String 设备 SN
SceneId String 场景 ID
SceneName String 场景名称
参数名称 类型 描述
Allowed Boolean 是否允许通行
Reason String 通行原因描述，如"命中核验规则：访客预约通行"
RequestId String 唯一请求 ID。每次请求都会返回 RequestId。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 91
4. 请求和响应示例
请求示例
POST / HTTP/1.1
Host: <客户回调地址域名>
Content-Type: application/json; charset=utf-8
X-TC-Action: CheckAccessPermission
{
"UserId": "user001",
"UserName": "张三",
"VerificationTime": "2025-07-15T09:30:15.500Z",
"VerificationMedium": "palm",
"DeviceSn": "device001",
"SceneId": "scene001",
"SceneName": "深圳南山门禁 1 号"
}
响应示例（允许通行）
{
"Response": {
"Allowed": true,
"Reason": "命中核验规则：访客预约通行",
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
响应示例（拒绝通行）
{
"Response": {
"Allowed": false,
"Reason": "用户未在允许时间范围内",
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 92
---
扫码录掌相关接口
扫码录掌服务，适合开放用户注册场景。
二维码由刷掌设备生成，用户录掌后，刷掌设备会展示二维码，二维码会携带用户信息，用
户扫码后，会通知给应用服务器，应用服务器根据用户信息进行用户注册。
二维码扫码获得的 URL 示例：
https://app.intl.palm.tencent.com/local_h5/brushAuth?ocode=***&session_id=***&se
ssion_key=***&app_id=***&access_token=***
扫码事件通知
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于通知服务端用户扫码事件。本接口仅验证 Token，不验证签名，HTTP 头部
不需要 Authorization 字段。
默认接口请求频率限制：20 次/秒/AppId。
注意：本接口需要在 HTTP 请求头中提供 X-Palm-Appid 字段和 X-Palm-Openapi-
Token 字段，来源于扫码 URL 中的 app_id/access_token 参数，可重复使用，直至令
牌过期。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
SessionId 是 String 会话 ID
参数名称 类型 描述
RequestId String 唯一请求 ID。每次请求都会返回 RequestId。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 93
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: NotifyQrCodeScanEvent
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: app_001
X-Palm-Openapi-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
{
"SessionId": "session_001"
}
输出示例
{
"Response": {
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
扫码绑定掌纹
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
接口说明：用于扫码绑定掌纹。本接口仅验证 Token，不验证签名，HTTP 头部不需要
Authorization 字段。
默认接口请求频率限制：20 次/秒/AppId。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 94
注意：本接口需要在 HTTP 请求头中提供 X-Palm-Appid 字段和 X-Palm-Openapi-
Token 字段，来源于扫码 URL 中的 app_id/access_token 参数，可重复使用，直至令
牌过期。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
SessionId 是 String 会话 ID
UserId 是 String 用户唯一标识
UserName 是 String 用户名称
ReplacePalm 否 Boolean 是否替换手掌
参数名称 类型 描述
UserSessionId String 用户会话 ID
RequestId String 唯一请求 ID。每次请求都会返回 RequestId。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 95
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: BindQrCodeScanPalm
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: app_001
X-Palm-Openapi-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
{
"SessionId": "session_001",
"UserId": "user001",
"UserName": "张三",
"ReplacePalm": false
}
输出示例
{
"Response": {
"UserSessionId": "user_session_001",
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
查询扫码录掌用户信息
1. 接口描述
接口请求域名：open.intl.palm.tencent.com
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 96
接口说明：用于查询扫码录掌用户信息。本接口仅验证 Token，不验证签名，HTTP 头部不
需要 Authorization 字段。
默认接口请求频率限制：20 次/秒/AppId。
注意：本接口需要在 HTTP 请求头中提供 X-Palm-Appid 字段和 X-Palm-Openapi-
Token 字段，来源于扫码 URL 中的 app_id/access_token 参数，可重复使用，直至令
牌过期。
2. 输入参数
3. 输出参数
参数名称 必选 类型 描述
SessionId 是 String 会话 ID
UserId 是 String 用户唯一标识
参数名称 类型 描述
UserId String 用户唯一标识
PalmState PalmState 录掌状态
RequestId String 唯一请求 ID。每次请求都会返回 RequestId。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 97
4. 示例
输入示例
POST / HTTP/1.1
Host: open.intl.palm.tencent.com
Content-Type: application/json; charset=utf-8
X-TC-Action: DescribeQrCodeScanUser
X-TC-Timestamp: 1704067200
X-TC-Version: 2025-07-15
X-TC-Nonce: b6a5c4e3a2b1c0d9e8f7a6b5c4d3e2f1
X-Palm-AppId: app_001
X-Palm-Openapi-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
{
"SessionId": "session_001",
"UserId": "user001"
}
输出示例
{
"Response": {
"UserId": "user001",
"PalmState": "registered",
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
---
数据结构
本节所有数据结构均根据 proto 文件自动生成，风格与腾讯云 API3.0 数据结构官方文档
（当前仅有中文版，需自行翻译）严格一致。
仅包含被多个接口复用的公共数据结构、枚举类型和通用结构体。各接口专属的请求/响应
参数已在对应接口章节详细说明。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 98
公共业务结构
UserTag
VerificationRecord
TimeRule
DateRange
名称 类型 描述
UserTagId String 用户标签 ID
UserTagName String 用户标签名称
名称 类型 描述
UserId String 用户 ID
UserName String 用户名
VerificationTime String 核验时间
VerificationMedium VerificationMedium 核验介质
DeviceSn String 设备 SN
SceneId String 场景 ID
SceneName String 场景名称
VerifierId String 核验人 ID
VerifierName String 核验人名
名称 类型 描述
AllowDateRange DateRange 可核验日期范围，空表示不限制
DisallowDateList Date[] 不可核验日期列表
AllowDayOfWeekList DayOfWeek[] 每周有效日
AllowTimePeriodList TimePeriod[] 每日允许通行时间段
名称 类型 描述
StartDate Date 开始日期
EndDate Date 结束日期
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 99
Date
TimeOfDay
TimePeriod
UserRule
UserTagInfo
UserInfo
名称 类型 描述
Year Integer 年
Month Integer 月
Day Integer 日
名称 类型 描述
Hours Integer 小时
Minutes Integer 分钟
Seconds Integer 秒
名称 类型 描述
StartTime TimeOfDay 开始时间
EndTime TimeOfDay 结束时间
MaxVerificationCount Integer 可核验次数，0 表示不限制
名称 类型 描述
UserTags UserTagInfo[] 用户标签列表
UserInfos UserInfo[] 用户信息列表
名称 类型 描述
UserTagId String 用户标签唯一标识
UserTagName String 用户标签名称
名称 类型 描述
UserId String 用户唯一标识
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 100
接口专属结构
用户管理接口
CreateUserResponsePartialFailureError
创建用户接口的部分失败错误信息。
ModifyUserResponsePartialFailureError
修改用户接口的部分失败错误信息。
枚举类型
PalmState
返回类型：字符串，取值为下表枚举值名称。
VerificationMedium
返回类型：字符串，取值为下表枚举值名称。
UserName String 用户名称
名称 类型 描述
NotExistUserTagIdList Array of String 不存在的用户标签 ID 列表
名称 类型 描述
NotExistUserTagIdList Array of String 不存在的用户标签 ID 列表
枚举值 描述
unregistered 未录掌
pre_registered 预录入
registered 已录掌
枚举值 描述
verification_medium_unspecified 未指定介质
palm 刷掌
card 刷卡
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 101
DayOfWeek
返回类型：字符串，取值为下表枚举值名称。
QrCodeScanState
返回类型:字符串，取值为下表枚举值名称。
ScenarioStrategy
返回类型：字符串，取值为下表枚举值名称。
code 刷码
枚举值 描述
NONE 未指定
MONDAY 周一
TUESDAY 周二
WEDNESDAY 周三
THURSDAY 周四
FRIDAY 周五
SATURDAY 周六
SUNDAY 周日
枚举值 描述
qrcode_scan_state_unspecified 扫码状态未指定
pending 等待扫码
scanned 已扫码
success 扫码录掌成功
failed 扫码录掌失败
expired 扫码录掌二维码会话过期
枚举值 描述
Default 默认
DemoOnDeviceRecognition100 演示端侧识别百人 100 User Demo On-device
Recognition
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 102
RegisterType
返回类型：字符串，取值为下表枚举值名称。
PalmDirection
返回类型：字符串，取值为下表枚举值名称。
通用结构
Error
AccessOnDeviceRecognition50k 门禁端侧识别五万人 50k User Access Control
On-device Recognition
EKYCCloudRecognition1M 核身纯云端识别百万人 1M User eKYC Cloud
Recognition
EKYCHybridRecognition1M 核身端云识别百万人 1M User eKYC Hybrid
Recognition
枚举值 描述
register_type_unspecified 注册类型未指定
device 设备注册
mobile 手机注册
枚举值 描述
palm_direction_unspecified 掌纹方向未指定
left 左手
right 右手
名称 类型 描述
Code String 错误码
Message String 错误信息
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 103
---
错误码
功能说明
如果返回结果中存在 Error 字段，则表示调用 API 接口失败。例如：
{
"Response": {
"Error": {
"Code": "AuthFailure.SignatureFailure",
"Message": "The provided credentials could not be validated. Please check
your signature is correct."
},
"RequestId": "d6a4c45b-d30f-49c8-a724-ecc37d0f0c42"
}
}
Error 中的 Code 表示错误码，Message 表示该错误的具体信息。
公共错误码
错误码 说明
InvalidParameter 参数错误（包括参数格式、类型等错误）
InvalidParameterValue 参数取值错误
MissingParameter 缺少参数错误，必传参数没填
UnknownParameter 未知参数错误，用户多传未定义的参数会导致错误
AuthFailure CAM 签名/鉴权错误
InternalError 内部错误。业务必须统一采用 InternalError 或者
InternalError.xxx 形式表示内部错误
InvalidAction 接口不存在
UnauthorizedOperation 未授权操作
RequestLimitExceeded 请求的次数超过了频率限制
NoSuchVersion 接口版本不存在
UnsupportedRegion 接口不支持所传地域
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 104
业务错误码
UnsupportedOperation 操作不支持
ResourceNotFound 资源不存在
LimitExceeded 超过配额限制
ResourceUnavailable 资源不可用
ResourceInsufficient 资源不足
FailedOperation 操作失败
ResourceInUse 资源被占用
DryRunOperation DryRun 操作，代表请求将会是成功的，只是多传了 DryRun
参数
ResourcesSoldOut 资源售罄
OperationDenied 操作被拒绝
错误码 说明
InvalidParameterValue.FiltersLimitExceed Filters
数量超
过限制
InvalidParameterValue.PageLimitExceed 分页参
数超过
限制
InvalidParameterValue.PageTokenExpired 分页令
牌已过
期
InvalidParameterValue.PageTokenSignatureFailure 分页令
牌签名
验证失
败
InvalidParameterValue.PageTokenQueryMismatch 分页令
牌查询
条件不
匹配
ResourceNotFound.TenantNotFound 指定的
租户不
存在，
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 105
或您无
权访问
该租户
InvalidParameterValue.UserIdEmpty 用户 ID
为空
InvalidParameterValue.UserIdLengthNotAllowed 用户 ID
长度不
满足限
制
InvalidParameterValue.UserIdShouldOnlyContainLettersAndDigits 用户 ID
只能包
含字母
和数字
InvalidParameterValue.UserIdShouldOnlyContainGraphicsAscii 用户 ID
只能包
含
ASCII
图形字
符
（ASCII
范围：
33-
126）
InvalidParameterValue.UserNameEmpty 用户名
称为空
InvalidParameterValue.UserNameLengthNotAllowed 用户名
称长度
不满足
限制
InvalidParameterValue.UserNameOrPasswordEmpty 用户名
称或密
码为空
InvalidParameterValue.PhoneNoEmpty 手机号
为空
InvalidParameterValue.PhoneNoLengthNotAllowed 手机号
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 106
长度不
满足限
制
InvalidParameterValue.InvalidPhoneNo 手机号
格式不
正确
InvalidParameterValue.PhysicalCardNoLengthNotAllowed 物理卡
号长度
不满足
限制
InvalidParameterValue.PhysicalCardNoShouldOnlyContainLettersAndDigits 物理卡
号只能
包含字
母和数
字
InvalidParameterValue.PalmIdEmpty 掌纹 ID
为空
InvalidParameterValue.SessionIdEmpty 会话 ID
为空
InvalidParameterValue.SessionIdLengthNotAllowed 会话 ID
长度不
满足限
制
InvalidParameterValue.SessionNotExist 会话不
存在
InvalidParameterValue.InvalidUserId 用户 ID
格式不
正确，
只能包
含数字
字母和
连字符
InvalidParameterValue.RegisterTypeNotAllowed 注册类
型不满
足限制
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 107
InvalidParameterValue.UserTagIdEmpty 用户标
签 ID
为空
InvalidParameterValue.UserTagIdLengthNotAllowed 用户标
签 ID
长度不
满足限
制
InvalidParameterValue.InvalidUserTagId 用户标
签 ID
格式不
正确
InvalidParameterValue.UserTagNameEmpty 用户标
签名称
为空
InvalidParameterValue.UserTagNameLengthNotAllowed 用户标
签名称
长度不
满足限
制
InvalidParameterValue.DeviceSnEmpty 设备 SN
为空
InvalidParameterValue.DeviceSnLengthNotAllowed 设备 SN
长度不
满足限
制
InvalidParameterValue.DeviceSnShouldOnlyContainLettersAndDigits 设备 SN
只能包
含字母
和数字
InvalidParameterValue.InvalidDeviceSn 设备 SN
格式不
正确
InvalidParameterValue.DeviceNameEmpty 设备名
称为空
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 108
InvalidParameterValue.DeviceNameLengthNotAllowed 设备名
称长度
不满足
限制
InvalidParameterValue.ErrDeviceNameInvalid 设备名
称格式
不正确
InvalidParameterValue.SceneIdEmpty 场景 ID
为空
InvalidParameterValue.SceneIdLengthNotAllowed 场景 ID
长度不
满足限
制
InvalidParameterValue.SceneIdShouldOnlyContainLettersAndDigits 场景 ID
只能包
含字母
和数字
InvalidParameterValue.InvalidSceneId 场景 ID
格式不
正确
InvalidParameterValue.SceneNameEmpty 场景名
称为空
InvalidParameterValue.SceneNameLengthNotAllowed 场景名
称长度
不满足
限制
InvalidParameterValue.SceneGroupIdEmpty 场景组
ID 为空
InvalidParameterValue.SceneGroupIdLengthNotAllowed 场景组
ID 长度
不满足
限制
InvalidParameterValue.SceneGroupIdShouldOnlyContainLettersAndDigits 场景组
ID 只能
包含字
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 109
母和数
字
InvalidParameterValue.InvalidSceneGroupId 场景组
ID 格式
不正确
InvalidParameterValue.SceneGroupNameEmpty 场景组
名称为
空
InvalidParameterValue.SceneGroupNameLengthNotAllowed 场景组
名称长
度不满
足限制
InvalidParameterValue.VerifierIdEmpty 核验人
ID 为空
InvalidParameterValue.VerifierIdLengthNotAllowed 核验人
ID 长度
不满足
限制
InvalidParameterValue.VerifierIdShouldOnlyContainLettersAndDigits 核验人
ID 只能
包含字
母和数
字
InvalidParameterValue.InvalidVerifierId 核验人
ID 格式
不正确
InvalidParameterValue.VerifierNameEmpty 核验人
名称为
空
InvalidParameterValue.VerifierNameLengthNotAllowed 核验人
名称长
度不满
足限制
InvalidParameterValue.QrCodeScanSessionIdEmpty 扫码录
掌会话
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 110
ID 为空
InvalidParameterValue.QrCodeScanSessionTtlNotAllowed 扫码录
掌会话
期望生
命周期
不满足
限制
FailedOperation.UserNotExist 用户不
存在
FailedOperation.UserAlreadyExists 用户已
存在
FailedOperation.UserIdAlreadyExists 用户 ID
已存在
FailedOperation.UserPalmAlreadyBound 用户手
掌已绑
定
FailedOperation.SceneNotExist 场景不
存在
FailedOperation.SceneAlreadyExists 场景已
存在
FailedOperation.SceneGroupNotExist 场景组
不存在
FailedOperation.SceneGroupAlreadyExists 场景组
已存在
FailedOperation.DuplicateSceneNameInSceneGroup 场景组
内场景
名称重
复
FailedOperation.DuplicateSceneGroupNameInSceneGroup 场景组
内场景
组名称
重复
FailedOperation.DeviceSceneBindingLimitExceeded 设备场
景绑定
超过限
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 111
制
FailedOperation.QrCodeExpired 扫描录
掌二维
码已过
期
FailedOperation.QrCodeFinished 扫描录
掌二维
码已被
使用
FailedOperation.QrCodeStatusInvalid 扫描录
掌二维
码状态
无效
FailedOperation.BindPalmUserIdAndUserNameNotMatch 绑定掌
纹用户
ID 与用
户名不
匹配
FailedOperation.VerifyRuleAlreadyExist 核验规
则已存
在
FailedOperation.VerifyRuleNotExist 核验规
则不存
在
FailedOperation.DeviceNotExist 设备不
存在
FailedOperation.DeviceAlreadyExists 设备已
存在
FailedOperation.DeviceCannotBeDeletedWhenBindWithScene 设备绑
定场景
时不允
许删除
FailedOperation.DeviceNotBoundWithScene 设备未
绑定场
景
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 112
FailedOperation.UserTagNotExist 用户标
签不存
在
FailedOperation.UserTagAlreadyExists 用户标
签已存
在
FailedOperation.UserTagNameAlreadyExists 用户标
签名称
已存在
InternalError.GetPaaSChannelFailed 获取
PaaS
渠道失
败
InternalError.UpdateUserPalmFailed 更新用
户手掌
失败
InternalError.CreateUserTokenFailed 创建用
户
Token
失败
InternalError.BindUserPalmByPaaSChannelFailed 通过
PaaS
渠道绑
定用户
手掌失
败
InternalError.DeleteUserPalmByPaaSChannelFailed 通过
PaaS
渠道删
除用户
手掌失
败
InternalError.DescribeUserPalmByPaaSChannelFailed 通过
PaaS
渠道查
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
服务端接口说明
文档版本 v1.8 密级：公开 113
询用户
手掌失
败
InternalError.CreateAccessTokenFailed 创建开
放接口
访问令
牌失败
InternalError.CreateDeviceAccessTokenFailed 创建开
放接口
设备访
问令牌
失败
InternalError.DescribeSecretKeyFailed 查询开
放接口
访问密
钥失败
FailedOperation.MemberNotExist 成员不
存在
FailedOperation.MemberAlreadyExists 成员已
存在
FailedOperation.MemberLoginExpired 成员登
录已过
期
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
设备端接口说明
文档版本 v1.8 密级：公开 114
3 设备端接口说明
设备端 M4 双向通信协议
版本更新记录表
版本
号
发布日期 更新内容
1.7.0 2026-1-5 第一版
1.8.0 2026-3-
10
补充使用场景说明、系统架构图、完善录掌注册错误码、新增全局错
误码汇总
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
设备端接口说明
文档版本 v1.8 密级：公开 115
使用场景
本文档描述上位机（如 PC、收银机、自助终端等外部主机）如何通过串口（USB 转串口，
芯片型号 PL2303）与刷掌设备（M4）进行双向通信的协议规范。
适用场景
当前协议支持注册、识别、模式切换三大功能，典型业务场景如下：
1. 录掌注册：柜台工作人员或自助终端在上位机端发起录掌请求，将用户信息（ID、姓名、
手机号、银行卡号）通过串口下发到刷掌设备，用户在设备上完成掌纹录入，录入结果回传
上位机。
2. 刷掌识别：上位机可唤起设备刷掌识别页面，用户完成刷掌后设备将识别到的用户信息
（UserId 或 CardNumber）回传上位机，用于身份确认、支付等业务。
3. 模式切换与查询：上位机可查询和切换设备当前的工作模式（识别模式、手机 H5 录掌、
设备端录掌、上位机录掌），灵活适配不同业务场景。
前置条件
● 设备与上位机通过 USB 串口线（PL2303 芯片）物理连接
● 上位机已安装对应操作系统的串口驱动
● 设备端需切换至上位机录掌模式（mode=4）方可执行录掌注册协议
系统架构

PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
设备端接口说明
文档版本 v1.8 密级：公开 116
通讯模式说明：
● 上位机与刷掌设备通过 USB 转串口（PL2303 芯片）连接，采用命令-响应模式进行双
向通信
● 上位机→设备：发送指令（唤起录掌、取消录掌、唤起识别、切换/查询模式）
● 设备→上位机：返回确认、上报结果（录掌结果、识别用户信息、模式切换结果、当前
模式）
上位机录掌注册时序

PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
设备端接口说明
文档版本 v1.8 密级：公开 117
通用配置与协议
上位机驱动
物理层协议配置
通用数据包格式示例
**操作系统** **下载链接**
macOS PL2303 Serial App
Windows PL2303GL
**参数** **配置**
波特率 115200
数据位 8
停止位 1
校验位 None
流控 None
**起始字符** **包序号** **命令码** **数据域长度** **数据域** **校验位**
5A5A5A5A 0001 A1 0001 01 2D
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
设备端接口说明
文档版本 v1.8 密级：公开 118
● 起始字符（4 字节）：
包开始的标识，固定为 0x5A5A5A5A
● 包序号（2 字节）：
从 0 开始，每发送一个数据包就加一，累加至 0xFFFF 后再循环至 0，刷掌设备返回序
号与上位机发送命令包序号一致，该参数由上位机主动更新维护
● 命令码（1 字节）：
用于区分不同类的命令，在业务场景会介绍相关命令码
● 数据域长度（2 字节）：
用来表示包中数据域中数据的长度，该值不包含校验位的长度
● 数据域（根据数据域长度确定）：
此字段的含义按各命令解析，有的命令可能没有此字段
● 校验位（1 字节）
这里采用 BCC 校验，为除起始字符外其他数据的异或值
上位机录掌注册协议
注：该协议流程需在设备端处于上位机录掌模式下才可正确执行
【上位机→设备】 唤起录掌
上位机唤起设备录掌，并提供相应录掌信息，包括用户 ID、用户名、手机号以及银行卡号。
唤起成功后，相应信息会显示在设备主界面，提示用户开始注册掌纹
● 通信协议：
**起始字符** **包序号** **命令码** **数据域长度** **数据域** **校验位**
5A5A5A5A 0001 **A1** 数据长度决定 用户信息 BCC 计算获得
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
设备端接口说明
文档版本 v1.8 密级：公开 119
● 传输数据格式：
{
"userId": "aaaaaaaa",
"userName": "测试人员",
"phone": "15997475680",
"physicalCardNumber": "12345678"
}
● 通信数据示例（16 进制）：
5A 5A 5A 5A 00 01 A1 00 65 7B 22 75 73 65 72 49 64 22 3A 22 61 61
61 61 61 61 61 61 22 2C 22 75 73 65 72 4E 61 6D 65 22 3A 22 E6 B5 8B
E8 AF 95 E4 BA BA E5 91 98 22 2C 22 70 68 6F 6E 65 22 3A 22 31 35 39
39 37 34 37 35 36 38 30 22 2C 22 70 68 79 73 69 63 61 6C 43 61 72 64
4E 75 6D 62 65 72 22 3A 22 31 32 33 34 35 36 37 38 22 7D AA
【设备→上位机】录掌信息确认
刷掌设备接收到上位机发送的**唤起录掌**指令后，发送该指令告知上位机，已经接收到用户
数据，并处于录掌流程中
● 通信协议：
● 通信数据示例（16 进制）：
5A 5A 5A 5A 00 01 A2 00 00 A3
【上位机→设备】取消录掌
上位机在等待用户在刷掌设备录掌结果的过程中，可以发送指令取消录掌
● 通信协议：
● 通信数据示例（16 进制）：
5A 5A 5A 5A 00 01 A3 00 00 A2
【设备→上位机】上报录掌结果
刷掌设备在用户录掌成功/失败后会返回对应的录掌结果，上位机可根据结果显示对应界面
● 通信协议：
**起始字符** **包序号** **命令码** **数据域长度** **数据域** **校验位**
5A5A5A5A 0001 **A2** 0000 无 A3
**起始字符** **包序号** **命令码** **数据域长度** **数据域** **校验位**
5A5A5A5A 0001 **A3** 0000 无 A2
**起始字符** **包序号** **命令码** **数据域长度** **数据域** **校验位**
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
设备端接口说明
文档版本 v1.8 密级：公开 120
● 传输数据格式：
{
"resultCode": 0,
"resultMessage": "success"
}
● 错误码列表：
● 通信数据示例（16 进制）：
5A 5A 5A 5A 00 01 A4 00 2A 7B 22 72 65 73 75 6C 74 43 6F 64 65 22
3A 30 2C 22 72 65 73 75 6C 74 4D 65 73 73 61 67 65 22 3A 22 73 75 63
63 65 73 73 22 7D 90
上位机刷掌识别协议
注：该协议流程需在设备端处于识别模式下才可正确执行
【上位机→设备】唤起刷掌识别
上位机唤起设备刷掌识别，唤起成功后，设备会弹出页面提示用户刷掌（该协议仅唤起提示
页面，不通过该协议仍可通过设备刷掌）
● 通信协议：
5A5A5A5A 0001 **A4** 数据长度决定 录掌结果 BCC 计算获得
**错误码** **说明**
0 录掌注册成功
6 云端服务返回业务错误，具体原因参考 resultMessage 字段
8 网络请求失败（设备无法连接云端服务）
104 掌纹模组运行时错误（录掌过程中模组异常）
143 该用户掌纹已注册，重复注册
144 云端未找到对应用户（用户 ID 不匹配）
145 用户名与云端记录不匹配
212 上位机下发的用户信息无效（userId 或 userName 为空）
-100 重复录掌，该用户的掌纹已在本设备注册过（设备端本地检测）
其他 未知错误，建议重试。具体原因参考 resultMessage 字段
**起始字符** **包序号** **命令码** **数据域长度** **数据域** **校验位**
5A5A5A5A 0001 **A5** 0000 无 A4
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
设备端接口说明
文档版本 v1.8 密级：公开 121
● 通信数据示例（16 进制）：
5A 5A 5A 5A 00 01 A5 00 00 A4
【设备→上位机】上报刷掌用户信息
刷掌设备在用户刷掌识别成功后会返回对应的用户信息，该信息类型可在设备 Output
Mode 设置中选择 UserId 或 CardNumber
● 通信协议：裸数据传输指定用户信息，不走上述通用数据协议
上位机模式切换协议
注：该协议流程需在设备端处于主界面下才可正确执行
【上位机→设备】 切换模式
上位机控制切换设备当前所处刷掌模式
● 通信协议：
● 传输数据格式：
{
"mode": 1
}
● 录掌模式列表：
● 通信数据示例（16 进制）：
5A 5A 5A 5A 00 01 A6 00 0B 7B 22 6D 6F 64 65 22 3A 20 31 7D 82
【设备→上位机】上报切换的模式
刷掌设备在用户录掌成功/失败后会返回对应的录掌结果，上位机可根据结果显示对应界面
● 通信协议：
**起始字符** **包序号** **命令码** **数据域长度** **数据域** **校验位**
5A5A5A5A 0001 **A6** 数据长度决定 需切换的模式 BCC 计算获得
**值** **模式**
1 识别模式
2 注册模式 - 手机 H5 录掌
3 注册模式 - 设备端录掌
4 注册模式 - 上位机录掌
**起始字符** **包序号** **命令码** **数据域长度** **数据域** **校验位**
5A5A5A5A 0001 **A7** 数据长度决定 模式切换结果 BCC 计算获得
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
设备端接口说明
文档版本 v1.8 密级：公开 122
● 传输数据格式：
{
"code": 0,
"message": "Success"
}
● 错误码列表：
● 通信数据示例（16 进制）：
5A 5A 5A 5A 00 01 A7 00 40 7B 22 63 6F 64 65 22 3A 20 30 2C 22 6D
65 73 73 61 67 65 22 3A 20 22 53 75 63 63 65 73 73 22 7D D9
上位机模式查询协议
【上位机→设备】查询设备模式
上位机查询设备当前所处模式
● 通信协议：
● 通信数据示例（16 进制）：
5A 5A 5A 5A 00 01 A8 00 00 A9
【设备→上位机】 响应查询模式
在上位机发送查询指令后，设备通过该协议返回当前所处模式
● 通信协议：
**错误码** **说明**
0 模式切换成功
1 参数错误，切换的模式并未在设备列表中
213 当前设备未处在主界面
其他 模式切换失败，请重试
**起始字符** **包序号** **命令码** **数据域长度** **数据域** **校验位**
5A5A5A5A 0001 **A8** 0000 无 A9
**起始字符** **包序号** **命令码** **数据域长度** **数据域** **校验位**
5A5A5A5A 0001 **A9** 数据长度决定 当前所处模式 BCC 计算获得
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
设备端接口说明
文档版本 v1.8 密级：公开 123
● 传输数据格式：
{
"mode": 1
}
● 录掌模式列表：参考【上位机→设备】切换模式
● 通信数据示例（16 进制）：
5A 5A 5A 5A 00 01 A9 00 0B 7B 22 6D 6F 64 65 22 3A 20 31 7D 8D
错误状态响应协议
【设备→上位机】未知命令码
刷掌设备在接收到未知命令码时做出响应
● 通信协议：
● 传输数据格式：
{
"cmd": 10,
}
● 通信数据示例（16 进制）：
5A 5A 5A 5A 00 01 F0 00 0B 7B 22 63 6D 64 22 3A 20 31 30 7D 8D
全局错误码汇总
以下为上位机与设备通信过程中可能遇到的所有错误码汇总，按场景分类整理。
录掌注册错误码（A4 上报录掌结果）
设备通过命令码 A4 上报录掌结果时，resultCode 可能出现以下值：
**起始字符** **包序号** **命令码** **数据域长度** **数据域** **校验位**
5A5A5A5A 0001 **F0** 数据长度决定 未知命令码 BCC 计算获得
**错误码** **说明**
0 录掌注册成功
6 云端服务返回业务错误，具体原因参考 resultMessage 字段
8 网络请求失败（设备无法连接云端服务）
104 掌纹模组运行时错误
143 该用户掌纹已注册（重复注册）
144 云端未找到对应用户（用户 ID 不匹配）
145 用户名与云端记录不匹配
212 上位机下发的用户信息无效（userId 或 userName 为空）
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
设备端接口说明
文档版本 v1.8 密级：公开 124
模式切换错误码（A7 上报切换结果）
通用错误码
-100 重复录掌，该用户的掌纹已在本设备注册过（设备端本地检测）
其他 未知错误，建议重试。具体原因参考 resultMessage 字段
**错误码** **说明**
0 模式切换成功
1 参数错误，目标模式不在合法范围内（1~4）
5 请求数据格式解析失败
213 当前设备未处在主界面，无法切换模式
其他 模式切换失败，请重试
**错误码** **说明**
0 成功
1 参数无效
2 服务未初始化
3 操作超时
5 JSON 数据解析失败
6 云端服务返回业务错误
7 不支持的操作
8 网络请求失败
143 重复注册
144 用户未找到
145 用户信息不匹配
211 上位机未连接（串口未连接）
212 上位机下发的用户信息无效
213 设备当前不在主界面
-100 重复录掌（设备端本地检测到该用户掌纹已注册）
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
移动端接口说明
文档版本 v1.8 密级：公开 125
4 移动端接口说明
版本更新记录表
版本号 发布日期 更新内容
1.8.0 2026-3-2 新增管理模块和采集模块接
入方式
优化手掌采集页面
1.7.0 2026-1-5 新增结果码；内部逻辑优
化；解决一些已知问题。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
移动端接口说明
文档版本 v1.8 密级：公开 126
Tencent Palm Mobile Manager SDK 提供了一套完整的移动端掌纹生物识别解决方案，
支持注册、核验和识别三种模式。它包含预构建的 UI 界面和强大的 AI 算法，旨在简化开
发流程，让您的应用能轻松集成全面的掌纹生物识别能力。
核心模块
SDK 由两大核心模块构成：管理模块与采集模块。
管理模块
用户管理中心，
主要负责管理掌纹信息，如：注册用户流程，管理用户掌纹信息：
● 用户管理 - 自动查询/创建用户，展示手掌注册状态（已注册/未注册/预录入）
● 业务流程 - 支持注册、识别(1:N)、核验(1:1)三种模式
● 界面交互 - 展示操作引导、处理结果、错误提示与重试
● 结果处理 - 接收采集结果，自动上报识别/核验记录（提示：需要在刷掌管理平台配置场
景对应 SN 为 PalmMobileManager，才支持记录上报）
● 结果回调 - 仅在关键错误（Token 失效、网关认证失败）或用户退出时回调您的应用
采集模块
手掌信息采集，主要负责采集算法部分，如：采集掌纹、注册/核验/识别：
● 相机采集 - 唤起摄像头，提供实时预览画面
● AI 处理 - 内置掌纹检测、质量评估、活体动作判断等算法能力
● 交互引导 - 引导用户完成"张开手掌"、"握拳"等动作
● 数据上报 - 将采集数据加密上传至服务器，可选上传采集视频
功能特性
● 多种模式：支持注册、核验和识别三种模式，覆盖全面的业务需求。
● 跨平台支持：提供开箱即用的 Android、iOS 与 Flutter 版本 SDK。
● 优化的 AI 算法：在 SDK 内部直接集成了高性能的检测配准、活体判断、质量控制、
动作判断等算法。
● 模块化 UI 组件：为管理和采集模块提供了完整、预构建的 UI，极大缩短了开发周期。
● 安全设计：所有掌纹数据在传输至服务器前均经过自动加密。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
移动端接口说明
文档版本 v1.8 密级：公开 127
核心概念
为了更好地理解本 SDK 采集结果和设备端使用差异，请了解以下特征库的区别：
● 【掌纹】单因子特征库
● 说明: 仅记录【掌纹】单因子信息。因手机摄像头无法采集【掌静脉】，本 SDK 仅采
集【掌纹】单因子信息。
● 【掌纹+掌静脉】双因子特征库
● 说明: 同时记录【掌纹】和【掌静脉】双因子信息。这是用于专业设备录入的高安全标准。
工作流程
1. 获取用户令牌
您的服务端必须首先从 Tencent PalmAI Platform OpenAPI 请求一个与用户 UserId 绑
定的 AccessToken
提示：调用【获取访问凭证】接口时，需要指定 GrantType 类型为
client_credential_user，同时指定 UserId 参数。
您的应用 --[UserId]--> 您的服务端 --[调用 CreateAccessToken]--> Tencent PalmAI
Platform
您的应用 <--[AccessToken]-- 您的服务端 <--[AccessToken]-- Tencent PalmAI
Platform
2. 启动 SDK
使用 AccessToken 和必填用户信息启动本 SDK 的管理模块。
| SDK 模块 | 对接后端 | 说明 |
| **管理模块** | 刷掌业务平台 | 提供完整的掌纹管理界面，从管理页面进入，进行页面交
互后跳转至采集画面，由 SDK 内部处理 result |
| **采集模块** | 刷掌算法平台 | 直接跳转摄像头采集画面，进行掌纹采集及算法处理，由
您自行设计管理页面并处理 result |
根据您的业务需求选择对应模块：
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
移动端接口说明
文档版本 v1.8 密级：公开 128
- **管理模块**：使用 `AccessToken` 和**必填用户信息**启动（`enableManager =
true`）
- **采集模块**：使用 `AccessToken` 和**必填用户信息**启动（`enableManager =
false`）
3. 自动化流程
管理模块会自动完成以下流程，无需您的应用干预：
1. 查询用户注册状态
2. 展示友好的界面和操作提示
3. 根据模式(注册/识别/核验)调用采集模块
4. 接收并处理采集模块的各种情况(成功、权限问题、网络问题、算法结果等)
5. 提示用户重试或展示最终结果
采集模块则需要自己处理 result 结果，其中 code 字段对应本文档中结果码
4. 获取回调
用户点击返回或遇到关键错误时，管理模块会关闭并回调至您的应用，采集模块需要您自己
处理
开发环境要求
为确保 SDK 的稳定运行与兼容性，请确保您的开发环境满足以下最低要求：
平台 要求
Android ● JDK: 17 或更高版本
● Android Gradle Plugin (AGP): 8.5 或
更高版本
● Android Studio: Koala | 2024.1.1 或
更高版本 (以匹配 AGP 要求)
● minSdkVersion: 24
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
移动端接口说明
文档版本 v1.8 密级：公开 129
● compileSdkVersion /
targetSdkVersion: 34+
iOS ● Xcode: 16.0 或更高版本
● Minimum Deployment Target: iOS
13.0
Flutter ● Flutter SDK: 3.25.0 或更高版本
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
移动端接口说明
文档版本 v1.8 密级：公开 130
集成步骤
前置条件：请联系交付人员获取本 SDK 软件包
以下目录结构均以软件包目录结构为准
前置条件：获取授权证书
您需要向我们提供您应用的 Android ApplicationId 和 iOS BundleId，以便我们为您生成
和绑定本 SDK 算法运行时需要的授权证书。
提示：用于 Demo 开发。如果您只是为了开发和测试，可以将应用的 ID 设置为符合
com.tencent.palm.* 通配符的格式（例如 com.tencent.palm.demo）。此方式可以免去申
请授权证书的步骤。
Android 集成
1. 导入 LocalMavenRepo 仓库
将 Android/repo 拷贝至您的项目下，例如 [YOUR_PROJECT]/app/repo.
2. 配置 app/build.gradle 文件
// ...
repositories {
// ... 其他仓库
maven {
name = "LocalMavenRepo"
url = uri("${projectDir}/repo") // 确保路径正确
}
}
dependencies {
// ... 其他依赖
implementation "com.tencent.palm:PalmMobileManager:0.0.0-dev"
}
3. 简要调用示例
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
移动端接口说明
文档版本 v1.8 密级：公开 131
PalmMobileManager.Params params = new
PalmMobileManager.Params.Builder(USER_TOKEN, USER_ID, USER_NAME,
USER_PHONE_NO)
// 设置模式（可选，默认为 REGISTRATION）
// .setMode(PalmMobileManager.Mode.VERIFICATION)
// .setTargetId(TARGET_USER_ID)
// 您也可以设置自己的 Tencent PalmAI Platform 服务器配置。
// .setBaseUrl(BASE_URL)
// .setAppId(APP_ID)
// 可以自定义 HTTP 请求头来访问您配置的 BaseUrl 所对应的网关（如传递
JWT Token）
// .addCustomHeader("Authorization", "YOUR_JWT_TOKEN")
// 您可以选择启动管理模块或采集模块
// - true: 启动管理模块（默认）
// - false: 启动采集模块
// .setEnableManager(true)
.build();
PalmMobileManager.start(this, params, result -> {
// TODO: 根据 result.code 处理业务逻辑
Log.i("PalmMobileManager", result.code + ": " + result.message);
// 使用采集模块时, 您需要自己对 result 的结果进行分析
// 请参考 README 中的 code 和 message 映射关系，data 中包含了 result
的详细信息
});
4. 参考示例工程
详见 Android/example 工程项目
iOS 集成
1. 导入 Framework
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
移动端接口说明
文档版本 v1.8 密级：公开 132
将 iOS/Frameworks/PalmMobileManager.xcframework 拖入您的 Xcode 项目，并确保
在 "General" -> "Frameworks, Libraries, and Embedded Content" 中设置为 "Embed
& Sign"。
2. 配置相机权限
在 Info.plist 文件中添加 Privacy - Camera Usage Description (相机权限使用描述)，
并填写对用户可见的说明文字。
3. 简要调用示例
let params = PalmMobileManagerParams(
token: token,
userId: userId,
userName: userName,
phoneNo: phoneNo,
)
// 设置模式（可选，默认为 registration）
// params.mode = .verification
// params.targetUserId = TARGET_USER_ID
// 您也可以设置自己的 Tencent PalmAI Platform 服务器配置。
// params.appId = APP_ID
// params.baseUrl = BASE_URL
// 可以自定义 HTTP 请求头来访问您配置的 BaseUrl 所对应的网关（如传递 JWT
Token）
// params.addCustomHeader(
// withKey: "Authorization",
// value: "YOUR_JWT_TOKEN"
// )
// 您可以选择启动管理模块或采集模块
// - true: 启动管理模块（默认）
// - false: 启动采集模块
// params.enableManager = true
PalmMobileManager.start(
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
移动端接口说明
文档版本 v1.8 密级：公开 133
from: controller,
params: params,
completion: { result in
// TODO: 根据 result.code 处理业务逻辑
print(result.code, result.message)
// 使用采集模块时, 您需要自己对 result 的结果进行分析
// 请参考 README 中的 code 和 message 映射关系，data 中包含了
result 的详细信息
}
}
)
4. 参考示例工程
详见 iOS/example 工程项目
Flutter 集成
1. 导入插件
将 flutter/palm_mobile_manager 放置于项目下的 packages 目录 (如果不存在请创建)。
[YOUR_FLUTTER_APP]/
├── packages/
│ └── palm_mobile_manager/ <-- 插件目录
├── lib/
...
└── pubspec.yaml
2. 添加依赖
在 [YOUR_FLUTTER_APP]/pubspec.yaml 中添加本地路径依赖：
dependencies:
flutter:
sdk: flutter
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
移动端接口说明
文档版本 v1.8 密级：公开 134
# ... 其他依赖
palm_mobile_manager:
path: packages/palm_mobile_manager
version: 0.0.0-dev
3. 添加 Android LocalMavenRepo 路径
在 [YOUR_FLUTTER_APP]/android/build.gradle.kts (或 build.gradle) 中添加 Maven
仓库路径：
allprojects {
repositories {
google()
mavenCentral()
// add next config to local maven repo
maven {
url =
uri(rootDir.resolve("../packages/palm_mobile_manager/android/repo"))
}
}
}
4. iOS 配置相机权限
在 [YOUR_FLUTTER_APP]/iOS/Runner/Info.plist 中添加
NSCameraUsageDescription
<key>NSCameraUsageDescription</key>
<string>需要相机权限以进行掌纹扫描。</string>
5. 简要调用示例
final params = Params(
token: _tokenController.text,
userId: _userIdController.text,
phoneNo: _phoneNoController.text,
userName: _userNameController.text,
// 设置模式（可选，默认为 REGISTRATION）
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
移动端接口说明
文档版本 v1.8 密级：公开 135
// mode: Mode.verification,
// targetUserId: TARGET_USER_ID,
// 您也可以设置自己的 Tencent PalmAI Platform 服务器配置。
// appId: APP_ID, // YOUR OWN APP ID
// baseUrl: BASE_URL,
);
Result result;
try {
result = await _palmMobileManager.start(params);
print('Success! Result from native: $result');
} catch (e) {
result = Result(code: -1, message: e.toString());
print('Error! Failed to start: $e');
}
6. 参考示例工程
详见 flutter/palm_mobile_manager/example 工程项目
API 参考
Params
启动 SDK 时的配置参数对象。
提示：必填参数+可选参数在启动 SDK 传入时，仅进行非空、非法校验，否则返回
code=10001。接入方应遵循下述格式要求，否则会在管理模块提示用户网络相关错误。
必填参数
参数 类型 描述
token String 用户身份令牌，用于授权本次 SDK 操作。
userId String 用户唯一标识符。
格式要求：4-32 字节，仅支持字母、数字等 ASCII 图形字符
（ASCII 范围：33-126）。
userName String 用户名称。
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
移动端接口说明
文档版本 v1.8 密级：公开 136
可选参数
格式要求：1-64 字节（UTF8 编码）。支持脱敏处理。
phoneNo String 用户手机号。
格式要求：纯数字、包含区号，如 (+86)13800138000。支持脱敏处
理。
参数 类型 默认值 描述
mode Mode REGISTRATION 业务模式。可选值：
• REGISTRATION -
注册模式
• VERIFICATION -
核验模式 (1:1)
• RECOGNITION -
识别模式 (1:N)
targetUserId String - 待核验的目标用户
ID。
注意：
VERIFICATION 模
式下必需。
appId int 223 应用 ID，由服务方
提供。
baseUrl String https://app.intl.pal
m.tencent.com
API 服务地址。
enableVideoUpload Boolean true 是否上传采集视频。
enableManager Boolean true 是否启动管理模块。
为 `true` 时启动管
理模块，为 `false`
时启动采集模块。
customHeaders Map<String,
String>
- 自定义 HTTP 请求
头。用于访问您配置
的 BaseUrl 所对应
的网关（如传递
JWT Token）
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
移动端接口说明
文档版本 v1.8 密级：公开 137
Result
SDK 退出时通过回调返回的结果对象。
回调结果码
管理模块会自动处理采集模块中的大部分结果。您的应用仅会收到以下结果码的回调：
完整结果码参考
说明：采集模块不会捕获结果码进行内部处理，完整结果码参考如下：
通用结果码
属性 类型 描述
code int 结果码，详见下方回调结果
码列表。
message String 描述信息，仅用于调试。
结果
码 场景 处理建议
0 操作成功或用户主动返
回
无需处理
10001 参数非法 检验参数是否合法，如必填项是否为空，BaseUrl 是否
合法等
10012 Token 无效或过期 重新获取 Token
10401 指定 BaseUrl 网关认
证失败
请联系 BaseUrl 提供者进行技术支持，或添加您网关对
应 jwt 认证信息
结果码 开发说明
0 操作成功（会回调）
10000 未知错误
10001 参数无效（会回调）
10002 用户取消采集操作
10003 相机权限被拒绝
10004 相机初始化失败
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
移动端接口说明
文档版本 v1.8 密级：公开 138
注册模式结果码
识别模式结果码
核验模式结果码
网络结果码
10005 不支持的相机预览尺寸
10006 SDK 初始化失败
10007 SDK 运行时错误
10008 采集超时（30 秒超时）
10012 Token 无效或已过期（会回调）
10016 授权证书验证失败
10017 用户名格式不正确
10018 用户 ID 格式不正确
10019 电话号码格式不正确
结果码 开发说明
10100 活体检测失败
10101 质量检查失败
10102 活体视频验证失败
10103 用户已注册
10104 与已有用户高度相似
结果码 说明
10200 用户未识别
结果码 说明
10200 待验证用户未找特征
10300 待验证用户不存在
10301 待验证用户未注册掌纹
10302 待验证用户未注册当前手掌方向
结果码 说明
10401 网关未认证访问（会回调）
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
移动端接口说明
文档版本 v1.8 密级：公开 139
10500 网络错误
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
移动端接口说明
文档版本 v1.8 密级：公开 140
安全警告
生产环境安全要求
严禁在生产环境的客户端代码中硬编码 SecretId 或 SecretKey！
这会将您的平台账户密钥暴露给所有用户，攻击者可利用这些密钥攻击您的服务，造成严重
损失。
正确做法（生产环境）：
您的应用 --[UserId]--> 您的服务端 --[调用 CreateAccessToken]--> Tencent PalmAI
Platform
您的应用 <--[AccessToken]-- 您的服务端 <--[AccessToken]-- Tencent PalmAI
Platform
测试环境快速启动
仅用于本地开发/内部测试/隔离 Demo 环境，演示如何快速获取 Token
/**
* [仅供测试] 快速获取 Token 并启动 SDK
* 警告：生产环境中，Token 必须从后端服务器获取
*/
private void startForTesting() {
// 初始化 OpenApiService
OpenApiService.init(OPEN_API_URL, APP_ID, SECRET_ID, SECRET_KEY);
CreateAccessTokenRequest req = new CreateAccessTokenRequest(USER_ID);
OpenApiService.getInstance().createAccessToken(req, new
ApiClient.Callback<CreateAccessTokenResponse>() {
@Override
public void onSuccess(CreateAccessTokenResponse response) {
start(response.accessToken); // 使用 Token 启动 SDK
}
PalmAI Standard_刷掌业务平台_
API 对接文档_V1.8
移动端接口说明
文档版本 v1.8 密级：公开 141
@Override
public void onFailure(int code, String message) {
Log.e("PalmMobileManager", "Failed to get token: " + code + " - " +
message);
}
});
}
提示：AppId/BaseUrl/SecretId/SecretKey 需匹配使用。如需测试凭证，请联系技术支
持获取。
后续步骤与支持
● 查阅示例工程: 我们强烈建议您在集成前，先编译并运行对应平台的示例工程，这将帮助
您快速了解 SDK 的完整调用流程。
● 获取技术支持: 如果在集成过程中遇到任何问题，请联系您的技术支持代表。