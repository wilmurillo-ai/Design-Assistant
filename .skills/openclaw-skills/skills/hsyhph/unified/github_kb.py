#!/usr/bin/env python3
"""
GitHub Knowledge Base Skill
管理本地GitHub仓库知识库，提供GitHub仓库的本地管理和分析功能
"""

import os
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional

class GitHubKnowledgeBase:
    def __init__(self):
        self.github_dir = Path("/home/node/clawd/skills/unified/github-kb")
        self.claude_md = self.github_dir / "CLAUDE.md"
        self.ensure_directory_exists()
    
    def ensure_directory_exists(self):
        """确保GitHub目录存在"""
        self.github_dir.mkdir(parents=True, exist_ok=True)
        if not self.claude_md.exists():
            self.claude_md.write_text("""# GitHub Knowledge Base

## 仓库摘要记录

*这个文件用于记录本地GitHub仓库的一句话摘要*

*创建时间: 2026-02-17 12:02 UTC*
*目录: /home/node/clawd/github-kb*

---
*暂无仓库记录*
---""")
    
    def get_repos_summary(self) -> Dict[str, str]:
        """获取所有仓库的摘要"""
        repos = {}
        if self.claude_md.exists():
            content = self.claude_md.read_text()
            # 解析CLAUDE.md中的仓库信息
            lines = content.split('\n')
            current_repo = None
            for line in lines:
                if line.startswith('## ') and not line.startswith('## 仓库摘要记录'):
                    current_repo = line[3:].strip()
                    repos[current_repo] = ""
                elif current_repo and line.startswith('- ') and not line.startswith('- *'):
                    repos[current_repo] = line[2:].strip()
        return repos
    
    def clone_repo(self, repo_url: str, repo_name: str) -> bool:
        """克隆仓库到本地"""
        try:
            repo_path = self.github_dir / repo_name
            if repo_path.exists():
                print(f"仓库 {repo_name} 已存在，跳过克隆")
                return True
            
            print(f"正在克隆仓库: {repo_url}")
            result = subprocess.run(
                ["git", "clone", repo_url, str(repo_path)],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                # 分析仓库并更新摘要
                self.analyze_repo(repo_name)
                return True
            else:
                print(f"克隆失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"克隆过程中出现错误: {e}")
            return False
    
    def analyze_repo(self, repo_name: str) -> Optional[str]:
        """分析仓库并生成摘要"""
        try:
            repo_path = self.github_dir / repo_name
            if not repo_path.exists():
                return None
            
            # 获取README内容
            readme_content = ""
            readme_files = ["README.md", "README.rst", "README.txt", "readme.md"]
            for readme_file in readme_files:
                readme_path = repo_path / readme_file
                if readme_path.exists():
                    readme_content = readme_path.read_text(encoding='utf-8', errors='ignore')
                    break
            
            # 生成摘要
            if readme_content:
                # 提取第一段作为摘要
                first_paragraph = re.split(r'\n\s*\n', readme_content.strip())[0]
                summary = first_paragraph[:100] + "..." if len(first_paragraph) > 100 else first_paragraph
            else:
                summary = "无README文件"
            
            # 更新CLAUDE.md
            self.update_claude_md(repo_name, summary)
            return summary
        except Exception as e:
            print(f"分析仓库时出现错误: {e}")
            return None
    
    def update_claude_md(self, repo_name: str, summary: str):
        """更新CLAUDE.md文件"""
        try:
            content = self.claude_md.read_text()
            lines = content.split('\n')
            
            # 查找仓库位置
            repo_index = -1
            for i, line in enumerate(lines):
                if line.startswith(f"## {repo_name}"):
                    repo_index = i
                    break
            
            if repo_index != -1:
                # 更新现有仓库
                lines[repo_index + 1] = f"- {summary}"
            else:
                # 添加新仓库
                insert_index = -1
                for i, line in enumerate(lines):
                    if line.startswith("---") and i > 0:
                        insert_index = i
                        break
                
                if insert_index != -1:
                    lines.insert(insert_index, f"## {repo_name}")
                    lines.insert(insert_index + 1, f"- {summary}")
                    lines.insert(insert_index + 2, "")
            
            self.claude_md.write_text('\n'.join(lines))
            print(f"已更新仓库 {repo_name} 的摘要")
        except Exception as e:
            print(f"更新CLAUDE.md时出现错误: {e}")
    
    def search_local_repo(self, query: str) -> List[str]:
        """在本地搜索仓库"""
        repos = self.get_repos_summary()
        results = []
        query_lower = query.lower()
        
        for repo_name, summary in repos.items():
            if query_lower in repo_name.lower() or query_lower in summary.lower():
                results.append(f"{repo_name}: {summary}")
        
        return results
    
    def search_github(self, query: str) -> List[str]:
        """在GitHub上搜索仓库（使用GH命令，如果没有则使用curl）"""
        try:
            # 尝试使用GitHub CLI
            result = subprocess.run(
                ["gh", "repo", "search", query, "--limit", "5", "--json", "nameWithOwner,description,stargazersCount,updatedAt"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                results = []
                for repo in data:
                    name = repo['nameWithOwner']
                    description = repo.get('description', 'No description')
                    stars = repo['stargazersCount']
                    results.append(f"{name}: {description} (⭐{stars})")
                return results
            else:
                print(f"GH命令失败，尝试使用curl")
                raise FileNotFoundError("GH command not found")
                
        except (FileNotFoundError, Exception):
            # 使用curl调用GitHub API
            try:
                encoded_query = urllib.parse.quote(query)
                search_url = f"https://api.github.com/search/repositories?q={encoded_query}&sort=stars&order=desc&per_page=5"
                
                # 使用curl命令
                curl_result = subprocess.run(
                    ["curl", "-s", "-H", "User-Agent: GitHub-KB-Skill", search_url],
                    capture_output=True,
                    text=True,
                    timeout=20
                )
                
                if curl_result.returncode == 0:
                    data = json.loads(curl_result.stdout)
                    results = []
                    for repo in data.get('items', []):
                        name = repo['full_name']
                        description = repo.get('description', 'No description')
                        stars = repo['stargazers_count']
                        results.append(f"{name}: {description} (⭐{stars})")
                    return results
                else:
                    print(f"curl请求失败: {curl_result.stderr}")
                    return [f"搜索 '{query}' 的结果需要网络连接", "请确保网络连接正常"]
                    
            except Exception as e:
                print(f"GitHub搜索过程中出现错误: {e}")
                return [f"搜索 '{query}' 的结果需要网络连接", "请确保网络连接正常"]
    
    def get_repo_info(self, repo_name: str) -> Dict:
        """获取仓库详细信息"""
        try:
            repo_path = self.github_dir / repo_name
            info = {
                "name": repo_name,
                "path": str(repo_path),
                "exists": repo_path.exists(),
                "summary": ""
            }
            
            if repo_path.exists():
                # 获取仓库基本信息
                info["summary"] = self.get_repos_summary().get(repo_name, "")
                
                # 获取仓库大小
                try:
                    size = sum(f.stat().st_size for f in repo_path.rglob('*') if f.is_file())
                    info["size_mb"] = round(size / (1024 * 1024), 2)
                except:
                    info["size_mb"] = 0
                
                # 获取分支数
                try:
                    result = subprocess.run(
                        ["git", "branch", "-a"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        branches = len([b.strip() for b in result.stdout.split('\n') if b.strip()])
                        info["branches"] = branches
                except:
                    info["branches"] = 0
            
            return info
        except Exception as e:
            print(f"获取仓库信息时出现错误: {e}")
            return {"name": repo_name, "error": str(e)}
    
    def search_github_issues(self, query: str, repo: str = "") -> List[str]:
        """在GitHub上搜索issues（优先使用GH命令，失败则使用curl）"""
        try:
            # 尝试使用GitHub CLI
            if repo:
                gh_command = ["gh", "issue", "search", query, "--repo", repo, "--limit", "5", "--json", "number,title,state,updatedAt,htmlUrl"]
            else:
                gh_command = ["gh", "issue", "search", query, "--limit", "5", "--json", "number,title,state,updatedAt,htmlUrl"]
            
            result = subprocess.run(
                gh_command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                results = []
                for issue in data:
                    issue_num = issue['number']
                    title = issue['title']
                    state = issue['state']
                    html_url = issue['htmlUrl']
                    results.append(f"#{issue_num}: {title} ({state}) - {html_url}")
                return results
            else:
                print(f"GH命令失败，尝试使用curl")
                raise FileNotFoundError("GH command not found")
                
        except (FileNotFoundError, Exception):
            # 使用curl调用GitHub API
            try:
                encoded_query = urllib.parse.quote(query)
                
                if repo:
                    # 搜索特定仓库的issues
                    encoded_repo = urllib.parse.quote(repo)
                    search_url = f"https://api.github.com/search/issues?q={encoded_query}+repo:{encoded_repo}&sort=updated&order=desc&per_page=5"
                else:
                    # 搜索所有仓库的issues
                    search_url = f"https://api.github.com/search/issues?q={encoded_query}&sort=updated&order=desc&per_page=5"
                
                # 使用curl命令
                curl_result = subprocess.run(
                    ["curl", "-s", "-H", "User-Agent: GitHub-KB-Skill", search_url],
                    capture_output=True,
                    text=True,
                    timeout=20
                )
                
                if curl_result.returncode == 0:
                    data = json.loads(curl_result.stdout)
                    results = []
                    for issue in data.get('items', []):
                        issue_num = issue['number']
                        title = issue['title']
                        state = issue['state']
                        html_url = issue['html_url']
                        repo_name = issue['repository_url'].split('/')[-1]
                        results.append(f"#{issue_num}: {title} ({state}) - {repo_name} - {html_url}")
                    return results
                else:
                    print(f"curl请求失败: {curl_result.stderr}")
                    return [f"搜索 '{query}' 的结果需要网络连接", "请确保网络连接正常"]
                    
            except Exception as e:
                print(f"GitHub搜索过程中出现错误: {e}")
                return [f"搜索 '{query}' 的结果需要网络连接", "请确保网络连接正常"]

# 使用示例
if __name__ == "__main__":
    gkb = GitHubKnowledgeBase()
    
    # 测试功能
    print("GitHub Knowledge Base 已初始化")
    print(f"GitHub目录: {gkb.github_dir}")
    print(f"CLAUDE.md: {gkb.claude_md}")
    
    # 显示现有仓库
    repos = gkb.get_repos_summary()
    if repos:
        print("\n现有仓库:")
        for name, summary in repos.items():
            print(f"- {name}: {summary}")
    else:
        print("\n暂无仓库记录")