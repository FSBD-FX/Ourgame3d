@echo off
pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\scripts\launch-fairytale-equipment-bound-v006.ps1" -Snapshot "source-assets/production/backups/v125-p1-157G" -ProofContract "source-assets/production/checkpoint-v125-root-input-v001/manual-proof-contract-v125-v001.json"
