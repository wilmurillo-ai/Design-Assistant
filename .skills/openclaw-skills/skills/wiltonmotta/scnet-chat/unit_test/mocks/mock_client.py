#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock SCNetClient - 模拟客户端行为
"""

from unittest.mock import MagicMock, patch
from api_responses import (
    MockTokenResponse,
    MockClusterInfo,
    MockJobInfo,
    MockNotebookInfo,
    MockContainerInfo,
    MockFileInfo,
)


class MockSCNetClient:
    """
    Mock SCNet 客户端
    
    用于单元测试，模拟所有 API 调用行为
    """
    
    def __init__(self):
        self.access_key = "mock_access_key"
        self.secret_key = "mock_secret_key"
        self.user = "mockuser"
        self.tokens_data = MockTokenResponse.success()
        self._notebook_manager = None
        self._container_manager = None
        self._file_manager = None
    
    def init_tokens(self):
        """模拟初始化 Token"""
        return True
    
    def get_default_token(self):
        return "mock_token_123456789"
    
    def get_default_cluster_name(self):
        return "华东一区【昆山】"
    
    def get_home_path(self, cluster_name=None):
        return "/public/home/mockuser"
    
    def get_token(self, cluster_name=None):
        return "mock_token_123456789"
    
    def get_hpc_url(self, cluster_name=None):
        return "https://mock.hpc.scnet.cn"
    
    def get_efile_url(self, cluster_name=None):
        return "https://mock.efile.scnet.cn"
    
    def get_scheduler_id(self, cluster_name=None):
        return "1"
    
    # ========== 账户操作 ==========
    
    def get_account_info(self):
        return {
            "code": "0",
            "msg": "success",
            "data": {
                "userName": "mockuser",
                "balance": "1000.00"
            }
        }
    
    # ========== 作业操作 ==========
    
    def get_user_queues(self, cluster_name=None):
        return {
            "code": "0",
            "msg": "success",
            "data": [
                {"queueName": "comp", "status": "open"},
                {"queueName": "debug", "status": "open"}
            ]
        }
    
    def submit_job(self, job_config, cluster_name=None):
        return MockJobInfo.submit_success("12345678")
    
    def get_job_detail(self, job_id, cluster_name=None):
        return MockJobInfo.job_detail(job_id, "statR")
    
    def get_running_jobs(self, cluster_name=None):
        return MockJobInfo.job_list(2)
    
    def get_history_jobs(self, days=7, cluster_name=None):
        return MockJobInfo.job_list(2)
    
    def delete_job(self, job_id, cluster_name=None):
        return {"code": "0", "msg": "success"}
    
    def submit_job_and_monitor(self, job_config, cluster_name=None, 
                                check_interval=180, enable_feishu=True, 
                                use_daemon=False):
        """模拟提交并监控"""
        submit_result = self.submit_job(job_config, cluster_name)
        return {
            'success': True,
            'job_id': '12345678',
            'monitor_started': True,
            'check_interval': check_interval,
            'submit_result': submit_result
        }
    
    # ========== 文件操作 ==========
    
    def list_dir(self, path=None, cluster_name=None):
        return MockFileInfo.file_list(path)
    
    def mkdir(self, path, create_parents=True, cluster_name=None):
        return True
    
    def touch(self, file_path, cluster_name=None):
        return True
    
    def upload(self, local_path, remote_path, cluster_name=None):
        return True
    
    def download(self, remote_path, local_path, cluster_name=None):
        # 模拟下载：创建一个本地文件
        try:
            import os
            dir_path = os.path.dirname(local_path)
            if dir_path:  # 只有当目录路径不为空时才创建
                os.makedirs(dir_path, exist_ok=True)
            with open(local_path, 'w') as f:
                f.write("Mock downloaded content")
            return True
        except Exception as e:
            print(f"Mock download error: {e}")
            return False
    
    def remove(self, path, recursive=False, cluster_name=None):
        return True
    
    def exists(self, path, cluster_name=None):
        return True
    
    # ========== Notebook 操作 ==========
    
    def get_notebook_manager(self):
        if self._notebook_manager is None:
            self._notebook_manager = MockNotebookManager()
        return self._notebook_manager
    
    # ========== 容器操作 ==========
    
    def get_container_manager(self):
        if self._container_manager is None:
            self._container_manager = MockContainerManager()
        return self._container_manager
    
    def get_file_manager(self):
        if self._file_manager is None:
            self._file_manager = MockFileManager()
        return self._file_manager


class MockNotebookManager:
    """Mock Notebook 管理器"""
    
    def __init__(self):
        self._notebooks = {}
    
    def get_images(self, **kwargs):
        """获取镜像列表"""
        return {
            "code": "0",
            "msg": "success",
            "data": {
                "list": [
                    {
                        "imagePath": "/mock/image1",
                        "imageName": "mock-image-1",
                        "version": "1.0"
                    }
                ]
            }
        }
    
    def create_notebook(self, cluster_id, image_config, 
                       accelerator_type="DCU", accelerator_number="1", **kwargs):
        import uuid
        notebook_id = f"nb-{uuid.uuid4().hex[:8]}"
        self._notebooks[notebook_id] = {
            "id": notebook_id,
            "status": "Creating",
            "cluster_id": cluster_id
        }
        return MockNotebookInfo.create_success(notebook_id)
    
    def start_notebook(self, notebook_id):
        if notebook_id in self._notebooks:
            self._notebooks[notebook_id]["status"] = "Running"
        return {"code": "0", "msg": "success"}
    
    def stop_notebook(self, notebook_id, save_env=False):
        if notebook_id in self._notebooks:
            self._notebooks[notebook_id]["status"] = "Terminated"
        return {"code": "0", "msg": "success"}
    
    def release_notebook(self, notebook_id):
        if notebook_id in self._notebooks:
            del self._notebooks[notebook_id]
        return {"code": "0", "msg": "success"}
    
    def list_notebooks(self, **kwargs):
        return MockNotebookInfo.notebook_list(len(self._notebooks))
    
    def get_notebook_detail(self, notebook_id):
        status = "Running" if notebook_id in self._notebooks else "Terminated"
        return MockNotebookInfo.notebook_detail(notebook_id, status)


class MockContainerManager:
    """Mock 容器管理器"""
    
    def __init__(self):
        self._containers = {}
    
    def get_resource_groups(self):
        return {"code": "0", "msg": "success", "data": []}
    
    def get_images(self, **kwargs):
        """获取镜像列表"""
        return {
            "code": "0",
            "msg": "success",
            "data": {
                "list": [
                    {
                        "imagePath": "/mock/container-image",
                        "version": "latest"
                    }
                ]
            }
        }
    
    def create_container(self, config):
        import uuid
        instance_id = f"container-{uuid.uuid4().hex[:8]}"
        self._containers[instance_id] = {
            "id": instance_id,
            "status": "Deploying",
            "config": config
        }
        return MockContainerInfo.create_success(instance_id)
    
    def start_container(self, instance_service_id):
        if instance_service_id in self._containers:
            self._containers[instance_service_id]["status"] = "Running"
        return {"code": "0", "msg": "success"}
    
    def stop_containers(self, ids):
        for cid in ids:
            if cid in self._containers:
                self._containers[cid]["status"] = "Terminated"
        return {"code": "0", "msg": "success"}
    
    def delete_containers(self, ids):
        for cid in ids:
            if cid in self._containers:
                del self._containers[cid]
        return {"code": "0", "msg": "success"}
    
    def list_containers(self, **kwargs):
        return MockContainerInfo.container_list(len(self._containers))
    
    def get_container_detail(self, instance_id):
        status = "Running" if instance_id in self._containers else "Terminated"
        return MockContainerInfo.container_detail(instance_id, status)


class MockFileManager:
    """Mock 文件管理器"""
    
    def list_files(self, path=None, limit=100):
        return MockFileInfo.file_list(path)
    
    def create_folder(self, path, create_parents=True):
        return True
    
    def create_file(self, file_path):
        return True
    
    def upload_file(self, local_path, remote_path, cover="cover"):
        return True
    
    def download_file(self, remote_path, local_path):
        return True
    
    def delete_file(self, path, recursive=False):
        return True
    
    def check_exists(self, path):
        return True
