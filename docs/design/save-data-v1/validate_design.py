"""Static source checks and a deliberately abstract recovery model; no UE/disk IO test."""
from pathlib import Path
from collections import Counter
import copy
import hashlib
import json
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
errors = []
checks = Counter()
abstract_results = []


def check(ok, group, label):
    checks[group] += 1
    if not ok:
        errors.append(f"{group}: {label}")


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"), parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk(value):
    yield value
    if isinstance(value, dict):
        for item in value.values():
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


def path_for(name):
    if name.startswith("docs/") or name.startswith("UnrealGame/"):
        return ROOT/name
    return HERE/name


def resolve(name, pointer=""):
    name, _, fragment = name.partition("#")
    path = path_for(name).resolve()
    if not path.is_file():
        raise ValueError(f"missing source {name}")
    if not pointer:
        pointer = fragment
    if not pointer:
        return read(path) if path.suffix == ".json" else path.read_text(encoding="utf-8-sig")
    value = read(path)
    if not pointer.startswith("/"):
        raise ValueError(f"invalid pointer {pointer}")
    for part in pointer[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def load_reference(markers):
    # Markers here are booleans supplied by paper vectors, not filesystem probes.
    if not markers:
        return "NO_COMMITTED_PROFILE"
    if any(not m["marker_valid"] or m["generation"] is None for m in markers):
        return "RECOVERY_REQUIRED"
    head = max(m["generation"] for m in markers)
    candidates = [m for m in markers if m["generation"] == head]
    if len({m.get("digest", str(head)) for m in candidates}) > 1:
        return "RECOVERY_REQUIRED"
    if any(not m["bundle_valid"] for m in candidates):
        return "RECOVERY_REQUIRED"
    if any(not m["supported"] for m in candidates):
        return "VERSION_BLOCKED"
    return f"LOAD_{head}"


def purchase_reference(state, operation_id, request):
    digest = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
    if operation_id in state["journal"]:
        receipt = state["journal"][operation_id]
        return "same_result" if receipt["digest"] == digest else "reject_digest_conflict"
    if request["source"] in state["consumed"]:
        return "source_already_consumed"
    if state["balance"] < request["cost"]:
        return "insufficient_balance"
    state["balance"] -= request["cost"]
    state["items"].append("INSTANCE-ONE")
    state["consumed"].add(request["source"])
    state["journal"][operation_id] = {"digest": digest, "result": "INSTANCE-ONE"}
    return "committed"


def main():
    required = ["save-rules.json", "state-schema.json", "transactions-and-rng.json", "compatibility-and-coop.json", "recovery-cases.json", "design-index.json"]
    docs = {}
    source_refs = set()
    for name in required:
        path = HERE/name
        check(path.is_file(), "files", name)
        if not path.is_file():
            continue
        data = read(path)
        docs[path.stem] = data
        check(data.get("module") == "D-13" and data.get("source_event") == "EV-031", "metadata", name + " module/event")
        check(data.get("design_date") == "2026-10-14", "metadata", name + " date")
        check(data.get("status") == "design_only" and data.get("runtime_implemented") is False, "metadata", name + " implementation scope")
        for value in walk(data):
            if isinstance(value, dict) and isinstance(value.get("path"), str) and "pointer" in value:
                source_refs.add((value["path"], value["pointer"]))
            if isinstance(value, dict) and isinstance(value.get("path"), str) and "json_pointer" in value:
                source_refs.add((value["path"], value["json_pointer"]))
            if isinstance(value, dict) and isinstance(value.get("path"), str):
                for pointer in value.get("pointers", []):
                    source_refs.add((value["path"], pointer))
                if "sha256" in value:
                    source_path = path_for(value["path"])
                    check(source_path.is_file() and sha(source_path) == value["sha256"], "source_hash", value["path"])
            if isinstance(value, dict) and isinstance(value.get("source_ref"), str) and "pointer" in value:
                ref_catalogue = {row["id"]: row for row in data.get("source_refs", []) if isinstance(row, dict) and "id" in row and "path" in row}
                if value["source_ref"] in ref_catalogue:
                    source_refs.add((ref_catalogue[value["source_ref"]]["path"], value["pointer"]))
            if isinstance(value, str) and re.fullmatch(r"(?:\.\./|docs/)[^\s#]+\.json(?:#/[\w/~.\-]+)?", value):
                source_refs.add((value, ""))
        # IDs are unique within each explicit catalogue, not globally across different scopes.
        for key, value in data.items():
            if isinstance(value, list) and value and all(isinstance(row, dict) and "id" in row for row in value):
                check(len({row["id"] for row in value}) == len(value), "identity", name + " /" + key)
    for name, pointer in sorted(source_refs):
        try:
            resolve(name, pointer)
            check(True, "source_reference", name + "#" + pointer)
        except (ValueError, KeyError, IndexError) as exc:
            check(False, "source_reference", str(exc))

    rules = docs["save-rules"]
    index = docs["design-index"]
    cases = docs["recovery-cases"]
    state = docs["state-schema"]
    transactions = docs["transactions-and-rng"]
    transaction_source_ids = {ref["id"] for ref in transactions["source_refs"]}
    for value in walk(transactions):
        if isinstance(value, dict) and "source_ref_ids" in value:
            check(set(value["source_ref_ids"]) <= transaction_source_ids, "transaction_sources", value.get("id", "source reference group"))
    check(len(transactions["operation_types"]) >= 12 and len(transactions["stable_reward_keys"]) >= 8, "transaction_coverage", "operations and independent reward-source identity")
    streams = transactions["rng_contract"]["streams"]
    check(len({stream["id"] for stream in streams}) == len(streams), "transaction_coverage", "RNG namespaces unique")
    group_ids = {group["id"] for group in state["field_groups"]}
    for group in state["field_groups"]:
        names = [f["name"] for f in group["fields"]]
        check(bool(names) and len(set(names)) == len(names), "state_fields", group["id"] + " unique fields")
        check(bool(group["restore_rule"]) and bool(group["invariants"]) and bool(group["source_refs"]), "state_fields", group["id"] + " restore/source/invariants")
    for case in state["future_acceptance_cases"]:
        check(set(case["field_group_refs"]) <= group_ids, "state_fields", case["id"] + " group references")
    for binding in state["stable_catalog_bindings"]:
        rows = resolve(binding["path"], binding["pointer"])
        original_ids = {row["id"] for row in rows} if isinstance(rows, list) else set(rows)
        check(set(binding["ids"]) == original_ids and len(binding["ids"]) == len(original_ids), "catalogue_identity", binding["path"] + "#" + binding["pointer"])
    for entry in rules["precedence"]:
        if "old" in entry:
            check(resolve(entry["source"]) == entry["old"] is False and entry["D13_decision"] is True, "precedence", entry["source"])
    check(rules["single_root_authority"]["no_mixing_generations"] and rules["single_root_authority"]["no_live_run_hub_progression_edit"], "root_contract", "one generation and unfinished hub progression lock")
    check(rules["autosave"]["interval_active_sim_s"] == 5 and rules["autosave"]["offline_clock_used"] is False, "root_contract", "request interval and clock")
    check(rules["technical_room_repair"]["normal_continue_repairs"] is False and rules["technical_room_repair"]["explicit_only"] is True, "root_contract", "repair is separate")
    check(rules["physical_storage_proposal"]["created_by_this_design"] is False, "root_contract", "no real game save creation")
    check(len(cases["future_cases"]) == 28 and all(c["runtime_tested"] is False for c in cases["future_cases"]), "case_scope", "28 unexecuted runtime cases")
    phases = [p["phase"] for p in rules["commit_pipeline"]]
    publish = phases.index("publish_new_marker")
    old = {"generation": 1, "account": {"shards": 10, "sample": False}, "run": {"gold": 10, "HP": 40, "item": None, "rng_cursor": 1}, "consumed": []}
    new = {"generation": 2, "account": {"shards": 13, "sample": True}, "run": {"gold": 6, "HP": 35, "item": "INSTANCE-ONE", "rng_cursor": 2}, "consumed": ["REWARD-ONE", "OFFER-ONE"]}
    for vector in cases["commit_reference_vectors"]:
        phase_index = phases.index(vector["crash_after"])
        recovered = copy.deepcopy(new if phase_index >= publish else old)
        check(recovered["generation"] == vector["expected_generation"], "abstract_commit", vector["id"])
        check(recovered == (new if vector["expected_generation"] == 2 else old), "abstract_commit", vector["id"] + " whole root; no mixing")
        abstract_results.append({"id": vector["id"], "result": recovered["generation"], "scope": "abstract_not_disk"})
    for vector in cases["load_reference_vectors"]:
        result = load_reference(vector["markers"])
        check(result == vector["expected"], "abstract_load", vector["id"])
        abstract_results.append({"id": vector["id"], "result": result, "scope": "abstract_not_disk"})
    # Older inactive bundle can mismatch during an unpublished write; highest published one remains valid.
    check(load_reference([{"generation": 1, "marker_valid": True, "bundle_valid": False, "supported": True}, {"generation": 2, "marker_valid": True, "bundle_valid": True, "supported": True}]) == "LOAD_2", "abstract_load", "older inactive mismatch")
    request = {"source": "OFFER-ONE", "cost": 4}
    for vector in cases["transaction_reference_scenarios"]:
        state = {"balance": 10, "HP": 35, "shards": 13, "items": [], "consumed": set(), "journal": {}}
        kind = vector["kind"]
        if kind in {"matching_retry", "changed_payload_retry"}:
            purchase_reference(state, "OP-ONE", request)
            retry = request if kind == "matching_retry" else {"source": "OFFER-ONE", "cost": 5}
            result = purchase_reference(state, "OP-ONE", retry)
            check(state["balance"] == vector["expected_balance"] and len(state["items"]) == vector["expected_item_count"], "abstract_transaction", vector["id"] + " ownership and balance")
        elif kind == "new_operation_same_reward_source":
            state["consumed"].add("OFFER-ONE")
            result = purchase_reference(state, "OP-DIFFERENT", request)
            check(state["shards"] == vector["expected_account_shards"] and state["balance"] == 10 and not state["items"], "abstract_transaction", vector["id"] + " consumed source blocks new ID")
        else:
            # Fork from real post-damage/pre-manual-transaction state, not old durable HP40.
            candidate = copy.deepcopy(state)
            purchase_reference(candidate, "OP-CANCELLED", request)
            candidate = copy.deepcopy(state)
            result = "rebuild_and_publish_mandatory_remainder"
            check(candidate["HP"] == vector["expected_HP"] and candidate["balance"] == vector["expected_balance"] and candidate["shards"] == vector["expected_account_shards"], "abstract_transaction", vector["id"] + " no damage/reward rollback")
        check(result == vector["expected"], "abstract_transaction", vector["id"] + " result")
        abstract_results.append({"id": vector["id"], "result": result, "scope": "abstract_not_runtime"})

    for group in ["historical_design_sha256", "observed_existing_code_and_manifest_sha256"]:
        for rel, digest in index[group].items():
            path = ROOT/rel
            check(path.is_file() and sha(path) == digest, "preservation", rel)
    observed_code = {rel for rel in index["observed_existing_code_and_manifest_sha256"] if rel.startswith('UnrealGame/Source/')}
    current_code = {p.relative_to(ROOT).as_posix() for p in (ROOT/'UnrealGame/Source').rglob('*') if p.is_file() and p.suffix in {'.cpp','.h','.cs'}}
    check(current_code == observed_code, "preservation", "engine Source file inventory unchanged")
    for ref in [index["overview"]] + index["reading_order"]:
        check((HERE/ref).is_file(), "navigation", ref)
    for path in [ROOT/'存档数据与后续合作边界设计.md'] + list(HERE.glob("*.md")):
        for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8-sig")):
            if not re.match(r"(?:https?:|#)", link):
                name = link.split("#")[0].strip("<>")
                if name and not name.endswith("validation-report.json"):
                    check((path.parent/name).is_file(), "navigation", path.name + " -> " + link)
    ledger = (ROOT/'项目需求台账.md').read_text(encoding='utf-8-sig')
    events = re.findall(r"^\| EV-(\d{3}) \|", ledger, re.M)
    check(events == [f"{n:03d}" for n in range(1, 32)], "bookkeeping", "EV001..031 continuous")
    row = next(line for line in ledger.splitlines() if line.startswith('| EV-031 |'))
    check('“继续”' in row and '2026-10-14' in row and '不新增独立REQ' in row, "bookkeeping", "exact user event")
    check('先追加 `EV-032`' in ledger and '下一事件EV-032' in ledger, "bookkeeping", "next event")
    reqs = re.findall(r"^\| REQ-(\d{3}) \|", ledger, re.M)
    check(reqs == [f"{n:03d}" for n in range(1, 18)], "bookkeeping", "REQ001..017 no invented new requirement")
    for name in ['README.md','AGENTS.md','整体设计清单与推进顺序.md']:
        body = (ROOT/name).read_text(encoding='utf-8-sig')
        check('EV-031' in body and 'D-14' in body and '存档数据与后续合作边界设计.md' in body, "bookkeeping", name)
    check('v1.13' in (ROOT/'整体设计清单与推进顺序.md').read_text(encoding='utf-8-sig'), "bookkeeping", "roadmap version")
    return docs


if __name__ == '__main__':
    docs = {}
    try:
        docs = main()
    except Exception as exc:
        errors.append(f"validator_exception: {type(exc).__name__}: {exc}")
    paths = [p for p in HERE.iterdir() if p.suffix in {'.json','.md','.py'} and p.name != 'validation-report.json'] + [ROOT/'存档数据与后续合作边界设计.md']
    index = docs.get('design-index', read(HERE/'design-index.json'))
    report = {
        'module':'D-13','design_date':'2026-10-14','source_event':'EV-031',
        'status':'static_and_abstract_design_checks_passed' if not errors else 'needs_correction',
        'checks':sum(checks.values()),'check_groups':dict(checks),'errors':errors,
        'runtime_implemented':False,'runtime_tested_this_turn':False,'disk_crash_or_power_loss_tested':False,
        'future_runtime_cases':28,'future_runtime_cases_executed':0,
        'abstract_reference_results':abstract_results,
        'historical_design_sha256':index['historical_design_sha256'],
        'observed_existing_code_and_manifest_sha256':index['observed_existing_code_and_manifest_sha256'],
        'current_design_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)},
        'limits':['Source pointers, stable IDs and preserved source hashes are static checks.', 'Abstract models operate on supplied booleans and in-memory dictionaries; they do not implement game saving, durable IO or crash recovery.', 'Full state reconstruction, event ordering, performance, storage interruption, migration and cooperation require future implementation and runtime tests.']}
    (HERE/'validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['status','checks','check_groups','errors']},ensure_ascii=False))
    sys.exit(1 if errors else 0)
