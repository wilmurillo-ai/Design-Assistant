# 预下订单

6.1 预下订单
​
Method	URL	ContentType
POST	/api/restful/order	application/json

请求入参说明：

如下参数均可配置 必填/非必填，可结合贵司业务流程联系科力普技术同学进行配置。
​
参数	类型说明	是否必须	长度	描述
yggc_order	string	必须	50	订单单号
name	string	必须	50	收货人
province	string	必须	50	一级地址
province_name	string	非必须	50	一级地址名称
city	string	必须	50	二级地址
city_name	string	非必须	50	二级地址名称
county	string	必须	50	三级地址
county_name	string	非必须	50	三级地址名称
town	string	非必须	50	四级地址
town_name	string	非必须	50	四级地址名称
purchaser	string	非必须	50	采购人
address	string	必须	300	详细地址
zip	string	非必须	10	邮编
customer_code	string	非必须	50	客户编码
phone	string	必须	50	座机号 (与mobile其中一个有值即可)
mobile	string	必须	50	手机号 （与phone其中一个有值即可）
email	string	非必须	50	邮箱
remark	string	非必须	500	备注（少于100字）
invoice_title	string	非必须	100	发票抬头，个人或公司名称
invoice_type	int	非必须	1	发票类型 1：纸质专用发票 2：纸质普通发票 3：电子普通发票 4:全电专用发票 5：全电普通发票
invoice_tax_num	string	非必须	20	发票税号
invoice_bank	string	非必须	100	发票开户行 发票类型为"增票" 必填
invoice_bank_account	string	非必须	50	发票银行账号 发票类型为"增票" 必填
invoice_address	string	非必须	100	发票地址 发票类型为"增票" 必填
invoice_phone	string	非必须	50	发票电话 发票类型为"增票" 必填
payment	int	必须	11	支付方式 9：账期支付（默认值）
order_price	double	必须	19,6	订单金额（包含运费）
freight	double	必须	19,6	运费（与业务确认）
sku	json	必须		[{"sku":"商品编号","num":商品数量,"price":含税单价,"naked_price":未税单价,"tax_price":商品税额,"tax_rate":税率,"naked_price_total":商品未税总额,"tax_price_total":商品税额合计,"price_total":商品含税总价/商品小计,"name":"商品名称","remark":"测试订单行备注","ext1":"扩展信息1","ext2":"扩展信息2","lineNo":0,"customSkuExt":[{"columnName":"扩展信息名称","columnRemark":"扩展信息备注","columnValue":"扩展信息值"}]}] ，其中sku，num，price为必填字段，其他字段非必填
extends	json	非必须		[{"ColumnName":"扩展信息名称", "ColumnRemark":"扩展信息备注", "ColumnValue":"扩展信息值"}]
dep_name	string	非必须	200	采购单位名称
purchaserPhone	string	非必须	50	下单人电话
purchaserMobile	string	非必须	50	下单人手机号
purchaserEmail	string	非必须	50	下单人邮箱

返回结果说明：

参数	类型说明	描述
yggc_order	string	订单单号
order_price	double	订单价格
order_naked_price	double	订单裸价
order_taxprice_total	double	订单税额合计
skus	json	[{ "sku": "商品编号1","num": 商品数量,"price": 含税单价,"naked_price": 未税单价,"tax_price": 商品税额,"tax_rate":税率,"naked_price_total": 商品未税总额,"tax_price_total": 商品税额合计,"price_total": 商品含税总价/商品小计]

请求参数示例：

json
{
	"yggc_order" : "CG202104190001",
	"name" : "CG测试订单",
	"province" : 110000,
	"province_name" : "上海",
	"city" : 110000,
	"city_name" : "上海市",
	"county" : 110101,
	"county_name" : "徐汇区",
	"purchaser" : "采购人",
	"address" : "古美路1553号",
	"zip" : "000000",
	"phone" : "021-12345678",
	"mobile" : "12345678901",
	"email" : "test@colipu.com",
	"remark" : "备注测试",
	"invoice_title" : "上海晨光科力普有限公司",
	"invoice_type" : 1,
	"invoice_tax_num" : "6216654512000235698",
	"invoice_bank" : "中国工商银行",
	"invoice_bank_account" : "987654321",
	"invoice_address" : "发票地址测试",
	"invoice_phone" : "1002546587",
	"payment" : 10,
	"order_price" : 0,
	"freight" : 0,
	"sku" : [{
                "sku": "164012",
                "num": 1,
                "price": 2.1,
                "naked_price": 1.86,
                "tax_price": 0.24,
                "tax_rate": 0.13,
                "naked_price_total": 1.86,
                "tax_price_total": 0.24,
                "price_total": 2.1,
                "name" : "科力普测试商品",
                "remark": "订单行备注",
				"ext1":"",
				"ext2":"",
				"customSkuExt":[
					{
						"columnName":"purchaserName",
						"columnRemark":"采购员名称",
						"columnValue":"张三"
					}
				]
            }
	],
	"extends" : [{
			"ColumnName" : "DepartmentName",
			"ColumnRemark" : "下单部门",
			"ColumnValue" : "采购部"
		}
	],
	"dep_name" : "采购单位名称",
	"purchaserPhone" : "12345678901",
	"purchaserMobile" : "12345678901"
}

返回数据示例：

json
{
    "result": {
        "yggc_order": "CG202104190001",
        "order_price": 2.1,
        "order_naked_price": 1.86,
        "order_taxprice_total": 0.24,
        "skus": [
            {
                "sku": "164012",
                "num": 1,
                "price": 2.1,
                "naked_price": 1.86,
                "tax_price": 0.24,
                "tax_rate": 0.13,
                "naked_price_total": 1.86,
                "tax_price_total": 0.24,
                "price_total": 2.1
            }
        ]
    },
    "success": true,
    "errormsg": "",
    "errorcode": "0",
    "requestId": "6d020fc3-4d97-47dc-926f-80e3e2b0c6c7"
}

# 确认订单

6.2 确认订单
​

接口说明：

Method	URL	ContentType
PATCH/POST	/api/restful/order/{order_id}/confirmation	application/json

请求入参说明：

支持整单确认、部分确认、确认时修改数量（默认为整单确认）

参数	类型说明	是否必须	长度	描述
order_id	string	必须	50	预下订单号
platformOrderDetails	json	非必须		当无请求体时，则为整单确定的情况 [{"sku":"商品编号", "quantity":确认数量,"ext1":"扩展字段"}]
extends	json	非必须		[{"columnName":"扩展信息名称", "columnRemark":"扩展信息备注", "columnValue:"扩展信息值"}]

返回结果说明：

参数	描述
result	null

请求参数示例：

/api/restful/order/CG20190428175212384/confirmation

json
{
    "platformOrderDetails": [
        {
            "sku": "sku",
            "quantity": 0,
            "ext1":"XXXXX"
        }
    ],
    "extends": [{
        "columnName": "sapOrderCode",
        "columnRemark": "SAP订单号",
        "columnValue": "59XXXXXXX"
    }]
}

返回数据示例：

json
{
    "result": "",
    "success": true,
    "errormsg": "",
    "errorcode": "0",
    "requestId": "a2ad326c185e40c2adda695103d99e46"
}

# 取消订单

6.3 取消订单
​

接口说明：

Method	URL	ContentType
PATCH/POST	/api/restful/order/{order_id}/cancellation	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
order_id	string	必须	50	预下订单号

请求入参说明：

参数	类型说明	是否必须	长度	描述
extends	json	非必须		[{"columnName":"扩展信息名称", "columnRemark":"扩展信息备注", "columnValue:"扩展信息值"}]

返回结果说明：

参数	描述
result	null

请求参数示例：

/api/restful/order/CG20190428175212384/cancellation

返回数据示例：

json
{
    "result": "",
    "success": true,
    "errormsg": "",
    "errorcode": "0",
    "requestId": "a2ad326c185e40c2adda695103d99e46"
}

# 获取订单状态

6.4.1 获取订单状态
​

接口说明：

Method	URL	ContentType
GET	/api/restful/order/{order_id}/status	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
order_id	string	必须	50	预下订单号

返回结果说明：

参数	类型说明	描述
orderId	string	预下订单编号
state	int	状态0：新建5：发货-2：取消-1：拒收1：签收

请求参数示例：

/api/restful/order/CG20190428175212384/status

返回数据示例：

json
{
    "result": {
        "orderId": "CG20190428175212384",
        "state": -2
    },
    "success": true,
    "errormsg": "",
    "errorcode": "0",
    "requestId": "06796339f44a4521ae5748db76316a8c"
}

# 获取发货单状态

6.4.2 获取发货单状态
​

接口说明：

Method	URL	ContentType
GET	/api/restful/order/{delivery_code}/delivery-status	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
delivery_code	string	必须	50	发货单号

返回结果说明：

参数	类型说明	描述
delivery_code	string	发货单号
state	int	状态0：新建5：发货-2：取消-1：拒收1：签收

请求参数示例：

/api/restful/order/756698995252/delivery-status

返回数据示例：

json
{
    "result": {
        "delivery_code": "756698995252",
        "state": -2
    },
    "success": true,
    "errormsg": "",
    "errorcode": "0",
    "requestId": "06796339f44a4521ae5748db76316a8c"
}

# 获取订单信息

6.5 获取订单信息
​

根据 订单编号(子订单/母订单) 查询订单明细接口、返回订单信息。
1、默认不拆单，如需要拆单请联系对接人员。
2、不拆单的情况下，子订单号与母订单号相同。

接口说明：

Method	URL	ContentType
GET	api/restful/order/{order_id}/query	application/json

URL 参数说明：

参数	类型说明	是否必须	长度	描述
order_id	string	必须	50	订单号

母订单/不拆单返回结果：

参数	类型说明	描述
order_type	int	订单类型（1：母订单 2：子订单）
order_id	string	母订单编号
full_address	string	收货详细地址
receiver	string	收货人
tel	string	收货人电话
mobile	string	收货人手机号
order_price	double	订单金额
c_orders	json	[{ "order_id":"子订单编号","porder_id":"母订单编号","order_type" : 订单类型（1：母订单 2：子订单）,"logistics_state" : 订单物流状态（0 新建； - 1 拒收； - 2 已取消；1 妥投完成；5 已出库）,"submit_state" : 订单处理状态（ - 1 取消 0 未确认 1 已确认）,"skus":[{"sku": "商品货号", "price": 商品价格, "num": 商品数量, "name" : "商品名称"}]}]
skus	json	[{"sku" : "商品货号","price" : 商品价格,"num" : 商品数量, "name" : "商品名称" }]
remark	string	备注
子订单返回结果说明：		
参数	类型说明	描述
order_type	int	订单类型 1：母订单 2：子订单
order_id	string	子订单编号
order_price	double	订单金额
porder_id	string	母订单编号
logistics_state	int	订单物流状态 0：新建-1： 拒收-2 ：已取消 1：妥投完成 5 ：已出库
submit_state	int	订单处理状态-1：取消 0 ：未确认 1：已确认
full_address	string	收货详细地址
receiver	string	收货人
tel	string	收货人电话
mobile	string	收货人手机号
skus	json	[{ "sku": "商品货号", "price": 商品价格, "num": 商品数量, "name" : "商品名称"}]
remark	string	备注

请求参数示例：/api/restful/order/Mo000001/query

母订单返回数据示例：

json
{
  "success": true,
  "errormsg ": "",
  "requestId ": "9245fe4a-d402-451c-b9ed-9c1a04247482",
  "errorcode": 0,
  "result": {
    "order_type": 1,
    "order_id": "Mo000001",
    "full_address": "收货详细地址",
    "receiver": "收货人",
    "tel": "收货人电话 ",
    "mobile": "收货人手机号",
    "c_orders": [
      {
        "order_id": "PO201806211653",
        "porder_id": "Mo000001",
        "order_type": 2,
        "logistics_state": 0,
        "submit_state": 0,
        "skus": [
          {
            "sku": "101091",
            "price": 1.35,
            "num": 100
          },
          {
            "sku": "102018",
            "price": 5.63,
            "num": 100
          }
        ]
      }
    ]
  }
}

不拆单示例:

json
{
    "success": true,
    "requestId": "668d183d26314639befa2d5b7bd65b29",
    "result": {
        "order_type": 1,
        "order_id": "Mo000001",
        "order_price": 12.6,
        "full_address": "福建南平市政和县岭腰乡飒飒撒",
        "receiver": "oiuyt",
        "tel": "18777777771",
        "mobile": "11111111111",
        "c_orders": [
            {
                "order_id": "Mo000001",
                "porder_id": "Mo000001",
                "order_type": 2,
                "logistics_state": 1,
                "submit_state": 1,
                "skus": [
                    {
                        "sku": "1067957",
                        "price": 2.52,
                        "num": 5,
                        "name": "晨光 M＆G 磁粒 ASC99366 30mm  8个/卡"
                    }
                ]
            }
        ]
    },
    "errorcode": "0",
    "errormsg": ""
}

子订单返回数据示例：

json
{
  "success": true,
  "errormsg ": "",
  "requestId ": "9245fe4a-d402-451c-b9ed-9c1a04247482",
  "errorcode": 0,
  "result": {
    "order_type": 2,
    "order_id": "PO201806211653",
    "porder_id": "Mo000001",
    "logistics_state": 0,
    "submit_state": 0,
    "full_address": "收货详细地址",
    "receiver": "收货人",
    "tel": "收货人电话 ",
    "mobile": "收货人手机号",
    "skus": [
      {
        "sku": "101091",
        "price": 1.35,
        "num": 100
      },
      {
        "sku": "102018",
        "price": 5.63,
        "num": 100
      }
    ]
  }
}

# 批量获取订单状态

6.6 批量获取订单状态
​

接口说明：

Method	URL	ContentType
POST	/api/restful/order/states/query	application/json

请求入参说明：

类型说明	是否必须	描述
字符串数组	必须	预下订单号，多个单号以英文逗号分隔；可参考示例代码

返回结果说明：

参数	类型说明	描述
orderId	string	预下订单编号
state	int	状态0：新建5：发货-2：取消-1：拒收1：签收

请求参数示例：

json
[
  "WY20200211002286","XZ20200207001522","WY20191230041606"
]

返回数据示例：

json
{
  "result": [
    {
      "orderId": "WY20200211002286",
      "state": 1
    },
    {
      "orderId": "XZ20200207001522",
      "state": 0
    },
    {
      "orderId": "WY20191230041606",
      "state": 1
    }
  ],
  "success": true,
  "errormsg": "",
  "errorcode": "0",
  "requestId": "5614c765-2379-4231-9aea-db1b852e6d83"
}

# 订单确认收货

6.7 订单确认收货
​

接口说明：

Method	URL	ContentType
POST	/api/restful/order/receiveConfirm	application/json

请求入参说明：

类型说明	类型说明	是否必填	备注
order_id	string	必须	订单号
delivery_code	string	非必须	发货单号。按照发货单维度则必填
receive_time	string	必须	确认收货时间
remark	string	非必须	备注
platform_order_status	int	非必须	收货状态： 90：待确认收货，100：确认收货
details	json	非必须	[{"sku":"商品编号", "receive_count":收货数量, "price:"商品单价","remark:"备注"}]

请求参数示例：

json
{
  "order_id": "XXXX",
  "delivery_code":"7662266989",
  "receive_time": "2020-04-29 13:50:55",
  "remark": "备注信息",
  "platform_order_status":90,
  "details":[{
	"sku":"1051983",
	"receive_count":10,
	"price":10.50,//商品单价
	"remark":"备注",
  }]
}

返回数据示例：

json
{
  "result": "",
  "success": true,
  "errormsg": "",
  "errorcode": "0",
  "requestId": "7ee1b064-4cf0-4c22-b38c-12c0508cf649"
}

# 批量查询订单

6.8 批量查询订单
​

接口说明：

Method	URL	ContentType
GET	/api/restful/order/order_code/{start_time}/{end_time}	application/json

URL参数说明：

类型说明	类型说明	是否必须	描述
start_time	datetime	必须	开始时间
end_time	datetime	必须	结束时间

请求参数示例：

json
/api/restful/order/order_code/2020-9-1/2020-9-8

返回数据示例：

json
{
    "result": [
        "CG20200907150043001"
    ],
    "success": true,
    "errormsg": "",
    "errorcode": "0",
    "requestId": "154cd572-8df7-4855-a8f1-b7b1cfaa3c10"
}

# 订单撤销

6.9 订单撤销
​

接口说明：订单确认后，可以通过此接口进行订单撤销，我司通过消息接口反馈撤销审核结果

Method	URL	ContentType
Post	/api/restful/order/retreat	application/json

请求入参说明：

类型说明	类型说明	是否必须	描述
order_id	string	必须	订单号
skus	list	非必须	商品明细，如果是整单取消，此字段无需回传

请求参数示例：

json
/api/restful/order/retreat
json
{
	"order_id": "CG202410301653",
	"skus": [{
		"sku": 商品编号,
		"num": 商品数量
	}]
}

返回数据示例：

json
{
    "result": "",
    "success": true,
    "errormsg": "",
    "errorcode": "0",
    "requestId": "a2ad326c185e40c2adda695103d99e46"
}