#!/usr/bin/env python3
# 中医面诊分析工具配置文件
import os
import sys

# def import_path_common():
#     current_dir = os.path.dirname(os.path.abspath(__file__))  # .../face_analysis/scripts
#     # common 位于 /root/.openclaw/workspace/skills/scripts/common
#     skills_dir = os.path.dirname(os.path.dirname(current_dir))  # .../skills
#     workspace_dir = os.path.dirname(skills_dir)  # .../skills
#     common_dir = os.path.join(skills_dir, 'scripts', 'common')
#     scripts_dir = os.path.join(skills_dir, 'scripts')
#     if scripts_dir not in sys.path:
#         sys.path.insert(1, workspace_dir)
#         sys.path.insert(1, scripts_dir)
#         sys.path.insert(1, common_dir)
#
#
# import_path_common()
from enum import Enum

from skills.scripts.common.config import ApiEnum as ApiEnumBase, ConstantEnum as ConstantEnumBase


class ApiEnum(ApiEnumBase):
    ANALYSIS_URL = "/web/health-analysis/v2/start-health-analysis"

    ANALYSIS_RESULT_URL = "/web/health-analysis/get-health-analysis-result"

    PAGE_URL = "/web/health-analysis/page-health-analysis-result"

    DETAIL_EXPORT_URL = ApiEnumBase.BASE_URL_HEALTH + "/health/order/api/getReportDetailExport?id="


class SceneCodeEnum(Enum):
    OPEN_HEALTH_AI_ANALYSIS = "OPEN_HEALTH_AI_ANALYSIS"
    OPEN_PERSON_RISK_ANALYSIS = "OPEN_PERSON_RISK_ANALYSIS"


class ConstantEnum(ConstantEnumBase):
    DEFAULT__SCENE_CODE = SceneCodeEnum.OPEN_HEALTH_AI_ANALYSIS.value

    # 视频上传参数
    SUPPORTED_FORMATS = ["mp4", "avi", "mov"]
    MAX_FILE_SIZE_MB = 100  # 最大支持100MB视频
