# 装备决策框架（Gear Framework）

按级别和板型定义装备决策规则。Agent 基于这些规则动态生成装备清单。

```yaml
gear_framework:
  level_0:
    snowboard:
      must_have: [头盔（必戴）, 护腕（必戴）, 雪镜, 防水手套, 速干内衣, 抓绒中间层, 防水外套, 防水裤]
      recommended: [护臀, 护膝, 防晒霜, 暖宝宝]
      rental: [雪板, 雪鞋, 固定器]
      note: 第一次不需要购买装备全部租用滑 3 天后再决定
    ski:
      must_have: [头盔（必戴）, 雪镜, 防水手套, 速干内衣, 抓绒中间层, 防水外套, 防水裤]
      recommended: [护膝, 防晒霜, 暖宝宝]
      rental: [雪板, 雪鞋, 雪杖]
      note: 第一次不需要购买装备全部租用滑 3 天后再决定

  level_1:
    snowboard:
      must_have: [头盔, 护腕, 雪镜, 防水手套, 速干内衣, 抓绒中间层, 防水外套, 防水裤, 护臀]
      recommended: [护膝, 面罩, 防晒霜]
      rental_or_buy: 滑 3 天后可考虑购买雪鞋和固定器雪板继续租用
    ski:
      must_have: [头盔, 雪镜, 防水手套, 速干内衣, 抓绒中间层, 防水外套, 防水裤]
      recommended: [护膝, 面罩, 防晒霜]
      rental_or_buy: 滑 3 天后可考虑购买雪鞋雪板和雪杖继续租用

  level_2:
    snowboard:
      must_have: [头盔, 护腕, 雪镜, 防水手套, 速干内衣, 抓绒中间层, 防水外套, 防水裤, 护臀, 护膝]
      recommended: [备用雪镜片, 面罩, 随身工具包]
      consider_buy: [自有雪板（根据风格选择板型）, 自有固定器, 自有雪鞋]
      carving: [选择 Camber 板型腰宽 245-255mm]
      freestyle: [选择 Twin Tip 板型更短更软]
      freeride: [选择 Directional 板型更宽浮力更好]
    ski:
      must_have: [头盔, 雪镜, 防水手套, 速干内衣, 抓绒中间层, 防水外套, 防水裤]
      recommended: [护膝, 备用雪镜片, 面罩]
      consider_buy: [自有雪板（根据风格选择）, 自有雪鞋, 自有固定器]

  level_3:
    snowboard:
      must_have: [头盔, 护腕, 雪镜, 防水手套, 速干内衣, 抓绒中间层, 防水外套, 防水裤, 护臀, 护膝]
      recommended: [备用装备, 随身工具包, 雪崩安全装备（道外必带）]
      carving: [Camber 高性能刻滑板腰宽 250-260mm 硬度 7-9]
      freestyle: [Twin Tip 公园板长度下巴到鼻子之间硬度 5-7]
      freeride: [Directional 野雪板腰宽 105mm 以上长度 +3-5cm]
      powder: [雪崩搜救仪探杆雪铲（道外必带）]
    ski:
      must_have: [头盔, 雪镜, 防水手套, 速干内衣, 抓绒中间层, 防水外套, 防水裤]
      recommended: [备用装备, 随身工具包]
      carving: [Camber 高性能卡宾板腰宽 68-80mm 硬度 7-9]
      mogul: [更短更软的蘑菇板长度鼻尖到眉毛之间]
      freeride: [野雪板腰宽 100mm 以上长度 +5cm]
      powder: [雪崩搜救仪探杆雪铲（道外必带）]
```
