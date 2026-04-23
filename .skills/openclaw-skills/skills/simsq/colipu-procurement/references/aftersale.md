# 退换货接口

🔁 退换货接口
​

当客户需要退换货时，调用本章节接口将申请信息同步到科力普。

⚠️ 关键校验：若退货 SKU 或数量与原订单不匹配，申请会直接失败。

建议流程
​
提交退换货申请；
查询退换货状态；
根据审核/处理结果推进后续业务。

# 退换货申请

8.1 退换货申请
​

接口说明：

Method	URL	ContentType
POST	api/restful/refund/apply	application/json

请求入参说明：

参数	类型说明	是否必须	长度	描述
apply_code	string	非必须	200	退换货申请编号（默认可不填，返回值会生成返回）
order_id	string	必须	50	退货对应订单编号，
delivery_code	string	非必须	50	发货单号。按照发货单维度售后则必填
apply_type	string	非必须	2	退换货申请类型（4=退货，5=换货，6=维修，7=退款） ,不填写默认是退货
skus	json	非必须		[{"sku":商品编号, "num":商品数量, "price”:价格,"ext1":"现金","ext2":"积分"}] 若skus字段为null则表示整单退。price 表示含税单价，和订单中的一致。
apply_time	string	非必须	0	退换货申请时间（2017-12-18 09:22:07）
apply_reason	string	非必须	200	退换货原因
apply_name	string	非必须	50	退换货联系人（默认订单收货人），不为空时收货人相关信息字段信息必填
apply_mobile	string	非必须	50	退换货联系手机（默认订单收货人手机）
apply_telephone	string	非必须	50	退换货联系固定电话
apply_email	string	非必须	50	退货人电子邮件
pickup_way	string	非必须	10	上门取件、第三方物流（上门=1，第三方=2）默认上门取件
province_code	string	非必须	11	退货人省份编码(默认订单中的编码)
city_code	string	非必须	11	退货人城市编码(默认订单中的编码)
county_code	string	非必须	11	退货人区县编码(默认订单中的地址)
town_code	string	非必须	11	退货人乡镇编码
address	string	非必须	300	地址(默认订单中的地址)
full_address	string	非必须	300	退货人详细地址(默认订单中的地址)例如 1_10_100_1000
extends	json	非必须		[{"ColumnName":"扩展信息名称", "ColumnRemark":"扩展信息备注", "ColumnValue”:"扩展信息值"}]

返回结果说明：

参数	参数说明	描述
apply_code	string	退货申请单编码

请求参数示例：

json
{
    "apply_code":"",
    "skus": [{
        "sku": "201027",
        "num": 10,
        "price": 21.15
    }, {
        "sku": "201030",
        "num": 20,
        "price": 48.6
    }],
    "order_id": "PO001",
    "delivery_code":"756323266",
    "apply_type": "4",
    "apply_time": "2017-12-18 14:11:48",
    "apply_reason": "产品发错",
    "pickup_way": "1",
    "address": "上海市XX区XX号",
	"extends" : [{
			"ColumnName" : "DepartmentName",
			"ColumnRemark" : "下单部门",
			"ColumnValue" : "采购部"
		}
	]
}

返回数据示例：

json
{
    "success": true,
    "errormsg ": "",
    "requestId ": "9245fe4a-d402-451c-b9ed-9c1a04247482",
    "errorcode": 0,
    "result": {
        " apply_code ": "RO001"
    }
}

# 退换货取消

8.2 退换货取消
​

客户取消退换货调用接口

接口说明：

Method	URL	ContentType
POST	api/restful/refund/cancle	application/json

请求入参说明：

参数	类型说明	是否必须	长度	描述
apply_code	string	必须	200	退换货申请编号
order_id	string	必须	200	订单编号
delivery_code	string	非必须	50	发货单号。按照发货单维度售后则必填
operator	string	非必须	200	操作人

返回结果说明：

参数	描述	参数说明
result	null	null

请求参数示例：

json
{
    "apply_code": "RO001",
    "order_id": "PO001",
    "delivery_code":"789233266"
}

返回数据示例：

json
{
    "success": true,
    "errormsg": "",
    "requestId ": "9245fe4a-d402-451c-b9ed-9c1a04247482",
    "errorcode": 0,
    "result": null
}

# 获取退货单信息

8.3 获取退货单信息
​

根据退货单申请编号查询退货状态。

接口说明：

Method	URL	ContentType
GET	api/restful/refund/query	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
apply_code	string	必须	200	退换货申请编号
order_id	string	非必须	200	订单编号
delivery_code	string	非必须	50	发货单号。按照发货单维度售后则必填

返回结果说明：

参数	参数说明	描述
apply_code	string	退货申请单编码
refund_code	string	退货单编码
apply_status	string	退货状态0=待审核1=审核通过2=客户取消3=对接方客服取消4=审核不通过
apply_type	string	退货类型4=退货5=换货
apply_time	string	退货时间
order_id	string	订单编号
refund_status	string	审核流程状态 30301 =退货中30305 =客户已发货30310 =对接方已收货30315=对接方已重新发货30320 =客户已收货30325=客户结束流程30330=客服结束流程
apply_reason	string	申请原因
apply_name	string	申请人姓名
apply_mobile	string	申请人手机号
apply_telephone	string	申请人电话
pickup_way	string	取货方式:上门取件、第三方物流（上门=1，第三方=2）默认上门取件
province_code	string	省
city_code	string	市
county_code	string	区
address	string	地址
full_address	string	全量地址
skus	json	退换货商品sku
请求参数示例：		
json
{
    "apply_code": "RO__20210615090903382",
    "orderId": "2106100015",
    "delivery_code":"78956362"
}

返回数据示例：

json
{
    "success": true,
    "errormsg ": "",
    "requestId ": "9245fe4a-d402-451c-b9ed-9c1a04247482",
    "errorcode": 0,
    "result": {
        "apply_code": "RO__20210615090903382",
        "refund_code": "RO__20210615090903382",
        "orderId": "2106100015",
        "delivery_code":"78956362",
        "apply_type": "4",
        "apply_status": "0",
        "refund_status": "0",
        "apply_time": "06/15/2021 09:09:02",
        "apply_reason": "售后测试123445321",
        "apply_name": "张三",
        "apply_mobile": "17628282828",
        "apply_telephone": "17628282828",
        "pickup_way": "1",
        "province_code": "6",
        "city_code": "303",
        "county_code": "36783",
        "address": "西矿街147号比亚迪店",
        "full_address": "6_303_36783_",
        "skus": [
            {
                "sku": "1032817",
                "num": 2,
                "price": 30.48
            },
            {
                "sku": "1050256",
                "num": 2,
                "price": 6552.0
            }
        ]
    }
}

# 退货完成

8.4 退货完成
​

当第三方和客户商城在退货流程完成之后，需要客户进行退货完成确认。

接口说明：

Method	URL	ContentType
POST	api/restful/refund/finish	application/json

请求入参说明：

参数	类型说明	是否必须	长度	描述
apply_code	string	必须	200	退换货申请编号
order_id	string	必须	200	退换货订单编号
delivery_code	string	非必须	50	发货单号。按照发货单维度售后则必填

返回结果说明：

参数	描述	参数说明
result	null	null

请求参数示例：

json
{
    "apply_code": "RO001",
    "order_id": "PO001",
    "delivery_code":"78956233"
}

返回数据示例：

json
{
    "success": true,
    "errormsg ": "",
    "requestId ": "9245fe4a-d402-451c-b9ed-9c1a04247482",
    "errorcode": 0,
    "result": null
}