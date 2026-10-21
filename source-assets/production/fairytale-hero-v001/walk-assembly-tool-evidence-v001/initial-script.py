"""Losslessly pack six existing native pose images for one shared-scale extraction.

No pose is redrawn, resized, relabeled, reordered or retimed. This is a source
animation trial, not a generation call, imported asset or motion acceptance.
Run with the sprite-gen virtual environment.
"""
from pathlib import Path
import hashlib
import json
import shutil
from PIL import Image

ROOT = Path("F:/Ourgame")
SOURCE = ROOT / "source-assets/production/fairytale-hero-v001"
PLAN = SOURCE / "walk-six-phase-source-plan-v001/source-plan.json"
NUMERIC = SOURCE / "numeric-walk-request-v002.json"
OUT = SOURCE / "walk-assembled-inputs-v001"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    assert not OUT.exists(), "Preserve previous outputs; use a new version"
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    numeric = json.loads(NUMERIC.read_text(encoding="utf-8"))
    assert plan["source_count"] == numeric["frame_count"] == 6
    assert numeric["expected_runtime_durations_ms"] == [83] * 6
    assert [p["source_request"] for p in plan["phases"]] == [138,142,143,137,141,145]
    assert [p["phase"] for p in plan["phases"]] == [p["phase"] for p in numeric["phase_contract"]]
    inputs = []
    for entry in plan["phases"]:
        raw = Path(entry["raw"]["path"])
        assert sha(raw) == entry["raw"]["sha256"]
        im = Image.open(raw)
        assert im.mode == "RGB" and im.size == (1254,1254)
        inputs.append((entry, raw, im.copy()))
    identity = Path(plan["identity"]["path"])
    assert sha(identity) == plan["identity"]["sha256"]
    OUT.mkdir()
    refs = OUT / "references"
    refs.mkdir()
    shutil.copy2(identity,refs / "identity131.png")
    row = Image.new("RGB",(1254*6,1254),(0,255,0))
    records = []
    for i,(entry,raw,im) in enumerate(inputs):
        name = f"phase-{i}-request{entry['source_request']}.png"
        shutil.copy2(raw,refs / name)
        row.paste(im,(i*1254,0))
        assert row.crop((i*1254,0,(i+1)*1254,1254)).tobytes() == im.tobytes()
        records.append({"frame":i,"phase":entry["phase"],"native_request":entry["source_request"],
            "source":str(raw),"source_sha256":sha(raw),"copied_reference":str(refs/name),
            "packing_xy":[i*1254,0],"source_pixel_size":[1254,1254],"packed_pixels_equal_source":True})
    raw = OUT / "walk-source-row.png"
    row.save(raw)
    request = {"version":1,"kind":"sprite-gen-request","engine":"component-row",
        "character":{"id":"fairytale-hero-walk-source-trial-v005","base_image":str(refs/"identity131.png"),
            "description":"Canonical131 identity, six existing native static phases, source-only motion trial"},
        "cell":{"shape":"square","size":512,"safe_margin":48},
        "chroma_key":{"name":"green","hex":"#00FF00","rgb":[0,255,0]},
        "chroma":{"mode":"rgb","unmix_reach":4,"spill_max_fraction":.005},
        "states":{"walk":{"frames":6,"fps":12,"loop":True,"durations_ms":[83]*6,
            "action":"Original six-phase walk, existing source roles preserved; not yet motion approved"}},
        "style":"Canonical131 dark-fairytale hand-drawn cartoon, not pixel art",
        "fit":{"pixel_unfake":False,"resample":"lanczos","align_x":"bbox-center","align_y":"bottom",
            "ground_frames":True,"segmentation":"components","shared_row_scale":True},
        "project_phase_contract":{"original":str(NUMERIC),"sha256":sha(NUMERIC),
            "phase_contract":numeric["phase_contract"],"actual_stride":None,"actual_body_foot_roots":None},
        "project_packing":{"source_plan":str(PLAN),"sha256":sha(PLAN),"row":str(raw),
            "row_sha256":sha(raw),"native_calls_added":0,"artwork_redrawn":False,"packing_only":True,"frames":records}}
    (OUT / "sprite-request-input.json").write_text(json.dumps(request,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT / "packing-receipt.json").write_text(json.dumps(request["project_packing"],ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"out":str(OUT),"row_size":list(row.size),"row_sha256":sha(raw),"six_source_pixel_comparisons":True,
        "native_generation_calls_added":0,"motion_accepted":False}))

if __name__ == "__main__":
    main()
