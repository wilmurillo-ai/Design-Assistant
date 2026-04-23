#!/usr/bin/env python3
import os
import platform
import urllib.request
import tarfile
import zipfile
import stat
import sys
import argparse

REPO = "jeeaay/coding-plan-usage"


def get_system_info():
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "darwin":
        goos = "darwin"
    elif system == "linux":
        goos = "linux"
    elif system == "windows":
        goos = "windows"
    else:
        raise OSError(f"unsupported os: {system}")

    if machine in ("x86_64", "amd64"):
        goarch = "amd64"
    elif machine in ("arm64", "aarch64"):
        goarch = "arm64"
    else:
        raise OSError(f"unsupported arch: {machine}")

    return goos, goarch


def extract_archive(archive_path, target_dir, goos):
    if goos == "windows":
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(target_dir)
    else:
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(target_dir)


def main():
    parser = argparse.ArgumentParser(description="Install coding-plan-usage")
    parser.add_argument("target_dir", nargs="?", default=os.path.dirname(os.path.abspath(__file__)))
    args = parser.parse_args()

    target_dir = args.target_dir
    goos, goarch = get_system_info()

    ext = "zip" if goos == "windows" else "tar.gz"
    asset = f"coding-plan-usage-{goos}-{goarch}.{ext}"
    url = f"https://github.com/{REPO}/releases/latest/download/{asset}"

    os.makedirs(target_dir, exist_ok=True)
    archive_path = os.path.join(target_dir, asset)
    bundle_dir = os.path.join(target_dir, f"coding-plan-usage-{goos}-{goarch}-bundle")

    print(f"Downloading {url}...", file=sys.stderr)
    urllib.request.urlretrieve(url, archive_path)

    print(f"Extracting to {target_dir}...", file=sys.stderr)
    extract_archive(archive_path, target_dir, goos)

    binary_name = "coding-plan-usage.exe" if goos == "windows" else "coding-plan-usage"
    binary_path = os.path.join(bundle_dir, binary_name)
    st = os.stat(binary_path)
    if goos != "windows":
        os.chmod(binary_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    print(f"installed_bundle={bundle_dir}")
    print(f"binary={binary_path}")


if __name__ == "__main__":
    main()
