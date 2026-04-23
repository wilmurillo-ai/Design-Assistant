import argparse
import json
from typing import Any, Optional, List, Dict

import requests

# 请求头信息
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Content-Type": "application/json",
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    "Referer": "https://www.toupiaoya.com/",
    "Accept-Encoding": "gzip, deflate",
}

toupiaoyastore_search_url = "https://msearch-api.toupiaoya.com/m/search/searchProducts"
basepreview_url = "https://www.toupiaoya.com/mall/detail-h5e/"
default_creator_base_url = "https://ai-api.toupiaoya.com"
BASE_IMAGE_URL = "https://asset.eqh5.com/"

class ToupiaoyaStoreWebSearch:
    name: str = "toupiaoya_template_search"
    description: str = """进行投票鸭模板搜索，返回模板内容"""

    def execute(
        self,
        query: str,
        page_no: int = 1,
        num_results: int = 10,
        sort_by: str = "common_total|desc",
        color: Optional[str] = None,
    ) -> dict:
        session = requests.Session()
        session.headers = HEADERS
        jsonquery = {
            "sortBy": sort_by,
            "pageNo": page_no,
            "pageSize": num_results,
            "searchCode":"42312"
        }
        if query:
            jsonquery["keywords"] = query 
        if color:
            jsonquery["color"] = color
        res = session.post(url=toupiaoyastore_search_url, json=jsonquery)
        res.encoding = "utf-8"
        result = json.loads(res.text)
        if result["obj"]["total"] == 0:
            return {}
        result_list = []
        for k in result["obj"]["dataList"]:
            result_list.append({"templateId": k["id"],"title": k["title"], "link":basepreview_url+ str(k["id"]), "description": k["description"], "pv":k["views"], "cover":BASE_IMAGE_URL+k.get("productTypeMap",{}).get("tmbPath") + "?imageMogr2/thumbnail/320x320>" })

        return {"total": result["obj"]["total"], "end":result["obj"]["end"], "results": result_list}


class ToupiaoyaCreator:
    name: str = "toupiaoya_create"
    description: str = """通过投票鸭API接口创建投票作品"""

    def __init__(self, base_url: str = default_creator_base_url) -> None:
        self.base_url = base_url.rstrip("/")

    def execute(
        self,
        brief_title: str,
        brief_desc: str,
        detail_title: Optional[str] = None,
        detail_desc: Optional[str] = None,
        vote_type: Optional[str] = None,
        time_start: Optional[str] = None,
        time_end: Optional[str] = None,
        group_list: Optional[List[Dict[str, Any]]] = None,
        template_id: Optional[int] = None,
        single_vote: Optional[bool] = True,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "briefTitle": brief_title,
            "briefDesc": brief_desc,
            "singleVote": single_vote,
        }
        if detail_title:
            payload["detailTitle"] = detail_title
        if detail_desc:
            payload["detailDesc"] = detail_desc
        if vote_type:
            payload["voteType"] = vote_type
        if time_start:
            payload["timeStart"] = time_start
        if time_end:
            payload["timeEnd"] = time_end
        if group_list is not None:
            payload["groupList"] = group_list
        if template_id is not None:
            payload["templateId"] = template_id

        url = f"{self.base_url}/iaigc-toupiaoya/create"
        response = requests.post(url=url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()


def _parse_group_list(group_list_text: Optional[str]) -> Optional[List[Dict[str, Any]]]:
    if not group_list_text:
        return None
    parsed = json.loads(group_list_text)
    if not isinstance(parsed, list):
        raise ValueError("--groupList 必须是 JSON 数组")
    return parsed


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="toupiaoya CLI: search / create")
    subparsers = parser.add_subparsers(dest="command")

    search_parser = subparsers.add_parser("search", help="搜索投票模板")
    search_parser.add_argument("--keywords", type=str, required=False, help="关键词")
    search_parser.add_argument("--pageNo", type=int, required=False, default=1, help="分页页码")
    search_parser.add_argument("--pageSize", type=int, required=False, default=10, help="每页条数")
    search_parser.add_argument("--sortBy", type=str, required=False, default="common_total|desc", help="排序字段，如 common_total|desc")
    search_parser.add_argument("--color", type=str, required=False, default=None, help="颜色，如 紫色、蓝色、粉色、红色、绿色、青色、橙色、黄色、黑色、白色、灰色")

    create_parser = subparsers.add_parser("create", help="创建投票作品")
    create_parser.add_argument("--briefTitle", type=str, required=True, help="封面标题")
    create_parser.add_argument("--briefDesc", type=str, required=True, help="封面简介")
    create_parser.add_argument("--detailTitle", type=str, required=False, default=None, help="详细标题")
    create_parser.add_argument("--detailDesc", type=str, required=False, default=None, help="详细说明")
    create_parser.add_argument("--voteType", type=str, required=False, default="textVote", help="投票类型：imageVote/textVote/videoVote")
    create_parser.add_argument("--timeStart", type=str, required=False, default=None, help="开始时间，格式 yyyy-MM-dd HH:mm")
    create_parser.add_argument("--timeEnd", type=str, required=False, default=None, help="结束时间，格式 yyyy-MM-dd HH:mm")
    create_parser.add_argument("--templateId", type=int, required=False, default=None, help="模板ID，不传则走后端默认")
    create_parser.add_argument("--groupList", type=str, required=False, default=None, help='分组JSON数组字符串，例如: \'[{"groupName":"第一组","choices":[{"name":"A"}]}]\'')
    create_parser.add_argument(
        "--multi",
        action="store_true",
        help="多选开关；默认不传即单选。",
    )
    return parser

if __name__ == "__main__":
    parser = _build_parser()
    args = parser.parse_args()

    # 兼容旧用法：不写子命令时默认按 search 执行。
    command = args.command or "search"
    if command == "search":
        search = ToupiaoyaStoreWebSearch()
        result = search.execute(
            getattr(args, "keywords", None),
            getattr(args, "pageNo", 1),
            getattr(args, "pageSize", 10),
            sort_by=getattr(args, "sortBy", "common_total|desc"),
            color=getattr(args, "color", None),
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "create":
        creator = ToupiaoyaCreator()
        group_list = _parse_group_list(args.groupList)
        single_vote = not getattr(args, "multi", False)
        result = creator.execute(
            brief_title=args.briefTitle,
            brief_desc=args.briefDesc,
            detail_title=args.detailTitle,
            detail_desc=args.detailDesc,
            vote_type=args.voteType,
            time_start=args.timeStart,
            time_end=args.timeEnd,
            group_list=group_list,
            template_id=args.templateId,
            single_vote=single_vote,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.print_help()
