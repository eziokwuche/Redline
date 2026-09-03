$ErrorActionPreference = 'Stop'

Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique |
    ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }

if (Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue) {
    throw 'Port 5173 is still in use.'
}

Push-Location "$PSScriptRoot\frontend"
try {
    npm run dev
} finally {
    Pop-Location
}
