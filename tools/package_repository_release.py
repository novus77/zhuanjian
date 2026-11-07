"""Package actual local deliveries and builds for a GitHub milestone release."""
import argparse
import hashlib
import json
import os
import re
import zipfile
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--development-workspace", type=Path)
options = parser.parse_args()
root = Path(__file__).resolve().parents[1]
workspace = options.development_workspace or root
out = root / ".release/v0.1.0-study-art"
out.mkdir(parents=True, exist_ok=True)
builds = workspace / "unity/Roomturn/Builds"
if not (builds / "WebArt/index.html").is_file():
    raise SystemExit("A real WebArt build is required before packaging")


def files(folder):
    return sorted(p for p in folder.rglob("*") if p.is_file() and p.name != ".DS_Store")


def archive(name, members, extra=None):
    destination = out / name
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as package:
        for source, target in sorted(members, key=lambda item: item[1]):
            package.write(source, target)
        for target, content in (extra or {}).items():
            package.writestr(target, content)
    with zipfile.ZipFile(destination) as package:
        bad = package.testzip()
        if bad:
            raise ValueError("Corrupt packaged member: " + bad)
        count = len(package.infolist())
    if destination.stat().st_size >= 2 * 1024 ** 3:
        raise ValueError("Release asset exceeds GitHub size limit; split this archive")
    digest = hashlib.sha256()
    with destination.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    result = {"name": name, "size": destination.stat().st_size, "sha256": digest.hexdigest(), "members": count}
    print(json.dumps(result), flush=True)
    return result


web = [(p, "WebArt/" + p.relative_to(builds / "WebArt").as_posix()) for p in files(builds / "WebArt")]
web.append((root / "tools/serve_unity_web.py", "serve_unity_web.py"))
results = [archive("roomturn-web-art.zip", web, {"README.txt":
    "转间 Roomturn · 第一关书房美术试玩\n\n解压全部文件后运行：\n"
    "python3 serve_unity_web.py WebArt --port 18769\n\n浏览器打开 http://127.0.0.1:18769/\n"
    "不能直接双击 index.html；服务需发送正确 Gzip / WASM 响应头。\n"
    "点击画面开始；WASD 移动，左右方向键转身，鼠标环视，E 交互，R 重开，Esc 释放鼠标。\n"
    "此包为真实 Unity WebGL 构建。第二、三关尚未制作完成。\n"})]

folders = [*sorted((root / "models/lux3d/_deliveries").glob("*")),
    *sorted((root / "models/blender/study-room-v1").glob("delivery*")),
    *sorted((root / "experiments").glob("*/delivery*"))]
members = [(p, p.relative_to(root).as_posix()) for folder in folders if folder.is_dir() for p in files(folder)]
results.append(archive("roomturn-delivery-history.zip", members, {"README.txt":
    "历史离线交付包，保留各轮 preview.html、原始模型及清单。\n"
    "最新书房入口：models/blender/study-room-v1/delivery-v2/preview.html\n"
    "城市沙盘入口：experiments/lux3d-mini-city-2026-11-06/delivery-v2/preview.html\n"
    "这些是模型查看器；实际可玩游戏请下载 roomturn-web-art.zip。\n"}))

previous = [(p, p.relative_to(builds).as_posix()) for folder in [builds / "Web", builds / "macOS"] if folder.exists() for p in files(folder)]
results.append(archive("roomturn-previous-builds.zip", previous,
    {"README.txt": "此前的 Unity Web 与 macOS 开发灰盒构建，保留制作过程；最新试玩请使用 WebArt 包。\n"}))

patterns = re.compile(r"gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{24,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")
logs = sorted([*root.glob("docs/production/validation/**/*.log"), *root.glob("models/blender/study-room-v1/records/*.log")])
for path in logs:
    if patterns.search(path.read_text(errors="replace")):
        raise ValueError("Credential-like value in log; do not publish: " + str(path.relative_to(root)))
results.append(archive("roomturn-verification-logs.zip", [(p, p.relative_to(root).as_posix()) for p in logs],
    {"README.txt": "实际模型、Unity、浏览器检查日志。包含失败和修复过程；最终验收结论见仓库 docs/production/validation。\n"}))
(out / "SHA256SUMS.txt").write_text("".join(item["sha256"] + "  " + item["name"] + "\n" for item in results))
(out / "release-manifest.json").write_text(json.dumps({"tag": "v0.1.0-study-art", "assets": results}, indent=2) + "\n")
