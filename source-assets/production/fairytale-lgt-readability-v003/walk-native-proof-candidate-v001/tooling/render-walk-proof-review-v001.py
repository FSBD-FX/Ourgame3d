"""Make a silent VFR review movie from verified original timestamps; never repaint pixels."""
from pathlib import Path
import argparse,hashlib,json,subprocess
import imageio_ffmpeg

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--archive",required=True);a=ap.parse_args();archive=Path(a.archive).resolve();original=archive/"原件";show=archive/"展示副本"
    verification=json.loads((original/"independent-walk-proof-verification-v001.json").read_text(encoding="utf-8"));assert verification["passed"] and verification["pixel_verification"]["every_source_viewport_pixel_crc_matches"]
    report=json.loads((original/"runtime-report.json").read_text(encoding="utf-8"));timing=report["capture_timing"];offsets=timing["frame_wall_offsets_s"];duration=timing["requested_video_wall_duration_s"]
    frames=sorted(original.glob("MovieFrame*.png"));assert len(frames)==len(offsets)>0 and duration>offsets[-1]
    pins=[{"file":p.name,"bytes":p.stat().st_size,"sha256":sha(p)} for p in frames]
    show.mkdir(exist_ok=True);concat=show/"native-frame-timing-v001.ffconcat";movie=show/"walk-native-core-proof-v001-silent.mp4";assert not movie.exists()
    lines=["ffconcat version 1.0"]
    for i,p in enumerate(frames):
        escaped=p.as_posix().replace("'","'\\''")
        lines += ["file '"+escaped+"'", "duration "+format((offsets[i+1] if i+1<len(frames) else duration)-offsets[i],".12f")]
    lines.append("file '"+frames[-1].as_posix().replace("'","'\\''")+"'")
    with concat.open("x",encoding="utf-8",newline="\n") as f:f.write("\n".join(lines)+"\n")
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    cmd=[ffmpeg,"-hide_banner","-loglevel","error","-n","-f","concat","-safe","0","-i",str(concat),"-vsync","vfr","-t",format(duration-offsets[0],".9f"),"-c:v","libx264","-crf","18","-pix_fmt","yuv420p","-an",str(movie)]
    result=subprocess.run(cmd,capture_output=True,text=True,encoding="utf-8",errors="replace")
    with (show/"encode-v001.log").open("x",encoding="utf-8") as f:f.write(result.stdout+result.stderr)
    assert result.returncode==0 and movie.stat().st_size>0,"Video encode failed; preserve output/log"
    decode=subprocess.run([ffmpeg,"-hide_banner","-loglevel","error","-i",str(movie),"-f","null","-"],capture_output=True,text=True,encoding="utf-8",errors="replace")
    with (show/"decode-v001.log").open("x",encoding="utf-8") as f:f.write(decode.stdout+decode.stderr)
    assert decode.returncode==0,"Video decode failed; preserve output/log"
    assert pins==[{"file":p.name,"bytes":p.stat().st_size,"sha256":sha(p)} for p in frames],"Native originals changed"
    receipt={"schema":"walk-native-review-derivative-v1","status":"encoded_decode_checked_pending_E_retention_and_visual_review","movie":{"path":str(movie),"bytes":movie.stat().st_size,"sha256":sha(movie)},"source_frames":pins,"silent":True,"actual_native_pixels_repainted":False,"visual_reviewed":False,"wall_stop_visually_recorded":False,"art_accepted":False,"formal_complete_units":0}
    with (show/"derivative-v001.json").open("x",encoding="utf-8") as f:json.dump(receipt,f,indent=2);f.write("\n")
    print(json.dumps({k:v for k,v in receipt.items() if k!="source_frames"},ensure_ascii=False))
if __name__=="__main__":main()
