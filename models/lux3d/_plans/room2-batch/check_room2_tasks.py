import json, os, sys
from pathlib import Path
sys.path.insert(0, '/Users/a77/.dsh/skills/aholo-lux3d/core/runtime')
import lux3d_client
ROOT=Path('/Users/a77/Desktop/3d解密游戏/models/lux3d')
os.environ['LUX3D_CN_API_KEY']=json.loads((Path.home()/'.config/lux3d/credentials.json').read_text())['apiKeys']['cn']
for rec in sorted(ROOT.glob('B*/records/*.json')):
    d=json.loads(rec.read_text())
    if 'taskId' not in d or not d.get('taskId'): continue
    if d.get('state') not in {'submitted','downloaded','submission_unknown'}: continue
    try:
        t=lux3d_client.get_task(d['taskId'], region='cn')
        print(rec.parent.parent.name, d['attemptId'], d['taskId'], 'status', t.get('status'))
    except Exception as exc:
        print(rec.parent.parent.name, d['attemptId'], d['taskId'], 'ERROR', type(exc).__name__)
