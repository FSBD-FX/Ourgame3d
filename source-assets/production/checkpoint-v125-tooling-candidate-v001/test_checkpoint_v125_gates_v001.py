"""Only pure/in-memory gate checks and read-only prior retained v124 compatibility.
Synthetic report values are NEVER written as native/build/automation evidence.
"""
import copy,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
import checkpoint_v125_common_v001 as C
N=0

def check(ok,label):
    global N
    if not ok:raise RuntimeError(label)
    N+=1

def rejects(fn,label):
    try:fn()
    except (C.GateError,KeyError,ValueError,TypeError):check(True,label)
    else:raise RuntimeError("Expected rejection: "+label)

root=Path("F:/Ourgame");base=root/"source-assets/production/backups/2026-10-17_LeatherReady12-GuardCoin-full154GREEN-v124"
base_m=C.read(base/"compiled-source-manifest.json");old=C.read(base/base_m["current_automation_report"])
names=C.strict_automation(old,154);check(len(names)==154,"real previous baseline154")
synthetic=copy.deepcopy(old)
for name in sorted(C.RESTORE_TESTS):synthetic["tests"].append({"fullTestPath":name,"state":"Success","errors":0,"warnings":0,"entries":[]})
synthetic["succeeded"]=157
check(C.strict_automation(synthetic,157,names|C.RESTORE_TESTS)==names|C.RESTORE_TESTS,"in-memory shape-only157 control")
for key in ("failed","succeededWithWarnings","notRun","inProcess"):
    bad=copy.deepcopy(synthetic);bad[key]=1;rejects(lambda b=bad:C.strict_automation(b,157,names|C.RESTORE_TESTS),key)
for key in ("errors","warnings"):
    bad=copy.deepcopy(synthetic);bad["tests"][-1][key]=1;rejects(lambda b=bad:C.strict_automation(b,157,names|C.RESTORE_TESTS),"test "+key)
    bad=copy.deepcopy(synthetic);bad["tests"][-1][key]=False;rejects(lambda b=bad:C.strict_automation(b,157,names|C.RESTORE_TESTS),"bool "+key)
bad=copy.deepcopy(synthetic);bad["tests"][-1]["fullTestPath"]=bad["tests"][0]["fullTestPath"];rejects(lambda:C.strict_automation(bad,157,names|C.RESTORE_TESTS),"duplicate registration")
bad=copy.deepcopy(synthetic);bad["tests"][-1]["fullTestPath"]="CodexDungeon.Unapproved";rejects(lambda:C.strict_automation(bad,157,names|C.RESTORE_TESTS),"unknown same-count registration")
bad=copy.deepcopy(synthetic);bad["tests"][-1]["entries"]=[{"event":{"type":"Warning"}}];rejects(lambda:C.strict_automation(bad,157,names|C.RESTORE_TESTS),"hidden warning")
bad=copy.deepcopy(synthetic);bad["tests"][-1]["state"]="NotRun";rejects(lambda:C.strict_automation(bad,157,names|C.RESTORE_TESTS),"not Success")
for value in ("../outside","F:/outside","/outside","a\\b","a//b","a/./b"):
    rejects(lambda v=value:C.relative(v),"unsafe path "+value)
row={"path":"a.txt","bytes":0,"sha256":"0"*64};check(C.pin(row)==row,"zero-byte descriptor")
for key,value in (("bytes",False),("sha256","A"*64),("sha256","0"*63)):
    bad=dict(row);bad[key]=value;rejects(lambda b=bad:C.pin(b),"bad descriptor "+key)
rejects(lambda:C.table([row,dict(row)]),"duplicate paths")
rejects(lambda:C.table([row,{**row,"path":"A.txt"}]),"Windows case alias")
rejects(lambda:json.loads('{"a":1,"\\u0061":2}',object_pairs_hook=C.pairs),"escaped duplicate JSON key")
rejects(lambda:C.snapshot(root,base),"previous154 checkpoint cannot pass current157 verifier")
a=root/"过程图稿与视频/2026-10-17_军剑真实换装绑定_v006-guardCoinGREEN"
ix=C.read(a/"index.json");v=C.read(a/"原件/runtime-report.json");pix=C.read(a/"原件/native-pixel-verification.json")
check(C.verify_native_values("default",ix,v,pix,False)["observations"]==141,"actual prior native semantics only")
for key,value in (("passed",False),("mismatches",[{}]),("leather_ready_only_trial",True),("native_async_capture_writes_flushed",False)):
    bad=copy.deepcopy(v);bad[key]=value;rejects(lambda b=bad:C.verify_native_values("default",ix,b,pix,False),"native "+key)
bad=copy.deepcopy(v)
for x in bad["observations"]:
    if x["clip"]=="sword_primary_3" and x["frame"]==5:x["frame"]=4
rejects(lambda:C.verify_native_values("default",ix,bad,pix,False),"reported masks cannot hide missing actual third-stage frame")
bad=copy.deepcopy(v);bad["observations"][0]["interface_visible"]=True;rejects(lambda:C.verify_native_values("default",ix,bad,pix,False),"UI gate")
bad=copy.deepcopy(v);bad["observations"][0]["canvas_size"]=72.;rejects(lambda:C.verify_native_values("default",ix,bad,pix,False),"canvas oracle wrong72")
wrong=copy.deepcopy(pix);wrong["native_async_writer_verified"]=False;rejects(lambda:C.verify_native_values("default",ix,v,wrong,False),"async writer gate")
wrong=copy.deepcopy(pix);wrong["verified_original_PNG_count"]-=1;rejects(lambda:C.verify_native_values("default",ix,v,wrong,False),"PNG count")
check(len(C.expected_art_stack("sword_ready_idle",0))==7 and len(C.expected_art_stack("sword_primary_1",5))==8,"exact source stack shapes")
print(json.dumps({"pure_unit_checks":N,"failed":0,"synthetic157_shape_control_only":True,"actual_current157_claim":False,"actual_new_native_proof_claim":False,"prior_v124_semantics_readonly":True,"UE_UBT_run":False,"actual_source_or_tools_written":False}))
