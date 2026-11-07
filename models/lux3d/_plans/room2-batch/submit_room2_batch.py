"""Submit selected room-2 Lux3D batch items once each, with local attempt guards."""
import datetime
import json
import os
import sys
from pathlib import Path

ROOT = Path("/Users/a77/Desktop/3d解密游戏")
PLAN = ROOT / "models/lux3d/_plans/room2-batch"
SKILL = Path("/Users/a77/.dsh/skills/aholo-lux3d")
sys.path.insert(0, str(SKILL / "core/runtime"))
import lux3d_client  # noqa: E402

MAPPING = [
    ("B01", "B01SewingMachineHead", "B01", "b01-a1", "1"),
    ("B02", "B02CassetteRadio", "B02", "b02-a1", "2"),
    ("B03L", "B03DressingTableLeg", "B03", "b03-leg-a1", "3"),
    ("B03M", "B03OvalMirrorFrame", "B03", "b03-frame-a1", "4"),
    ("B04", "B04UpholsteredStool", "B04", "b04-a1", "5"),
    ("B05C", "B05WardrobeCrest", "B05", "b05-crest-a1", "6"),
    ("B05H", "B05LeafHandle", "B05", "b05-handle-a1", "7"),
    ("B06", "B06BedOrnament", "B06", "b06-a1", "8"),
    ("B10", "B10CeramicCup", "B10", "b10-a1", "9"),
]
SELECT = set(sys.argv[1:]) if len(sys.argv) > 1 else {m[0] for m in MAPPING}
quote_doc = json.loads((PLAN / "quote-result.json").read_text())
quote = quote_doc["quote"]
account = quote_doc["account"]
items = json.loads((PLAN / "quote-items.json").read_text())
now = datetime.datetime.now(datetime.timezone.utc)
if datetime.datetime.fromisoformat(quote["expiresAt"]) <= now:
    raise SystemExit("quote_expired")
if quote["estimatedCreditsTotal"] != 180:
    raise SystemExit("quote_changed")
if account["availableCredits"] < 180:
    raise SystemExit("insufficient_balance")
os.environ["LUX3D_CN_API_KEY"] = json.loads(
    (Path.home() / ".config/lux3d/credentials.json").read_text()
)["apiKeys"]["cn"]

for key, name, folder, attempt_id, seq in MAPPING:
    if key not in SELECT:
        continue
    task_dir = ROOT / "models/lux3d" / folder
    records = task_dir / "records"
    records.mkdir(parents=True, exist_ok=True)
    record_path = records / f"{attempt_id}.json"
    if record_path.exists():
        record = json.loads(record_path.read_text())
        if record.get("taskId") or record.get("state") in {"submitted", "submission_unknown"}:
            print(json.dumps({"key": key, "status": "existing", "state": record.get("state"), "taskId": record.get("taskId")}, ensure_ascii=False))
            continue
    body = items[seq]["parameters"]["body"]
    record = {
        "asset": key,
        "name": name,
        "attemptId": attempt_id,
        "region": "cn",
        "operation": "text-to-3d",
        "parameters": body,
        "expectedFormats": ["zip", "glb"],
        "quotedCredits": 20,
        "quoteId": quote["quoteId"],
        "reviewId": quote.get("review", {}).get("reviewId"),
        "approval": "Automatic execution within the user-authorized cumulative 500-credit room-2 budget",
        "state": "reserved",
        "createdAt": now.isoformat(),
    }
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    try:
        task_id = lux3d_client.create_text_to_3d_task(
            body["prompt"], version=body["version"], style=body.get("style"),
            faceCount=body.get("faceCount"), outputFormat=body.get("outputFormat"),
            aiPredictSize=body.get("aiPredictSize"), customSize=body.get("customSize"),
            region="cn", content_id=quote["quoteId"],
        )
    except Exception as exc:
        record["state"] = "submission_unknown"
        record["error"] = type(exc).__name__
        record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"key": key, "status": "submission_unknown", "error": type(exc).__name__}, ensure_ascii=False))
        raise
    record["state"] = "submitted"
    record["taskId"] = str(task_id)
    record["submittedAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"key": key, "status": "submitted", "taskId": str(task_id)}, ensure_ascii=False))
