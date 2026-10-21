"""Standard shared-row whole-component extraction of Root E413 retained native227.
Default mode validates only; --extract creates NEW candidate media, never View.
"""
from pathlib import Path
import argparse,copy,hashlib,json,shutil,subprocess,sys
HERE=Path(__file__).resolve().parent
PROJECT=Path("F:/Ourgame")
SKILL=Path("C:/Users/22499/.codex/skills/sprite-gen")
INPUT=HERE.parent/"hurt4-grip-correction-standard-input-v001"
RUN=HERE/"runs/run-hurt227-shared-HD-v001"
def pin(p):
    b=p.read_bytes();return {"path":p.as_posix(),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
def write(p,x):
    if p.exists():raise ValueError("Preserve prior candidate: "+str(p))
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(x if isinstance(x,str) else json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def verify_frozen():
    count=0
    for fp in [INPUT/"candidate-input-freeze-v001.json",HERE.parent/"standard-input-candidate-v001/standard-input-freeze-v001.json",HERE.parent/"hero218-220-extraction-v001/extraction-complete-files-freeze-v001.json"]:
        f=json.loads(fp.read_text(encoding="utf-8-sig"))
        for z in f["files"]:
            actual=pin(Path(z["path"]))
            if actual["bytes"]!=z["bytes"] or actual["sha256"]!=z["sha256"]:raise ValueError("Frozen input drift: "+z["path"])
            count+=1
    meta=json.loads((INPUT/"input-authority-and-pins-v001.json").read_text(encoding="utf-8"))
    for z in meta["tools"]:
        if pin(Path(z["path"]))!=z:raise ValueError("Pinned tool drift: "+z["path"])
    return count

def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument("--extract",action="store_true");args=a.parse_args()
    if Path(sys.executable).resolve()!=(SKILL/".venv/Scripts/python.exe").resolve():raise ValueError("Use pinned SG venv")
    oldcount=verify_frozen()
    admission=json.loads((HERE/"actual-raw-admission-E413-v001.json").read_text(encoding="utf-8"))
    if admission["root_notification_received"] is not True or admission["native_request_number"]!=227 or admission["F_E_differences"]!=0:raise ValueError("Root exact E413 raw admission required")
    if not args.extract:
        print(json.dumps({"frozen_inputs":oldcount,"tool_pins_valid":True,"raw_read":False,"new_media":False}));return
    for k in ["F_raw","E_original"]:
        if pin(Path(admission[k]["path"]))!=admission[k]:raise ValueError("Raw F/E changed")
    if RUN.exists():raise ValueError("Preserve prior run; choose NEW version")
    RUN.mkdir(parents=True)
    receipt={"schema":"hero227-shared-extraction-receipt-v001","native_request":227,"state":"hurt","raw_admission":admission,"commands":[],"status":"STARTED","View":False,"new_generation":False,"UE":False,"grip_axis_floor_root":None,"art_accepted":False}
    try:
        from PIL import Image
        req=copy.deepcopy(json.loads((INPUT/"prepared-run-v001/sprite-request.json").read_text(encoding="utf-8")))
        assert list(req["states"])==["hurt"] and (req["states"]["hurt"]["frames"],req["states"]["hurt"]["fps"],req["states"]["hurt"]["loop"])==(4,10,False)
        req["chroma"]={"mode":"rgb","unmix_reach":4,"spill_max_fraction":.005}
        write(RUN/"sprite-request.json",req);requestbytes=(RUN/"sprite-request.json").read_bytes()
        for rel in ["prompts/hurt.txt","references/layout-guides/hurt.png","references/identity/Ready002-body-only-frame-0.png","references/motion/native219-Hurt4-original-motion-only.png"]:
            src=INPUT/"prepared-run-v001"/rel;dest=RUN/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest);assert src.read_bytes()==dest.read_bytes()
        raw=RUN/"raw/hurt.png";raw.parent.mkdir(parents=True);shutil.copyfile(Path(admission["F_raw"]["path"]),raw)
        assert pin(raw)["sha256"]==admission["F_raw"]["sha256"]
        with Image.open(raw) as im:receipt["actual_raw"]={"file":pin(raw),"mode":im.mode,"size":list(im.size)}
        write(RUN/"frozen-original-input-pins-v001.json",{"numeric_input":pin(INPUT/"prepared-run-v001/sprite-request.json"),"chroma_defaults_explicit_only":req["chroma"],"no_timing_or_fit_change":True})
        shutil.copyfile(INPUT/"runtime-timing-and-null-markers-v001.json",RUN/"runtime-timing-and-null-markers-v001.json")
        cmds=[("extract-shared-row",PROJECT/"tools/scripts/extract-sprite-shared-row-scale.py",[]),("compose-atlas",SKILL/"scripts/compose_sprite_atlas.py",[]),("export-curated",SKILL/"scripts/export_curated_pngs.py",["--state","hurt"]),("preview-standard-QA",SKILL/"scripts/preview_animation.py",[]),("inspect-standard",SKILL/"scripts/inspect_sprite_run.py",[])]
        for name,tool,extra in cmds:
            argv=[sys.executable,"-B","-X","utf8",str(tool),"--run-dir",str(RUN)]+extra
            z=subprocess.run(argv,capture_output=True,text=True,encoding="utf-8",errors="replace")
            log=RUN/"pipeline-logs"/(name+"-v001.log");write(log,z.stdout+z.stderr)
            receipt["commands"].append({"argv":argv,"tool":pin(tool),"exit_code":z.returncode,"log":pin(log)})
            if (RUN/"sprite-request.json").read_bytes()!=requestbytes:raise ValueError("Unexpected request normalization/fit change")
            if z.returncode:raise ValueError(name+" failed; preserve output and unchanged QA")
        fm=json.loads((RUN/"frames/frames-manifest.json").read_text(encoding="utf-8"));qa=json.loads((RUN/"sprite-inspect.report.json").read_text(encoding="utf-8"));manifest=json.loads((RUN/"manifest.json").read_text(encoding="utf-8"))
        assert fm["errors"]==fm["warnings"]==[] and qa["errors"]==qa["warnings"]==[] and len(fm["rows"])==1
        row=fm["rows"][0];fit=row["shared_row_fit"];assert row["state"]=="hurt" and row["frames"]==4 and row["method"]=="components" and fit["per_frame_scale_normalization"] is False
        am=manifest["animation"]["rows"]["hurt"];assert (am["frames"],am["fps"],am["loop"])==(4,10,False) and len(manifest["frame_layout"]["rows"]["hurt"])==4
        frames=[]
        for i in range(4):
            p=RUN/"curated"/("frame-"+str(i)+".png")
            with Image.open(p) as im:
                assert im.size==(512,512) and im.mode=="RGBA"
                alpha=im.getchannel("A");bbox=alpha.getbbox();core=alpha.point(lambda v:255 if v>=128 else 0).getbbox();assert bbox
                frames.append({"frame":i,"file":pin(p),"decoded_RGBA_sha256":hashlib.sha256(im.tobytes()).hexdigest(),"alpha_bbox":list(bbox),"alpha128_bbox":list(core),"Grip":None,"Axis":None,"handmask":None,"floor":None,"Root":None,"bodydensity_accepted":False})
        assert len({z["decoded_RGBA_sha256"] for z in frames})==4
        with Image.open(RUN/"qa/hurt.gif") as im:gif={"actual_frames":im.n_frames,"encoded_loop":im.info.get("loop"),"scope":"Standard convenience GIF only; loop1 is SDKnonloop QA encoding, not actual source/runtime replay contract"}
        receipt.update({"status":"STANDARD_EXTRACTED_NO_QA_FINDINGS_WAIT_ROOT_E_VIEW","frames":frames,"shared_row_fit":fit,"frames_manifest":pin(RUN/"frames/frames-manifest.json"),"manifest":pin(RUN/"manifest.json"),"inspect":pin(RUN/"sprite-inspect.report.json"),"extract_errors":fm["errors"],"extract_warnings":fm["warnings"],"inspect_errors":qa["errors"],"inspect_warnings":qa["warnings"],"QA_gif":gif,"frozen_old_file_count":oldcount,"old_freezes_after":verify_frozen(),"cross_row_identity_bodydensity":"Pending actualView/comparison after Root E retention"})
    except BaseException as e:
        receipt["status"]="STOPPED_PRESERVE_FAILED_OUTPUT_NO_ART_ACCEPTANCE";receipt["failure"]=repr(e);raise
    finally:
        write(RUN/"extraction-receipt-v001.json",receipt)
        files=[pin(p) for p in sorted(RUN.rglob("*")) if p.is_file()]
        write(RUN/"extracted-files-freeze-v001.json",{"schema":"hero227-extracted-files-freeze-v001","status":receipt["status"],"files":files,"indexed_files":len(files),"View":False,"E_retention_pending":True,"art_accepted":False})
        print(json.dumps({"status":receipt["status"],"receipt":pin(RUN/"extraction-receipt-v001.json"),"freeze":pin(RUN/"extracted-files-freeze-v001.json"),"E_pending":True},ensure_ascii=False))
if __name__=="__main__":main()
