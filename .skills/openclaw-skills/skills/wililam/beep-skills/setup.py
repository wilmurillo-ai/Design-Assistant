"""beep-skills: Make your OpenClaw Agent talk!"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README.md
this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8") if (this_dir / "README.md").exists() else ""

setup(
    name="beep-skills",
    version="2.1.0-dev",
    author="miaoweilin (wililam)",
    author_email="uinecn@126.com",
    description="Real-time voice announcements for OpenClaw actions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wililam/beep-skills",
    project_urls={
        "Bug Reports": "https://github.com/wililam/beep-skills/issues",
        "Source": "https://github.com/wililam/beep-skills",
        "ClawHub": "https://clawhub.ai/skill/beep-skills",
        "Skill Name": "beep-skills",
    },
    packages=find_packages(include=["audio_announcement", "audio_announcement.*"]),
    include_package_data=True,
    package_data={
        "audio_announcement": ["scripts/*.py", "scripts/*.sh"],
    },
    install_requires=[
        "edge-tts>=7.2.8",
        "pygame>=2.6.1; platform_system=='Windows'",
    ],
    extras_require={
        "dev": ["pytest", "black"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "beep=audio_announcement.cli:main",           # 新命令（推荐）
            "audio-announce=audio_announcement.cli:main", # 向后兼容
        ],
    },
    keywords=["openclaw", "tts", "text-to-speech", "announcement", "voice", "audio", "beep", "小喇叭", "one-click-verify"],
)
