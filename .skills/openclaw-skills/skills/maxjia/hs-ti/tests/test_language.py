import sys
import os

script_dir = os.path.join(os.path.dirname(__file__), '..', 'scripts')
sys.path.insert(0, script_dir)

from hs_ti_plugin import YunzhanThreatIntel

def test_language_switching():
    print("=== Testing Language Switching / 测试语言切换 ===\n")
    
    intel = YunzhanThreatIntel()
    
    print(f"Initial language: {intel.language}")
    print(f"Initial language text: {intel.get_text('current_language')}: {intel.get_text('default_language')}\n")
    
    print("--- Testing English / 测试英文 ---")
    intel.set_language('en')
    print(f"Language: {intel.language}")
    print(f"Text: {intel.get_text('language_switched_to_en')}")
    print(f"Query Results: {intel.get_text('query_results')}")
    print(f"Malicious: {intel.get_text('result_malicious')}\n")
    
    print("--- Testing Chinese / 测试中文 ---")
    intel.set_language('cn')
    print(f"Language: {intel.language}")
    print(f"Text: {intel.get_text('language_switched_to_cn')}")
    print(f"Query Results: {intel.get_text('query_results')}")
    print(f"Malicious: {intel.get_text('result_malicious')}\n")
    
    print("--- Testing Invalid Language / 测试无效语言 ---")
    result = intel.set_language('fr')
    print(f"Set to 'fr': {result}")
    print(f"Current language: {intel.language}\n")
    
    print("--- Testing Persistence / 测试持久化 ---")
    intel.set_language('en')
    print(f"Set to English, saved to file")
    
    new_intel = YunzhanThreatIntel()
    print(f"New instance language: {new_intel.language}")
    print(f"New instance text: {new_intel.get_text('language_switched_to_en')}\n")
    
    print("=== Test Completed / 测试完成 ===")

if __name__ == "__main__":
    test_language_switching()