<#
.SYNOPSIS
KUIO — Disinstaller del Servizio Windows

.DESCRIPTION
Rimuove il Servizio Windows KUIO. NON cancella i dati utente in %LOCALAPPDATA%\KUIO\
(per preservare config e conversazioni in caso di reinstall).
#>

$ErrorActionPreference = "Stop"
$ServiceName = "KUIO"
$InstallDir  = "${env:ProgramFiles}\KUIO"
$NssmExe     = "$InstallDir\nssm.exe"

function Test-Admin {
    $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Admin)) {
    Write-Host "ERRORE: Esegui come Amministratore." -ForegroundColor Red
    exit 1
}

$svc = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if (-not $svc) {
    Write-Host "Servizio $ServiceName non installato. Nessuna azione richiesta." -ForegroundColor Yellow
    exit 0
}

Write-Host "Stop servizio $ServiceName..."
if (Test-Path $NssmExe) {
    & $NssmExe stop $ServiceName confirm 2>&1 | Out-Null
    Start-Sleep -Seconds 2
    & $NssmExe remove $ServiceName confirm 2>&1 | Out-Null
} else {
    Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
    sc.exe delete $ServiceName | Out-Null
}

if (Test-Path $InstallDir) {
    Write-Host "Rimuovo binari da $InstallDir..."
    Remove-Item -Path $InstallDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "KUIO disinstallato." -ForegroundColor Green
Write-Host "I tuoi dati restano in ${env:LOCALAPPDATA}\KUIO\ (cancellali a mano se vuoi)." -ForegroundColor Yellow
exit 0
