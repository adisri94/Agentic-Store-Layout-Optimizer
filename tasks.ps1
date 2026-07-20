<#
.SYNOPSIS
    Windows-native task runner for the Store Layout Optimizer — a PowerShell
    equivalent of the documented Makefile targets (see architecture.md §16).

.DESCRIPTION
    Mirrors the six canonical commands so Windows users need no `make` install
    (decision_log.md D-031). Verb names match the Makefile contract exactly.

    Usage:
        ./tasks.ps1 setup     # Install dependencies via uv
        ./tasks.ps1 seed      # Generate synthetic data into data/samples/
        ./tasks.ps1 demo      # Start FastAPI (8000) + Streamlit (8501)
        ./tasks.ps1 test      # Run ruff + pytest
        ./tasks.ps1 reset     # Wipe SQLite DB, FAISS index, audit log (keep Parquet)
        ./tasks.ps1 clean     # Full clean incl. Parquet (forces regeneration)
        ./tasks.ps1 help      # Show this list
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('setup', 'seed', 'demo', 'test', 'reset', 'clean', 'help')]
    [string]$Task = 'help'
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = $PSScriptRoot
$DataDir = Join-Path $ProjectRoot 'data'

# Resolve how to invoke uv: prefer the `uv` binary on PATH, else fall back to
# `python -m uv` (e.g. when uv was pip-installed --user and Scripts isn't on PATH).
$script:UvExe = $null
$script:UvArgs = @()
function Resolve-Uv {
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        $script:UvExe = 'uv'; $script:UvArgs = @(); return
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        & python -c "import uv" 2>$null
        if ($LASTEXITCODE -eq 0) {
            $script:UvExe = 'python'; $script:UvArgs = @('-m', 'uv'); return
        }
    }
    throw "uv is not available. Install it with:  python -m pip install --user uv  (see README.md / decision_log.md D-031)."
}

function Invoke-Uv {
    if (-not $script:UvExe) { Resolve-Uv }
    & $script:UvExe @script:UvArgs @args
}

function Invoke-Setup {
    Resolve-Uv
    Write-Host "==> Installing dependencies via uv..." -ForegroundColor Cyan
    Invoke-Uv sync
}

function Invoke-Seed {
    Resolve-Uv
    Write-Host "==> Generating synthetic data into data/samples/..." -ForegroundColor Cyan
    Invoke-Uv run python -m data.seed
}

function Invoke-Demo {
    Resolve-Uv
    Write-Host "==> Starting FastAPI on :8000 (background) + Streamlit on :8501..." -ForegroundColor Cyan
    $api = Start-Process -PassThru -NoNewWindow -FilePath $script:UvExe `
        -ArgumentList ($script:UvArgs + @('run', 'uvicorn', 'api.main:app', '--host', '127.0.0.1', '--port', '8000'))
    try {
        Invoke-Uv run streamlit run ui/streamlit_app.py
    }
    finally {
        if ($api -and -not $api.HasExited) {
            Write-Host "==> Stopping FastAPI (PID $($api.Id))..." -ForegroundColor Cyan
            Stop-Process -Id $api.Id -Force -ErrorAction SilentlyContinue
        }
    }
}

function Invoke-Test {
    Resolve-Uv
    Write-Host "==> Linting with ruff..." -ForegroundColor Cyan
    Invoke-Uv run ruff check .
    Write-Host "==> Running pytest..." -ForegroundColor Cyan
    Invoke-Uv run pytest tests/ -v
}

function Invoke-Reset {
    Write-Host "==> Wiping SQLite DB, FAISS index, and audit log (keeping Parquet)..." -ForegroundColor Cyan
    Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path $DataDir 'app.db')
    Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path $DataDir 'audit.jsonl')
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $DataDir 'faiss_index')
    Write-Host "    Done. Run './tasks.ps1 seed' if you need to regenerate operational state." -ForegroundColor DarkGray
}

function Invoke-Clean {
    Invoke-Reset
    Write-Host "==> Removing generated Parquet files (forces regeneration on next seed)..." -ForegroundColor Cyan
    Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path $DataDir 'samples/*.parquet')
    Write-Host "    Done. Run './tasks.ps1 seed' to regenerate all synthetic data." -ForegroundColor DarkGray
}

function Show-Help {
    Write-Host ""
    Write-Host "Store Layout Optimizer - task runner (PowerShell equivalent of the Makefile)" -ForegroundColor Green
    Write-Host ""
    Write-Host "  ./tasks.ps1 setup    Install dependencies via uv"
    Write-Host "  ./tasks.ps1 seed     Generate synthetic data into data/samples/"
    Write-Host "  ./tasks.ps1 demo     Start FastAPI (8000) + Streamlit (8501)"
    Write-Host "  ./tasks.ps1 test     Run ruff + pytest"
    Write-Host "  ./tasks.ps1 reset    Wipe SQLite DB, FAISS index, audit log (keep Parquet)"
    Write-Host "  ./tasks.ps1 clean    Full clean incl. Parquet (forces regeneration)"
    Write-Host ""
}

switch ($Task) {
    'setup' { Invoke-Setup }
    'seed'  { Invoke-Seed }
    'demo'  { Invoke-Demo }
    'test'  { Invoke-Test }
    'reset' { Invoke-Reset }
    'clean' { Invoke-Clean }
    default { Show-Help }
}
