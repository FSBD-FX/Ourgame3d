    def test_joint_fixed1115_two18_and_final_P2_hash_binding(self):
        imports={clip:{"path":"synthetic/"+clip+".json","bytes":1,"sha256":"a"*64} for clip in C.CLIPS}
        new_prod={}
        for clip in ("Primary2","Primary3"):
            for component in C.COMPONENTS:
                for frame in range(6):
                    key="UnrealGame/Content/"+C.NAMESPACES[clip][len("/Game/"):]+f"T_Fairytale_Leather{clip}{component}_{frame:03d}_v001.uasset"
                    new_prod[key]={"path":key,"bytes":1,"sha256":"b"*64}
        inventory={"schema":"root-leather-combo-final36-inventory-v001","template_only":False,"production_packages":1151,"old_packages_unchanged":1115,"new_packages":36,
            "p2_saved_hashes_unchanged_after_p3":True,"mismatches":0,"files":list(new_prod.values())}
        proof={"schema":"root-leather-combo-joint-import-proof-v001","template_only":False,"mode":"single_process_two18_fixed_old1115","same_process":True,
            "process":{"pid":42,"exit_code":0},"receipts":{clip:imports[clip] for clip in ("Primary2","Primary3")},"old_packages_unchanged":1115,"p2_saved_hashes_unchanged_after_p3":True}
        C.joint_import_values(proof,imports,new_prod,inventory)
        for mutate in (lambda p,i:p.update(template_only=True),lambda p,i:p["process"].update(pid=None),lambda p,i:p["process"].update(exit_code=1),
            lambda p,i:p.update(old_packages_unchanged=1133),lambda p,i:p.update(same_process=False),lambda p,i:p["receipts"].pop("Primary2"),
            lambda p,i:i.update(production_packages=1115),lambda p,i:i.update(template_only=True),lambda p,i:i["files"][0].update(sha256="c"*64),
            lambda p,i:i.update(p2_saved_hashes_unchanged_after_p3=False)):
            with self.subTest(mutate=str(mutate)):
                wrong_proof,wrong_inventory=copy.deepcopy(proof),copy.deepcopy(inventory);mutate(wrong_proof,wrong_inventory)
                with self.assertRaises(C.GateError):C.joint_import_values(wrong_proof,imports,new_prod,wrong_inventory)

    def test_joint_log_single_real_invocation_two_receipts_and_clean_exit(self):
        importer=(HERE/"synthetic-importer.py").resolve();receipts=[(HERE/(clip+"-synthetic.json")).resolve() for clip in ("P2","P3")]
        log="LogInit: Command Line: -ExecutePythonScript="+str(importer)+"\n"+"\n".join("LogPython: Leather combo receipt: "+str(value) for value in receipts)+"\nLogExit: Exiting.\n"
        C.joint_log_values(log,importer,receipts)
        for wrong in (log.replace(str(importer),str(importer)+" --validate-only"),log.replace(str(receipts[1]),str(receipts[0])),
            log.replace("LogExit: Exiting.",""),log+"LogPython: Error: synthetic failure\n",log.replace(str(receipts[0]),"other.json")):
            with self.assertRaises(C.GateError):C.joint_log_values(wrong,importer,receipts)

