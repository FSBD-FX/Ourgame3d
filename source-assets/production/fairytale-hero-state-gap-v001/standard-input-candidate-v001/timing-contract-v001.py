"""Read-only art sampling proposal, never a replacement gameplay kernel.

Inputs must come from an actual public fighter/kernel observation. No source,
UObject, actor position, action admission, health, or resource is mutated here.
"""
from __future__ import annotations
import argparse
import json
import math

DODGE_DURATION = .40
DODGE_DISTANCE = 185.
DODGE_SPEED = 462.5
IFRAME_START = .06
IFRAME_END = .20
HURT_DURATION = .40
DEATH_SETTLED_VISUAL_AGE = .80  # Art proposal; no gameplay deadline exists.


def finite_age(value):
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError("Actual nonnegative finite state age required")
    return value


def sample(observation):
    """Return an art frame from real state facts, without admitting an action.

    Dodge age: GetDodgeState().Time - accepted Records.back().Start.
    Hurt/death age: actual public AnimationTime, with state selection facts.
    Blocked travel is supplied from the actual record, not synthesized.
    """
    state = observation["state"]
    if state == "dodge":
        start = finite_age(observation["record_start_seconds"])
        now = finite_age(observation["kernel_time_seconds"])
        if now < start:
            raise ValueError("Kernel Time must not precede accepted Record.Start")
        age = now - start
        end = start + DODGE_DURATION
        phase = observation["kernel_phase"]
        finish = observation.get("finish", "None")
        finished_at = observation.get("record_finished_at_seconds")
        block = observation.get("block", "None")
        if phase not in ("Idle", "Dodging", "Dead"):
            raise ValueError("Actual DungeonDodge phase required")
        if finish not in ("None", "Completed", "PoiseBreak", "Death"):
            raise ValueError("Actual DungeonDodge finish required")
        if block not in ("None", "Wall", "Body"):
            raise ValueError("Actual DungeonDodge block required")
        if finish == "None" and (finished_at is not None or phase != "Dodging" or now >= end):
            raise ValueError("Unfinished dodge must be active before its actual End")
        if finish != "None":
            finished_at = finite_age(finished_at)
            if finished_at < start or finished_at > now or finished_at > end:
                raise ValueError("Finish must be a real earlier boundary")
            if finish == "Completed" and finished_at != end:
                raise ValueError("Completed means the native .40 End")
            if finish in ("PoiseBreak", "Death") and finished_at >= end:
                raise ValueError("Native interruption precedes End")
            if finish == "PoiseBreak" and start + IFRAME_START <= finished_at < start + IFRAME_END:
                raise ValueError("Protected direct contact cannot be a native poise-break interruption")
            if finish == "Death" and phase != "Dead":
                raise ValueError("Death finish requires native Dead phase")
            if finish != "Death" and phase != "Idle":
                raise ValueError("Completed/poise-break finish requires native Idle phase")
        effective_end = start + IFRAME_END if finished_at is None else min(start + IFRAME_END, finished_at)
        # Match native absolute comparisons. Subtracting Start first can change
        # exact-boundary results at large absolute times through cancellation.
        protected = start + IFRAME_START <= now < effective_end
        active = phase == "Dodging" and finish == "None" and now < end
        travel_at = now if finished_at is None else min(now, finished_at)
        if block == "None":
            travel = DODGE_DISTANCE if travel_at >= end else min(DODGE_DISTANCE, max(0., DODGE_SPEED * (travel_at-start)))
            travel_role = "Native unobstructed scalar travel formula, not a commanded actor position"
        else:
            travel = float(observation["actual_record_travelled_world"])
            if not math.isfinite(travel) or not 0 <= travel <= DODGE_DISTANCE:
                raise ValueError("Actual blocked-record Travelled required")
            travel_role = "Actual native record Travelled; block does not shorten the .40 action"
        return {"state": state, "frame": min(3, int(age * 10)) if active else None,
                "active": active, "direct_contact_protected_at_observation": protected,
                "travel_world": travel, "travel_role": travel_role,
                "facing_does_not_determine_move_vector": True,
                "world_speed_is_not_an_art_easing_curve": True}
    if state == "hurt":
        age = finite_age(observation["age_seconds"])
        if observation.get("bDead") is not False or observation.get("animation_name") != "hurt":
            raise ValueError("Actual living hurt presentation required; HP loss alone is insufficient")
        if age >= HURT_DURATION:
            return {"state": state, "frame": None, "active": False,
                    "boundary": "Actual state transition selects next pose; never loop or hold Hurt"}
        return {"state": state, "frame": min(3, int(age * 10)), "active": True,
                "trigger_fact_required": "Actual accepted direct poise break; generic/enemy routes excluded"}
    if state == "death":
        age = finite_age(observation["age_seconds"])
        if observation.get("bDead") is not True:
            raise ValueError("Actual bDead required")
        return {"state": state, "frame": min(4, int(age * 5)), "active": True,
                "settled_visual_hold": age >= DEATH_SETTLED_VISUAL_AGE,
                "clock": "Actual AnimationTime / AdvanceTerminalPresentation; not frozen SimulationTime",
                "gameplay_deadline_seconds": None}
    raise ValueError("Unknown state")


def hit_presentation(facts):
    """Classify already-resolved player hit facts; never resolve damage/poise."""
    before, after = float(facts["hp_before"]), float(facts["hp_after"])
    if not all(math.isfinite(x) and x >= 0 for x in (before, after)) or after > before:
        raise ValueError("Actual finite resolved HP facts required")
    if facts.get("accepted") is not True or after == before:
        return "No newly proven HP-loss presentation"
    if after == 0:
        return "Death, including lethal DamageOverTime; no new gameplay deadline"
    if facts.get("damage_over_time") is True:
        return "No Hurt/poise/push from this status tick"
    if facts.get("actual_poise_broken") is True:
        return "Hurt .40; combat/weapon action interrupted and native dodge interruption requested"
    return "HitFlash .22; HP loss does not itself authorize Hurt action interruption"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observation-json", help="Actual state observation as a JSON object")
    parser.add_argument("--hit-facts-json", help="Actual resolved hit facts as a JSON object")
    args = parser.parse_args()
    if args.observation_json:
        result = sample(json.loads(args.observation_json))
    elif args.hit_facts_json:
        result = {"classification": hit_presentation(json.loads(args.hit_facts_json))}
    else:
        result = {"schema": "hero-state-art-sampling-proposal-v001", "runtime_implemented": False,
                  "dodge": {"frames": 4, "interval_seconds": .10, "active_end_exclusive": .40,
                            "distance_world": 185., "speed_world_per_second": 462.5,
                            "direct_iframe_start_inclusive": .06, "direct_iframe_end_exclusive": .20,
                            "block_keeps_original_end": True, "cooldown_seconds": 1.20},
                  "hurt": {"frames": 4, "interval_seconds": .10, "duration_seconds": .40,
                           "ordinary_damage_is_not_hurt_interrupt": True},
                  "death": {"frames": 5, "key_ages_seconds": [0, .2, .4, .6, .8],
                            "last_frame_holds_until_state_changes": True,
                            "gameplay_deadline_seconds": None}}
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
