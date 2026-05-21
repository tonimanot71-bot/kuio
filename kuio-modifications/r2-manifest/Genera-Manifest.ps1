<#
.SYNOPSIS
KUIO — Genera la voce manifest per un file appena costruito.

.DESCRIPTION
Dato un file locale (es. nssm.exe, kuio.exe, kuio-core-v0.1.0.zip), calcola SHA-256 e
dimensione, e produce un blocco JSON pronto da incollare in r2-manifest/manifest.json.

USO:
    .\Genera-Manifest.ps1 -File "C:\Downloads\nssm.exe"
    .\Genera-Manifest.ps1 -File "E:\kuio\binari\kuio.exe" -Version "0.1.0"

Output: stampa il blocco JSON aggiornato + lo copia nella clipboard pronto da incollare.

DOPO:
- Aggiornare il manifest.json sostituendo "DA_POPOLARE_DOPO_..." con i valori prodotti
- Caricare il file binario su R2 (dashboard Cloudflare -> kuio-installer)
- Caricare anche manifest.json su R2 (sostituendo il precedente)
#>

param(
    [Parameter(Mandatory=$true)][string]$File,
    [string]$Version = "",
    [string]$Url = ""
)

if (-not (Test-Path $File)) {
    Write-Host "ERRORE: File non trovato: $File" -ForegroundColor Red
    exit 1
}

$fileName = [System.IO.Path]::GetFileName($File)
$sha = (Get-FileHash $File -Algorithm SHA256).Hash.ToLower()
$size = (Get-Item $File).Length
$nowIso = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
if (-not $Url) { $Url = "https://installer.kuio.ai/$fileName" }

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Manifest KUIO — voce per: $fileName" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "File:        $File"
Write-Host "Dimensione:  $size byte ($('{0:N1}' -f ($size / 1MB)) MB)"
Write-Host "SHA-256:     $sha"
Write-Host "URL R2:      $Url"
Write-Host "Timestamp:   $nowIso"
Write-Host ""

# Blocco JSON pronto da incollare
$block = @"
    "$fileName": {
      "url": "$Url",
      "version": "$Version",
      "size_bytes": $size,
      "sha256": "$sha",
      "uploaded": "$nowIso"
    }
"@

Write-Host "--- BLOCCO JSON DA INCOLLARE NEL MANIFEST ---" -ForegroundColor Yellow
Write-Host $block
Write-Host ""

# Copia in clipboard se possibile (richiede Windows + STA)
try {
    Set-Clipboard -Value $block
    Write-Host "[OK] Blocco JSON copiato in clipboard. Incolla nel manifest.json e aggiorna." -ForegroundColor Green
} catch {
    Write-Host "[INFO] Clipboard non disponibile — copia il blocco a mano." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "PROSSIMI PASSI:"
Write-Host "  1. Aggiorna E:\kuio\kuio-modifications\r2-manifest\manifest.json con questo blocco"
Write-Host "  2. Carica $fileName su R2 (dashboard Cloudflare -> kuio-installer)"
Write-Host "  3. Carica anche manifest.json aggiornato su R2 (sovrascrivi il precedente)"
Write-Host ""
