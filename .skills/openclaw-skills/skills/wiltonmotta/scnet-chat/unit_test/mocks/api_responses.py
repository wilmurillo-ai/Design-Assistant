#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock API 响应数据
"""

import time
from datetime import datetime, timedelta


class MockTokenResponse:
    """模拟 Token 响应"""
    
    @staticmethod
    def success():
        return {
            "code": "0",
            "msg": "success",
            "data": [
                {
                    "clusterId": "11250",
                    "clusterName": "华东一区【昆山】",
                    "token": "mock_token_123456789",
                    "default": True
                },
                {
                    "clusterId": "11251",
                    "clusterName": "西北一区【西安】",
                    "token": "mock_token_987654321",
                    "default": False
                }
            ]
        }
    
    @staticmethod
    def failure():
        return {
            "code": "10001",
            "msg": "认证失败",
            "data": None
        }


class MockClusterInfo:
    """模拟集群信息响应"""
    
    @staticmethod
    def center_info():
        return {
            "code": "0",
            "msg": "success",
            "data": {
                "hpcUrls": [
                    {"url": "https://mock.hpc.scnet.cn", "enable": "true"}
                ],
                "aiUrls": [
                    {"url": "https://mock.ai.scnet.cn", "enable": "true"}
                ],
                "efileUrls": [
                    {"url": "https://mock.efile.scnet.cn", "enable": "true"}
                ],
                "clusterUserInfo": {
                    "homePath": "/public/home/mockuser"
                }
            }
        }
    
    @staticmethod
    def cluster_detail():
        return {
            "code": "0",
            "msg": "success",
            "data": [
                {"id": "1", "name": "cluster1", "status": "active"}
            ]
        }


class MockJobInfo:
    """模拟作业信息响应"""
    
    @staticmethod
    def submit_success(job_id="12345678"):
        return {
            "code": "0",
            "msg": "success",
            "data": job_id
        }
    
    @staticmethod
    def job_detail(job_id="12345678", status="statR"):
        return {
            "code": "0",
            "msg": "success",
            "data": {
                "jobId": job_id,
                "jobName": f"test_job_{job_id}",
                "jobStatus": status,
                "jobManager": "pbs",
                "jobQueue": "comp",
                "jobNodes": "1",
                "jobCpus": "4",
                "jobWalltime": "01:00:00",
                "jobWorkDir": "/public/home/mockuser/workspace"
            }
        }
    
    @staticmethod
    def job_list(count=2):
        jobs = []
        for i in range(count):
            jobs.append({
                "jobId": f"1234567{i}",
                "jobName": f"job_{i}",
                "jobStatus": "statR" if i == 0 else "statC",
                "jobQueue": "comp"
            })
        return {
            "code": "0",
            "msg": "success",
            "data": {
                "list": jobs,
                "total": count
            }
        }


class MockNotebookInfo:
    """模拟 Notebook 信息响应"""
    
    @staticmethod
    def create_success(notebook_id="nb-123456"):
        return {
            "code": "0",
            "msg": "success",
            "data": {
                "notebookId": notebook_id,
                "name": f"test-notebook-{notebook_id}",
                "status": "Creating"
            }
        }
    
    @staticmethod
    def notebook_detail(notebook_id="nb-123456", status="Running"):
        return {
            "code": "0",
            "msg": "success",
            "data": {
                "id": notebook_id,
                "notebookName": f"test-notebook-{notebook_id}",
                "status": status,
                "clusterId": "11250",
                "acceleratorType": "DCU",
                "acceleratorNumber": "1",
                "jupyterUrl": f"https://jupyter-{notebook_id}.scnet.cn"
            }
        }
    
    @staticmethod
    def notebook_list(count=2):
        notebooks = []
        for i in range(count):
            notebooks.append({
                "id": f"nb-{i}23456",
                "notebookName": f"notebook_{i}",
                "status": "Running" if i == 0 else "Terminated"
            })
        return {
            "code": "0",
            "msg": "success",
            "data": {
                "list": notebooks,
                "total": count
            }
        }


class MockContainerInfo:
    """模拟容器信息响应"""
    
    @staticmethod
    def create_success(instance_id="container-123456"):
        return {
            "code": "0",
            "msg": "success",
            "data": instance_id
        }
    
    @staticmethod
    def container_detail(instance_id="container-123456", status="Running"):
        return {
            "code": "0",
            "msg": "success",
            "data": {
                "id": instance_id,
                "instanceServiceName": f"test-container-{instance_id}",
                "status": status,
                "acceleratorType": "dcu",
                "cpuNumber": 3,
                "gpuNumber": 1,
                "ramSize": 15360,
                "accessUrl": f"https://{instance_id}.scnet.cn"
            }
        }
    
    @staticmethod
    def container_list(count=2):
        containers = []
        for i in range(count):
            containers.append({
                "id": f"container-{i}23456",
                "instanceServiceName": f"container_{i}",
                "status": "Running" if i == 0 else "Terminated"
            })
        return {
            "code": "0",
            "msg": "success",
            "data": {
                "list": containers,
                "total": count
            }
        }


class MockFileInfo:
    """模拟文件信息响应"""
    
    @staticmethod
    def file_list(path="/public/home/mockuser"):
        return {
            "code": "0",
            "msg": "success",
            "data": {
                "total": 3,
                "fileList": [
                    {"name": "workspace", "path": f"{path}/workspace", "isDirectory": True},
                    {"name": "test.txt", "path": f"{path}/test.txt", "isDirectory": False, "size": 1024},
                    {"name": "data", "path": f"{path}/data", "isDirectory": True}
                ]
            }
        }
    
    @staticmethod
    def file_exists(exists=True):
        return {
            "code": "0",
            "msg": "success",
            "data": {
                "exist": exists
            }
        }
    
    @staticmethod
    def operation_success():
        return {
            "code": "0",
            "msg": "success"
        }
