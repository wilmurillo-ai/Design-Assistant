# 玄关开放平台 API 调用示例

## Python 调用示例

### 基础配置

```python
import requests
import json

# =============================
# 1. 环境配置
# =============================
# 测试环境
BASE_URL = "https://cwork-api.mediportal.com.cn/open-api"

# 环境变量 `XG_BIZ_API_KEY`
APP_KEY = "${XG_BIZ_API_KEY}"

# 通用请求头
headers = {
    "Content-Type": "application/json",
    "appKey": APP_KEY,
    "Accept": "application/json"
}
```

---

### 示例 1: 按姓名搜索员工

```python
def search_employee_by_name(search_key):
    """
    按姓名搜索员工（含外部联系人）
    
    Args:
        search_key: 搜索关键词，支持按姓名模糊搜索
    
    Returns:
        员工列表
    """
    url = f"{BASE_URL}/cwork-user/searchEmpByName"
    
    params = {
        "searchKey": search_key
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("resultCode") == 1:
                return result.get("data", {})
            else:
                print(f"接口返回错误: {result.get('resultMsg')}")
                return None
        else:
            print(f"HTTP错误: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return None


# 使用示例
if __name__ == "__main__":
    result = search_employee_by_name("张三")
    if result:
        print("搜索结果:")
        print(json.dumps(result, indent=4, ensure_ascii=False))
```

---

### 示例 2: 批量获取员工信息

```python
def get_employees_by_person_ids(corp_id, person_ids):
    """
    根据 personId+corpId 批量获取员工信息
    
    Args:
        corp_id: 企业ID
        person_ids: personId 列表
    
    Returns:
        员工信息列表
    """
    url = f"{BASE_URL}/cwork-user/employee/getByPersonIds/{corp_id}"
    
    try:
        response = requests.post(
            url, 
            headers=headers, 
            json=person_ids  # Body 直接传数组
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("resultCode") == 1:
                return result.get("data", [])
            else:
                print(f"接口返回错误: {result.get('resultMsg')}")
                return []
        else:
            print(f"HTTP错误: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return []


# 使用示例
if __name__ == "__main__":
    corp_id = 12345
    person_ids = [1001, 1002, 1003]
    employees = get_employees_by_person_ids(corp_id, person_ids)
    print(f"获取到 {len(employees)} 个员工信息")
```

---

### 示例 3: 上传文件

```python
def upload_file(file_path):
    """
    上传本地文件
    
    Args:
        file_path: 本地文件路径
    
    Returns:
        文件ID
    """
    url = f"{BASE_URL}/cwork-file/uploadWholeFile"
    
    # 文件上传需要使用 multipart/form-data，不设置 Content-Type
    file_headers = {
        "appKey": APP_KEY,
        "Accept": "application/json"
    }
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                url, 
                headers=file_headers, 
                files=files
            )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("resultCode") == 1:
                file_id = result.get("data")
                print(f"文件上传成功，文件ID: {file_id}")
                return file_id
            else:
                print(f"接口返回错误: {result.get('resultMsg')}")
                return None
        else:
            print(f"HTTP错误: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return None


# 使用示例
if __name__ == "__main__":
    file_id = upload_file("/path/to/your/file.pdf")
```

---

### 示例 4: 获取文件下载信息

```python
def get_file_download_info(resource_id):
    """
    获取文件下载信息（下载链接有效期1小时）
    
    Args:
        resource_id: 资源ID
    
    Returns:
        下载信息，包含下载URL
    """
    url = f"{BASE_URL}/cwork-file/getDownloadInfo"
    
    params = {
        "resourceId": resource_id
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("resultCode") == 1:
                return result.get("data", {})
            else:
                print(f"接口返回错误: {result.get('resultMsg')}")
                return None
        else:
            print(f"HTTP错误: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return None


def download_file(resource_id, save_path):
    """
    下载文件到本地
    
    Args:
        resource_id: 资源ID
        save_path: 保存路径
    """
    # 1. 获取下载信息
    download_info = get_file_download_info(resource_id)
    if not download_info:
        return False
    
    download_url = download_info.get("downloadUrl")
    file_name = download_info.get("fileName")
    
    print(f"文件名: {file_name}")
    print(f"文件大小: {download_info.get('size')} 字节")
    
    # 2. 下载文件
    try:
        response = requests.get(download_url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"文件已保存到: {save_path}")
            return True
        else:
            print(f"下载失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"下载异常: {str(e)}")
        return False


# 使用示例
if __name__ == "__main__":
    resource_id = 12345
    download_file(resource_id, "/path/to/save/downloaded_file.pdf")
```

---

### 示例 5: 知识库 - 获取文件夹内容

```python
def get_document_children(parent_id, file_type=None, order=None):
    """
    根据父id获取下级文件/文件夹
    
    Args:
        parent_id: 父文件夹id
        file_type: 类型，空为所有，1为文件夹，2为文件
        order: 排序方式
    
    Returns:
        文件/文件夹列表
    """
    url = f"{BASE_URL}/document-database/file/getChildFiles"
    
    params = {
        "parentId": parent_id
    }
    if file_type is not None:
        params["type"] = file_type
    if order is not None:
        params["order"] = order
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("resultCode") == 1:
                return result.get("data", [])
            else:
                print(f"接口返回错误: {result.get('resultMsg')}")
                return []
        else:
            print(f"HTTP错误: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return []


# 使用示例
if __name__ == "__main__":
    # 获取根目录内容（parent_id=0 或具体的根目录id）
    files = get_document_children(0)
    for file in files:
        file_type = "文件夹" if file.get("type") == 1 else "文件"
        print(f"[{file_type}] {file.get('name')}")
```

---

### 示例 6: 发送工作汇报

```python
def submit_report(template_id, main, content, level_params, file_list=None):
    """
    发送工作汇报
    
    Args:
        template_id: 事项ID
        main: 汇报标题
        content: 汇报内容
        level_params: 汇报层级参数列表
        file_list: 附件列表（可选）
    
    Returns:
        汇报基本信息
    """
    url = f"{BASE_URL}/work-report/report/record/submit"
    
    payload = {
        "templateId": template_id,
        "main": main,
        "contentHtml": content,
        "levelParams": level_params
    }
    
    if file_list:
        payload["fileList"] = file_list
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("resultCode") == 1:
                return result.get("data", {})
            else:
                print(f"接口返回错误: {result.get('resultMsg')}")
                return None
        else:
            print(f"HTTP错误: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return None


# 使用示例
if __name__ == "__main__":
    # 构建汇报层级
    level_params = [
        {
            "level": 1,
            "type": "suggest",  # suggest-建议、decide-决策、read-传阅
            "nodeCode": "startNode",
            "nodeName": "发起人",
            "levelUserList": [
                {"empId": 12345, "requirement": ""}
            ]
        },
        {
            "level": 2,
            "type": "decide",
            "nodeCode": "approval",
            "nodeName": "审批人",
            "levelUserList": [
                {"empId": 67890, "requirement": "请审批"}
            ]
        }
    ]
    
    result = submit_report(
        template_id=1001,
        main="本周工作汇报",
        content="<p>本周完成了...</p>",
        level_params=level_params
    )
    
    if result:
        print(f"汇报发送成功，ID: {result.get('id')}")
```

---

### 示例 7: 回复汇报

```python
def reply_report(report_record_id, content, at_emp_ids=None, attachments=None):
    """
    回复工作汇报
    
    Args:
        report_record_id: 汇报记录ID
        content: 回复内容
        at_emp_ids: @的员工ID列表（可选）
        attachments: 附件列表（可选）
    
    Returns:
        回复ID
    """
    url = f"{BASE_URL}/work-report/report/record/reply"
    
    payload = {
        "reportRecordId": str(report_record_id),
        "contentHtml": content,
        "isMedia": 1 if attachments else 0,
        "sendMsg": True
    }
    
    if at_emp_ids:
        payload["addEmpIdList"] = [str(emp_id) for emp_id in at_emp_ids]
    
    if attachments:
        payload["mediaVOList"] = attachments
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("resultCode") == 1:
                reply_id = result.get("data")
                print(f"回复成功，回复ID: {reply_id}")
                return reply_id
            else:
                print(f"接口返回错误: {result.get('resultMsg')}")
                return None
        else:
            print(f"HTTP错误: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return None


# 使用示例
if __name__ == "__main__":
    attachments = [
        {
            "fileId": "12345",
            "name": "附件.pdf",
            "type": "file",
            "fsize": 1024000
        }
    ]
    
    reply_report(
        report_record_id=10001,
        content="<p>收到，已阅</p>",
        at_emp_ids=[12345, 67890],
        attachments=attachments
    )
```

---

### 示例 8: 查询工作任务列表

```python
def search_work_tasks(keyword=None, status=None, page_index=1, page_size=30):
    """
    查询工作任务列表
    
    Args:
        keyword: 任务名称关键字
        status: 任务状态 0-关闭、1-进行中
        page_index: 页码，从1开始
        page_size: 每页数量
    
    Returns:
        分页任务列表
    """
    url = f"{BASE_URL}/work-report/report/plan/searchPage"
    
    payload = {
        "pageIndex": page_index,
        "pageSize": page_size
    }
    
    if keyword:
        payload["keyWord"] = keyword
    if status is not None:
        payload["status"] = status
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("resultCode") == 1:
                data = result.get("data", {})
                return {
                    "total": data.get("total"),
                    "list": data.get("list", []),
                    "pageNum": data.get("pageNum"),
                    "pageSize": data.get("pageSize")
                }
            else:
                print(f"接口返回错误: {result.get('resultMsg')}")
                return None
        else:
            print(f"HTTP错误: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return None


# 使用示例
if __name__ == "__main__":
    result = search_work_tasks(
        keyword="项目",
        status=1,  # 进行中
        page_index=1,
        page_size=10
    )
    
    if result:
        print(f"共 {result['total']} 条记录")
        for task in result['list']:
            print(f"- {task['main']} (状态: {task['status']})")
```

---

### 示例 9: 查询 BP 周期列表

```python
def get_bp_periods(name=None):
    """
    查询 BP 目标管理周期列表
    
    Args:
        name: 周期名称（模糊搜索）
    
    Returns:
        周期列表
    """
    url = f"{BASE_URL}/bp/period/getAllPeriod"
    
    params = {}
    if name:
        params["name"] = name
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("resultCode") == 1:
                return result.get("data", [])
            else:
                print(f"接口返回错误: {result.get('resultMsg')}")
                return []
        else:
            print(f"HTTP错误: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return []


# 使用示例
if __name__ == "__main__":
    periods = get_bp_periods("2024")
    for period in periods:
        print(f"周期: {period['name']} ({period['year']})")
        print(f"  时间: {period['startDate']} ~ {period['endDate']}")
        print(f"  状态: {'启用' if period['status'] == 1 else '未启用'}")
```

---

### 示例 10: 获取待办列表

```python
def get_todo_list(page_index=1, page_size=30, report_record_type=None):
    """
    获取待处理列表
    
    Args:
        page_index: 页码
        page_size: 每页数量
        report_record_type: 汇报类型 1-工作交流、2-工作指引、3-文件签批、4-AI汇报、5-工作汇报
    
    Returns:
        分页待办列表
    """
    url = f"{BASE_URL}/work-report/todoTask/todoList"
    
    payload = {
        "pageIndex": page_index,
        "pageSize": page_size
    }
    
    if report_record_type:
        payload["reportRecordType"] = report_record_type
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("resultCode") == 1:
                data = result.get("data", {})
                return {
                    "total": data.get("total"),
                    "list": data.get("list", []),
                    "pageNum": data.get("pageNum"),
                    "pageSize": data.get("pageSize")
                }
            else:
                print(f"接口返回错误: {result.get('resultMsg')}")
                return None
        else:
            print(f"HTTP错误: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return None


# 使用示例
if __name__ == "__main__":
    result = get_todo_list(page_index=1, page_size=20)
    if result:
        print(f"共 {result['total']} 条待办")
        for todo in result['list']:
            print(f"- [{todo.get('levelType')}] {todo.get('main')}")
            print(f"  来自: {todo.get('writeEmpName')}")
```

---

## 错误处理最佳实践

```python
class CworkAPIError(Exception):
    """玄关开放平台 API 错误"""
    def __init__(self, message, result_code=None, result_msg=None):
        super().__init__(message)
        self.result_code = result_code
        self.result_msg = result_msg


def api_request(method, url, **kwargs):
    """
    统一的 API 请求封装
    
    Args:
        method: 请求方法 (get/post/put/delete)
        url: 请求地址
        **kwargs: 其他参数
    
    Returns:
        API 响应数据
    
    Raises:
        CworkAPIError: API 调用失败
    """
    try:
        response = requests.request(method, url, **kwargs)
        
        # 检查 HTTP 状态码
        if response.status_code != 200:
            raise CworkAPIError(
                f"HTTP错误: {response.status_code}",
                result_code=response.status_code
            )
        
        # 解析响应
        result = response.json()
        
        # 检查业务状态码
        if result.get("resultCode") != 1:
            raise CworkAPIError(
                f"业务错误: {result.get('resultMsg')}",
                result_code=result.get("resultCode"),
                result_msg=result.get("resultMsg")
            )
        
        return result.get("data")
        
    except requests.exceptions.RequestException as e:
        raise CworkAPIError(f"网络请求异常: {str(e)}")
    except json.JSONDecodeError as e:
        raise CworkAPIError(f"响应解析失败: {str(e)}")


# 使用示例
try:
    data = api_request(
        "get",
        f"{BASE_URL}/cwork-user/searchEmpByName",
        headers=headers,
        params={"searchKey": "张三"}
    )
    print(f"搜索结果: {data}")
except CworkAPIError as e:
    print(f"API调用失败: {e}")
    print(f"错误码: {e.result_code}")
    print(f"错误信息: {e.result_msg}")
```
