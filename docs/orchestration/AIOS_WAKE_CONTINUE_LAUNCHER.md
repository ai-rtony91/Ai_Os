# AIOS Wake Continue Launcher

Use this wrapper from the repo root:

```powershell
.\automation\orchestration\Start-AiOsWakeContinue.ps1
```

Default behavior runs:

```powershell
python .\automation\orchestration\aios_wake_continue.py --goal forex-paper-bot --apply --max-cycles 3 --max-repairs 1 --write-resume-state --write-control-plane-status --emit-continuation-controller
```

To override the defaults, pass explicit arguments:

```powershell
.\automation\orchestration\Start-AiOsWakeContinue.ps1 --goal forex-paper-bot --apply --max-cycles 1 --max-repairs 0
```

`wake_continue` is a Python script. It is not a native PowerShell command unless a wrapper script, function, or alias exists. This wrapper provides the repo-supported PowerShell command path.
