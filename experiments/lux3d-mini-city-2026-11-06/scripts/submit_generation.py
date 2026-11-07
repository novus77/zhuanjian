#!/usr/bin/env python3
"""Submit the quoted image-to-3D task and persist its task ID immediately."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, "/Users/a77/.dsh/skills/aholo-lux3d/core/runtime")
import lux3d_client  # noqa: E402

quote = json.loads((ROOT / "logs" / "quote.json").read_text())["quote"]
items = json.loads((ROOT / "logs" / "items.json").read_text())
params = items["1"]["parameters"]["body"]
attempt_path = ROOT / "logs" / "attempt-001.json"
attempt = json.loads(attempt_path.read_text())

print(json.dumps({"submitting": True, "quoteId": quote["quoteId"]}, ensure_ascii=False))
task_id = lux3d_client.create_image_to_3d_task(
    img=params["img"],
    version=params["version"],
    faceCount=params.get("faceCount"),
    outputFormat=params.get("outputFormat"),
    enablePbr=params.get("enablePbr"),
    region="cn",
    content_id=quote["quoteId"],
)
attempt["submissionState"] = "submitted"
attempt["taskId"] = str(task_id)
attempt["submittedAt"] = "2026-11-06T14:42:30+08:00"
attempt_path.write_text(json.dumps(attempt, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"taskId": str(task_id)}, ensure_ascii=False))
