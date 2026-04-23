# 上传到七牛

## 流程（两步）

### Step 1：获取上传凭证

| 项 | 值 |
|---|---|
| 请求方式 | GET（fallback POST） |
| URL | `https://sg-cwork-api.mediportal.com.cn/ai-business/qiNiu/getSimpleUploadCredentials` |
| 需要 token | 是（`access-token` Header） |

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| fileKey | string | 是 | 文件 key（如 `1774421851829-report.pdf`） |
| corpId | string | 否 | 企业 ID（可为空） |

**响应**：

```json
{
  "resultCode": 1,
  "data": {
    "token": "1TVghGd...",
    "domain": "https://filegpt-hn.file.mediportal.com.cn"
  }
}
```

### Step 2：上传文件到七牛

| 项 | 值 |
|---|---|
| 请求方式 | POST multipart/form-data |
| URL | `https://up-z2.qiniup.com/` |
| 需要 token | 否（使用 Step 1 的七牛 token） |

**Form 字段**：

| 字段 | 说明 |
|------|------|
| token | Step 1 获取的七牛 token |
| key | fileKey |
| file | 文件二进制数据 |

## 对应脚本

`scripts/file_storage/qiniu_upload.py`
