#!/usr/bin/env python3
"""
Lann预约信息验证脚本
用于验证预约请求参数的完整性和正确性

注意：此工具为独立的辅助验证工具，不依赖 MCP 协议，可独立使用。
主要用于在调用 MCP 工具前验证参数格式是否正确。
"""

import re
import sys
from datetime import datetime, timedelta
import json

class BookingValidator:
    """预约验证器"""
    
    def __init__(self):
        # 手机号正则：11位数字，1开头
        self.phone_regex = re.compile(r'^1[3-9]\d{9}$')
        
        # 支持的时长列表（分钟）
        self.supported_durations = [60, 90, 120, 150]
        
        # 最大预约人数
        self.max_people = 20
        
        # 最小预约人数
        self.min_people = 1
        
        # 预约时间限制（天）
        self.max_booking_days = 30
        self.min_booking_hours = 1
    
    def validate_phone(self, phone: str) -> tuple:
        """验证手机号格式
        
        Args:
            phone: 手机号字符串
            
        Returns:
            (是否有效, 错误信息)
        """
        if not phone:
            return False, "手机号不能为空"
        
        if not self.phone_regex.match(phone):
            return False, "手机号格式不正确，应为11位中国大陆手机号"
        
        return True, "手机号格式正确"
    
    def validate_store_name(self, store_name: str) -> tuple:
        """验证门店名称
        
        Args:
            store_name: 门店名称
            
        Returns:
            (是否有效, 错误信息)
        """
        if not store_name:
            return False, "门店名称不能为空"
        
        if len(store_name.strip()) < 2:
            return False, "门店名称过短"
        
        # 检查是否包含特殊字符
        if re.search(r'[<>{}[\]]', store_name):
            return False, "门店名称包含非法字符"
        
        return True, "门店名称格式正确"
    
    def validate_service_name(self, service_name: str) -> tuple:
        """验证服务名称
        
        Args:
            service_name: 服务名称
            
        Returns:
            (是否有效, 错误信息)
        """
        if not service_name:
            return False, "服务名称不能为空"
        
        if len(service_name.strip()) < 3:
            return False, "服务名称过短"
        
        # 检查是否包含特殊字符
        if re.search(r'[<>{}[\]]', service_name):
            return False, "服务名称包含非法字符"
        
        return True, "服务名称格式正确"
    
    def validate_people_count(self, people_count: int) -> tuple:
        """验证预约人数
        
        Args:
            people_count: 预约人数
            
        Returns:
            (是否有效, 错误信息)
        """
        if not isinstance(people_count, int):
            return False, "预约人数应为整数"
        
        if people_count < self.min_people:
            return False, f"预约人数不能少于{self.min_people}人"
        
        if people_count > self.max_people:
            return False, f"预约人数不能超过{self.max_people}人"
        
        return True, "预约人数正确"
    
    def validate_booking_time(self, booking_time_str: str) -> tuple:
        """验证预约时间
        
        Args:
            booking_time_str: ISO 8601格式的时间字符串
            
        Returns:
            (是否有效, 错误信息, 解析后的datetime对象)
        """
        if not booking_time_str:
            return False, "预约时间不能为空", None
        
        try:
            # 解析ISO 8601格式时间
            booking_time = datetime.fromisoformat(booking_time_str.replace('Z', '+00:00'))
        except ValueError:
            return False, "预约时间格式不正确，请使用ISO 8601格式（如：2024-01-15T14:00:00）", None
        
        # 获取当前时间
        now = datetime.now()
        
        # 检查是否为未来时间
        if booking_time <= now:
            return False, "预约时间必须为未来时间", booking_time
        
        # 检查是否在未来30天内
        max_future_time = now + timedelta(days=self.max_booking_days)
        if booking_time > max_future_time:
            return False, f"预约时间不能超过{self.max_booking_days}天", booking_time
        
        # 检查是否至少1小时后
        min_future_time = now + timedelta(hours=self.min_booking_hours)
        if booking_time < min_future_time:
            return False, f"预约时间需至少{self.min_booking_hours}小时后", booking_time
        
        return True, "预约时间正确", booking_time
    
    def validate_booking_request(self, booking_data: dict) -> dict:
        """验证完整的预约请求
        
        Args:
            booking_data: 预约请求数据
            
        Returns:
            验证结果字典
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "validated_data": {}
        }
        
        # 检查必需字段
        required_fields = ['phone', 'storeName', 'serviceName', 'peopleCount', 'bookingTime']
        missing_fields = []
        for field in required_fields:
            if field not in booking_data:
                missing_fields.append(field)
        
        if missing_fields:
            results["valid"] = False
            results["errors"].append(f"缺少必需字段: {', '.join(missing_fields)}")
            return results
        
        # 验证手机号
        phone_valid, phone_msg = self.validate_phone(booking_data['phone'])
        if not phone_valid:
            results["valid"] = False
            results["errors"].append(f"手机号错误: {phone_msg}")
        else:
            results["validated_data"]["phone"] = booking_data['phone']
        
        # 验证门店名称
        store_valid, store_msg = self.validate_store_name(booking_data['storeName'])
        if not store_valid:
            results["valid"] = False
            results["errors"].append(f"门店名称错误: {store_msg}")
        else:
            results["validated_data"]["storeName"] = booking_data['storeName']
        
        # 验证服务名称
        service_valid, service_msg = self.validate_service_name(booking_data['serviceName'])
        if not service_valid:
            results["valid"] = False
            results["errors"].append(f"服务名称错误: {service_msg}")
        else:
            results["validated_data"]["serviceName"] = booking_data['serviceName']
        
        # 验证预约人数
        try:
            people_count = int(booking_data['peopleCount'])
        except (ValueError, TypeError):
            results["valid"] = False
            results["errors"].append("预约人数应为整数")
        else:
            people_valid, people_msg = self.validate_people_count(people_count)
            if not people_valid:
                results["valid"] = False
                results["errors"].append(f"预约人数错误: {people_msg}")
            else:
                results["validated_data"]["peopleCount"] = people_count
        
        # 验证预约时间
        time_valid, time_msg, parsed_time = self.validate_booking_time(booking_data['bookingTime'])
        if not time_valid:
            results["valid"] = False
            results["errors"].append(f"预约时间错误: {time_msg}")
        else:
            results["validated_data"]["bookingTime"] = booking_data['bookingTime']
            results["validated_data"]["parsedTime"] = parsed_time.isoformat()
        
        # 检查所有验证是否通过
        if not results["valid"]:
            results["summary"] = "预约信息验证失败"
        else:
            results["summary"] = "预约信息验证通过"
            results["warnings"].append("建议确认门店和服务信息的准确性")
        
        return results

def main():
    """主函数：验证预约请求"""
    validator = BookingValidator()
    
    # 示例预约数据
    sample_booking = {
        "phone": "13800138000",
        "storeName": "淮海店",
        "serviceName": "传统古法全身按摩 -90分钟",
        "peopleCount": 2,
        "bookingTime": "2024-01-15T14:00:00"
    }
    
    print("=== Lann预约信息验证工具 ===")
    print()
    
    # 演示验证过程
    print("1. 验证示例预约数据:")
    print(f"   手机号: {sample_booking['phone']}")
    print(f"   门店: {sample_booking['storeName']}")
    print(f"   服务: {sample_booking['serviceName']}")
    print(f"   人数: {sample_booking['peopleCount']}")
    print(f"   时间: {sample_booking['bookingTime']}")
    print()
    
    result = validator.validate_booking_request(sample_booking)
    
    print("2. 验证结果:")
    print(f"   总体状态: {result['summary']}")
    print(f"   是否有效: {'是' if result['valid'] else '否'}")
    
    if result['errors']:
        print(f"   错误信息:")
        for error in result['errors']:
            print(f"     - {error}")
    
    if result['warnings']:
        print(f"   警告信息:")
        for warning in result['warnings']:
            print(f"     - {warning}")
    
    print()
    print("3. 验证通过的数据:")
    if result['validated_data']:
        for key, value in result['validated_data'].items():
            if key != 'parsedTime':  # 跳过内部字段
                print(f"   {key}: {value}")
    
    # 命令行参数处理
    if len(sys.argv) > 1:
        print()
        print("4. 验证命令行参数:")
        
        if sys.argv[1] == "--validate":
            if len(sys.argv) > 2:
                try:
                    booking_json = sys.argv[2]
                    booking_data = json.loads(booking_json)
                    user_result = validator.validate_booking_request(booking_data)
                    
                    print(f"   验证结果: {user_result['summary']}")
                    
                    if not user_result['valid']:
                        print("   错误详情:")
                        for error in user_result['errors']:
                            print(f"      {error}")
                        sys.exit(1)
                    else:
                        print("   验证通过!")
                        sys.exit(0)
                        
                except json.JSONDecodeError:
                    print("   JSON格式错误，请提供有效的JSON字符串")
                    sys.exit(1)
            else:
                print("   请提供JSON格式的预约数据")
                sys.exit(1)

if __name__ == "__main__":
    main()