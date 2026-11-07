#!/usr/bin/env python3
"""Wait for the Lux3D task and download the GLB artifact."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, "/Users/a77/.dsh/skills/aholo-lux3d/core/runtime")
import lux3d_client  # noqa: E402

task_id = "4745712"
attempt_path = ROOT / "logs" / "attempt-001.json"
attempt = json.loads(attempt_path.read_text())

result = lux3d_client.complete_task(
    task_id,
    output_path=str(ROOT / "output" / "mini-city.glb"),
    expected_formats=["glb"],
    region="cn",
    max_attempts=80,
    interval=15,
)
payload = {
    "taskId": task_id,
    "downloadedAt": "2026-11-06T14:43:00+08:00",
    "downloads": [{"path": str(path), "bytes": size} for path, size in result],
}
(ROOT / "logs" / "download-001.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
)
attempt["submissionState"] = "downloaded"
attempt["downloadedAt"] = payload["downloadedAt"]
attempt["downloads"] = payload["downloads"]
attempt_path.write_text(json.dumps(attempt, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(payload, ensure_ascii=False, indent=2))
