# 下载七牛文件

## 接口信息

| 项 | 值 |
|---|---|
| 请求方式 | GET |
| URL | 七牛公开下载地址（如 `https://filegpt-hn.file.mediportal.com.cn/{fileKey}`） |
| 需要 token | 否（公开 URL 直接下载） |

## 说明

七牛文件上传成功后返回的 `domain + fileKey` 即为公开下载地址，直接 HTTP GET 即可下载。

## 对应脚本

`scripts/file_storage/qiniu_download.py`
