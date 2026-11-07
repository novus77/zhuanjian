"""Poll and download completed room-2 asset batch items."""
import datetime
import json
import os
import sys
from pathlib import Path

ROOT = Path("/Users/a77/Desktop/3d解密游戏/models/lux3d")
SKILL = Path("/Users/a77/.dsh/skills/aholo-lux3d")
sys.path.insert(0, str(SKILL / "core/runtime"))
import lux3d_client  # noqa: E402

os.environ["LUX3D_CN_API_KEY"] = json.loads(
    (Path.home() / ".config/lux3d/credentials.json").read_text()
)["apiKeys"]["cn"]

asset_keys = sys.argv[1:] or []
for key in asset_keys:
    records_dir = ROOT / key / "records"
    for record_path in sorted(records_dir.glob("*.json")):
        record = json.loads(record_path.read_text())
        if record.get("state") != "submitted" or not record.get("taskId"):
            continue
        task_id = record["taskId"]
        output_base = ROOT / key / "source" / record["name"]
        outputs = lux3d_client.complete_task(
            task_id, output_path=str(output_base), expected_formats=["zip", "glb"],
            region="cn", max_attempts=90, interval=15,
        )
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        record["state"] = "downloaded"
        record["lastKnownProviderStatus"] = 3
        record["updatedAt"] = now
        record["downloadedAt"] = now
        record["downloadedArtifacts"] = [{"path": p, "bytes": size} for p, size in outputs]
        record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        state = {
            "schema": "lux3d.workflow-state/v2",
            "taskId": task_id,
            "status": "succeeded",
            "lastKnownProviderStatus": 3,
            "request": {
                "operation": "text-to-3d",
                "region": "cn",
                "version": record["parameters"].get("version", "G1"),
                "prompt": record["parameters"].get("prompt", ""),
            },
            "expectedFormats": ["zip", "glb"],
            "downloadedArtifacts": [
                {"path": str(Path(p).resolve()), "format": "zip" if p.endswith("_zip.zip") else "glb"}
                for p, _ in outputs
            ],
            "createdAt": record.get("createdAt"),
            "updatedAt": now,
            "localCompletedAt": now,
        }
        (records_dir / f"{record['attemptId']}-state.json").write_text(
            json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(json.dumps({"asset": key, "attemptId": record["attemptId"], "taskId": task_id, "outputs": outputs}, ensure_ascii=False), flush=True)
