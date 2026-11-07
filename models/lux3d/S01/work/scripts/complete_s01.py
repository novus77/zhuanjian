"""Poll the submitted S01 task, download its artifacts, and update the local record."""
import datetime
import json
import os
import sys
from pathlib import Path

SKILL = Path("/Users/a77/.dsh/skills/aholo-lux3d")
TASK = Path("/Users/a77/.codex/worktrees/unity-graybox/3d解密游戏/models/lux3d/S01")
sys.path.insert(0, str(SKILL / "core/runtime"))
import lux3d_client  # noqa: E402

record_path = TASK / "records/attempt.json"
record = json.loads(record_path.read_text())
task_id = record["taskId"]
os.environ["LUX3D_CN_API_KEY"] = json.loads(
    (Path.home() / ".config/lux3d/credentials.json").read_text()
)["apiKeys"]["cn"]

outputs = lux3d_client.complete_task(
    task_id,
    output_path=str(TASK / "source/S01Gramophone"),
    expected_formats=["zip", "glb"],
    region="cn",
    max_attempts=80,
    interval=15,
)
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
(TASK / "records/task-status.json").write_text(
    json.dumps({"taskId": task_id, "status": 3, "outputs": outputs, "checkedAt": now}, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
record["state"] = "downloaded"
record["downloadedAt"] = now
record["downloadedArtifacts"] = [{"path": p, "bytes": size} for p, size in outputs]
record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"status": "downloaded", "taskId": task_id, "artifacts": outputs}, ensure_ascii=False))
