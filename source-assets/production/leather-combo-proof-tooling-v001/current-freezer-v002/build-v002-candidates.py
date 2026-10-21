"""Author-only minimal sibling version; v001 frozen files are read, never changed."""
from pathlib import Path
import hashlib

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/"current-freezer-v001"
source=(OLD/"checkpoint_v126_common_v001.py").read_bytes()
assert hashlib.sha256(source).hexdigest()=="909089980817b358fc2c451b6608f105652a42cd9d54242ad7f7ab9255b90ea0"
text=source.decode("utf-8")
text=text.replace('"build_history","new_import_order","proof_tools","additional_files"','"build_history","new_import_order","joint_import_proof","proof_tools","additional_files"')
text=text.replace('checkpoint-v126-combo-freeze-request-v001','checkpoint-v126-combo-freeze-request-v002')
text=text.replace('new_prod={};expected_old={clip:1115+18*position for position,clip in enumerate(order)};import_manifest_pins={}',
    'require(order==["Primary2","Primary3"],"Reviewed joint importer runs P2 then P3 in one process")\n    new_prod={};expected_old={clip:1115 for clip in order};import_manifest_pins={}')
needle='    tools=table(request["proof_tools"]);require(REQUIRED_TOOLS<=set(tools),"All combo capture/postprocess/verify/pixel tools must be explicit pins")'
insert='''    require(contract.get("joint_import_proof")==request["joint_import_proof"],"Runtime contract and request joint import proof differ")
    joint_pins,joint_audit=validate_joint_import(root,request["joint_import_proof"],contract,old_prod,new_prod,import_manifest_pins)
    for row in joint_pins:add(row)
'''
assert needle in text;text=text.replace(needle,insert+needle)
text=text.replace('"contract_pin":contract_pin,"imports":','"joint_import_audit":joint_audit,"contract_pin":contract_pin,"imports":')
text=text.replace('def validate_request(root,request,virtual=None):',(HERE/"joint-import-v001.py.inc").read_text(encoding="utf-8")+'def validate_request(root,request,virtual=None):')
(HERE/"checkpoint_v126_common_v002.py").write_text(text,encoding="utf-8",newline="\n")
for name in ("prepare-current-build-v126-v001.py","freeze-current-build-v126-v001.py"):
    text=(OLD/name).read_text(encoding="utf-8").replace('checkpoint_v126_common_v001','checkpoint_v126_common_v002').replace('freeze-request-v126-v001','freeze-request-v126-v002')
    text=text.replace('checkpoint-v126-preparation-input-v001','checkpoint-v126-preparation-input-v002').replace('checkpoint-v126-combo-freeze-request-v001','checkpoint-v126-combo-freeze-request-v002')
    if name.startswith('prepare'):
        text=text.replace('"imports":draft["imports"],"assemblies":draft["assemblies"],"formal_complete_units":0}',
            '"imports":draft["imports"],"assemblies":draft["assemblies"],"joint_import_proof":draft["joint_import_proof"],"formal_complete_units":0}')
        text=text.replace('"build_history":draft["build_history"],"new_import_order":draft["new_import_order"],"proof_tools":draft["proof_tools"],',
            '"build_history":draft["build_history"],"new_import_order":draft["new_import_order"],"joint_import_proof":draft["joint_import_proof"],"proof_tools":draft["proof_tools"],')
        # Bind the actual executing preparer as well as its common module in the Root request.
        text=text.replace('"additional_files":draft["additional_files"]+[C.desc(root,draft_path)]}',
            '"additional_files":draft["additional_files"]+[C.desc(root,draft_path),C.desc(root,Path(__file__)),C.desc(root,Path(C.__file__))]}')
    else:
        text=text.replace('"contract_pin","imports","import_manifests","build_audit"','"contract_pin","imports","import_manifests","build_audit","joint_import_audit"')
        text=text.replace('"freeze_request":C.desc(root,request_path),"combo_proof_contract":request["combo_proof_contract"],',
            '"freeze_request":C.desc(root,request_path),"combo_proof_contract":request["combo_proof_contract"],"joint_import_audit":plan["joint_import_audit"],')
    (HERE/name.replace('v001.py','v002.py')).write_text(text,encoding="utf-8",newline="\n")
text=(OLD/'test_current_freezer_v126_v001.py').read_text(encoding="utf-8").replace('checkpoint_v126_common_v001.py','checkpoint_v126_common_v002.py')
text=text.replace("if __name__==\"__main__\":unittest.main(verbosity=2)",(HERE/"joint-tests-v001.py.inc").read_text(encoding="utf-8")+'\nif __name__=="__main__":unittest.main(verbosity=2)')
(HERE/'test_current_freezer_v126_v002.py').write_text(text,encoding="utf-8",newline="\n")
