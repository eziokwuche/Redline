$ErrorActionPreference = 'Stop'

Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique |
    ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }

if (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue) {
    throw 'Port 8000 is still in use.'
}

& "$PSScriptRoot\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
