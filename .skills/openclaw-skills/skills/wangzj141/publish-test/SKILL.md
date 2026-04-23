

蚁小二插件使用说明

核心能力
1、内容发布
2、账号数据与作品数据查询


完整接口文档参考
https://s.apifox.cn/e66df935-0c39-44d0-8096-abd39417fa6a/llms.txt

### 基础域名与鉴权 (Base URL & Authentication)
- **Base URL**: `https://www.yixiaoer.cn/api`
- **鉴权方式 / Auth**: 在 HTTP Header 中传参 `Authorization: <api-key>`


核心能力引导

接口调用需要用户提供龙虾插件授权令牌apikey
检查当前团队是否为vip，如果不是，则返回该团队未开通vip不支持使用小龙虾插件

1、内容发布
找到【 创建任务集v2对接开放平台】  接口填充表单数据，publishChannel为cloud，clientId参数不要传（切记不要传空字符串），local则需要提醒用户将clientId告诉你。如果涉及到平台个性化信息，则需要查询 【获取活动分类】，【获取账号音乐】【获取账号音乐分类】【获取账号地理位置】，并将接口返回的信息合理插入到表单的对应字段


如果涉及到视频或图片上传，参考【 获取资源直传地址】，发布填写 cloud-publish，contentType需要填写和上传对象一直的类型，且在返回的serviceUrl后，同样需要设置一样的contentType，上传方式为Binary，上传地址切记不能转码，容易被curl转义。



账号数据查询为：【账号概览-新版】
作品数据则为：【作品数据列表】

其他能力请基于完整的接口文档去探索吧