@echo off
chcp 65001 >nul
pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\scripts\launch-leather-combo-trial-v001.ps1" -Snapshot "source-assets/production/backups/v126-combo-161G" -Archive "过程图稿与视频/2026-10-17_软皮轻甲左右三段连击试装_v001"
