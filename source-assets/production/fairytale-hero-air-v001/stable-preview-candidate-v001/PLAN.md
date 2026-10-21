# Stable Editor-game Preview Implementation Plan

> **For agentic workers:** Use the supplied Root task and implement this scoped candidate directly; reviewer reads independently. Do not stage or launch actual UE.

**Goal:** Prepare a physical runtime snapshot copier and a launcher that remains independent of later project source edits.

**Architecture:** One Python copier freezes a conservative runtime list and copies file bytes with exclusive creation. One PowerShell launcher checks only staged runtime and retained compilation/native evidence, plus the fixed installed engine. Root performs actual staging and supplies truthful LIMITED_WIP approval after staged native verification.

**Tech Stack:** Python standard library, PowerShell 7, installed UE5.5 Editor -game.

**Spec:** Parent Root task, 2026-10-19, candidate-only ownership.

## Global Constraints

- Only this new candidate directory is writable by this worker; no actual stage, Source, Content, tools, E or UE work.
- Preserve all v013 ordinary flags plus Air/Light/Guard, no proof or automatic input in manual launcher.
- Copy runtime1778 files including Editor.target; no Source/Intermediate/Saved/PDB/exp, no links.
- Stable launch checks physical copies and retained fixed CM52f evidence, never live development Source.
- Root approval templates remain false; full playback/listening/final acceptance remain false and joins open.

## Review Focus

- Source changed before/during copy: reject, retain partial files and failure report.
- Existing destination or linked path: reject without overwrite or cleanup.
- Extra or altered immutable staged runtime member, including hidden files: reject.
- Engine BuildId/module or fixed binary mismatch: reject.
- Missing actual staged proof or non-template Root approval: reject before UE.

## Tasks

- [x] Read actual runtime inventory and freeze manifest with existing CM/build/full203 evidence pins.
- [x] Implement exclusive physical copy with source/target two-pass SHA checks and exact immutable membership.
- [x] Implement staged-only LIMITED_WIP launcher and false Root templates.
- [x] Run small host copy positive/negative cases and PowerShell syntax/false-template rejection; self-review and freeze candidate; Root will independently review before actual staging.
