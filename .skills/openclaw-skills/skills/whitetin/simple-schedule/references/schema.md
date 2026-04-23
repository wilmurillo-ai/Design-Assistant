# 数据结构定义

## 日程对象 ScheduleItem

```python
{
  "id": str,              # UUID，唯一标识
  "type": "schedule" | "ddl", # 类型：行程/DDL截止日期
  "datetime": str,        # ISO 8601 格式：行程是到达时间，DDL是截止时间
  "where": str|null,      # 目的地（DDL不需要可为null）
  "what": str,            # 做什么/DDL事项
  "from_address": str|null, # 出发地（可选，没填用默认，DDL不需要）
  "duration_minutes": int|null, # 路程耗时分钟数（地图计算得出，DDL不需要）
  "created_at": str,      # 创建时间 ISO 8601
  "updated_at": str,      # 最后更新时间 ISO 8601
  "remind_departure_at": str|null, # 出发提醒时间 ISO 8601（行程用）
  "remind_arrive_at": str,    # 到达/DDL提醒时间 ISO 8601
  "remind_ddl_1day_before": str|null, # DDL提前一天提醒时间
  "remind_ddl_1hour_before": str|null # DDL提前一小时提醒时间
}
```

## 存储文件格式 schedule.json

```json
{
  "version": 1,
  "schedules": [ScheduleItem...]
}
```

## 配置文件格式 config.json

```json
{
  "amap_api_key": "",
  "default_start_address": "家",
  "buffer_minutes": 10,
  "same_location_remind_before_minutes": 10,
  "data_path": "~/.openclaw/workspace/data/simple-schedule/schedule.json",
  "config_path": "~/.openclaw/workspace/data/simple-schedule/config.json"
}
```
