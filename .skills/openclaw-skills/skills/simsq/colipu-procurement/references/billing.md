# 对账查询(按创建时间)

7.1.1 对账查询(按创建时间)
​

接口说明：

Method	URL	ContentType
GET	/api/restful/order/signstatus	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述	备注
order_id	string	非必须	50	订单编号	
start_date	datetime	必须		开始时间yyyy-MM-dd	此时间为订单创建时间
end_date	datetime	必须		结束时间yyyy-MM-dd	此时间为订单创建时间

返回结果说明：

参数	类型说明	描述
order_id	string	订单编号
status	int	订单状态 0 新建订单；1 妥投订单； 2 拒收订单（取消和拒收都是拒收）； 5 发货订单
create_date	string	订单创建时间

请求参数示例：

/api/restful/order/signstatus?start_date=2019/12/01&end_date=2019/12/03

返回数据示例：

json
{
    "result": [
        {
            "order_id": "PO-mg-20191128104355812",
            "status": 30,
            "create_date": "12/02/2019 15:15:38"
        }
    ],
    "success": true,
    "errormsg": "",
    "errorcode": "0",
    "requestId": "7f7a776e-788a-4ea8-98a6-e0df358ea7ed"
}

# 对账查询(按签收时间)

7.1.2 对账查询(按签收时间)
​

接口说明：

Method	URL	ContentType
POST	/api/restful/order/sign-info	application/json

请求入参说明：

参数	类型说明	是否必须	描述	备注
start_date	datetime	必须	格式为yyyy-MM-dd，此时间为订单签收时间	
end_date	datetime	必须	格式为yyyy-MM-dd，此时间为订单签收时间	
page	int	必须	页号，必须大于0	
page_size	datetime	必须	页大小，每页最多返回100条	

返回结果说明：

参数	类型说明	描述	示例值
metaData	对象	包含元数据信息的容器	-
totalItemCount	整数	订总数目	10
pageCount	整数	总页数	5
items	数组	包含多个订单详情的对象数组	-
order_id	字符串	订单的唯一标识符	240126180853851214
details	数组	订单商品详情数组	-
sku	字符串	商品的唯一标识符	1033838
signed_count	整数	签收数量	5
signed_amount	浮点数	签收金额	86.95

请求参数示例：

/api/restful/order/sign-info

返回数据示例：

json
{
	"success": true,
	"requestId": "5f8cbf48f6014c0bbc66e9f65361ad93",
	"result": {
		"metaData": {
			"totalItemCount": 10,
			"pageCount": 5
		},
		"items": [{
				"details": [{
						"sku": "1033838",
						"signed_count": 5,
						"signed_amount": 86.95
					},
					{
						"sku": "1033892",
						"signed_count": 5,
						"signed_amount": 62.95
					},
					{
						"sku": "3254560",
						"signed_count": 1,
						"signed_amount": 50.05
					}
				],
				"order_id": "240126180853851214"
			},
			{
				"details": [{
						"sku": "WF2029312",
						"signed_count": 6,
						"signed_amount": 1590.00
					},
					{
						"sku": "225005",
						"signed_count": 13,
						"signed_amount": 4200.30
					}
				],
				"order_id": "240227190380291214"
			}
		]
	},
	"errorcode": "0",
	"errormsg": ""
}

# 订单对账(按订单维度)

7.1.3 订单对账(按订单维度)
​

接口说明：

Method	URL	ContentType
POST	api/restful/order/statement	application/json

请求入参说明：

参数	类型说明	是否必须	长度	描述
数组	list	必须	200	订单编号组

请求参数示例：

json
["ED202004171440001", "ED202004161846001"]

返回数据示例：

参数	类型说明	描述
order_id	string	订单编号
status	Int	订单状态 0：新建5：发货-2：取消-1：拒收1：签收4：退换货中
refundStatus	Int	退换货状态 0：无退换货操作 1：退换货中 2：已完成退换货
create_date	string	订单创建时间
skus	json	[{"sku":"188030",//商品编号"price":2,//商品单价"count":15,//商品数量"signedCount":10,//签收数量"signedAmount":20,//签收金额"returnCount":5,//退货数量"returnAmount":10,//退货金额}]

请求参数示例：

json
{
   "success": true,
   "errormsg ": "",
   "requestId ": "9245fe4a-d402-451c-b9ed-9c1a04247482",
   "errorcode": 0,
   "result": {
   	[{
   		"order_id": "ED202004171440001",
   		"status": 2,
   		"create_date": "2019-09-17 10:52:55",
   		"skus": [{
   			"sku": "1054349",
   			"price": 379,
   			"count": 1,
   			"signedCount": 1,
   			"signedAmount": 379,
   			"returnCount": 0,
   			"returnAmount": 0
   		}, {
   			"sku": "188030",
   			"price": 195,
   			"count": 1,
   			"signedCount": 1,
   			"signedAmount": 195,
   			"returnCount": 1,
   			"returnAmount": 195
   		}]
   	}, {
   		"order_id": "ED202004161846001",
   		"status": 2,
   		"create_date": "2019-09-24 16:21:58",
   		"skus": [{
   			"sku": "188030",
   			"price": 195,
   			"count": 1,
   			"signedCount": 1,
   			"signedAmount": 195,
   			"returnCount": 0,
   			"returnAmount": 0
   		}, {
   			"sku": "223015",
   			"price": 78.2,
   			"count": 1,
   			"signedCount": 1,
   			"signedAmount": 78.2,
   			"returnCount": 1,
   			"returnAmount": 78.2
   		}]
   	}]
   }
}

# 结算单申请

7.2.1 结算单申请
​

接口说明（订单维度或者发货单维度）：

Method	URL	ContentType
POST	api/restful/apiBill	application/json

请求入参说明：

参数	类型说明	是否必须	长度	描述
bill_no	string	必须	200	结算单号
order_ids	string	非必须	200	发票请求订单号批量以 ,号分割。 order_ids 和 delivery_codes不能同时为空
delivery_codes	string	非必须	200	发票请求 发货单号批量以 ,号分割。order_ids 和 delivery_codes不能同时为空
mark_id	string	必须	200	第三方申请发票的唯一id标识
settle_num	int	非必须	11	结算单订单总数
settle_naked_price	double	必须	0	结算单不含税总金额（裸价）
settle_tax_price	double	必须	0	结算单总税价
invoice_type	int	必须	11	发票类型1：增票 2：普票 3：电子发票 4：全电专票 5：全电普票
invoice_content	string	必须	500	开票内容
invoice_date	datetime	非必须	0	期望开票时间 yyyy-MM-dd
invoice_title	string	必须	200	发票抬头
invoice_address	string	必须	500	发票地址
invoice_phone	string	必须	100	发票电话
invoice_tax_num	string	必须	100	税号
invoice_bank	string	必须	100	发票开户行
invoice_bank_accout	string	必须	100	银行账号
invoice_company_name	string	必须	100	收票单位
bill_toer	string	必须	50	收票人
bill_to_contact	string	必须	50	收票人联系方式
bill_to_province	string	必须	50	收票人地址（省编码）
bill_to_city	string	必须	50	收票人地址（市编码）
bill_to_county	string	必须	50	收票人地址（区编码）
bill_to_town	string	必须	50	收票人地址（镇编码）
bill_to_address	string	必须	500	收票人全量地址
repayment_date	datetime	非必须	0	预计还款时间
bill_to_email	string	非必须	200	邮箱
remark	string	非必须	200	备注
extends	json	非必须		[{"ColumnName":"扩展信息名称", "ColumnRemark":"扩展信息备注", "ColumnValue”:"扩展信息值"}]

请求参数示例：

json
{
    "bill_no": "BO20180606162632",
    "order_ids": "PO201801091623,PO201801091625,PO201801091626",
    "delivery_codes":"7566923326",
    "mark_id": "100001",
    "settle_num": 3,
    "settle_naked_price": 100.1,
    "settle_tax_price": 5,
    "invoice_type": 1,
    "invoice_content": "明细",
    "invoice_date": "2018/05/14 ",
    "invoice_title": "上海晨光科力普有限公司",
    "invoice_address": "上海晨光科力普有限公司古美路1528号",
    "invoice_phone": " 888888888 ",
    "invoice_tax_num": 666666666,
    "invoice_bank": "中国银行",
    "invoice_bank_accout": "99999999",
    "invoice_company_name": "上海晨光科力普有限公司",
    "bill_toer": "晨光测试",
    "bill_to_contact": "18701744139 ",
    "bill_to_province": "16",
    "bill_to_city": "1315",
    "bill_to_county": "1316",
    "bill_to_town": "53522",
    "bill_to_address": "上海市徐汇区古美路1528号",
    "repayment_date": "2018/12/14",
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
    "result": "",
    "success": true,
    "errormsg ": "",
    "requestId ": "9245fe4a-d402-451c-b9ed-9c1a04247482",
    "errorcode": "0"
}

# 结算单申请(部分)

7.2.2 结算单申请(部分)
​

接口说明：

Method	URL	ContentType
POST	api/restful/apiBillPart	application/json

请求入参说明：

参数	类型说明	是否必须	长度	描述
bill_no	string	必须	200	结算单号
order_info	json	必须		订单信息:[{"order_id":"订单号","sku_info":[{"sku":"商品编号","num":"商品数量"}]}]
mark_id	string	必须	200	第三方申请发票的唯一id标识
settle_num	int	非必须	11	结算单订单总数
settle_naked_price	double	必须	0	结算单不含税总金额（裸价）
settle_tax_price	double	必须	0	结算单总税价
invoice_type	int	必须	11	发票类型1：增票 2：普票 3：电子发票 4：全电专票 5：全电普票
invoice_content	string	必须	500	开票内容
invoice_date	datetime	非必须	0	期望开票时间 yyyy-MM-dd
invoice_title	string	必须	200	发票抬头
invoice_address	string	必须	500	发票地址
invoice_phone	string	必须	100	发票电话
invoice_tax_num	string	必须	100	税号
invoice_bank	string	必须	100	发票开户行
invoice_bank_accout	string	必须	100	银行账号
invoice_company_name	string	必须	100	收票单位
bill_toer	string	必须	50	收票人
bill_to_contact	string	必须	50	收票人联系方式
bill_to_province	string	必须	50	收票人地址（省编码）
bill_to_city	string	必须	50	收票人地址（市编码）
bill_to_county	string	必须	50	收票人地址（区编码）
bill_to_town	string	必须	50	收票人地址（镇编码）
bill_to_address	string	必须	500	收票人全量地址
repayment_date	datetime	非必须	0	预计还款时间
bill_to_email	string	非必须	200	邮箱
remark	string	非必须	200	备注

请求参数示例：

json
{
    "bill_no": "BO20180606162632",
    "order_info" : [{
         "order_id": "CG123456",
          "sku_info": [{
               "sku": "3041983",
               "num": 2
           }]
     }],
    "mark_id": "100001",
    "settle_num": 3,
    "settle_naked_price": 100.1,
    "settle_tax_price": 5,
    "invoice_type": 1,
    "invoice_content": "明细",
    "invoice_date": "2018/05/14 ",
    "invoice_title": "上海晨光科力普有限公司",
    "invoice_address": "上海晨光科力普有限公司古美路1528号",
    "invoice_phone": " 888888888 ",
    "invoice_tax_num": 666666666,
    "invoice_bank": "中国银行",
    "invoice_bank_accout": "99999999",
    "invoice_company_name": "上海晨光科力普有限公司",
    "bill_toer": "晨光测试",
    "bill_to_contact": "18701744139 ",
    "bill_to_province": "16",
    "bill_to_city": "1315",
    "bill_to_county": "1316",
    "bill_to_town": "53522",
    "bill_to_address": "上海市徐汇区古美路1528号",
    "repayment_date": "2018/12/14"
}

返回数据示例：

json
{
    "result": "",
    "success": true,
    "errormsg ": "",
    "requestId ": "9245fe4a-d402-451c-b9ed-9c1a04247482",
    "errorcode": "0"
}

# 开票查询

7.3 开票查询
​

接口说明：

Method	URL	ContentType
GET	/api/restful/apiBill/{mark_id}/invoice	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
mark_id	string	必须	200	第三方申请发票唯一标识

返回结果说明：

参数	类型说明	描述
invoice_code	string	发票代码
invoice_num	string	发票号码
invoice_date	string	发票日期
invoice_naked_amount	double	发票金额（裸价）
invoice_tax_rate	double	发票税率
invoice_tax_amount	double	发票税额
invoice_amount	double	价税合计
invoice_type	int	发票类型
invoice_urls	list	发票链接

请求参数示例：

/api/restful/apiBill/100001/invoice

返回数据示例：

json
{
    "result": [{
        "invoice_code": "A0001",
        "invoice_num": "1001",
        "invoice_date": "2018-06-11 00:00:00",
        "invoice_naked_amount": 100,
        "invoice_tax_rate": 1.5,
        "invoice_tax_amount": 1,
        "invoice_amount": 100,
        "invoice_type": 1,
        "invoice_urls": [
				"https://clpres.oss-cn-shanghai.aliyuncs.com/cip/project/HuaDian/e-invoice-demo.png"
    }],
    "success": true,
    "errormsg": "",
    "errorcode": "",
    "requestId": "9245fe4a-d402-451c-b9ed-9c1a04247482"
}

# 查询电子发票

7.4 查询电子发票
​

接口说明：

Method	URL	ContentType
POST	/api/restful/getEInvoiceList	application/json

请求入参说明：

参数	类型说明	是否必须	描述
order_ids	string	必须	订单编号，多个订单以英文逗号分隔

返回结果说明：

参数	参数说明	描述
result	map	key为订单编号，value为发票图片数组

请求示例：

{ "order_ids": "CG20220117155300002, CG20220117155300003" }

响应示例：

json
{
	"result": {
		"success": true,
		"result": {
			"CG20220117155300002": [
				"https://clpres.oss-cn-shanghai.aliyuncs.com/cip/project/HuaDian/e-invoice-demo.png",
				"https://clpres.oss-cn-shanghai.aliyuncs.com/cip/project/HuaDian/e-invoice-demo.png"
			],
			"CG20220117155300003": [
				"https://clpres.oss-cn-shanghai.aliyuncs.com/cip/project/HuaDian/e-invoice-demo.png"
			]
		}
	},
	"success": true,
	"errormsg": "",
	"errorcode": "0",
	"requestId": "c33740bc-cef0-4882-8e64-ee03c5f17764"
}