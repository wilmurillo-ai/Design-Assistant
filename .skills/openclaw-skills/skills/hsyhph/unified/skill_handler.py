#!/usr/bin/env python3
"""
GitHub Knowledge Base Skill - 激活脚本
当用户提到 github、repo、仓库 时自动触发
"""

import re
from github_kb import GitHubKnowledgeBase

class GitHubKBSkill:
    def __init__(self):
        self.gkb = GitHubKnowledgeBase()
    
    def should_activate(self, message: str) -> bool:
        """判断是否应该激活技能"""
        keywords = ['github', 'repo', 'repository', '仓库', 'git']
        return any(keyword in message.lower() for keyword in keywords)
    
    def handle_message(self, message: str) -> str:
        """处理用户消息"""
        import subprocess
        import json
        
        message_lower = message.lower()
        
        # 检查是否要搜索免费token相关issue
        if any(keyword in message_lower for keyword in ['免费token', 'token获取', 'token issue']):
            print("🎯 检测到免费token相关搜索")
            try:
                # 尝试使用curl搜索GitHub issue
                
                # 搜索免费token相关的issue
                query = "free token获取"
                curl_result = subprocess.run(
                    ["curl", "-s", "-H", "User-Agent: GitHub-KB-Skill", 
                     f"https://api.github.com/search/issues?q=free+token+获取+language:中文&sort=updated&order=desc&per_page=3"],
                    capture_output=True,
                    text=True,
                    timeout=20
                )
                
                if curl_result.returncode == 0:
                    data = json.loads(curl_result.stdout)
                    total_count = data.get('total_count', 0)
                    
                    # 计算token使用量
                    tokens_used = len(query) * 10
                    tokens_used += total_count * 5
                    
                    if total_count == 0:
                        return "🔍 未找到中文的免费token相关issue"
                    
                    # 准备响应
                    response = f"🎯 搜索到 {total_count} 个免费token相关的GitHub issue\n\n"
                    
                    for i, issue in enumerate(data.get('items', [])):
                        issue_num = issue['number']
                        title = issue['title']
                        state = issue['state']
                        html_url = issue['html_url']
                        repo_name = issue['repository_url'].split('/')[-1]
                        
                        response += f"🚀 #{issue_num}: {title}\n"
                        response += f"🔴 状态: {state}\n"
                        response += f"🏷️ 仓库: {repo_name}\n"
                        response += f"🔗 URL: {html_url}\n\n"
                        
                        # 累积token使用
                        tokens_used += len(title) * 10
                        tokens_used += len(repo_name) * 5
                        
                        # 检查token使用是否超过50万限制
                        if tokens_used > 500000:
                            response += "⚠️ Token使用已超过50万限制，请说'继续'以查看更多结果"
                            break
                    
                    return response
                    
                else:
                    return "❌ 搜索失败，请确保网络连接正常"
                    
            except Exception as e:
                print(f"搜索失败: {e}")
                return "❌ 搜索失败，请确保网络连接正常"
                
        # 检查是否要下载仓库
        download_match = re.search(r'下载\s+(.+?)(?:\s+仓库)?$', message, re.IGNORECASE)
        if download_match:
            repo_name = download_match.group(1).strip()
            if '/' in repo_name:
                # 完整的仓库名称
                full_name = repo_name
                repo_url = f"https://github.com/{full_name}.git"
                success = self.gkb.clone_repo(repo_url, full_name.split('/')[-1])
                if success:
                    return f"成功下载仓库: {full_name}"
                else:
                    return f"下载仓库失败: {full_name}"
            else:
                # 简化的仓库名称，假设是组织/用户名
                return f"请提供完整的仓库名称，例如: '下载 openai/gpt-3'"
        
        # 检查是否要搜索仓库
        search_match = re.search(r'搜索\s+(.+?)(?:\s+仓库)?$', message, re.IGNORECASE)
        if search_match:
            query = search_match.group(1).strip()
            local_results = self.gkb.search_local_repo(query)
            
            if local_results:
                response = f"本地找到相关仓库:\n" + "\n".join(local_results[:3])
                # 同时搜索GitHub
                github_results = self.gkb.search_github(query)
                if github_results:
                    response += f"\n\nGitHub相关仓库:\n" + "\n".join(github_results[:2])
            else:
                github_results = self.gkb.search_github(query)
                if github_results:
                    response = f"GitHub相关仓库:\n" + "\n".join(github_results[:5])
                else:
                    response = f"未找到与 '{query}' 相关的仓库"
            
            return response
        
        # 检查是否要搜索仓库信息
        info_match = re.search(r'(.+?)\s*(?:的|的)?信息$', message, re.IGNORECASE)
        if info_match:
            repo_name = info_match.group(1).strip()
            if repo_name in ['github', 'repo', 'repository', '仓库']:
                # 显示所有仓库信息
                repos = self.gkb.get_repos_summary()
                if repos:
                    response = "本地仓库列表:\n"
                    for name, summary in repos.items():
                        response += f"- {name}: {summary}\n"
                else:
                    response = "暂无本地仓库"
                return response
            else:
                # 特定仓库信息
                info = self.gkb.get_repo_info(repo_name)
                if info.get('exists'):
                    response = f"仓库信息: {repo_name}\n"
                    response += f"路径: {info['path']}\n"
                    response += f"大小: {info['size_mb']} MB\n"
                    response += f"分支数: {info['branches']}\n"
                    response += f"摘要: {info['summary']}"
                else:
                    response = f"本地未找到仓库: {repo_name}"
                    # 搜索GitHub
                    github_results = self.gkb.search_github(repo_name)
                    if github_results:
                        response += f"\n\nGitHub相关仓库:\n" + "\n".join(github_results[:3])
                return response
        
        # 检查是否要查看仓库列表
        if any(word in message_lower for word in ['列表', 'list', '有哪些', '有什么']):
            repos = self.gkb.get_repos_summary()
            if repos:
                response = "本地仓库列表:\n"
                for name, summary in repos.items():
                    response += f"- {name}: {summary}\n"
            else:
                response = "暂无本地仓库"
            return response
        
        # 默认处理：搜索本地仓库
        results = self.gkb.search_local_repo(message)
        if results:
            return f"找到相关仓库:\n" + "\n".join(results[:3])
        else:
            return "未找到相关仓库，可以尝试搜索GitHub仓库"

# 使用示例
if __name__ == "__main__":
    skill = GitHubKBSkill()
    
    # 测试不同场景
    test_messages = [
        "下载 openai/gpt-3",
        "搜索 python machine learning",
        "react 仓库的信息",
        "有哪些仓库",
        "github 相关的项目"
    ]
    
    for msg in test_messages:
        print(f"测试消息: {msg}")
        response = skill.handle_message(msg)
        print(f"响应: {response}")
        print("-" * 50)