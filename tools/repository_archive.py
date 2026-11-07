"""Index versioned project content and validate hydrated or pointer-only LFS checkouts."""
import argparse
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

GENERATED = {"docs/archive-manifest.json", "docs/asset-catalog.md"}
POINTER = re.compile(rb"version https://git-lfs.github.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n?")


def snapshot(root):
    names = sorted(set(subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root
    ).decode().strip("\0").split("\0")) - GENERATED - {""})
    names = [name for name in names if (root / name).is_file()]
    attributes = subprocess.check_output(["git", "check-attr", "--stdin", "-z", "filter"],
        input=("\0".join(names) + "\0").encode(), cwd=root).decode().split("\0")
    filters = {attributes[i]: attributes[i + 2] for i in range(0, len(attributes) - 1, 3)}
    files = []
    for name in names:
        path = root / name
        size = path.stat().st_size
        with path.open("rb") as source:
            prefix = source.read(256)
            pointer = POINTER.fullmatch(prefix) if size <= 256 else None
            if pointer:
                digest, size = pointer.group(1).decode(), int(pointer.group(2))
            else:
                checksum = hashlib.sha256(prefix)
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    checksum.update(block)
                digest = checksum.hexdigest()
        files.append({"path": name, "size": size, "sha256": digest,
            "storage": "git-lfs" if filters.get(name) == "lfs" else "git"})
    return {"schema": "roomturn.archive/v1", "files": files,
        "totalLogicalBytes": sum(item["size"] for item in files),
        "uniqueLfsBytes": sum({item["sha256"]: item["size"] for item in files if item["storage"] == "git-lfs"}.values())}


def markdown(data):
    groups = defaultdict(lambda: [0, 0])
    for item in data["files"]:
        group = item["path"].split("/")[0]
        groups[group][0] += 1
        groups[group][1] += item["size"]
    lines = ["# 项目文件与资产目录", "", "由 `python3 tools/repository_archive.py update` 生成。",
        "源文件与过程资料由 Git / Git LFS 管理；构建与离线预览另见 [版本发布](releases.md)。",
        "完整逐文件路径、SHA-256 和逻辑大小见 [archive-manifest.json](archive-manifest.json)。", "",
        "| 内容 | 文件数 | 逻辑大小 MiB |", "|---|---:|---:|"]
    lines += [f"| {name} | {count} | {size / 1048576:.2f} |" for name, (count, size) in sorted(groups.items())]
    lines += ["", f"Git LFS 去重后的当前内容大小：{data['uniqueLfsBytes'] / 1048576:.2f} MiB。历史版本另计。",
        "", "## 模型文件", "", "| 模型 | MiB | 存储 |", "|---|---:|---|"]
    lines += [f"| [{item['path']}](../{quote(item['path'], safe='/')}) | {item['size'] / 1048576:.2f} | {item['storage']} |"
        for item in data["files"] if item["path"].startswith("models/") and Path(item["path"]).suffix in {".blend", ".fbx", ".glb"}]
    return "\n".join(lines) + "\n"


def update(root):
    data = snapshot(root)
    (root / "docs").mkdir(exist_ok=True)
    (root / "docs/archive-manifest.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    (root / "docs/asset-catalog.md").write_text(markdown(data))
    return data


def check(root):
    data = snapshot(root)
    path = root / "docs/archive-manifest.json"
    if not path.exists() or json.loads(path.read_text()) != data:
        raise ValueError("Archive catalog is stale; run python3 tools/repository_archive.py update")
    if (root / "docs/asset-catalog.md").read_text() != markdown(data):
        raise ValueError("Markdown catalog is stale; regenerate the archive catalog")
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["update", "check"])
    options = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    data = update(root) if options.action == "update" else check(root)
    print(json.dumps({"files": len(data["files"]), "logicalMiB": round(data["totalLogicalBytes"] / 1048576, 2),
        "uniqueLfsMiB": round(data["uniqueLfsBytes"] / 1048576, 2)}))
