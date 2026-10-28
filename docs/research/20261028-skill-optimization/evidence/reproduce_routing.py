"""Read-only, deterministic reproduction of the user-provided routing scenarios."""
import copy
import json
import sys
import tempfile
from pathlib import Path
root=Path(sys.argv[1]).resolve()
sys.dont_write_bytecode=True
sys.path.insert(0,str(root/'skill/plan-and-execute/scripts'))
import run_concise
run=run_concise.run_isolated
import availability, routing_config, planctl
cfg=routing_config.merge(planctl.default_config(),routing_config.EXTRA_DEFAULTS)
custom=copy.deepcopy(cfg)
custom['tier_routes']={t:{'primary':p[0],'fallbacks':p[1:]} for t,p in {
'economy':['antigravity','codex','claude'],'standard':['antigravity','codex','claude'],
'advanced':['antigravity','codex','claude'],'strong':['codex','claude','antigravity'],
'max':['codex','claude']}.items()}
custom['claude']['models']={'economy':'haiku','standard':'claude-sonnet-5-5','strong':'claude-opus-5-5','max':'claude-opus-5-5'}
custom['codex']['models']={'economy':'gpt-6-luna','standard':'gpt-6.1-sol','strong':'gpt-6.1-sol','max':'gpt-6.1-sol'}
custom['antigravity']['models']={'economy':'gemini-3.8-flash-medium','standard':'claude-sonnet-5-5-medium','advanced':'claude-sonnet-5-5-high','strong':'claude-opus-5-5-high','max':'claude-opus-5-5-high'}
custom['antigravity']['models_without_effort']=list(custom['antigravity']['models'].values())
custom.setdefault('workload_routing', {})['enabled']=False
results=[]
for fixture,config in [('default',cfg),('user-equivalent',custom)]:
 for tier,effort,kind in [('strong','high','unknown'),('max','high','semantic'),('standard','medium','unknown'),('standard','medium','mechanical'),('advanced','high','unknown')]:
  task={'id':'001','provider':'auto','model_tier':tier,'reasoning_effort':effort,'functional_failures':0,'failure_classes':[],'max_attempts':8}
  case={'fixture':fixture,'tier':tier,'effort':effort,'failure_class':kind,'attempts':[]}
  with tempfile.TemporaryDirectory() as tmp:
   for attempt in range(8):
    try:
     if run.ladder_exhausted(task,config,None,check_availability=False):
      case['stop']='ladder_exhausted';break
     intent=run.choose_route(task,config,None,check_availability=False)
     route=availability.select(Path(tmp),task,config,intent,None,'implementation',set(),lambda _: True,run.clamp_effort,persist=False)
     case['attempts'].append({'n':attempt+1,'intent_provider':intent['provider'],**route})
    except Exception as exc:
     case['stop']=type(exc).__name__+': '+str(exc);break
    task['functional_failures']+=1;task['failure_classes'].append(kind)
   else: case['stop']='max_attempts'
  results.append(case)
print(json.dumps({'base_tree':'f4b5a2285b7f2b1089d974c9e60814e46db858f4','live_provider_calls':0,'cases':results},indent=2))
