import hashlib
import hmac
import json
import time
import os
from datetime import datetime, timedelta

from dataclasses import dataclass
from http.client import HTTPSConnection
import argparse
from typing import List

SERVICE = "wsa"
HOST = "wsa.tencentcloudapi.com"
ALGORITHM = "TC3-HMAC-SHA256"


@dataclass
class Doc:
    url : str
    title: str
    snippet: str
    date: str
    site: str
    images: List[str]

@dataclass
class Option:
    query:str
    mode: int
    site:str
    from_time:int
    to_time:int
    action:str
    version:str

def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

def generate_header_and_payload(params:Option, secret_id:str, secret_key:str):
    timestamp = int(time.time())
    date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")
    # ************* 步骤 1：拼接规范请求串 *************
    http_request_method = "POST"
    canonical_uri = "/"
    canonical_querystring = ""
    ct = "application/json; charset=utf-8"
    canonical_headers = "content-type:%s\nhost:%s\nx-tc-action:%s\n" % (ct, HOST, params.action.lower())
    signed_headers = "content-type;host;x-tc-action"
    body = {"Query": params.query, "Mode":params.mode}
    if len(params.site) > 0:
        body["Site"] = params.site
    if params.from_time > 0 and params.to_time > 0:
        body["FromTime"] = params.from_time
        body["ToTime"] = params.to_time
    payload = json.dumps(body)
    hashed_request_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    canonical_request = (http_request_method + "\n" +
                         canonical_uri + "\n" +
                         canonical_querystring + "\n" +
                         canonical_headers + "\n" +
                         signed_headers + "\n" +
                         hashed_request_payload)

    # ************* 步骤 2：拼接待签名字符串 *************
    credential_scope = date + "/" + SERVICE + "/" + "tc3_request"
    hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
    string_to_sign = (ALGORITHM + "\n" +
                      str(timestamp) + "\n" +
                      credential_scope + "\n" +
                      hashed_canonical_request)

    # ************* 步骤 3：计算签名 *************
    secret_date = sign(("TC3" + secret_key).encode("utf-8"), date)
    secret_service = sign(secret_date, SERVICE)
    secret_signing = sign(secret_service, "tc3_request")
    signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    # ************* 步骤 4：拼接 Authorization *************
    authorization = (ALGORITHM + " " +
                     "Credential=" + secret_id + "/" + credential_scope + ", " +
                     "SignedHeaders=" + signed_headers + ", " +
                     "Signature=" + signature)

    headers = {
        "Authorization": authorization,
        "Content-Type": "application/json; charset=utf-8",
        "Host": HOST,
        "X-TC-Action": params.action,
        "X-TC-Timestamp": timestamp,
        "X-TC-Version": params.version,
    }

    return headers, payload


# 请参见：https://cloud.tencent.com/document/product/1278/85305
# 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取

def search(params:Option, secret_id:str, secret_key:str):
    headers,payload = generate_header_and_payload(params, secret_id=secret_id, secret_key=secret_key)
    query = params.query
    try:
        req = HTTPSConnection(HOST)
        req.request("POST", "/", headers=headers, body=payload.encode("utf-8"))
        resp = req.getresponse()
        rsp = resp.read()
        ret = json.loads(rsp)
        docs = parse(ret)
        print(f"查询词:{query},共查询到:{len(docs)}条结果")
        for idx, doc in enumerate(docs):
            if doc.images and len(doc.images) > 0:
                images_info = "\t".join(doc.images)
                print(
                    f"【{idx + 1}】 url:{doc.url},title:{doc.title},snippet:{doc.snippet},date:{doc.date},site:{doc.site},相关图片:{images_info}")
            else:
                print(
                    f"【{idx + 1}】 url:{doc.url},title:{doc.title},snippet:{doc.snippet},date:{doc.date},site:{doc.site}")
    except Exception as err:
        print(f"request error: {err}")


def parse(rsp:dict):
    res = rsp.get("Response")
    if res is None or not isinstance(res, dict):
        print("response is null")
        return []
    pages = res.get("Pages")
    if pages is None:
        return []

    docs = []
    for page in pages:
        json_page = json.loads(page)
        is_vr = json_page.get("vr", False)
        if is_vr:
            display = json_page.pop("display")
            if display is None:
                continue
            url = display.get("url")
            title = display.get("title")
            date = display.get("date")
            content = page
            docs.append(Doc(url=url, title=title, site="", date=date, snippet=content,images=[]))
        else:
            passage = json_page.get("passage")
            url = json_page.get("url")
            title = json_page.get("title")
            site = json_page.get("site")
            date = json_page.get("date")
            if len(title) == 0 or len(passage) == 0:
                continue
            docs.append(Doc(url = url,title= title, site=site, date=date, snippet=passage, images=json_page.get("images")))
    return docs


if __name__=="__main__":
    secret_id = os.getenv("TENCENTCLOUD_SECRET_ID")
    secret_key =  os.getenv("TENCENTCLOUD_SECRET_KEY")

    if secret_id is None or secret_key is None:
        print("secret id and secret key are not set, 前往 https://console.cloud.tencent.com/cam/capi 进行获取")
        exit(1)

    parser = argparse.ArgumentParser(description="websearch command arguments")
    parser.add_argument("--query", type=str, help="search query", required=True)
    parser.add_argument("--mode", type=int, help="返回结果类型，0-自然检索结果(默认)，1-多模态VR结果，2-混合结果（多模态VR结果+自然检索结果)", default=0)
    parser.add_argument("--site",type=str, help="指定站点搜索", default="")
    parser.add_argument("--freshness", choices=['','day','week','month','year'], help="查询结果的时效性要求")

    args = parser.parse_args()
    if len(args.query) == 0:
        print("invalid input arguments, query is empty")
        exit(1)

    reqOptions = Option(
        query=args.query,
        mode=args.mode,
        site=args.site,
        from_time=-1,
        to_time=-1,
        action="SearchPro",
        version="2025-05-08"
    )
    current_time = datetime.now()
    start_date = None
    if args.freshness == 'day':
        start_date = (current_time - timedelta(days=1))
    elif args.freshness == 'week':
        start_date = (current_time - timedelta(weeks=1))
    elif args.freshness == 'month':
        start_date = (current_time - timedelta(days=30))
    elif args.freshness == 'year':
        start_date = (current_time - timedelta(days=365))

    if start_date is not None:
        reqOptions.from_time = int(start_date.timestamp())
        reqOptions.to_time = int(current_time.timestamp())

    search(reqOptions, secret_id, secret_key)
