#!/usr/bin/env python3
"""
GitHub Image CDN Uploader
将本地图片上传到 GitHub 仓库，通过 jsDelivr CDN 访问
"""

import base64
import json
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("缺少依赖，请先运行: pip install requests")
    sys.exit(1)


class GitHubImageUploader:
    """GitHub 图片上传封装类"""

    def __init__(self, config_path: str = "config.json"):
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(
                f"配置文件不存在: {config_path}\n"
                f"请复制 config.example.json 为 config.json 并填入 token"
            )

        with open(config_file, "r") as f:
            config = json.load(f)

        self.token = config["github_token"]
        self.repo = config.get("repo", "smallyangy/temporary_images")
        self.branch = config.get("branch", "master")
        self.images_path = config.get("images_path", "images").strip("/")
        self.cdn_base = config.get(
            "cdn_base",
            f"https://cdn.jsdelivr.net/gh/{self.repo}@{self.branch}"
        )

        self._api_base = f"https://api.github.com/repos/{self.repo}/contents"
        self._headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def upload(self, local_path: str, remote_name: str = None) -> str:
        """
        上传单张图片

        Args:
            local_path: 本地图片路径
            remote_name: 远程文件名，默认使用原文件名

        Returns:
            str: jsDelivr CDN 访问链接
        """
        file = Path(local_path)
        if not file.exists():
            raise FileNotFoundError(f"文件不存在: {local_path}")

        name = remote_name or file.name
        remote_path = f"{self.images_path}/{name}"

        with open(file, "rb") as f:
            content_b64 = base64.b64encode(f.read()).decode("utf-8")

        # 如果文件已存在，需要带上 sha 才能覆盖
        sha = self._get_sha(remote_path)

        payload = {
            "message": f"upload {name}",
            "content": content_b64,
            "branch": self.branch,
        }
        if sha:
            payload["sha"] = sha

        url = f"{self._api_base}/{remote_path}"
        resp = requests.put(url, headers=self._headers, json=payload)

        if resp.status_code not in (200, 201):
            raise RuntimeError(
                f"上传失败 [{resp.status_code}]: {resp.json().get('message', resp.text)}"
            )

        cdn_url = f"{self.cdn_base}/{remote_path}"
        return cdn_url

    def upload_batch(self, local_paths: list[str]) -> dict[str, str]:
        """
        批量上传图片

        Args:
            local_paths: 本地图片路径列表

        Returns:
            dict: {本地路径: CDN链接} 成功的结果
        """
        results = {}
        for path in local_paths:
            try:
                cdn_url = self.upload(path)
                results[path] = cdn_url
                print(f"  [OK] {Path(path).name}")
                print(f"       {cdn_url}")
            except Exception as e:
                print(f"  [FAIL] {Path(path).name}: {e}")
        return results

    def _get_sha(self, remote_path: str) -> str | None:
        """获取已存在文件的 sha（更新文件时必需）"""
        url = f"{self._api_base}/{remote_path}"
        resp = requests.get(url, headers=self._headers)
        if resp.status_code == 200:
            return resp.json().get("sha")
        return None


# ── 命令行入口 ──────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python upload.py <图片路径>              # 上传单张")
        print("  python upload.py <图片1> <图片2> ...     # 批量上传")
        sys.exit(1)

    uploader = GitHubImageUploader("config.json")
    files = sys.argv[1:]

    if len(files) == 1:
        cdn_url = uploader.upload(files[0])
        print(f"上传成功: {cdn_url}")
    else:
        print(f"批量上传 {len(files)} 张图片...")
        uploader.upload_batch(files)


if __name__ == "__main__":
    main()
