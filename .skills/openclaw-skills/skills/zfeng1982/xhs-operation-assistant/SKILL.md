---
name: xhs-operation-assistant
displayName: 小红书运营助手
author: sardinesInQianhai
description: 自媒体博主必备,获取小红书官方帐号最新笔记,热点话题,种草话题
metadata: { "openclaw": { "emoji": "🔍︎",  "requires": { "bins": ["curl"], } }
---
# 小红书运营助手
自媒体博主必备
  - 获取小红书官方帐号最新笔记,包括官方最新活动和小红书近期运营重点  
  - 获取热点话题,包括平台热点和种草热点
## 描述
1. 官方笔记查询(/xhs/get_op_note_list)：支持分页、按账号精确匹配、按类型精确匹配、按描述模糊搜索（不区分大小写）。
2. 官方帐号列表(/xhs/get_op_account_list)：返回所有运营账号及其描述，不分页、无过滤。
3. 热点话题列表(/xhs/get_hot_topic):返回平台热点或种草热点,最多40条,无需分页

## 基础 URL
默认：`http://119.29.63.139/`
---
## 1.获取小红书官方笔记列表和内容接口
 - 返回数据按时间从新到旧排序
 - 如果没有指定笔记类型(note_type)和笔记账号(note_account),则返回最新的官方笔记 
 - 由于小红书笔记详情页必须从帐号首页跳到详情页,不要使用id拼url直接跳转,只能用account_url跳到帐号首页
```
GET /xhs/get_op_note_list
```
- ### 请求参数（全部可选）
| 参数              | 类型      | 默认值 | 说明                                                                                                            |
|-----------------|---------|-----|---------------------------------------------------------------------------------------------------------------|
| `page`          | integer | 1   | 页码，从 1 开始  ,参数最大为 100，超出会被服务端限制为 100。                                                                         |
| `page_size`     | integer | 20  | 每页记录数，最大 100                                                                                                  |
| `note_account`  | string  | -   | 笔记账号，精确匹配 ,帐号可由/xhs/get_op_account_list接口获取,中文使用URL编码                                                         |
| `note_type`     | string  | -   | 笔记类型，精确匹配,包括创作类,综合类,安全类,周边类,美妆类,生活类,学习求职类,娱乐类,运动类,旅行类,摄影类,艺术类,直播带货类,家居类,宠物类,运营类,美食类,公益类,数码类,汽车类,游戏类,中文使用URL编码 |
| `note_desc`     | string  | -   | 笔记描述，模糊包含匹配（不区分大小写）,中文使用URL编码;模糊匹配是基于内存的字符串包含，性能与缓存数据量成正比（通常 < 10 万条无压力）。                                                                                |
- ### 响应格式
JSON 数组，每个元素包含以下字段：
```json
{
  "note_id": "string",
  "note_type": "string",
  "note_account": "string",
  "account_url": "string",
  "note_title": "string or null",
  "note_desc": "string or null",
  "note_date": "string or null"
}
```
- ### curl 示例
```bash

# 基础分页查询（第一页，每页 10 条）
curl "http://119.29.63.139/xhs/get_op_note_list?page=1&page_size=10"
# 按账号精确查询
curl "http://119.29.63.139/xhs/get_op_note_list?note_account=%40%E8%96%AF%E9%98%9F%E9%95%BF"
# 按类型查询 + 分页
curl "http://119.29.63.139/xhs/get_op_note_list?note_type=%E5%AE%98%E6%96%B9%E5%8F%B7&page=1&page_size=20"
# 按描述模糊搜索（包含“旅游”）
curl "http://119.29.63.139/xhs/get_op_note_list?note_desc=%E6%97%85%E6%B8%B8"
# 组合条件
curl "http://119.29.63.139/xhs/get_op_note_list?note_account=%40%E8%96%AF%E9%98%9F%E9%95%BF&note_type=%E5%AE%98%E6%96%B9%E5%8F%B7&note_desc=%E9%BB%91%E5%AE%A2%E6%9D%BE&page=1&page_size=5"
```
---
## 2.获取小红书所有官方账号列表接口
op_url可直接跳转到帐号首页
```
GET /xhs/get_op_account_list
```
- ### 请求参数
无
- ### 响应格式
JSON 数组，每个元素包含：
```json
{
  "op_account": "string",
  "op_url": "string",
  "op_desc": "string or null"
}
```
- ### curl 示例
```bash

curl "http://119.29.63.139/xhs/get_op_account_list"
```
---

## 3.获取热点话题
```
GET /xhs/get_hot_topic
```
- ### 请求参数
| 参数              | 类型      | 默认值 | 说明                                                                                                            |
|-----------------|---------|-----|---------------------------------------------------------------------------------------------------------------|
| `hot_rank`          | integer | -   | 话题分类:1为平台热点话题,2为种草热点话题
- ### 响应格式
JSON 数组，按热点指数降序排序,每个元素包含：  
hot_title:话题  
hot_heat_index:热点指数  
hot_search_url:小红书搜索链接  
```json
{
  "hot_title": "string",
  "hot_heat_index": "string",
  "hot_search_url": "string or null"
}
```
- ### curl 示例
```bash
# 获取平台热点话题
curl "http://119.29.63.139/xhs/get_hot_topic?hot_rank=1"
```
---
## 4.健康检查接口（可选）
- ### curl 示例
```bash

curl "http://119.29.63.139/health"
```
- ### 返回示例：
```json
{
  "status": "ok",
  "cached_notes": 240,
  "cached_accounts": 48
}
```

