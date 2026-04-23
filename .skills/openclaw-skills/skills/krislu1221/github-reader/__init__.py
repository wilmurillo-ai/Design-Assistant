"""
GitHub Reader Skill - 自动解读 GitHub 项目

用法：
  /github-read owner/repo
  或发送 GitHub URL 自动触发
"""

from .github_reader_v3_secure import run, SecureGitHubReaderV3

__all__ = ['run', 'SecureGitHubReaderV3']
