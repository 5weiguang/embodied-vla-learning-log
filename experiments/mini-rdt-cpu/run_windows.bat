@echo off
setlocal
if not exist .venv\Scripts\python.exe (
  echo Please create .venv first following README.md
  exit /b 1
)
.venv\Scripts\python.exe mini_rdt.py --mlp-steps 900 --diff-steps 2400
pause
