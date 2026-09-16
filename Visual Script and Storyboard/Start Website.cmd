@echo off
start "Sin Star I Website" /b pwsh -NoProfile -WindowStyle Hidden -File "%~dp0production\serve.ps1"
