"""Build a truthful delivery specification from reused generation records and this export."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"models/blender/study-room-v1"
items=[]
sources=[]
labels={"S01":"留声机","S02":"雕花桌腿","S03":"书桌椅","S04":"阅读扶手椅","S05":"地球仪","S06":"花瓣灯","S07":"书柜冠饰","S08":"镜框叶饰","S09":"花瓶花束"}
for ident,label in labels.items():
    folder=ROOT/"models/lux3d"/ident
    original=json.loads((folder/"records/original-state.json").read_text())
    artifacts=[]
    for artifact in original["downloadedArtifacts"]:
        path=folder/"source"/Path(artifact["path"]).name
        assert path.is_file(),path
        artifacts.append({"path":str(path),"format":artifact["format"]})
    snapshot={key:original[key] for key in ("schema","taskId","status","lastKnownProviderStatus","expectedFormats","createdAt","updatedAt","localCompletedAt") if key in original}
    snapshot["request"]={key:original["request"][key] for key in ("operation","region","version") if key in original["request"]}
    snapshot["downloadedArtifacts"]=artifacts
    state=OUT/"records"/(ident+"-delivery-state.json")
    state.write_text(json.dumps(snapshot,indent=2)+"\n")
    attempt=ident.lower()+"-original"
    items.append({"id":ident.lower(),"label":ident+" · "+label+"（生成源件）","selectedAttemptId":attempt,"attempts":[{"id":attempt,"statePath":str(state)}]})
    artifact=next(a for a in artifacts if a["format"]=="glb")
    sources.append({"itemId":ident.lower(),"attemptId":attempt,"artifactId":attempt+":glb","sha256":hashlib.sha256(Path(artifact["path"]).read_bytes()).hexdigest()})
execution=json.loads((OUT/"records/export-execution.json").read_text())
evidence={"schema":"lux3d.scene-execution/v1","kind":"external-tool","toolName":"exec_command","callId":execution["callId"],"recordRef":execution["recordRef"],"executedAt":execution["executedAt"],"exportSha256":hashlib.sha256((OUT/"scene.glb").read_bytes()).hexdigest(),"sources":sources}
(OUT/"records/scene-execution.json").write_text(json.dumps(evidence,indent=2)+"\n")
spec={"schema":"lux3d.delivery-spec/v2","title":"转间 Roomturn · 四门书房（剖切检查与生成源件）","items":items,"scene":{"status":"ready","artifactPath":str(OUT/"scene.glb"),"evidencePath":str(OUT/"records/scene-execution.json")}}
(OUT/"records/delivery-spec.json").write_text(json.dumps(spec,indent=2,ensure_ascii=False)+"\n")
print("Prepared nine original source bindings and real Blender export evidence; no new generation.")
