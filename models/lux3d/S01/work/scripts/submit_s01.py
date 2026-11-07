"""Submit the S01 gramophone generation once, with a local attempt guard."""
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
budget_path = TASK / "records/budget-ledger.json"
if record_path.exists():
    record = json.loads(record_path.read_text())
    if record.get("taskId") or record.get("state") in {"submitted", "submission_unknown"}:
        print(json.dumps({"status": "existing_attempt", "state": record.get("state"), "taskId": record.get("taskId")}))
        raise SystemExit(2)

quote_doc = json.loads((TASK / "quote-result.json").read_text())
quote = quote_doc["quote"]
account = quote_doc["account"]
items = json.loads((TASK / "quote-items.json").read_text())
body = items["1"]["parameters"]["body"]
now = datetime.datetime.now(datetime.timezone.utc)
expires = datetime.datetime.fromisoformat(quote["expiresAt"])
if expires <= now:
    raise SystemExit("quote_expired")
if quote["estimatedCreditsTotal"] != 20:
    raise SystemExit("quote_changed")
if account["availableCredits"] < 20:
    raise SystemExit("insufficient_balance")

record = {
    "attemptId": "s01-gramophone-a1",
    "itemId": "s01-gramophone",
    "region": "cn",
    "operation": "text-to-3d",
    "parameters": body,
    "expectedFormats": ["zip", "glb"],
    "quotedCredits": 20,
    "quoteId": quote["quoteId"],
    "reviewId": quote.get("review", {}).get("reviewId"),
    "state": "reserved",
    "createdAt": now.isoformat(),
    "approval": {
        "mode": "automatic",
        "authorizedTotalCredits": 200,
        "currentPlanEstimatedCredits": 20,
        "decision": "user authorized automatic execution with a cumulative budget of 200 credits",
    },
}
record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
budget = {
    "conversationSessionId": os.environ.get("DSH_SESSION_ID"),
    "mode": "automatic",
    "authorizedTotalCredits": 200,
    "entries": [{
        "attemptId": "s01-gramophone-a1",
        "quoteId": quote["quoteId"],
        "quotedCredits": 20,
        "status": "reserved",
        "taskId": None,
    }],
    "committedCredits": 0,
    "reservedCredits": 20,
    "remainingCredits": 180,
}
budget_path.write_text(json.dumps(budget, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

os.environ["LUX3D_CN_API_KEY"] = json.loads(
    (Path.home() / ".config/lux3d/credentials.json").read_text()
)["apiKeys"]["cn"]

try:
    task_id = lux3d_client.create_text_to_3d_task(
        body["prompt"],
        version=body["version"],
        style=body.get("style"),
        faceCount=body.get("faceCount"),
        outputFormat=body.get("outputFormat"),
        aiPredictSize=body.get("aiPredictSize"),
        customSize=body.get("customSize"),
        region="cn",
        content_id=quote["quoteId"],
    )
except Exception as exc:
    record["state"] = "submission_unknown"
    record["error"] = type(exc).__name__
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "submission_unknown", "error": type(exc).__name__}))
    raise

record["state"] = "submitted"
record["taskId"] = str(task_id)
record["submittedAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
budget["entries"][0]["status"] = "committed"
budget["entries"][0]["taskId"] = str(task_id)
budget["committedCredits"] = 20
budget["reservedCredits"] = 0
budget["remainingCredits"] = 180
budget_path.write_text(json.dumps(budget, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"status": "submitted", "taskId": str(task_id), "quotedCredits": 20, "remainingCredits": 180}, ensure_ascii=False))
