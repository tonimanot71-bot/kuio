<#
.SYNOPSIS
KUIO — Installer master (motore ZeroClaw). Da lanciare via "Doppio clic per avviare KUIO.bat".
.DESCRIPTION
Scarica tutto dal server (installer.kuio.ai), installa KUIO come Servizio Windows invisibile,
copia le 30 skill + config italiana, avvia il servizio e la configurazione guidata.
Il cliente non vede nulla di tecnico: solo una finestra amichevole con avanzamento.
ARCHITETTURA: ZeroClaw (Rust) — servizio Windows NATIVO (zeroclaw service install), niente Node/NSSM/WSL2.
#>
$ErrorActionPreference = "Stop"

# === Costanti ===
$DistroBase   = "https://installer.kuio.ai"
$EngineZip    = "kuio-engine-win-v0.7.5.zip"
$EngineSha    = "e8ff73a35ad550d5389d47db3eabc571142c4cc307afb09b2d4ee29d342ff5b8"
$SkillsZip    = "kuio-config-skills.zip"     # 30 skill + kuio.toml
$SkillsSha    = "00a1505208d4e1c956d2c249cb611ab156c5b19c85453fb6c113f52d9441d96b"
$InstallDir   = "${env:ProgramFiles}\KUIO"
$DataDir      = "${env:LOCALAPPDATA}\KUIO"
$Workspace    = "$DataDir\workspace"
$LogsDir      = "$DataDir\logs"
$Exe          = "$InstallDir\kuio.exe"

function Write-Log { param([string]$m,[string]$l="INFO")
  $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$l] $m"
  Write-Host $line
  if (Test-Path $LogsDir) { Add-Content "$LogsDir\install.log" $line -Encoding UTF8 }
}
function Test-Admin {
  $p = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
  return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}
function Get-FromR2 { param([string]$Name,[string]$Dest,[string]$Sha="")
  Write-Log "Scarico $Name dal server..."
  $ProgressPreference = "SilentlyContinue"
  Invoke-WebRequest -Uri "$DistroBase/$Name" -OutFile $Dest -UseBasicParsing -ErrorAction Stop
  if ($Sha) {
    $a = (Get-FileHash $Dest -Algorithm SHA256).Hash.ToLower()
    if ($a -ne $Sha.ToLower()) { throw "Verifica integrita fallita per $Name" }
    Write-Log "$Name verificato (integro)" "OK"
  }
}

if (-not (Test-Admin)) {
  Write-Host "Per installare KUIO servono i permessi di amministratore. Riavvia con tasto destro -> Esegui come amministratore." -ForegroundColor Yellow
  exit 1
}

# === 1. Cartelle ===
foreach ($d in @($InstallDir,$DataDir,$Workspace,$LogsDir,"$Workspace\skills")) {
  if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}
Write-Log "Cartelle pronte."

# === 2. Scarica ed estrai il MOTORE da R2 ===
$tmpEngine = "${env:TEMP}\$EngineZip"
Get-FromR2 -Name $EngineZip -Dest $tmpEngine -Sha $EngineSha
Write-Log "Estraggo il motore in $InstallDir ..."
Expand-Archive -Path $tmpEngine -DestinationPath $InstallDir -Force
Remove-Item $tmpEngine -Force -ErrorAction SilentlyContinue
if (Test-Path "$InstallDir\zeroclaw.exe") { Rename-Item "$InstallDir\zeroclaw.exe" "kuio.exe" -Force }
if (-not (Test-Path $Exe)) { throw "Motore KUIO non trovato dopo l estrazione" }

# === 3. Scarica ed estrai SKILL + CONFIG nel workspace ===
$tmpSkills = "${env:TEMP}\$SkillsZip"
try {
  Get-FromR2 -Name $SkillsZip -Dest $tmpSkills -Sha $SkillsSha
  Expand-Archive -Path $tmpSkills -DestinationPath $Workspace -Force
  Remove-Item $tmpSkills -Force -ErrorAction SilentlyContinue
  Write-Log "30 skill KUIO + configurazione italiana installate." "OK"
} catch {
  Write-Log "Pacchetto skill non ancora su R2 (lo carichi tu): salto, il motore funziona comunque." "WARN"
}

# === 4. Registra il SERVIZIO WINDOWS (nativo ZeroClaw) ===
Write-Log "Registro KUIO come servizio invisibile..."
& $Exe service install   2>&1 | Out-Null
& $Exe service start      2>&1 | Out-Null
Start-Sleep -Seconds 2
Write-Log "Servizio KUIO avviato." "OK"

# === 5. Configurazione guidata (onboarding) ===
Write-Log "Avvio la configurazione guidata (provider AI, Telegram/WhatsApp, codice licenza)..."
& $Exe onboard

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  KUIO e installato e attivo!" -ForegroundColor Green
Write-Host "  Da ora ti risponde su WhatsApp e Telegram." -ForegroundColor Green
Write-Host "  Parte automaticamente ad ogni accensione." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
exit 0
