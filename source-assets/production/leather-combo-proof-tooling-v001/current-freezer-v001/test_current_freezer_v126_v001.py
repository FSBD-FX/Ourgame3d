"""Candidate-only synthetic gates; no UE, UBT, import or media writes."""
from pathlib import Path
import copy
import importlib.util
import json
import os
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("current_freezer", HERE / "checkpoint_v126_common_v001.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


class CurrentFreezer(unittest.TestCase):
    def test_explicit161_unique_clean_full_set(self):
        names = ["Synthetic.Group." + str(i) for i in range(161)]
        report = {"succeeded": 161, "failed": 0, "succeededWithWarnings": 0, "notRun": 0, "inProcess": 0,
            "tests": [{"fullTestPath": name, "state": "Success", "errors": 0, "warnings": 0, "entries": []} for name in names]}
        self.assertEqual(C.strict_automation(report, 161, names), set(names))
        for mutate in (lambda r:r.update(succeeded=157), lambda r:r["tests"][-1].update(fullTestPath=names[0]),
            lambda r:r["tests"][-1].update(state="Fail"), lambda r:r["tests"][0]["entries"].append({"event":{"type":"Warning"}})):
            wrong = copy.deepcopy(report); mutate(wrong)
            with self.assertRaises(C.GateError): C.strict_automation(wrong, 161, names)

    def test_source_deltas_exact_and_no_removed_historical_source(self):
        def row(name, sha): return {"path":name,"bytes":1,"sha256":sha*64}
        before={"UnrealGame/Source/a.cpp":row("UnrealGame/Source/a.cpp","a")}
        after={**before,"UnrealGame/Source/b.h":row("UnrealGame/Source/b.h","b")}
        self.assertEqual(C.source_changes(before,after,[after["UnrealGame/Source/b.h"]]),{"UnrealGame/Source/b.h"})
        for current,pins in (({},[]),(after,[]),(after,[before["UnrealGame/Source/a.cpp"]])):
            with self.assertRaises(C.GateError):C.source_changes(before,current,pins)

    def test_transitive_header_and_inl_require_all_cpp_consumers(self):
        with tempfile.TemporaryDirectory(dir=HERE,prefix="synthetic-include-") as directory:
            root=Path(directory); source=root/"UnrealGame/Source/CodexDungeon"; source.mkdir(parents=True)
            texts={"Shared.h":"#pragma once\n", "Bridge.h":'#include "Shared.h"\n',
                "One.cpp":'#include "Bridge.h"\n',"Two.cpp":'#include "Shared.h"\n',"Pose.inl":"// synthetic\n",
                "Three.cpp":'#include "Pose.inl"\n'}
            for name,text in texts.items():(source/name).write_text(text,encoding="utf-8")
            current={C.desc(root,path)["path"]:C.desc(root,path) for path in source.iterdir()}
            affected=C.affected_translation_units(root,current,{"UnrealGame/Source/CodexDungeon/Shared.h","UnrealGame/Source/CodexDungeon/Pose.inl"})
            self.assertEqual(set(affected),{"UnrealGame/Source/CodexDungeon/One.cpp","UnrealGame/Source/CodexDungeon/Two.cpp","UnrealGame/Source/CodexDungeon/Three.cpp"})
            C.check_translation_units(affected,sorted(affected))
            with self.assertRaises(C.GateError):C.check_translation_units(affected,sorted(affected)[:-1])

    def test_build_history_requires_post_write_compile_and_final_link(self):
        with tempfile.TemporaryDirectory(dir=HERE,prefix="synthetic-build-") as directory:
            root=Path(directory); cpp=root/"One.cpp";cpp.write_text("// synthetic",encoding="utf-8");os.utime(cpp,(10,10))
            dll=root/"UnrealEditor-CodexDungeon.dll";dll.write_text("synthetic, not a DLL",encoding="utf-8");os.utime(dll,(20,20))
            report=root/"report.json";report.write_text("{}",encoding="utf-8");os.utime(report,(30,30))
            log=root/"build.log";log.write_text("[1/2] Compile [x64] One.cpp\n[2/2] Link [x64] UnrealEditor-CodexDungeon.dll\n",encoding="utf-8")
            receipt=root/"receipt.json";receipt.write_text(json.dumps({"Utc":"1970-01-01T00:00:25Z","Target":"CodexDungeonEditor","ExitCode":0,"Log":str(log)}),encoding="utf-8")
            entry={"receipt":C.desc(root,receipt),"log":C.desc(root,log)}
            C.validate_build_history(root,[entry],{"One.cpp":{"One.cpp"}},C.desc(root,dll),C.desc(root,report))
            os.utime(cpp,(26,26))
            with self.assertRaises(C.GateError):C.validate_build_history(root,[entry],{"One.cpp":{"One.cpp"}},C.desc(root,dll),C.desc(root,report))
            os.utime(cpp,(10,10))
            log.write_text("[1/1] Link [x64] UnrealEditor-CodexDungeon.dll\n",encoding="utf-8");entry["log"]=C.desc(root,log)
            with self.assertRaises(C.GateError):C.validate_build_history(root,[entry],{"One.cpp":{"One.cpp"}},C.desc(root,dll),C.desc(root,report))
            log.write_text("[1/2] Compile [x64] One.cpp\n[2/2] Link [x64] Other.dll\n",encoding="utf-8");entry["log"]=C.desc(root,log)
            with self.assertRaises(C.GateError):C.validate_build_history(root,[entry],{"One.cpp":{"One.cpp"}},C.desc(root,dll),C.desc(root,report))

    def test_new_import_registry_disk_count_and_namespace_gates(self):
        assets=[]
        for component in C.COMPONENTS:
            for frame in range(6):
                name=f"T_Fairytale_LeatherPrimary2{component}_{frame:03d}_v001";package=C.NAMESPACES["Primary2"]+name
                assets.append({"component":component,"frame":frame,"name":name,"package_path":package,"object_path":package+"."+name,"actual_object_type":"Texture2D"})
        imported={"success":True,"namespace":C.NAMESPACES["Primary2"].rstrip("/"),"actual_count":18,"expected_count":18,"saved_count":18,
            "old_packages_unchanged":1115,"registry_exact_set_passed":True,"disk_exact_set_passed":True,"assets":assets}
        self.assertEqual(len(C.import_values(imported,"Primary2",1115)),18)
        for mutate in (lambda r:r.update(saved_count=17),lambda r:r.update(old_packages_unchanged=True),lambda r:r.update(registry_exact_set_passed=False),
            lambda r:r.update(disk_exact_set_passed=False),lambda r:r["assets"][0].update(actual_object_type="Sprite"),lambda r:r["assets"][0].update(object_path="/Game/Wrong.Wrong")):
            wrong=copy.deepcopy(imported);mutate(wrong)
            with self.assertRaises(C.GateError):C.import_values(wrong,"Primary2",1115)

    def test_assembly_relative_closure_and_failure_never_publishes_manifest(self):
        with tempfile.TemporaryDirectory(dir=HERE,prefix="synthetic-copy-") as directory:
            root=Path(directory);source=root/"source";source.mkdir();member=source/"member.txt";member.write_text("synthetic",encoding="utf-8")
            freeze=source/"freeze.json";row={"path":"member.txt","bytes":9,"sha256":C.desc(root,member)["sha256"]}
            freeze.write_text(json.dumps({"files":[row],"file_count_excluding_manifest":1,"total_bytes_excluding_manifest":9}),encoding="utf-8")
            self.assertEqual(C.assembly_closure(root,C.desc(root,freeze))[0],[C.desc(root,member)])
            bad=copy.deepcopy(row);bad["path"]="../member.txt";freeze.write_text(json.dumps({"files":[bad]}),encoding="utf-8")
            with self.assertRaises(C.GateError):C.assembly_closure(root,C.desc(root,freeze))
            out=root/"new-snapshot";plan={"rows":[C.desc(root,member)]}
            def reject():raise C.GateError("synthetic endpoint race")
            with self.assertRaises(C.GateError):C.copy_new_snapshot(root,out,plan,lambda:{"schema":"synthetic"},reject)
            self.assertFalse((out/"compiled-source-manifest.json").exists());self.assertTrue((out/"freeze-failure-v001.json").exists())
            out2=root/"serialization-failure"
            with self.assertRaises(TypeError):C.copy_new_snapshot(root,out2,plan,lambda:{"not_json":object()},lambda:None)
            self.assertFalse((out2/"compiled-source-manifest.json").exists());self.assertTrue((out2/"freeze-failure-v001.json").exists())


if __name__=="__main__":unittest.main(verbosity=2)
