# Media Saber MCP Tool Reference

This reference is aligned with your latest MCP server response (toolCount=28).

Connection baseline:

- type: streamable-http
- url: http://localhost:22698/message
- auth header: Authorization: Bearer <API_KEY>

## 1) add_offline_download

Description: 添加云下载任务

Params:

- link (string, required): 链接, 仅支持: ed2k、magnet 资源链接

Example:

```json
{"link":"magnet:?xt=urn:btih:..."}
```

## 2) cloud_share_receive

Description: 云存储转存

Params:

- link (string, required): 链接, 仅支持: 115 资源链接

Example:

```json
{"link":"https://115.com/s/xxxx"}
```

## 3) get_media_servers

Description: 查询媒体服务列表

Params: none

## 4) get_media_status

Description: 查询媒体状态，例如：已发布站点列表、是否已入库等。

Params:

- tmdbId (integer, required)
- mediaType (string, required): movie | tv

Example:

```json
{"tmdbId":603,"mediaType":"movie"}
```

## 5) get_miss_episodes

Description: 查询媒体库中有漏集的电视剧

Params: none

## 6) get_site_data

Description: 查询站点数据

Params:

- name (string, optional): 站点名称

## 7) get_site_message

Description: 查询站点消息

Params:

- name (string, optional): 站点名称

## 8) get_site_notice

Description: 查询站点公告

Params:

- name (string, optional): 站点名称

## 9) get_sites

Description: 查询站点

Params:

- name (string, optional): 站点名称

## 10) get_tmdb_info

Description: 获取电影/电视剧 TMDB 信息

Params:

- tmdbId (integer, required)
- mediaType (string, required): movie | tv

## 11) get_zspace_system_state

Description: 获取极空间系统状态和硬件配置信息

Params: none

## 12) recommend_movies

Description: 推荐电影

Params:

- country (string, optional): 空 | zh | en | ja | ko | fr | de | ru | hi
- sort (string, optional): 空 | popularity.desc | vote_average.desc | release_date.desc
- tag (string, optional): 空 | 28 | 12 | 16 | 35 | 80 | 99 | 18 | 10751 | 14 | 36 | 27 | 10402 | 9648 | 10749 | 878 | 10770 | 53 | 10752 | 37
- year (string, optional): 空 | 2026-2026 | 2025-2025 | 2024-2024 | 2023-2023 | 2022-2022 | 2021-2021 | 2020-2020 | 2010-2019 | 2000-2009 | 1990-1999 | 1980-1989 | 1970-1979 | 1000-1959

## 13) recommend_tvs

Description: 推荐电视剧

Params:

- sort (string, optional): 空 | popularity.desc | vote_average.desc | first_air_date.desc
- tag (string, optional): 空 | 10759 | 16 | 35 | 80 | 99 | 18 | 10751 | 10762 | 9648 | 10763 | 10764 | 10765 | 10766 | 10767 | 10768 | 37
- year (string, optional): 空 | 2026-2026 | 2025-2025 | 2024-2024 | 2023-2023 | 2022-2022 | 2021-2021 | 2020-2020 | 2010-2019 | 2000-2009 | 1990-1999 | 1980-1989 | 1970-1979 | 1000-1959
- country (string, optional): 空 | zh | en | ja | ko | fr | de | ru | hi

## 14) refresh_subscribe

Description: 刷新订阅列表, 立即开始搜索、下载电影或电视剧

Params: none

## 15) search_tmdb

Description: 搜索电影/电视剧 TMDB 信息

Params:

- query (string, required)
- mediaType (string, required): movie | tv

## 16) site_sign_in

Description: 站点签到

Params: none

## 17) subscribe_movie

Description: 订阅电影, 订阅成功后会自动搜索、下载电影

Params:

- tmdbId (integer, required)

## 18) subscribe_tv

Description: 订阅电视剧, 订阅成功后会自动搜索、下载电视剧

Params:

- tmdbId (integer, required)
- season (integer, required)
- beginEpisode (integer, optional)
- episodes (array, optional)

## 19) sync_libraries

Description: 同步媒体库

Params: none

## 20) sync_site_data

Description: 同步站点数据

Params: none

## 21) sync_site_message

Description: 同步站点消息

Params: none

## 22) sync_site_notice

Description: 同步站点公告

Params: none

## 23) test_network

Description: 网络连接测试

Params: none

## 24) test_site

Description: 站点测试

Params: none

## 25) test_site_rss

Description: 站点 RSS 测试

Params: none

## 26) today_site_data

Description: 查询站点数据今日汇总，例如：总上传量、总下载量

Params: none

## 27) total_site_data

Description: 查询站点总数据，例如：上传、下载、魔力、做种数、做种体积等统计数据信息。

Params: none

## 28) update_site_configs

Description: 更新站点适配文件

Params: none

## Practical prompt templates

- 帮我搜索 复仇者联盟 (movie)，确认后订阅并刷新。
- 查询 tmdbId=1399, mediaType=tv 的状态，并检查是否有漏集。
- 给我推荐 2024 年高分电影，地区 zh，返回 5 个结果。
- 执行站点签到并同步数据、消息、公告，最后输出汇总。
- 把这个 magnet 链接添加为离线下载任务。
