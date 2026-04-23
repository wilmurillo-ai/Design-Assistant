# 消息池

10.1 消息推送（不推荐）
​

建议优先使用分页消息接口（10.2/10.3/10.4）进行稳定消费。 本接口仍可用，但更适合存量系统兼容。

Method	URL	ContentType
GET	/api/restful/messages	application/json

URL参数说明：

参数	是否必须	描述
del	必须	整数，表示是否删除标示 0为获取后不删除1为获取后删除消息(默认删除前50条消息) 注：若消费成功后不删除，接口始终返回前50条消息
type	必须	字符串，表示消息类型业务代码，支持多种业务消息查询，多个以逗号分隔
202：商品价格变更
203：商品库存变更
204：商品上下架变更
205：A添加、R删除、M更新商品
206：A添加、R删除、M更新商品池
302：订单状态 （0：新建，1：妥投完成，-1：拒收，-2：取消，5：已发货，3: 审批通过， -3： 审批不通过"）
303：退换货状态
304：退换货审核状态
701：结算单开票
801：拆单消息
700：结算单审核

返回结果说明：

参数	描述	参数说明
id	消息编号	int
type	消息类型	int
time	推送时间	datetime
result	消息正文，根据消息类型返回不同格式的数据,如下所示	int
消费建议
​
拉取后先按 type 分发到对应处理器；
业务处理成功后删除消息，避免重复消费；
对失败消息记录重试日志，并设置最大重试次数。

result结果说明：

业务代码	
数据描述
	响应内容
202	商品价格变更	{"id" : 推送id,"result" : {"skuId" : 商品编号},"type" : 202,"time" : 推送时间}
203	商品库存变更	{id" : 推送id,result" : {skuId" : 商品编号},"type" : 203,"time" : 推送时间}
204	商品上下架变更	{"id" : 推送id,"result" : {"skuId" : 商品编号,"state" : 0是下架，1是上架},"type" : 204,"time" : 推送时间}
205	A添加、R删除、M更新商品	{"id" : 推送id,"result" : {"skuId" : 商品编号,"state" : "A添加，R删除M更新"},"type" : 205,"time" : 推送时间}
206	A添加、R删除、M更新商品池	{"id" : 推送id,"result" : {"poolId" : 商品池编号,"state" : "A添加，R删除M更新","skuId" : 商品编号},"type" : 206,"time" : 推送时间}
302	订单状态变化
0：新建
1：妥投完成
-1：拒收
-2：取消
4：退换货中
5：已发货，
3: 审批通过，
-3： 审批不通过	{"id" : 推送id,"result" : {"orderId" : "订单编号","deliveryCode":"发货单号","state" : "0：新建，1：妥投完成，-1：拒收，-2：取消，5：已发货，3: 审批通过， -3： 审批不通过","auditComment":"审批描述"},"type" : 302,"time" : 推送时间}
303	退换货状态变化	{"id" : 推送id,"result" : {"POCode" : "订单编号","ApplyCode" : "退货单申请编号","ProcessStatus" :30301：处理中，30305：客户已发货，30310：我方收到货，30315：我方重新发货，30320：已签收，30325 : 客户完成，30330：客服完成},"type" : 303,"time" : 推送时间}
306	退换货导入产生变更队列	{"OrderCode":"订单编号","ReturnGoodsCode":"退货单编号"}
304	退换货申请状态变化	{"id" : 推送id,"result" : {"POCode" : "订单编号","ApplyCode" : "退货单申请编号","ApplyStatus" : 0：申请中，1：审核通过 2：客户取消，3：客服取消，4：审核不通过},"type" : 304,"time" : 推送时间}
701	结算单开票	{"id" : 推送id,"result" : {"bill_id" : 结算单号,"mark_id" : 第三方申请发票唯一标识},"type" : 701,"time" : 推送时间}
700	结算单审核	{"id": 推送id,"result": {"billRowNo": 结算行号,"auditStatus": 1: 审批通过， 2： 审批不通过， "auditComment": 审批意见,"billNo": 结算单号},"type": 700,"time": 推送时间}
801	拆单消息	{"OrderCode":"订单编号"}

请求参数示例：

json
/api/restful/messages&del=0&type=202,203

返回数据示例：

json
{
    "success": true,
    "requestId": "CD3DE2CE-D297-4436-809B-AD82B5C26DE6",
    "errorcode": "0",
    "errormsg": "",
    "result": [
        {
            "id": "11",
            "type": 202,
            "time": "2017-08-31 17:07:38",
            "result": {
                "skuId": "1037259"
            }
        },
        {
            "id": "14",
            "type": 203,
            "time": "2017-08-31 17:20:14",
            "result": {
                "skuId": "1037259"
            }
        },
        {
            "id": "12",
            "type": 204,
            "time": "2017-08-31 17:07:49",
            "result": {
                "state": 0,
                "skuId": "1037259"
            }
        },
        {
            "id": "3585844",
            "type": 205,
            "time": "2024-10-16 14:56:20",
            "result": {
                "state": "M",
                "skuId": "102101"
            }
        },
        {
            "id": "3585844",
            "type": 206,
            "time": "2024-10-16 14:56:20",
            "result": {
                "state": "M",
                "skuId": "102101",
                "poolId": "01"
            }
        },
        {
            "id": "3585837",
            "type": 302,
            "time": "2024-10-16 14:42:54",
            "result": {
                "orderId": "test0010",
                "deliveryCode": "CLP87712400000",
                "state": "5"
            }
        },
        {
            "id": "3585836",
            "type": 303,
            "time": "2024-10-16 14:38:17",
            "result": {
                "ProjectCode": "CeShi",
                "ApplyCode": "1771046685821296641",
                "POCode": "1770722705780424705",
                "ProcessStatus": 30330
            }
        },
        {
            "id": "3585835",
            "type": 304,
            "time": "2024-10-16 14:37:43",
            "result": {
                "ProjectCode": "CeShi",
                "POCode": "1770722705780424705",
                "ApplyCode": "1771046685821296641",
                "ApplyStatus": 1
            }
        },
        {
            "id": "3585839",
            "type": 701,
            "time": "2024-10-16 14:44:09",
            "result": {
                "bill_id": "BO20180606162632",
                "mark_id": "100001"
            }
        },
        {
            "id": "3585840",
            "type": 700,
            "time": "2024-10-16 14:46:36",
            "result": {
                "billRowNo": "811271",
                "auditStatus": 1,
                "auditComment": "1111",
                "billNo": "DZ-MALL20211130000005-001"
            }
        }
    ]
}

# 消息分页查询

10.2 消息分页查询（推荐）
​
Method	URL	ContentType
GET	/api/restful/paged/messages	application/json

URL参数说明：

参数	是否必须	描述
type	必须	字符串，表示消息类型业务代码，支持多种业务消息查询，多个以逗号分隔
202：商品价格变更
203：商品库存变更
204：商品上下架变更
205：A添加、R删除、M更新商品
206：A添加、R删除、M更新商品池
302：订单状态 0：新建，1：妥投完成，-1：拒收，-2：取消，5：已发货，3: 审批通过， -3： 审批不通过
303：退换货状态变化
304：退换货申请状态变化
700：结算单审核
701：结算单开票
801：拆单消息
del	必须	整数，表示是否删除标示 0为获取后不删除1为获取后删除消息
page	必须	页号,必须大于0
pageSize	必须	获取数据的大小，必须大于0

返回结果说明：

参数	描述	参数说明
id	消息编号	int
type	消息类型	int
time	推送时间	datetime
result	消息正文，根据消息类型返回不同格式的数据	int

result结果说明：

业务代码	
数据描述
	响应内容
202	商品价格变更	{"id" : 推送id,"result" : {"skuId" : 商品编号},"type" : 202,"time" : 推送时间}
203	商品库存变更	{id" : 推送id,result" : {skuId" : 商品编号},"type" : 203,"time" : 推送时间}
204	商品上下架变更	{"id" : 推送id,"result" : {"skuId" : 商品编号,"state" : 0是下架，1是上架},"type" : 204,"time" : 推送时间}
205	A添加、R删除、M更新商品	{"id" : 推送id,"result" : {"skuId" : 商品编号,"state" : "A添加，R删除M更新"},"type" : 205,"time" : 推送时间}
206	A添加、R删除、M更新商品池	{"id" : 推送id,"result" : {"poolId" : 商品池编号,"state" : "A添加，R删除M更新","skuId" : 商品编号},"type" : 206,"time" : 推送时间}
302	订单状态变化
0：新建
1：妥投完成
-1：拒收
-2：取消
5：已发货，
3: 审批通过，
-3： 审批不通过	{"id" : 推送id,"result" : {"orderId" : "订单编号","deliveryCode":"发货单号","state" : "0：新建，1：妥投完成，-1：拒收，-2：取消，5：已发货，3: 审批通过， -3： 审批不通过","auditComment":"审批描述"},"type" : 302,"time" : 推送时间}
303	退换货状态变化	{"id" : 推送id,"result" : {"POCode" : "订单编号","ApplyCode" : "退货单申请编号","ProcessStatus" :30301：处理中，30305：客户已发货，30310：我方收到货，30315：我方重新发货，30320：已签收，30325 : 客户完成，30330：客服完成},"type" : 303,"time" : 推送时间}
306	退换货导入产生变更队列	{"OrderCode":"订单编号","ReturnGoodsCode":"退货单编号"}
304	退换货申请状态变化	{"id" : 推送id,"result" : {"POCode" : "订单编号","ApplyCode" : "退货单申请编号","ApplyStatus" : 0：申请中，1：审核通过 2：客户取消，3：客服取消，4：审核不通过},"type" : 304,"time" : 推送时间}
701	结算单开票	{"id" : 推送id,"result" : {"bill_id" : 结算单号,"mark_id" : 第三方申请发票唯一标识},"type" : 701,"time" : 推送时间}
700	结算单审核	{"id": 推送id,"result": {"billRowNo": 结算行号,"auditStatus": 1: 审批通过， 2： 审批不通过， "auditComment": 审批意见,"billNo": 结算单号},"type": 700,"time": 推送时间}
801	拆单消息	{"OrderCode":"订单编号"}

请求参数示例：

/api/restful/paged/messages?type=302&del=0&page=1

返回数据示例：

json
{
    "success": true,
    "requestId": "CD3DE2CE-D297-4436-809B-AD82B5C26DE6",
    "errorcode": "0",
    "errormsg": "",
    "result": [
        {
            "id": "11",
            "type": 202,
            "time": "2017-08-31 17:07:38",
            "result": {
                "skuId": "1037259"
            }
        },
        {
            "id": "14",
            "type": 203,
            "time": "2017-08-31 17:20:14",
            "result": {
                "skuId": "1037259"
            }
        },
        {
            "id": "12",
            "type": 204,
            "time": "2017-08-31 17:07:49",
            "result": {
                "state": 0,
                "skuId": "1037259"
            }
        },
        {
            "id": "3585844",
            "type": 205,
            "time": "2024-10-16 14:56:20",
            "result": {
                "state": "M",
                "skuId": "102101"
            }
        },
        {
            "id": "3585844",
            "type": 206,
            "time": "2024-10-16 14:56:20",
            "result": {
                "state": "M",
                "skuId": "102101",
                "poolId": "01"
            }
        },
        {
            "id": "3585837",
            "type": 302,
            "time": "2024-10-16 14:42:54",
            "result": {
                "orderId": "test0010",
                "deliveryCode": "CLP87712400000",
                "state": "5"
            }
        },
        {
            "id": "3585836",
            "type": 303,
            "time": "2024-10-16 14:38:17",
            "result": {
                "ProjectCode": "CeShi",
                "ApplyCode": "1771046685821296641",
                "POCode": "1770722705780424705",
                "ProcessStatus": 30330
            }
        },
        {
            "id": "3585835",
            "type": 304,
            "time": "2024-10-16 14:37:43",
            "result": {
                "ProjectCode": "CeShi",
                "POCode": "1770722705780424705",
                "ApplyCode": "1771046685821296641",
                "ApplyStatus": 1
            }
        },
        {
            "id": "3585839",
            "type": 701,
            "time": "2024-10-16 14:44:09",
            "result": {
                "bill_id": "BO20180606162632",
                "mark_id": "100001"
            }
        },
        {
            "id": "3585840",
            "type": 700,
            "time": "2024-10-16 14:46:36",
            "result": {
                "billRowNo": "811271",
                "auditStatus": 1,
                "auditComment": "1111",
                "billNo": "DZ-MALL20211130000005-001"
            }
        }
    ]
}

# 消息批量删除

10.3 消息批量删除
​
Method	URL	ContentType
POST	/api/restful/messages	application/json

请求入参说明：

类型说明	是否必须	描述
整形数组	必须	消息id，多个id以英文逗号分隔；可参考示例代码

返回结果说明：

参数	描述	参数说明
result	null	null

请求参数示例：

json
[134420,134420,134422,134423]

返回数据示例：

json
{
    "result": null,
    "success": true,
    "errormsg": "",
    "errorcode": "0",
    "requestId": "db38301a65884e7a83b630a98e6bb49e"
}

# 消息删除(已作废)

10.4 消息删除（已作废）
​

接口说明：

Method	URL	ContentType
DELETE	/api/restful/message/{id}/	application/json

URL参数说明：

参数	是否必须	描述
id	必须	消息id
type	必须	202：商品价格变更203：商品库存变更204：商品上下架变更205：A添加、R删除、M更新商品池内商品 302：订单状态303：退换货状态变化304：退换货申请状态变化701：结算单开票801：拆单消息

返回结果说明：

参数	描述	参数说明
result	null	null

请求参数示例：

/api/restful/message/7526/302

返回数据示例：

json
{
    "result": null,
    "success": true,
    "errormsg": "",
    "errorcode": "0",
    "requestId": "db38301a65884e7a83b630a98e6bb49e"
}