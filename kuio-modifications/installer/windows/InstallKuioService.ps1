<#
.SYNOPSIS
KUIO — Installer del Servizio Windows (Sprint 4)

.DESCRIPTION
Registra KUIO come Servizio Windows invisibile, configurato per partire al boot
e auto-riavviarsi al crash. Da eseguire DOPO InstallKuio.ps1 (check sistema).

REQUISITI:
- Admin (UAC richiesto)
- C:\Program Files\KUIO\kuio.exe presente (scaricato da R2)
- C:\Program Files\KUIO\nssm.exe presente

ARCHITETTURA: vedi docs/servizio-windows-architettura.md
#>

$ErrorActionPreference = "Stop"

# === Costanti ===
$ServiceName     = "KUIO"
$ServiceDisplay  = "KUIO Personal Assistant"
$ServiceDescr    = "Il tuo segretario personale digitale (https://kuio.ai)"
$InstallDir      = "${env:ProgramFiles}\KUIO"
$KuioExe         = "$InstallDir\kuio.exe"
$NssmExe         = "$InstallDir\nssm.exe"
$DataDir         = "${env:LOCALAPPDATA}\KUIO"
$WorkspaceDir    = "$DataDir\workspace"
$LogsDir         = "$DataDir\logs"
$StdoutLog       = "$LogsDir\kuio-stdout.log"
$StderrLog       = "$LogsDir\kuio-stderr.log"
$InstallLog      = "$LogsDir\install-service.log"

# === Server di distribuzione (Cloudflare R2) ===
# Tutti i binari KUIO sono distribuiti via custom domain del bucket R2 kuio-installer.
# NON dipendiamo dal PC del cliente per nessun file.
$DistroBase      = "https://installer.kuio.ai"
$KuioExeUrl      = "$DistroBase/kuio.exe"
$KuioExeSha256   = ""  # SHA-256 da popolare dal manifest pubblicato su R2 (post-build)
$NssmExeUrl      = "$DistroBase/nssm.exe"
$NssmExeSha256   = "f689ee9af94b00e9e3f0bb072b34caaf207f32dcb4f5782fc9ca351df9a06c97"

# === Logging ===
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp] [$Level] $Message"
    Write-Host $line
    if (Test-Path $LogsDir) { Add-Content -Path $InstallLog -Value $line -Encoding UTF8 }
}

# === Check admin ===
function Test-Admin {
    $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Admin)) {
    Write-Host "ERRORE: Lo script deve essere eseguito come Amministratore." -ForegroundColor Red
    Write-Host "Riavvia con: tasto destro -> Esegui come amministratore" -ForegroundColor Yellow
    exit 1
}

# === Crea directory dati ===
foreach ($dir in @($DataDir, $WorkspaceDir, $LogsDir, "$DataDir\config", "$DataDir\config\secrets")) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Log "Creata cartella: $dir"
    }
}

# Lock-down permessi su secrets (solo utente corrente)
$secretsAcl = Get-Acl "$DataDir\config\secrets"
$secretsAcl.SetAccessRuleProtection($true, $false)
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    [System.Security.Principal.WindowsIdentity]::GetCurrent().Name,
    "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$secretsAcl.SetAccessRule($rule)
Set-Acl "$DataDir\config\secrets" $secretsAcl
Write-Log "Permessi secrets ristretti all utente corrente"

# === Crea cartella InstallDir (Program Files\KUIO) se manca ===
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    Write-Log "Creata cartella binari: $InstallDir"
}

# === Funzione: download da R2 con verifica SHA-256 ===
function Get-FileFromR2 {
    param(
        [Parameter(Mandatory=$true)][string]$Url,
        [Parameter(Mandatory=$true)][string]$Destination,
        [string]$ExpectedSha256 = ""
    )
    Write-Log "Scarico $Url ..."
    try {
        $ProgressPreference = "SilentlyContinue"  # velocizza Invoke-WebRequest
        Invoke-WebRequest -Uri $Url -OutFile $Destination -UseBasicParsing -ErrorAction Stop
    } catch {
        Write-Log "Download fallito: $_" "ERROR"
        return $false
    }
    if (-not (Test-Path $Destination)) {
        Write-Log "Download completato ma file mancante: $Destination" "ERROR"
        return $false
    }
    $size = (Get-Item $Destination).Length
    Write-Log "Scaricato $($size) byte in $Destination" "OK"
    if ($ExpectedSha256) {
        $actualSha = (Get-FileHash $Destination -Algorithm SHA256).Hash.ToLower()
        if ($actualSha -ne $ExpectedSha256.ToLower()) {
            Write-Log "SHA-256 non corrispondente! atteso=$ExpectedSha256 ottenuto=$actualSha" "ERROR"
            Remove-Item $Destination -Force -ErrorAction SilentlyContinue
            return $false
        }
        Write-Log "SHA-256 verificato" "OK"
    } else {
        Write-Log "SHA-256 atteso non configurato — skip verifica (rischio integrita)" "WARN"
    }
    return $true
}

# === Scarica binari da R2 (kuio.exe + nssm.exe) ===
if (-not (Test-Path $NssmExe)) {
    if (-not (Get-FileFromR2 -Url $NssmExeUrl -Destination $NssmExe -ExpectedSha256 $NssmExeSha256)) {
        Write-Log "Impossibile ottenere nssm.exe da $NssmExeUrl" "ERROR"
        exit 2
    }
} else {
    Write-Log "nssm.exe gia presente, salto download"
}

if (-not (Test-Path $KuioExe)) {
    if (-not (Get-FileFromR2 -Url $KuioExeUrl -Destination $KuioExe -ExpectedSha256 $KuioExeSha256)) {
        Write-Log "Impossibile ottenere kuio.exe da $KuioExeUrl" "ERROR"
        exit 3
    }
} else {
    Write-Log "kuio.exe gia presente, salto download (per update usa InstallKuio.ps1 con --force)"
}

# === Servizio gia esistente? ===
$existing = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Log "Servizio $ServiceName gia esistente: stato $($existing.Status)" "WARN"
    Write-Log "Stop + rimozione per re-install pulita..."
    & $NssmExe stop $ServiceName confirm 2>&1 | Out-Null
    Start-Sleep -Seconds 2
    & $NssmExe remove $ServiceName confirm 2>&1 | Out-Null
    Start-Sleep -Seconds 1
}

# === Registra servizio con NSSM ===
Write-Log "Registrazione servizio $ServiceName..."
& $NssmExe install $ServiceName $KuioExe
& $NssmExe set $ServiceName AppParameters "gateway run --workspace `"$WorkspaceDir`""
& $NssmExe set $ServiceName AppDirectory $InstallDir
& $NssmExe set $ServiceName DisplayName $ServiceDisplay
& $NssmExe set $ServiceName Description $ServiceDescr
& $NssmExe set $ServiceName Start SERVICE_AUTO_START

# Log con rotazione 10MB
& $NssmExe set $ServiceName AppStdout $StdoutLog
& $NssmExe set $ServiceName AppStderr $StderrLog
& $NssmExe set $ServiceName AppRotateFiles 1
& $NssmExe set $ServiceName AppRotateOnline 1
& $NssmExe set $ServiceName AppRotateBytes 10485760

# Auto-restart su crash
& $NssmExe set $ServiceName AppExit Default Restart
& $NssmExe set $ServiceName AppRestartDelay 5000

# Identita: gira come utente corrente (per accesso a %LOCALAPPDATA% suo)
# NB: richiede password dell utente - in install pulita la chiediamo
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
Write-Log "Servizio sara registrato per utente: $currentUser"
Write-Log "Per motivi di sicurezza, NSSM chiedera la password dell utente Windows una volta."
Write-Host ""
Write-Host "Inserisci la password Windows del tuo utente ($currentUser):" -ForegroundColor Cyan
$securePwd = Read-Host -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePwd)
$plainPwd = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
& $NssmExe set $ServiceName ObjectName $currentUser $plainPwd
$plainPwd = $null  # cancella subito
[GC]::Collect()

# === Avvio ===
Write-Log "Avvio del servizio..."
& $NssmExe start $ServiceName
Start-Sleep -Seconds 3

# === Verifica ===
$svc = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($svc -and $svc.Status -eq "Running") {
    Write-Log "SUCCESSO: Servizio $ServiceName e in esecuzione." "OK"
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "  KUIO e ora attivo come Servizio Windows" -ForegroundColor Green
    Write-Host "  Parte automaticamente al boot." -ForegroundColor Green
    Write-Host "  Log: $LogsDir" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    exit 0
} else {
    Write-Log "Servizio NON in esecuzione. Stato: $($svc.Status)" "ERROR"
    Write-Log "Controlla i log in: $StderrLog" "ERROR"
    exit 4
}
