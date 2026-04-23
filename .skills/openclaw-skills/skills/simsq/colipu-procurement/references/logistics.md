# 查询订单物流轨迹

9.1.1.1 查询订单物流轨迹
​

接口说明：

Method	URL	ContentType
GET	/api/restful/order/{order_id}/logistics	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
order_id	string	必须	200	预下订单号

返回结果说明：

参数	描述
result	null

请求参数示例：

/api/restful/order/PO20181115150235837/logistics

返回数据示例：

json
{
    "result" : {
        "orderTrack" : [
            {
                "content": "【圆通速递】【YT000000000】您的快件被【四川省成都市土桥镇】揽收，揽收人: 李德茂 (18521177971)",
                "OperateTime": "2023-06-26 18:29:37",
                "Operator": "系统"
            },
            {
                "content": "【圆通速递】【YT000000000】您的快件离开【四川省成都市土桥镇】，已发往【成都转运中心公司】",
                "OperateTime": "2023-06-26 18:30:37",
                "Operator": "系统"
            }, 
            {
                "content": "【圆通速递】【YT111122222】您的快件被【四川省成都市土桥镇】揽收，揽收人: 李德茂 (18521177971)",
                "OperateTime": "2023-06-26 18:29:37",
                "Operator": "系统"
            },
            {
                "content": "【圆通速递】【YT111122222】您的快件离开【四川省成都市土桥镇】，已发往【成都转运中心公司】",
                "OperateTime": "2023-06-26 18:30:37",
                "Operator": "系统"
            },
            {
                "content": "您的包裹7115333634已分配到仓库",
                "OperateTime": "2023-06-26 23:57:07",
                "Operator": "系统"
            },
            {
                "content": "您提交了订单，系统处理中",
                "OperateTime": "2023-06-26 23:57:40",
                "Operator": "系统"
            }
        ],
        "orderId" : "PO190521000233"
    },
    "success" : true,
    "errormsg" : "",
    "errorcode" : "0",
    "requestId" : "74496963-d576-46fe-a8a9-694e10717988"
}

# 查询发货单物流轨迹

9.1.1.2 查询发货单物流轨迹
​

接口说明

Method	URL	ContentType
GET	/api/restful/order/{delivery_code}/logistics/delivery	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
delivery_code	string	必须	200	发货单号

返回结果说明：

参数	类型说明	描述
delivery_code	string	发货单号
logistics_company_name	string	物流公司名称
logistics_number	string	物流单号
order_track	list	物流轨迹[{"content":"","operate_time":"","operator":""}]

请求参数示例：

json

/api/restful/order/DD190521000233/logistics/delivery

返回数据示例：

json
{
	"success": true,
	"requestId": "075F5297-6C4C-43A9-B6B4-DE196D17CAF7",
	"result": {
		"delivery_code": "2408101341544250",
		"logistics_company_name": "德邦快递",
		"logistics_number": "DPK369075955497",
		"order_track": [{
				"content": "您的订单已被收件员揽收,【北京朝阳区广渠东路经营分部】库存中，部门电话：010-80909434",
				"operate_time": "2024-08-12 17:40:44",
				"operator": "系统"
			},
			{
				"content": "运输中，离开【北京朝阳区广渠东路经营分部】，下一部门【天津枢纽中心】",
				"operate_time": "2024-08-12 20:51:19",
				"operator": "系统"
			},
			{
				"content": "派送中，德邦已开启“安全呼叫”，保护您的电话隐私，小哥今日将为您配送，也可联系小哥将包裹放置指定地点，祝您身体健康。,派送人：杨善银,电话:13296402286",
				"operate_time": "2024-08-14 20:25:35",
				"operator": "系统"
			},
			{
				"content": "正常签收，签收人类型：本人，如有疑问请联系：13296402286",
				"operate_time": "2024-08-16 16:38:06",
				"operator": "系统"
			}
		]
	},
	"errorcode": "0",
	"errormsg": ""
}

# 查询物流明细

9.1.2.1 查询物流明细
​

接口说明

Method	URL	ContentType
GET	/api/restful/order/{order_id}/logistics/tracks	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
order_id	string	必须	200	预下订单号

返回结果说明：

参数	类型说明	描述
package_id	string	发货单号
logistics_company_name	string	物流公司
logistics_number	string	物流单号
logistics_number	json	物流轨迹

请求参数示例：

json

/api/restful/order/PO20181115150235837/logistics/tracks

返回数据示例：

{
	"success": true,
	"requestId": "075F5297-6C4C-43A9-B6B4-DE196D17CAF7",
	"result": [{
		"package_id": "2408101341544250",
		"logistics_company_name": "德邦快递",
		"logistics_number": "DPK369075955497",
		"order_track": [{
				"content": "您的订单已被收件员揽收,【北京朝阳区广渠东路经营分部】库存中，部门电话：010-80909434",
				"operate_time": "2024-08-12 17:40:44",
				"operator": "系统"
			},
			{
				"content": "运输中，离开【济南转运场】，下一部门【【H】济南济阳县崔寨镇营业部】",
				"operate_time": "2024-08-14 08:12:39",
				"operator": "系统"
			},
			{
				"content": "正常签收，签收人类型：本人，如有疑问请联系：13296402286",
				"operate_time": "2024-08-16 16:38:06",
				"operator": "系统"

			}
		]
	}],
	"errorcode": "0",
	"errormsg": ""
}

# 查询包裹明细

9.1.2.2 查询包裹明细
​

接口说明

Method	URL	ContentType
GET	/api/restful/order/{packageId}/logistics/package	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
packageId	string	必须	200	包裹单号

返回结果说明：

参数	类型说明	描述
sku	string	商品编号
quantity	int	商品数量

请求参数示例：

/api/restful/order/PO20181115150235837/logistics/package

返回数据示例：

json
{
    "success": true,
    "requestId": "068E608D-97DD-4F9C-BE0B-C61C0E162525",
    "result": [
        {
            "sku": "148019",
            "quantity": 1
        }
    ],
    "errorcode": "0",
    "errormsg": ""
}

# 查询物流轨迹和包裹明细

9.1.3 查询物流轨迹和包裹明细
​

接口说明

Method	URL	ContentType
GET	/api/restful/order/{order_id}/logistics/tracks-package	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
order_id	string	必须	200	预下订单号

返回结果说明：

参数	类型说明	描述
package_id	string	包裹单号
logistics_company_name	string	物流公司名称
logistics_number	string	物流单号
sku_list	list	商品明细[{"sku":"","quantity":0}]
order_track	list	物流轨迹[{"content":"","operate_time":"","operator":""}]

请求参数示例：

json

/api/restful/order/DD190521000233/logistics/tracks-package

返回数据示例：

json
{
	"success": true,
	"requestId": "075F5297-6C4C-43A9-B6B4-DE196D17CAF7",
	"result": [{
		"package_id": "2408101341544250",
		"logistics_company_name": "德邦快递",
		"logistics_number": "DPK369075955497",
		"sku_list": [{
			"sku": "148019",
			"quantity": 2
		}],
		"order_track": [{
				"content": "您的订单已被收件员揽收,【北京朝阳区广渠东路经营分部】库存中，部门电话：010-80909434",
				"operate_time": "2024-08-12 17:40:44",
				"operator": "系统"
			},
			{
				"content": "运输中，离开【北京朝阳区广渠东路经营分部】，下一部门【天津枢纽中心】",
				"operate_time": "2024-08-12 20:51:19",
				"operator": "系统"
			},
			{
				"content": "派送中，德邦已开启“安全呼叫”，保护您的电话隐私，小哥今日将为您配送，也可联系小哥将包裹放置指定地点，祝您身体健康。,派送人：杨善银,电话:13296402286",
				"operate_time": "2024-08-14 20:25:35",
				"operator": "系统"
			},
			{
				"content": "正常签收，签收人类型：本人，如有疑问请联系：13296402286",
				"operate_time": "2024-08-16 16:38:06",
				"operator": "系统"
			}
		]
	}],
	"errorcode": "0",
	"errormsg": ""
}

# 查询物流签收信息

9.1.4 查询物流签收信息
​

接口说明

Method	URL	ContentType
GET	/api/restful/order/{order_id}/logistics-sign-info	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
order_id	string	必须	200	预下订单号

返回结果说明：

参数	类型说明	描述
expressInfo	json	{"expressName":"快递公司","expressTime":"快递时间","expressNo":"快递单号"}
deliverInfo	json	{"deliver":"快递员","deliverTime":"配送时间","deliverDesc":"快递员手机号等信息"}
receiveInfo	json	{"receiveTime":"签收时间","receiveDesc":"签收信息"}
orderId	string	预下订单号

请求参数示例：

json

/api/restful/order/DD190521000233/logistics-sign-info

返回数据示例：

{
	"result": {
		"expressInfo": {
			"expressName": "德邦快递",
			"expressTime": "2023-09-18 21:38:08",
			"expressNo": "DPK0000000001"
		},
		"deliverInfo": {
			"deliver": "张三",
			"deliverTime": "2023-09-19 13:54:07",
			"deliverDesc": "15500001111"
		},
		"receiveInfo": {
			"receiveTime": "2023-09-19 13:54:30",
			"receiveDesc": "已签收，签收人类型：同事"
		},
		"orderId": "DD190521000233"
	},
	"success": true,
	"errormsg": "",
	"errorcode": "0",
	"requestId": "74496963-d576-46fe-a8a9-694e10717988"
}

# 查询订单签收凭证信息

9.1.5 查询订单签收凭证接口
​

接口说明

Method	URL	ContentType
GET	/api/restful/order/{orderId}/order-sign-receipt	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
orderId	string	必须	200	预下订单号

返回结果说明：

参数	类型说明	描述
orderId	string	预下订单号
signInfos	json	签收信息
deliveryCompany	string	发货公司
paths	json	签收凭证
photos	json	发货照片

请求参数示例：

json

/api/restful/order/DD20230331405206284285/order-sign-receipt

返回数据示例：

{
    "success": true,
    "requestId": "898C5E61-67E9-4C6F-81A3-385DF1CED215",
    "result": {
        "orderId": "DD20230331405206284285",
        "signInfos": [
            {
                "deliveryCompany": "科力普",
                "paths": [
                    "https://clpres.oss-cn-shanghai.aliyuncs.com/cip/prd/apiprojects/hubeinonghang/DD20230331405206284285/7114363107/1_WF319383.jpg"
                ]，
“photos”:[
  "https://clpres.oss-cn-shanghai.aliyuncs.com/cip/prd/apiprojects/hubeinonghang/DD20230331405206284285/7114363107/1_WF319383.jpg"
]
            },
            {
                "deliveryCompany": "德邦快递",
                "paths": [
                    "https://clpres.oss-cn-shanghai.aliyuncs.com/cip/prd/apiprojects/hubeinonghang/DD20230331405206284285/7114363106/33617_6811135.jpg"
                ]
            }
        ]
    },
    "errorcode": "0",
    "errormsg": ""
}

# 发票物流接口

9.2 发票物流接口
​

接口说明：

Method	URL	ContentType
GET	/api/restful/invoice/logistics	application/json

URL 参数说明：

参数	类型说明	是否必须	长度	描述
invoiceNo	string	必须	50	发票号码
invoiceCode	string	必须	50	发票代码

返回结果说明：

参数	描述
result	null

请求参数示例：

json
/api/restful/invoice/logistics?invoiceNo=XXX&invoiceCode=XXXX

返回数据示例：

json
{
	"result": {
		"trackInfo": [{
				"content": "您的快件已签收，如有疑问请电联小哥【XXX，电话：XXXXX】。疫情期间顺丰每日对网点消毒、小哥每日测温、配戴口罩，感谢您使用顺丰，期待再次为您服务。（主单总件数：1件）",
				"operateTime": "2020-12-21 09:14:14"
			},
			{
				"content": "快件交给XXXX,正在派送途中（联系电话：XXXXX,顺丰已开启安全呼叫保护您的电话隐私,请放心接听！）（ 主单总件数： 1 件)",
				"operateTime": "2020-12-19 12:10:08"
			},
			{
				"content": "快件已发车",
				"operateTime": "2020-12-19 11:15:42"
			},
			{
				"content": "快件到达 【西安沣东集散中心】",
				"operateTime": "2020-12-19 10:18:00"
			},
			{
				"content": "快件到达【西安】，准备发往【西安沣东集散中心】",
				"operateTime": "2020-12-19 08:23:00"
			},
			{
				"content": "快件在【上海飞往西安航班上】已起飞",
				"operateTime": "2020-12-19 06:06:00"
			},
			{
				"content": "快件在【上海总集散中心】已装车,准备发往 【西安沣东集散中心】",
				"operateTime": "2020-12-19 03:01:46"
			},
			{
				"content": "快件到达 【上海总集散中心】",
				"operateTime": "2020-12-19 01:54:08"
			},
			{
				"content": "快件已发车",
				"operateTime": "2020-12-19 00:48:55"
			},
			{
				"content": "快件在【上海浦江集散中心】已装车,准备发往 【上海总集散中心】",
				"operateTime": "2020-12-19 00:48:37"
			},
			{
				"content": "快件到达 【上海浦江集散中心】",
				"operateTime": "2020-12-18 22:38:04"
			},
			{
				"content": "快件已发车",
				"operateTime": "2020-12-18 21:38:54"
			},
			{
				"content": "快件在【上海徐汇田林营业部】已装车,准备发往 【上海浦江集散中心】",
				"operateTime": "2020-12-18 21:30:56"
			},
			{
				"content": "顺丰速运 已收取快件",
				"operateTime": "2020-12-18 20:55:14"
			},
			{
				"content": "顺丰速运 已收取快件",
				"operateTime": "2020-12-18 20:47:54"
			}
		],
		"expressNo": "XXXXX",
		"expressCompany": "顺丰"
	},
	"success": true,
	"errormsg": "",
	"errorcode": "0",
	"requestId": "ed6e33ee-d9f0-4281-bbca-9f6c16d76944"

}