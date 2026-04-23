#!/usr/bin/env python3
"""
日程增删改查和冲突检测核心逻辑
"""

import json
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import copy

# 尝试相对导入，如果失败则使用绝对导入
try:
    from .config_manager import expand_user
except ImportError:
    # 直接运行脚本时的导入方式
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config_manager import expand_user

class ScheduleManager:
    def __init__(self, data_path: str):
        self.data_path = expand_user(data_path)
        self._ensure_dir_exists()
        self.data = self._load_data()
        self._last_save_time = time.time()
        self._save_interval = 300  # 自动保存间隔（秒）
    
    def _ensure_dir_exists(self):
        dir_path = os.path.dirname(self.data_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, mode=0o700)  # 设置目录权限为仅当前用户可访问
    
    def _load_data(self) -> Dict:
        if not os.path.exists(self.data_path):
            return {
                "version": 1,
                "schedules": []
            }
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # 如果文件损坏，返回空数据
            return {
                "version": 1,
                "schedules": []
            }
        except Exception as e:
            # 其他错误，返回空数据
            print(f"加载数据文件失败: {e}", file=sys.stderr)
            return {
                "version": 1,
                "schedules": []
            }
    
    def _save_data(self, force: bool = False):
        # 检查是否需要保存
        current_time = time.time()
        if not force and current_time - self._last_save_time < self._save_interval:
            return
        
        try:
            # 保存前确保目录存在
            self._ensure_dir_exists()
            # 写入文件
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            # 在Windows上设置文件属性为隐藏
            if os.name == 'nt':
                try:
                    import ctypes
                    FILE_ATTRIBUTE_HIDDEN = 0x02
                    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                    file_attr = kernel32.GetFileAttributesW(self.data_path)
                    if file_attr != -1:
                        kernel32.SetFileAttributesW(self.data_path, file_attr | FILE_ATTRIBUTE_HIDDEN)
                except Exception:
                    pass
            # 更新最后保存时间
            self._last_save_time = current_time
        except Exception as e:
            print(f"保存数据文件失败: {e}", file=sys.stderr)
    
    def save(self):
        """手动保存数据"""
        self._save_data(force=True)
    
    def _parse_datetime(self, dt_str: str) -> datetime:
        return datetime.fromisoformat(dt_str)
    
    def check_conflict(self, new_dt: datetime, exclude_id: str = None, threshold_minutes: int = 30) -> List[Dict]:
        """
        检查时间冲突，返回和新时间间隔小于 threshold_minutes 的已有日程
        """
        conflicts = []
        new_start = new_dt - timedelta(minutes=threshold_minutes)
        new_end = new_dt + timedelta(minutes=threshold_minutes)
        
        for schedule in self.data['schedules']:
            if schedule['id'] == exclude_id:
                continue
            dt = self._parse_datetime(schedule['datetime'])
            if not (dt <= new_start or dt >= new_end):
                conflicts.append(schedule)
        return conflicts
    
    def add_schedule(self, schedule: Dict) -> Tuple[bool, List[Dict], str]:
        """添加日程，返回 (是否成功，冲突列表，消息)"""
        # 验证输入数据完整性
        required_fields = ['id', 'type', 'datetime', 'what']
        for field in required_fields:
            if field not in schedule:
                return False, [], f"缺少必要字段: {field}"
        
        # 验证数据类型
        if not isinstance(schedule['id'], str) or not schedule['id']:
            return False, [], "无效的日程ID"
        if schedule['type'] not in ['schedule', 'ddl']:
            return False, [], "无效的日程类型"
        if not isinstance(schedule['what'], str) or not schedule['what']:
            return False, [], "无效的日程内容"
        
        # 验证日期时间格式
        try:
            dt = self._parse_datetime(schedule['datetime'])
        except Exception as e:
            return False, [], f"无效的日期时间格式: {e}"
        
        # 验证日期时间是否合理（不允许过去的时间）
        if dt < datetime.now().astimezone() - timedelta(minutes=5):
            return False, [], "日程时间不能是过去的时间"
        
        # 验证地点和出发地（如果存在）
        if 'where' in schedule and schedule['where'] is not None:
            if not isinstance(schedule['where'], str):
                return False, [], "无效的地点"
        if 'from_address' in schedule and schedule['from_address'] is not None:
            if not isinstance(schedule['from_address'], str):
                return False, [], "无效的出发地"
        
        # 检查时间冲突
        conflicts = self.check_conflict(dt)
        if conflicts:
            return False, conflicts, f"检测到{len(conflicts)}个时间冲突"
        
        self.data['schedules'].append(schedule)
        self._save_data()  # 使用自动保存机制，减少文件IO
        return True, [], "添加成功"
    
    def update_schedule(self, schedule_id: str, updated_data: Dict) -> Tuple[bool, List[Dict], str]:
        """更新日程"""
        # 验证输入参数
        if not schedule_id or not isinstance(schedule_id, str):
            return False, [], "无效的日程ID"
        if not updated_data or not isinstance(updated_data, dict):
            return False, [], "无效的更新数据"
        
        for i, schedule in enumerate(self.data['schedules']):
            if schedule['id'] == schedule_id:
                updated = copy.deepcopy(schedule)
                updated.update(updated_data)
                updated['updated_at'] = datetime.now().astimezone().isoformat()
                
                # 验证更新后的数据
                required_fields = ['id', 'type', 'datetime', 'what']
                for field in required_fields:
                    if field not in updated:
                        return False, [], f"缺少必要字段: {field}"
                
                # 验证数据类型
                if not isinstance(updated['type'], str) or updated['type'] not in ['schedule', 'ddl']:
                    return False, [], "无效的日程类型"
                if not isinstance(updated['what'], str) or not updated['what']:
                    return False, [], "无效的日程内容"
                
                # 验证日期时间格式
                try:
                    dt = self._parse_datetime(updated['datetime'])
                except Exception as e:
                    return False, [], f"无效的日期时间格式: {e}"
                
                # 验证日期时间是否合理（不允许过去的时间）
                if dt < datetime.now().astimezone() - timedelta(minutes=5):
                    return False, [], "日程时间不能是过去的时间"
                
                # 验证地点和出发地（如果存在）
                if 'where' in updated and updated['where'] is not None:
                    if not isinstance(updated['where'], str):
                        return False, [], "无效的地点"
                if 'from_address' in updated and updated['from_address'] is not None:
                    if not isinstance(updated['from_address'], str):
                        return False, [], "无效的出发地"
                
                # 检查时间冲突
                conflicts = self.check_conflict(dt, exclude_id=schedule_id)
                if conflicts:
                    return False, conflicts, f"检测到{len(conflicts)}个时间冲突"
                
                self.data['schedules'][i] = updated
                self._save_data()  # 使用自动保存机制，减少文件IO
                return True, [], "更新成功"
        
        return False, [], "找不到该日程"
    
    def delete_schedule(self, schedule_id: str) -> Tuple[bool, str]:
        """删除日程"""
        # 验证输入参数
        if not schedule_id or not isinstance(schedule_id, str):
            return False, "无效的日程ID"
        
        for i, schedule in enumerate(self.data['schedules']):
            if schedule['id'] == schedule_id:
                del self.data['schedules'][i]
                self._save_data()  # 使用自动保存机制，减少文件IO
                return True, "删除成功"
        return False, "找不到该日程"
    
    def find_matching_schedule(self, text: str) -> Optional[Dict]:
        """根据用户描述匹配最接近的日程（用于修改/删除）"""
        # 简单策略：找时间最接近现在，并且文本包含关键词的
        now = datetime.now().astimezone()
        best_match = None
        best_score = 0
        
        text_lower = text.lower()
        for schedule in self.data['schedules']:
            score = 0
            # 关键词匹配
            if schedule['what'].lower() in text_lower or schedule['where'].lower() in text_lower:
                score += 10
            # 时间越近分数越高
            dt = self._parse_datetime(schedule['datetime'])
            delta = abs((dt - now).total_seconds())
            if delta > 0:
                score += 100000 / delta
            
            if score > best_score:
                best_score = score
                best_match = schedule
        
        return best_match
    
    def list_by_date_range(self, start: datetime, end: datetime) -> List[Dict]:
        """列出时间范围内的日程，按时间排序"""
        # 预解析所有日程的时间，提高查询效率
        parsed_schedules = []
        for schedule in self.data['schedules']:
            try:
                dt = self._parse_datetime(schedule['datetime'])
                if start <= dt <= end:
                    parsed_schedules.append((dt, schedule))
            except Exception:
                # 跳过解析失败的日程
                continue
        
        # 按时间排序
        parsed_schedules.sort(key=lambda x: x[0])
        # 提取日程对象
        result = [schedule for _, schedule in parsed_schedules]
        return result
    
    def list_today(self, include_expired: bool = False) -> List[Dict]:
        """列出今天的日程，默认过滤掉已经过期的"""
        now = datetime.now().astimezone()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        result = self.list_by_date_range(start, end)
        if not include_expired:
            # 过滤掉已经过了时间的
            result = [s for s in result if datetime.fromisoformat(s['datetime']) > now]
        return result
    
    def list_week(self) -> List[Dict]:
        """列出本周的日程"""
        now = datetime.now().astimezone()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start = start - timedelta(days=start.weekday())
        end = start + timedelta(days=7)
        return self.list_by_date_range(start, end)

if __name__ == "__main__":
    import sys
    # 修复Windows中文输出乱码：强制stdout用utf-8
    if sys.stdout.encoding and 'utf' not in sys.stdout.encoding.lower():
        sys.stdout.reconfigure(encoding='utf-8')
    manager = ScheduleManager("~/.openclaw/workspace/data/simple-schedule/schedule.json")
    if len(sys.argv) > 1 and sys.argv[1] == "list-today":
        schedules = manager.list_today()
        print(json.dumps(schedules, ensure_ascii=False, indent=2))
