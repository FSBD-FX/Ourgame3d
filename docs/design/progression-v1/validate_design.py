"""D09 design consistency and reference ledger checks. No UE/runtime test."""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import math
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
checks = Counter()
errors = []


def check(ok, group, message):
    checks[group] += 1
    if not ok:
        errors.append(f"{group}: {message}")


def read(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def close(a, b):
    return math.isclose(a, b, abs_tol=1e-10)


def acyclic(graph):
    done, visiting = set(), set()
    def visit(n):
        if n in visiting or n not in graph:
            return False
        if n in done:
            return True
        visiting.add(n)
        if not all(visit(x) for x in graph[n]):
            return False
        visiting.remove(n)
        done.add(n)
        return True
    return all(visit(n) for n in graph)


class Ledger:
    """Independent in-memory reference, not production transaction/save code."""
    def __init__(self, earned, talents, unlocks):
        self.earned = self.wallet = earned
        self.talents, self.unlocks = talents, unlocks
        self.ranks, self.researched = {}, set()
        self.receipts, self.research_receipts, self.journal = [], [], {}
        self.version, self.state, self.active_run_id = 0, "HUB_IDLE", None
        self.selected_sample, self.sample_flags, self.run_snapshot = None, set(), None

    def transaction(self, op, operation_id, id=None, preview_version=None):
        request = (op, id)
        if operation_id in self.journal:
            old_request, result = self.journal[operation_id]
            if old_request != request:
                raise ValueError("operation_payload_conflict")
            return result
        if self.state != "HUB_IDLE" or self.active_run_id is not None:
            raise ValueError("unfinished_run")
        if preview_version is not None and preview_version != self.version:
            raise ValueError("stale_version")
        refund = 0
        if op == "buy_talent":
            n = self.talents[id]
            r = self.ranks.get(id, 0)
            if r >= n["max_rank"]:
                raise ValueError("max_rank")
            for p in n["prerequisites"]:
                if self.ranks.get(p["talent_id"], 0) < p["minimum_owned_rank"]:
                    raise ValueError("prerequisite")
            price = n["cost_by_next_rank"][r]
            if self.wallet < price:
                raise ValueError("insufficient")
            self.wallet -= price
            self.ranks[id] = r + 1
            self.receipts.append({"op": operation_id, "id": id, "rank": r+1, "paid": price, "refunded": None})
        elif op == "buy_research":
            n = self.unlocks[id]
            if id in self.researched:
                raise ValueError("already_owned")
            if not set(n["prerequisite_unlock_ids"]) <= self.researched:
                raise ValueError("prerequisite")
            if self.wallet < n["cost_shards"]:
                raise ValueError("insufficient")
            self.wallet -= n["cost_shards"]
            self.researched.add(id)
            self.research_receipts.append(n["cost_shards"])
        elif op == "reset":
            active = [r for r in self.receipts if r["refunded"] is None]
            required = Counter((id, rank) for id,n in self.ranks.items() for rank in range(1,n+1))
            actual = Counter((r["id"], r["rank"]) for r in active)
            if actual != required or any(r["paid"] < 0 for r in active):
                raise ValueError("receipt_coverage")
            refund = sum(r["paid"] for r in active)
            self.wallet += refund
            self.ranks.clear()
            for r in active:
                r["refunded"] = operation_id
        elif op == "create_new_run":
            if self.selected_sample is not None and (self.selected_sample not in self.researched or self.selected_sample in self.sample_flags):
                raise ValueError("invalid_pending_sample")
            self.run_snapshot = {"talent_ranks":deepcopy(self.ranks),"selected_sample_unlock_id":self.selected_sample,"sample_purchase_flags_snapshot":sorted(self.sample_flags)}
            self.selected_sample = None
            self.state = "RUN_STARTING"
            self.active_run_id = operation_id
        else:
            raise ValueError("unsupported_operation")
        self.version += 1
        result = {"wallet": self.wallet, "refund": refund, "version": self.version}
        self.journal[operation_id] = (request, result)
        return result

    def conserved(self):
        return self.earned == self.wallet + sum(r["paid"] for r in self.receipts if r["refunded"] is None) + sum(self.research_receipts)


def rejection(ledger, kwargs, expected):
    before = deepcopy(ledger.__dict__)
    try:
        ledger.transaction(**kwargs)
        check(False, "ledger", f"expected rejection {expected}")
    except ValueError as e:
        check(str(e) == expected, "ledger", f"rejection reason {expected}")
    check(ledger.__dict__ == before, "ledger", f"no mutation on {expected}")


def main():
    t = read(HERE / "talents.json")
    u = read(HERE / "unlocks.json")
    hub = read(HERE / "hub-rules.json")
    cases = read(HERE / "progression-cases.json")
    index = read(HERE / "design-index.json")
    rewards = read(ROOT / "docs/design/economy-v1/reward-sources.json")
    items = {x["id"]: x for x in read(ROOT / "docs/design/items-v1/items.json")["items"]}
    talents = {x["id"]: x for x in t["nodes"]}
    unlocks = {x["id"]: x for x in u["unlocks"]}
    sources = {x["id"]: x for x in rewards["sources"]}
    for obj in [t, u, hub, cases, index]:
        check(obj["module"] == "D-09" and obj["source_event"] == "EV-027", "metadata", "event/module")
        check(obj["runtime_implemented"] is False and obj["status"] == "design_only", "metadata", "design only")
    check(len(talents) == len(t["nodes"]) == 9, "talents", "unique9")
    check(sum(n["max_rank"] for n in talents.values()) == 27, "talents", "27 ranks")
    check(sum(sum(n["cost_by_next_rank"]) for n in talents.values()) == 280, "talents", "280 costs")
    check(len(unlocks) == len(u["unlocks"]) == 14, "unlocks", "unique14")
    check(sum(x["cost_shards"] for x in unlocks.values()) == 130, "unlocks", "cost130")
    check(hub["scope"]["all_catalog_cost_shards"] == 280+130, "unlocks", "total410")
    meta = {i for i,x in items.items() if x["unlock"] != "base_pool"}
    check({x["item_id"] for x in unlocks.values()} == meta and len(items)-len(meta) == 22, "unlocks", "exact D03 meta14/base22")
    graph = {id: x["prerequisite_unlock_ids"] for id,x in unlocks.items()}
    check(acyclic(graph), "unlocks", "acyclic research")
    check(sum(not x for x in graph.values()) == 10 and sum(map(len,graph.values())) == 4, "unlocks", "10 roots4 edges")
    price_list = [33,19,16,16,16,18,18,16,18,40,40,40,18,27]
    expected_ids = ["REC-002","REC-006","BOO-005","BOO-006","THR-004","THR-005","THR-006","TRP-003","TRP-004","PAS-005","PAS-006","PAS-008","FUN-003","FUN-005"]
    for suffix,price in zip(expected_ids,price_list):
        x = unlocks["UNL-"+suffix]
        check(x["item_id"] == "ITM-"+suffix and x["name"] == items[x["item_id"]]["name"], "unlocks", suffix+" ID/name")
        check(x["cost_shards"] > 0 and not x["prerequisite_talent_ids"] and not x["required_Boss_kills_or_unseen_item_pickups"], "unlocks", suffix+" no cyclic external gate")
        check(x["refund_or_disable_supported"] is False, "unlocks", suffix+" permanent")
        category = x["category"]
        expected_pools = {"POOL-RELIC"} if category=="PAS" else {"POOL-BONUS-ITEM"}
        if category in ["REC","THR","TRP"]:
            expected_pools.add("POOL-COMMON-SUPPLY")
        check({s["pool_id"] for s in x["natural_sources"]} == expected_pools, "sources", suffix+" routes")
        for s in x["natural_sources"]:
            pool_id = s["pool_id"]
            check(set(s["source_ids"]) == {id for id,z in sources.items() if z.get("pool_id")==pool_id}, "sources", suffix+" source list exact")
            check(set(s["node_ids"]) == {id for sid in s["source_ids"] for id in sources[sid]["node_ids"]}, "sources", suffix+" node refs")
            check(x["item_id"] in json.dumps(rewards["pools"][pool_id]), "sources", suffix+" pool membership")
        sample = x["research_sample"]
        check(sample["price_gold"] == price and sample["quantity"]==1 and sample["account_successful_purchase_limit"]==1, "samples", suffix+" finite paid quote")
        check(sample["item_id"] == x["item_id"] and not sample["random_content_grade_enchant_or_stats"], "samples", suffix+" exact existing item")
        check(sample["delivery_action_s"] == (.5 if category=="PAS" else .25), "samples", suffix+" D04 action")
    check(math.ceil(55/30*18)==33 and math.ceil(20/30*18+25/45*12)==19, "samples", "potion price rationale")
    sample = u["research_sample_order"]
    check(sample["per_account_per_ContentUnlockID_successful_purchase_limit"]==1 and sample["per_run_selected_unlock_count_max"]==1, "samples", "account/run caps")
    check(sample["offer_generation"]["first_matching_only"] and not sample["stock"]["restock_refresh_return_move_or_reprice"], "samples", "single stable quote")
    check(not sample["payment"]["function_discounts_waivers_or_meta_shards_allowed"] and sample["live_account_flags_revalidated_at_purchase"], "samples", "cash and live claim")
    check(hub["lifecycle"]["mutations_allowed_only_in"] == "HUB_IDLE" and hub["lifecycle"]["requires_active_run_id_null"], "lifecycle", "unfinished runs block")
    check(not hub["talent_reset"]["uses_current_catalog_prices"] and not hub["talent_reset"]["research_refunded_or_disabled"], "lifecycle", "receipt refund / research preserved")
    check(hub["new_run"]["immutable_snapshot"] and not hub["new_run"]["continue_repeats_initialization"], "lifecycle", "new vs continue")
    starter = hub["new_run"]["starter"]
    check(starter["weapon_id"]=="WPN-SWD-001" and starter["gold"]==20 and starter["basic_upgrade_grade"]==0 and starter["enchantment"] is None, "lifecycle", "D02 starter D08 gold")
    results = []
    for seq in cases["reference_ledger_sequences"]:
        ledger = Ledger(seq["initial_earned_shards"], talents, unlocks)
        for step in seq["steps"]:
            result = ledger.transaction(**{k:step[k] for k in ["op","operation_id","id"] if k in step})
            check(ledger.wallet == step["expected_wallet"], "ledger", seq["id"]+step["operation_id"]+" wallet")
            if "expected_refund" in step:
                check(result["refund"]==step["expected_refund"], "ledger", seq["id"]+" refund")
            check(ledger.conserved(), "ledger", seq["id"]+" conservation")
        check(ledger.researched==set(seq["expected_research"]) and ledger.ranks==seq["expected_talent_ranks"], "ledger", "final ownership")
        results.append({"id":seq["id"],"wallet":ledger.wallet,"researched":sorted(ledger.researched),"ranks":ledger.ranks})
    empty = Ledger(0,talents,unlocks)
    rejection(empty, {"op":"buy_talent","operation_id":"x","id":"TAL-VIT"}, "insufficient")
    ledger = Ledger(1000,talents,unlocks)
    rejection(ledger, {"op":"buy_talent","operation_id":"x","id":"TAL-MED"}, "prerequisite")
    rejection(ledger, {"op":"buy_research","operation_id":"x","id":"UNL-REC-006"}, "prerequisite")
    for i in range(3):
        ledger.transaction("buy_talent",f"v{i}","TAL-VIT")
    rejection(ledger, {"op":"buy_talent","operation_id":"v3","id":"TAL-VIT"}, "max_rank")
    rejection(ledger, {"op":"buy_research","operation_id":"v0","id":"UNL-REC-002"}, "operation_payload_conflict")
    rejection(ledger, {"op":"reset","operation_id":"stale","preview_version":0}, "stale_version")
    for state in ["RUN_STARTING","RUN_ACTIVE","RUN_SUSPENDED","RUN_ENDING","RECOVERY_REQUIRED"]:
        ledger.state=state
        for op,id in [("buy_talent","TAL-ATK"),("buy_research","UNL-REC-002"),("reset",None),("create_new_run",None)]:
            rejection(ledger, {"op":op,"operation_id":"blocked","id":id}, "unfinished_run")
    ledger.state="HUB_IDLE"
    ledger.active_run_id="unfinished-despite-menu"
    rejection(ledger, {"op":"reset","operation_id":"not-ui-only"}, "unfinished_run")
    ledger.active_run_id=None
    lost=deepcopy(ledger)
    lost.receipts.pop()
    rejection(lost, {"op":"reset","operation_id":"missing"}, "receipt_coverage")
    migrated=Ledger(12,talents,unlocks)
    migrated.wallet=5; migrated.ranks={"TAL-VIT":2}
    migrated.receipts=[{"op":"old1","id":"TAL-VIT","rank":1,"paid":2,"refunded":None},{"op":"old2","id":"TAL-VIT","rank":2,"paid":5,"refunded":None}]
    check(migrated.transaction("reset","oldreset")["refund"]==7 and migrated.wallet==12 and migrated.conserved(), "ledger", "original price after price change")
    race=Ledger(10,talents,unlocks)
    race.transaction("create_new_run","new-run",preview_version=0)
    rejection(race,{"op":"buy_talent","operation_id":"race","id":"TAL-VIT","preview_version":0},"unfinished_run")
    pending=Ledger(20,talents,unlocks)
    pending.selected_sample="UNL-REC-002"
    rejection(pending,{"op":"create_new_run","operation_id":"invalid-selection"},"invalid_pending_sample")
    pending.transaction("buy_research","research-pending","UNL-REC-002")
    first_result=pending.transaction("create_new_run","sample-run1")
    snapshot=deepcopy(pending.run_snapshot)
    check(pending.selected_sample is None and snapshot["selected_sample_unlock_id"]=="UNL-REC-002", "ledger", "transfer pending to frozen run")
    check(pending.transaction("create_new_run","sample-run1")==first_result and pending.run_snapshot==snapshot, "ledger", "retry start preserves original snapshot")
    # Simulate a successful sample claim and completed ending; no claim of storage recovery testing.
    pending.sample_flags.add("UNL-REC-002")
    pending.state="HUB_IDLE"; pending.active_run_id=None
    pending.transaction("create_new_run","sample-run2")
    check(pending.run_snapshot["selected_sample_unlock_id"] is None and "UNL-REC-002" in pending.sample_flags and snapshot["selected_sample_unlock_id"]=="UNL-REC-002", "ledger", "next run no stale selection; old snapshot intact")
    pending.state="HUB_IDLE"; pending.active_run_id=None; pending.selected_sample="UNL-REC-002"
    rejection(pending,{"op":"create_new_run","operation_id":"spent-selection"},"invalid_pending_sample")
    b=rewards["currency_budget"]
    check(b["mainline_N05_ground_fragments"][0]==2 and b["mainline_boss_automatic_fragments"][0]==4, "income", "first region base6")
    for e in cases["income_cases"]:
        if "purchases" in e:
            cost=0
            for p in e["purchases"]:
                if p.startswith("TAL-"):
                    id,rank=p.split(":"); cost+=talents[id]["cost_by_next_rank"][int(rank)-1]
                else:
                    cost+=unlocks[p]["cost_shards"]
            check(cost==e["cost"] and e["banked"]-cost==e["remaining"],"income",e["id"])
        if "repeat_count" in e:
            check(e["first_income"]+e["repeat_count"]*e["repeat_income"]==e["banked"] and e["banked"]-280-130==e["remaining"],"income",e["id"])
    probability_results=[]
    bonus=rewards["pools"]["POOL-BONUS-ITEM"]
    for e in cases["limited_probability_cases"]:
        cat=e["item_id"].split("-")[1]
        group=next(g for g in bonus["purpose_groups"][cat] if e["item_id"] in g["item_ids"])
        check(close(group["weight"]/100,e["purpose_share"]) and close(bonus["category_weights"][cat]/100,e["category_share"]), "probability",e["id"]+" source weights")
        p=e["source_presence"]*e["category_share"]*e["purpose_share"]/e["eligible_IDs_in_purpose"]
        calc=1-(1-p)**e["rooms"]
        check(close(p,e["per_room"]) and close(calc,e["at_least_once"]),"probability",e["id"]+" arithmetic")
        probability_results.append({"id":e["id"],"per_room":p,"at_least_once":calc})
    historical=index["historical_design_sha256"]
    for path,expected in historical.items():
        check((ROOT/path).exists() and digest(ROOT/path)==expected, "preservation", path)
    for p in [ROOT/"局内成长与局外天赋解锁设计.md",*HERE.glob("*.md"),ROOT/"README.md",ROOT/"整体设计清单与推进顺序.md",ROOT/"项目需求台账.md"]:
        for link in re.findall(r"\]\(([^\s)]+)\)",p.read_text(encoding="utf-8-sig")):
            if "://" in link or link.startswith("#"):
                continue
            target=(p.parent/link.split("#")[0]).resolve()
            # Report generated at end of this invocation; verify it is the sole deferred file.
            check(target.exists() or target==HERE/"validation-report.json", "links", str(p.name)+":"+link)
    from validate_talents import validate
    talent_result=validate()
    checks["talent_formula_subcheck"]+=talent_result["checks"]
    errors.extend(talent_result["errors"])
    current_files=[ROOT/"局内成长与局外天赋解锁设计.md", *sorted(p for p in HERE.iterdir() if p.suffix in [".json",".md",".py"] and p.name!="validation-report.json")]
    report={
        "design_date":"2026-10-14", "source_event":"EV-027", "module":"D-09", "status":"design_only", "runtime_implemented":False,
        "scope":"static references, dependencies, arithmetic, original paid receipt reference ledger; does not execute UE or save storage",
        "checks":sum(checks.values()),"checks_by_group":dict(checks),"errors":errors,
        "counts":{"talents":len(talents),"talent_ranks":27,"research":len(unlocks),"talent_cost":280,"research_cost":130,"all_cost":410,"boundary_cases_documented_not_all_executed":len(cases["boundary_cases"]),"talent_examples_checked":talent_result["examples_checked"]},
        "ledger_results":results,"probability_results":probability_results,
        "cross_review_resolved":["unfinished and suspended runs lock account mutations", "refund original active receipts once, missing receipts no guessed refund", "research prerequisites independent of refundable talents", "rare probability examples limited to named sources", "no income does not imply no prior wallet", "sample pending selection revalidated then atomically cleared at new run", "TAL-EX005 replaces unsupported extra20 with real BOO001 source15"],
        "historical_design_sha256":historical,
        "current_design_sha256":{p.relative_to(ROOT).as_posix():digest(p) for p in current_files},
        "limitations":["boundary narratives are future acceptance cases, not all executable tests", "sample atomicity and persistence only specified, not implemented", "no measured drops, playtime, zero-talent clear or combat balance", "no new game code/assets/paid generation"],
        "reproduce":"python -X utf8 docs/design/progression-v1/validate_design.py"
    }
    (HERE/"validation-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"checks":report["checks"],"errors":errors,"counts":report["counts"]},ensure_ascii=False))
    raise SystemExit(bool(errors))


if __name__=="__main__":
    main()
