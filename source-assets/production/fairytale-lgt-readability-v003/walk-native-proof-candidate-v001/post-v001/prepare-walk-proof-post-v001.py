"""Create 12 Walk +36 real primary unscaled QA crops from verified native PNGs.
No capture, source repair, resizing, pose substitution, or visual acceptance.
"""
from pathlib import Path
import argparse,hashlib,json,math,re,subprocess,sys,zlib
from urllib.parse import quote
from PIL import Image
HERE=Path(__file__).resolve().parent
CANDIDATE=HERE.parent

def need(v,why):
    if not v:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def fact(p):
    p=Path(p);b=p.read_bytes();return {"path":str(p.resolve()),"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
def new(p,v):
    with Path(p).open("x",encoding="utf-8",newline="\n") as f:f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2)+"\n")
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--archive",required=True);ap.add_argument("--version",default="v001");ap.add_argument("--encode-video",action="store_true");a=ap.parse_args()
    need(re.fullmatch(r"[A-Za-z0-9_-]+",a.version),"Unsafe post version")
    archive=Path(a.archive).resolve();original=archive/"原件";show=archive/"展示副本";out=(show/("walk-crops-"+a.version)).resolve()
    need(out.is_relative_to(show.resolve()) and not out.exists(),"Use a new crop version; never overwrite originals or prior review")
    verification_path=original/"independent-walk-proof-verification-v001.json";verification=read(verification_path)
    need(verification["schema"]=="independent-walk-native-proof-verification-v1" and verification["passed"] is True and verification["masks_left_right"]==[63,63] and verification["actual_unique_attacks"]==6 and verification["actual_primary_phase_facing_pairs"]==36 and verification["pixel_verification"]["every_source_viewport_pixel_crc_matches"],"Independent actual native motion/gear/frame/CRC proof required first")
    frozen=read(CANDIDATE/"tooling-freeze-v001.json")
    project=Path("F:/Ourgame").resolve()
    for row in frozen["files"]:
        path=project/row["path"];actual=fact(path);need(actual["bytes"]==row["bytes"] and actual["sha256"]==row["sha256"],"Frozen proof tooling changed")
    report_path=original/"runtime-report.json";report=read(report_path);obs=report["observations"];offsets=report["capture_timing"]["frame_wall_offsets_s"]
    movies=sorted(original.glob("MovieFrame*.png"));receipts=[json.loads(line) for line in (original/"native-frame-pixels.jsonl").read_text(encoding="utf-8-sig").splitlines() if line]
    movie_receipts=[r for r in receipts if r["file"].startswith("MovieFrame")]
    need(len(movies)==len(obs)==len(offsets)==len(movie_receipts)>0,"Actual movie/observation/FIFO count mismatch")
    need([p.name for p in movies]==[r["file"] for r in movie_receipts],"Original FIFO names differ")
    selected={}
    for i,o in enumerate(obs):
        side=-1 if o["facing"]<0 else 1
        if o["clip"]=="sword_walk" and o["flow_step"]==(4 if side<0 else 9) and o["frame"] in range(6):selected.setdefault(("Walk",side,-1,o["frame"]),i)
        if o["clip"].startswith("sword_primary_") and o["flow_step"]==(6 if side<0 else 11) and o["stage"] in range(3) and o["frame"] in range(6):selected.setdefault(("Primary",side,o["stage"],o["frame"]),i)
    expected={("Walk",side,-1,f) for side in (-1,1) for f in range(6)}|{("Primary",side,s,f) for side in (-1,1) for s in range(3) for f in range(6)}
    need(set(selected)==expected and len(selected)==len(set(selected.values()))==48,"12 actual Walk +36 actual primary facing/phases missing")
    out.mkdir(parents=True);maps=[];source_pins={};report_pin=fact(report_path);verification_pin=fact(verification_path)
    for kind,side,stage,frame in sorted(expected):
        i=selected[(kind,side,stage,frame)];o=obs[i];source=movies[i];receipt=movie_receipts[i]
        before=fact(source);source_pins[source.name]=before
        need(o["rendered_player_stack"]==o["draw_stack"] and o["armor_drawn"] and o["rendered_armor_used"] and o["rendered_armor_paths"]==[o["draw_stack"][x] for x in (1,2,4)],"Selected actual rendered LGT/SWD stack differs")
        scale=o["canvas_size"]/512.;root_x=o["grip_screen"][0]-side*(o["grip"][0]-o["root"][0])*scale;root_y=o["grip_screen"][1]-(o["grip"][1]-o["root"][1])*scale
        left=max(0,min(1040,math.floor(root_x)-110));top=max(0,min(560,math.floor(root_y)-130));rect=(left,top,left+240,top+160)
        name=f"{'left' if side<0 else 'right'}-{kind.lower()}-stage{stage+1}-phase{frame}-{source.name}"
        destination=out/name
        with Image.open(source) as image:
            need(image.format=="PNG" and image.size==(1280,720),"Original viewport format/dimensions changed")
            crc=zlib.crc32(image.convert("RGBA").tobytes("raw","BGRA"))&0xffffffff
            need(crc==receipt["native_BGRA8_crc32"],"Selected native pixel CRC changed")
            crop=image.crop(rect);mode,pixels=crop.mode,crop.tobytes();crop.save(destination)
        with Image.open(destination) as image:need(image.size==(240,160) and image.mode==mode and image.tobytes()==pixels,"Unscaled crop pixel roundtrip differs")
        need(fact(source)==before,"Original PNG changed while cropping")
        maps.append({"kind":kind,"facing":side,"stage":stage,"frame":frame,"observation_index":i,"flow_step":o["flow_step"],"flow_phase":o["flow_phase"],"wall_offset_s":offsets[i],"actual_attack_id":o["action_id"],"actual_light_id":o["light_id"],"actual_sword_id":o["sword_id"],"actual_rendered_stack":o["rendered_player_stack"],"actual_rendered_armor_paths":o["rendered_armor_paths"],"writer_sequence":receipt["writer_sequence"],"native_BGRA8_crc32":receipt["native_BGRA8_crc32"],"source_whole":before,"unscaled_crop":fact(destination),"crop_rect_xywh_px":[left,top,240,160],"crop_resampled":False,"actually_viewed":False,"whole_url":"../../原件/"+quote(source.name),"crop_url":quote(name)})
    payload=json.dumps(maps,ensure_ascii=False).replace("<","\\u003c")
    page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>Walk实际原生帧核对</title><style>body{margin:20px;background:#171816;color:#eee;font:15px system-ui}button{margin:4px;padding:8px;background:#34372f;color:#eee;border:1px solid #666;cursor:pointer}#crop{width:240px;height:160px;image-rendering:auto}#whole{max-width:100%;height:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere;color:#b8c2ac}a{color:#e6ba6b}</style><p>12个真实Walk相位/朝向与36个真实三刀相位/朝向。裁图240×160，未缩放，尚未实际审看；停墙视觉未录、正式完整内容未验收。静音录像另列。</p><div id="buttons"></div><p><a id="source">原生整帧</a> · <a id="download">原比例裁图</a></p><img id="crop"><pre id="facts"></pre><img id="whole"><script>const rows='''+payload+''';function select(i){const r=rows[i];document.getElementById('crop').src=r.crop_url;document.getElementById('whole').src=r.whole_url;document.getElementById('source').href=r.whole_url;document.getElementById('download').href=r.crop_url;document.getElementById('facts').textContent=JSON.stringify(r,null,2)}rows.forEach((r,i)=>{const b=document.createElement('button');b.textContent=(r.facing<0?'左':'右')+' '+r.kind+' '+(r.stage+1)+' / '+r.frame;b.onclick=()=>select(i);document.getElementById('buttons').appendChild(b)});select(0)</script></html>'''
    new(out/"native-48-phase-view-v001.html",page)
    for name,pin in source_pins.items():need(fact(original/name)==pin,"Native original changed after postprocess")
    need(fact(report_path)==report_pin and fact(verification_path)==verification_pin,"Native reports changed after postprocess")
    result={"schema":"walk-native-unscaled-review-crops-v1","status":"derived_pending_E_retention_and_actual_visual_review","crop_count":48,"walk_phase_facing_pairs":12,"primary_phase_facing_pairs":36,"crop_pixels_roundtrip_verified":True,"crop_resampled":False,"native_report":report_pin,"independent_verification":verification_pin,"maps":maps,"actually_viewed":False,"wall_stop_visually_recorded":False,"art_accepted":False,"formal_complete_units":0}
    new(out/"crop-source-map-v001.json",result)
    if a.encode_video:
        render=subprocess.run([sys.executable,"-B","-X","utf8",str(CANDIDATE/"tooling/render-walk-proof-review-v001.py"),"--archive",str(archive)],capture_output=True,text=True,encoding="utf-8",errors="replace")
        new(out/"video-helper-output-v001.log",render.stdout+render.stderr);need(render.returncode==0,"Frozen silent VFR encode/decode helper failed; outputs preserved")
    print(json.dumps({k:v for k,v in result.items() if k!="maps"},ensure_ascii=False))
if __name__=="__main__":main()
