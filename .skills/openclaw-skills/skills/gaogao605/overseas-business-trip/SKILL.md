name: overseas-business-trip-suite
displayName: 海外商旅一体化套件
description: 海外航班查询、酒店预订、差旅校验、预订支付、自动报销一体化 Skill
version: 1.0.0
author: your-name
protocol: mcp
type: composite

inputSchema:
  type: object
  required:
    - user_id
    - dep_city
    - arr_city
    - dep_date
    - checkin
    - checkout
  properties:
    user_id:
      type: string
      description: 员工工号
    dep_city:
      type: string
      description: 出发城市
    arr_city:
      type: string
      description: 到达城市
    dep_date:
      type: string
      format: date
      description: 出发日期
    checkin:
      type: string
      format: date
      description: 入住日期
    checkout:
      type: string
      format: date
      description: 离店日期
    route_type:
      type: string
      enum: [direct, all]
      default: direct
    pay_method:
      type: string
      enum: [company, personal]
      default: company

outputSchema:
  type: object
  properties:
    success:
      type: boolean
    flight_order_id:
      type: string
    hotel_order_id:
      type: string
    expense_id:
      type: string
    message:
      type: string

instruction: |
  本 Skill 为海外商旅全流程自动化套件，执行流程：
  1. 查询海外直飞航班
  2. 校验差旅政策与额度
  3. 机票预订与企业支付
  4. 酒店预订与企业支付
  5. 自动生成并提交报销单
  全程由 Agent 自动执行，无需人工干预。