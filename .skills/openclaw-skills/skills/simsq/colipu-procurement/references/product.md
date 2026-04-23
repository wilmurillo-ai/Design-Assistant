# 获取商品末级分类

4.1.1获取商品末级分类
​

接口说明：

Method	URL	ContentType
GET	/api/restful/categories	application/json

返回结果说明：

参数	类型说明	描述
success	bool	成功：true 失败：false
errorcode	int	错误码
errormsg	string	错误消息
result	Json 数组	{"name":"工程设备及用品","id":"0028-0003" }

请求参数示例：

/api/restful/categories

返回数据示例：

json
{
    "result": [{
        "name": "笔类",
        "id": "010101"
    }, {
        "name": "显卡",
        "id": "020204"
    }, {
        "name": "手写板",
        "id": "020212"
    }, {
        "name": "充电宝",
        "id": "020503"
    }, {
        "name": "电视",
        "id": "030202"
    }],
    "success": true,
    "errormsg": "",
    "errorcode": "0",
    "requestId": "f2d0dcad158849e5a82081e4e9241f62"
}

# 获取商品全量分类

4.1.2获取商品全量分类
​

接口说明：

Method	URL	ContentType
GET	/api/restful/categories/page	application/json

URL参数说明：

参数	是否必须	描述
pageNum	必须	页号,必须大于0
pageSize	必须	获取数据的大小，必须大于0
level	非必须	分类层级，不填的情况默认返回全部
parentld	非必须	父类编码，不填的情况默认返回全部
customerCode	非必须	客户编码，不填的情况默认返回全部
id	非必须	分类编码，不填的情况默认返回全部

返回结果说明：

参数	类型说明	描述
success	bool	成功：true 失败：false
errorcode	int	错误码
errormsg	string	错误消息
result	Json 数组	全量分类

请求参数示例：

/api/restful/categories/page

返回数据示例：

json
{
    "success": true,
    "requestId": "D7C5294D-2811-4500-9C55-0F8CDCBB0CFF",
    "result": {
        "pageNum": 1,
        "pageSize": 100,
        "pageTotal": 12,
        "pageCount": 1,
        "items": [
            {
                "parentId": "10259013",
                "customerCode": "*",
                "level": 3,
                "name": "2G模块",
                "id": "10259014"
            },
            {
                "parentId": "10259013",
                "customerCode": "*",
                "level": 3,
                "name": "4G模块",
                "id": "10259024"
            },
            {
                "parentId": "10259013",
                "customerCode": "*",
                "level": 3,
                "name": "OBU模块",
                "id": "12250936"
            }
        ]
    },
    "errorcode": "0",
    "errormsg": ""
}

# 获取分类下Sku

4.2.1 获取分类下Sku
​

接口说明：

Method	URL	ContentType
GET	/api/restful/category/{id}/skus	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
id	string	必须	50	商品分类编号

返回结果说明：

参数	类型说明	描述
result	string 数组	商品编号（sku）数组

请求参数示例：

/api/restful/category/010101/skus

返回数据示例：

json
{
    "result": [
        "1049204",
        "105019",
        "1034373",
        "1034184",
        "1049200",
        "1045561"
    ],
    "success": true,
    "errormsg": "",
    "errorcode": "0",
    "requestId": "d89eac5cfc6a443bae110ba92c41916e"
}

# 获取分类下Sku明细

4.2.2 获取分类下Sku明细
​

接口说明：

Method	URL	ContentType
GET	/api/restful/category/{id}/skuinfo	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
id	string	必须	50	商品分类编号

返回结果说明：

参数	类型说明	描述
result	List	商品信息

请求参数示例：

/api/restful/category/010101/skuinfo

返回数据示例：

json
{
	"result": [{
		"sku": "1049204",
		"name": "惠普 HP 硒鼓 CF411A 410A （青色）"
	}, {
		"sku": "105019",
		"name": "宝克 圆珠笔 B14 0.7mm (蓝色) 48支/盒"
	}],
	"success": true,
	"errormsg": "",
	"errorcode": "0",
	"requestId": "d89eac5cfc6a443bae110ba92c41916e"
}

# 获取商品详情

4.3.1 获取商品详情接口
​

接口说明：

Method	URL	ContentType
GET	/api/restful/product/{sku}/detail	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
sku	string	必须	50	商品编号

返回结果说明：

参数	类型说明	描述
sku	string	商品编号
url	string	商品url
model	string	型号
weight	double	重量
image_path	string	主图地址
state	int	上下架状态
brand_name	string	品牌
name	string	商品名称
product_area	string	产地
upc	string	条形码
unit	string	单位
category	string	类别
categoryName	string	类别名称
service	string	售后服务
introduction	string	商品描述（图文, html）
param	string	商品属性（html）
prdParams	json	商品属性
ware	string	包装清单
tax_rate	float	商品税率
sale_actives	int	是否促销
tax_catetory_code	string	税收分类编码
search_keyword	string	搜索关键词
productExtensions	List	扩展信息

请求参数示例：

/api/restful/product/1049204/detail

返回数据示例：

json
{
	"result": {
		"sku": "1049204",
		"url": "",
		"model": "MP399A",
		"weight": 18.6,
		"image_path": "http://res.clpcdn.com/pmspic/ItemPicture/2/20/126/49191/Original/1049204.jpg",
		"state": 1,
		"brand_name": "宝克",
		"name": "宝克 可加墨白板笔 MP399A (蓝色) 12支/盒",
		"product_area": "中国",
		"upc": "6921738085234",
		"unit": "支",
		"category": "010101",
		"categoryName": "笔类",
		"service": "/",
		"introduction": "<div id='Background' style='border-bottom: medium none; border-left: medium none; margin: 0px auto; width: 790px; border-top: medium none; border-right: medium none'><table id='__01' width='790' height='5169' border='0' cellpadding='0' cellspacing='0'><tbody><tr class='firstRow'><td><img src='http://pic.colipu.com/ProductDescribe/1049204/1049204_01.jpg' width='790' height='925' alt=''/></td></tr><tr><td><img src='http://pic.colipu.com/ProductDescribe/1049204/1049204_02.jpg' width='790' height='488' alt=''/></td></tr><tr><td><img src='http://pic.colipu.com/ProductDescribe/1049204/1049204_03.jpg' width='790' height='620' alt=''/></td></tr><tr><td><img src='http://pic.colipu.com/ProductDescribe/1049204/1049204_04.jpg' width='790' height='781' alt=''/></td></tr><tr><td><img src='http://pic.colipu.com/ProductDescribe/1049204/1049204_05.jpg' width='790' height='820' alt=''/></td></tr><tr><td><img src='http://pic.colipu.com/ProductDescribe/1049204/1049204_06.jpg' width='790' height='730' alt=''/></td></tr><tr><td><img src='http://pic.colipu.com/ProductDescribe/1049204/1049204_07.jpg' width='790' height='805' alt=''/></td></tr></tbody></table><style= border-bottom:='' medium='' border-left:='' border-top:='' border-right:=''></style=></div>",
		"param": "",
		"ware": "白板笔*1支",
		"tax_rate": 13,
		"tax_catetory_code":"109062703",
		"search_keyword":"白板笔",
		"sale_actives": 0,
		"prdParams": [{
				"name": "包装规格",
				"value": "500张/包 5包/箱"
			},
			{
				"name": "产地",
				"value": "中国"
			},
			{
				"name": "克重",
				"value": "70g"
			},
			{
				"name": "品牌",
				"value": "益思"
			},
			{
				"name": "入数",
				"value": "1包"
			},
			{
				"name": "纸质",
				"value": "全木浆"
			}
		],
		 "productExtensions": [
            {
                "columnName": "第三方链接",
                "columnKey": "ThirdUrl",
                "columnValue": "https://item.jd.com/1525554.html"
            }
        ]
	},
	"success": true,
	"errormsg": "",
	"errorcode": "0",
	"requestId": "2f1e4985-68be-486c-b4ea-2d4b0cd7d024"
}

# 获取商品全量详情

4.3.2 获取商品全量详情接口
​

接口说明：

Method	URL	ContentType
GET	/api/restful/product/{sku}/full/detail	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
sku	string	必须	50	商品编号
customer_code	string	非必须	50	客户编码 ,不填的情况，默认返回全部

返回结果说明

参数	子字段	类型说明	描述
sku		string	商品编号
detail		JSON	商品详情
	url	string	商品url
	model	string	型号
	weight	double	重量
	image_path	string	主图地址
	state	int	上下架状态
	brand_name	string	品牌
	name	string	商品名称
	product_area	string	产地
	upc	string	条形码
	unit	string	单位
	category	string	类别
	categoryName	string	类别名称
	service	string	售后服务
	introduction	string	商品描述（图文, html）
	param	string	商品属性（html）
	prdParams	json	商品属性
	ware	string	包装清单
	sale_actives	int	是否促销
	tax_catetory_code	string	税收分类编码
	search_keyword	string	搜索关键词
	productExtensions	List	扩展信息
images		JSON	图片信息：[{"path": "图片路径", "order": 图片排序}]
	path	string	图片路径
	order	int	图片排序
price		JSON	价格
	price	double	协议优惠价（双方签订的协议价格）
	mall_price	double	商城售价（商品在我司商城的售价）
	market_price	double	市场售价（商品市面上的价格）
	tax_rate	float	商品税率
	naked_price	double	商品裸价
	tax_amount	double	发票税额
stock		JSON	库存
	desc	string	描述（有货、缺货）
	num	double	库存数量
	area	string	地址，默认*

请求参数示例：

/api/restful/product/1049204/full/detail

返回数据示例：

json
{
	"result": {
		"sku": "1049204",
		"detail": {
			"url": "",
			"model": "MP399A",
			"weight": 18.6,
			"image_path": "http://res.clpcdn.com/pmspic/ItemPicture/2/20/126/49191/Original/1049204.jpg",
			"state": 1,
			"brand_name": "宝克",
			"name": "宝克 可加墨白板笔 MP399A (蓝色) 12支/盒",
			"product_area": "中国",
			"upc": "6921738085234",
			"unit": "支",
			"category": "010101",
			"categoryName": "笔类",
			"service": "/",
			"introduction": "<div id='Background' style='border-bottom: medium none; border-left: medium none; margin: 0px auto; width: 790px; border-top: medium none; border-right: medium none'><table id='__01' width='790' height='5169' border='0' cellpadding='0' cellspacing='0'><tbody><tr class='firstRow'><td><img src='http://pic.colipu.com/ProductDescribe/1049204/1049204_01.jpg' width='790' height='925' alt=''/></td></tr><tr><td><img src='http://pic.colipu.com/ProductDescribe/1049204/1049204_02.jpg' width='790' height='488' alt=''/></td></tr><tr><td><img src='http://pic.colipu.com/ProductDescribe/1049204/1049204_03.jpg' width='790' height='620' alt=''/></td></tr><tr><td><img src='http://pic.colipu.com/ProductDescribe/1049204/1049204_04.jpg' width='790' height='781' alt=''/></td></tr><tr><td><img src='http://pic.colipu.com/ProductDescribe/1049204/1049204_05.jpg' width='790' height='820' alt=''/></td></tr><tr><td><img src='http://pic.colipu.com/ProductDescribe/1049204/1049204_06.jpg' width='790' height='730' alt=''/></td></tr><tr><td><img src='http://pic.colipu.com/ProductDescribe/1049204/1049204_07.jpg' width='790' height='805' alt=''/></td></tr></tbody></table><style= border-bottom:='' medium='' border-left:='' border-top:='' border-right:=''></style=></div>",
			"param": "",
			"prdParams": [{
					"name": "包装规格",
					"value": "500张/包 5包/箱"
				},
				{
					"name": "产地",
					"value": "中国"
				},
				{
					"name": "克重",
					"value": "70g"
				},
				{
					"name": "品牌",
					"value": "益思"
				},
				{
					"name": "入数",
					"value": "1包"
				},
				{
					"name": "纸质",
					"value": "全木浆"
				}
			],
			"ware": "白板笔*1支",
			"sale_actives": 1,
			"tax_catetory_code": "109062703",
			"search_keyword": "白板笔",
			"productExtensions": [{
				"columnName": "第三方链接",
				"columnKey": "ThirdUrl",
				"columnValue": "https://item.jd.com/1525554.html"
			}]
		},
		"images": [{
				"path": "http://res.clpcdn.com/pmspic/ItemPicture/2/20/126/49191/Original/1049204.jpg",
				"order": 1
			},
			{
				"path": "http://res.clpcdn.com/pmspic/ItemPicture/2/20/126/49191/Largest/1_1049204.jpg",
				"order": 2
			}
		],
		"price": {
			"price": 1.18,
			"mall_price": 1.6,
			"market_price": 1.9,
			"tax_rate": 0.13,
			"naked_price": 1.04,
			"tax_amount": 0.14
		},
		"stock": {
			"desc": "有货",
			"num": 50,
			"area": "*"
		}
	},
	"success": true,
	"errormsg": "",
	"errorcode": "0",
	"requestId": "2f1e4985-68be-486c-b4ea-2d4b0cd7d024"
}

# 获取商品图片

4.4 获取商品图片
​

接口说明：

Method	URL	ContentType
GET	/api/restful/products/images	applicatioin/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
skus	string	必须	50	多个商品编号；支持批量，以英文逗号分隔

返回结果说明：

参数	类型说明	描述
sku	string	商品编号
path	string	图片路径
order	int	图片排序

请求参数示例：

/api/restful/products/images?skus=1049204,105019

返回数据示例：

json
{
    "result": [{
        "sku": "1049204",
        "images": [{
            "path": "http://res.clpcdn.com/pmspic/ItemPicture/2/20/126/49191/Original/1049204.jpg",
            "order": 1
        }, {
            "path": "http://res.clpcdn.com/pmspic/ItemPicture/2/20/126/49191/Largest/1_1049204.jpg",
            "order": 2
        }, {
            "path": "http://res.clpcdn.com/pmspic/ItemPicture/2/20/126/49191/DetailBig/1_1049204.jpg",
            "order": 2
        }, {
            "path": "http://res.clpcdn.com/pmspic/ItemPicture/2/20/126/49191/Original/2_1049204.jpg",
            "order": 3
        }]
    }, {
        "sku": "105019",
        "images": [{
            "path": "http://res.clpcdn.com/pmspic/ItemPicture/2/20/126/734/Original/105019.jpg",
            "order": 1
        }, {
            "path": "http://res.clpcdn.com/pmspic/ItemPicture/2/20/126/734/Largest/1_105019.jpg",
            "order": 2
        }]
    }],
    "success": true,
    "errormsg": "",
    "errorcode": "0",
    "requestId": "818de4cd1d0f467e86609a09df13688f"
}

# 获取商品好评度(废弃)

4.5 获取商品好评度（废弃）
​

接口说明：

Method	URL	ContentType
GET	/api/restful/products/ratings	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
skus	string	必须	50	多个商品编号; 支持批量，以英文逗号分隔

返回结果说明：

参数	类型说明	描述
average	double	商品评分
good	double	好评度
medium	double	中评度
bad	double	差评度
sku	string	商品编号

请求参数示例：

/api/restful/products/ratings?skus=1049204,105019

返回数据示例：

json
{
    "result": [{
        "average": 5,
        "medium": 0.0,
        "good": 1.0,
        "sku": "1049204",
        "bad": 0.0
    }, {
        "average": 5,
        "medium": 0.0,
        "good": 1.0,
        "sku": "105019",
        "bad": 0.0
    }],
    "success": true,
    "errormsg": "",
    "errorcode": "",
    "requestId": "818de4cd1d0f467e86609a09df136881"
}

# 获取商品上下架状态

4.6 获取商品上下架状态
​

接口说明：

Method	URL	ContentType
GET	/api/restful/products/status	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
skus	string	必须	50	多个商品编号; 支持批量，以英文逗号分隔
customer_code	string	非必须	50	客户编码 ,不填的情况，默认返回全部

返回结果说明：

参数	类型说明	描述
state	Int	状态（1：上架 0：下架）
sku	string	商品编号
customer_code	string	客户编码，*代表全部

请求参数示例：

/api/restful/products/status?skus=1049204,105019&&customer_code=106253

返回数据示例：

json
{
    "result": [{
        "sku": "1049204",
        "state": 1,
        "customer_code": "106253"
    }, {
        "sku": "105019",
        "state": 1,
        "customer_code": "106253"
    }],
    "success": true,
    "errormsg": "",
    "errorcode": "0",
    "requestId": "a089a39e2fe74f3b8281fa2bfd799c44"
}

# 获取商品价格

4.7 获取商品价格
​

接口说明：返回协议优惠价格price，和商城售价mall_price。

Method	URL	ContentType
GET	/api/restful/products/prices	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
skus	string	必须	50	多个商品编号; 支持批量，以英文逗号分隔
customer_code	string	非必须	50	客户编码 ,不填的情况，默认返回全部

返回结果说明：

参数	类型说明	描述
price	double	协议优惠价(双方签订的协议价格)
mall_price	double	商城售价（商品在我司商城的售价）
market_price	double	市场售价（商品市面上的价格）
sku	string	商品编号
tax_rate	float	商品税率
naked_price	double	商品裸价
tax_amount	double	发票税额
customer_code	string	客户编码，*代表全部

请求参数示例：

/api/restful/products/prices?skus=1049204,105019&customer_code=106253

返回数据示例：

json
{
    "result": [{
        "sku": "1049204",
        "market_price": 1.9,
        "mall_price": 1.6,
        "price": 1.18,
        "tax_rate":0.13,
        "naked_price":1.04,
        "tax_amount":0.14,
        "customer_code": "106253"
    }, {
        "sku": "105019",
        "market_price": 10.9,
        "mall_price": 9.9,
        "price": 7.1,
        "tax_rate":0.13,
        "naked_price":6.28,
        "tax_amount":0.82,
        "customer_code": "106253"
    }],
    "success": true,
    "errormsg": "",
    "errorcode": "0",
    "requestId": "3071c687f2b74caf893f9f27caa05dbc"
}

# 获取商品库存

4.8 获取商品库存
​

接口说明：

Method	URL	ContentType
GET	/api/restful/products/areastocks	application/json

URL参数说明：

参数	类型说明	是否必须	长度	描述
skus	string	必须	50	多个商品编号; 支持批量，以英文逗号分隔
area	string	必须	10	省编号_市编号_区编号
customer_code	string	非必须	50	客户编码，不传的情况下默认返回全部

返回结果说明：

参数	类型说明	描述
area	string	地址
desc	string	描述（有货、缺货）
num	double	库存数量
sku	string	商品编号
customer_code	string	客户编码,*默认全部

请求参数示例：

/api/restful/products/areastocks?skus=1049204,105019&area=*&customer_code=106234

返回数据示例：

json
{
    "result": [{
        "sku": "1049204",
        "num": 9999,
        "area": "*",
        "desc": "有货",
        "customer_code": "106234"
    }, {
        "sku": "105019",
        "num": 9999,
        "area": "*",
        "desc": "有货",
        "customer_code": "106234"
    }],
    "success": true,
    "errormsg": "",
    "errorcode": "0",
    "requestId": "8d98d82c2de740cb92b56f4e5f15049a"
}