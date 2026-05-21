# Architettura — Servizio Windows invisibile per KUIO

## Obiettivo

KUIO deve girare sul PC del cliente come **processo invisibile sempre attivo**:
- Parte al boot, senza intervento utente
- Ascolta WhatsApp/Telegram in background
- Sopravvive a logout/login dello stesso utente
- Si auto-riavvia se crasha
- Update silenziosi senza fermare il cliente

## Regola d'oro: tutto viene da R2

**Ogni binario, manifest, asset, e zip viene scaricato al volo da `https://installer.kuio.ai` (bucket R2 `kuio-installer` su Cloudflare).** Il PC del cliente NON contiene file pre-installati: lo script si scarica tutto quello che gli serve, verifica SHA-256, e procede. Questo vale per `kuio.exe`, `nssm.exe`, `kuio-core-v*.zip`, manifest di versione, futuri update. Il cliente ha solo l'installer iniziale (chiavetta USB o link diretto su `installer.kuio.ai/InstallKuio.bat`).

Distinguere domini:
- `www.kuio.ai` / `kuio.ai` → sito vetrina (marketing, link install, FAQ)
- `installer.kuio.ai` → R2 bucket (binari, manifest, update)
- `support@kuio.ai` → email supporto

## Decisione: NSSM, non sc.exe

**NSSM** (Non-Sucking Service Manager — https://nssm.cc) wrappa qualsiasi eseguibile come Servizio Windows nativo.

| Aspetto | NSSM | `sc.exe` |
|---|---|---|
| Auto-restart al crash | ✅ Configurabile | ❌ Solo via Recovery Actions complesse |
| Redirect stdout/stderr a file | ✅ Built-in | ❌ Eseguibile deve scriverli da solo |
| Gestione segnali (graceful shutdown) | ✅ | ⚠️ Solo se eseguibile implementa SCM correttamente |
| Wrapping di Node.js | ✅ Standard | ❌ Node non implementa SCM Windows nativamente |

Conclusione: **NSSM è obbligatorio** perché KUIO è basato su Node.js, che non implementa il protocollo Windows SCM.

## Layout file su disco cliente

```
C:\Program Files\KUIO\                       (binario read-only)
  kuio.exe                                    Node SEA bundle (60-80 MB)
  nssm.exe                                    Service Manager (~300 KB)
  LICENSE
  version.json

%LOCALAPPDATA%\KUIO\                         (dati utente, scrivibile)
  config\
    kuio.json                                 Configurazione (provider AI, canali)
    secrets\                                  Credenziali (file ACL 600)
      *.token
  workspace\
    skills\                                   Skill installate
    sessions\                                 Storico conversazioni
  logs\
    kuio-stdout.log                           Output gateway (rolling)
    kuio-stderr.log                           Errori (rolling)
    install.log                               Log installer
```

## Account servizio

**Default: LocalService** ❌ — NO, non può accedere a %LOCALAPPDATA% dell'utente.

**Scelta: gira come utente loggato** ✅ — il servizio è registrato per l'utente specifico (account "DOMINIO\nome.utente"). Pro/contro:
- ✅ Accede a credenziali e config dell'utente
- ✅ Può accedere a OneDrive/Google Drive sincronizzato
- ⚠️ Se l'utente cambia password Windows, va riconfigurato (raro per uso domestico)
- ⚠️ Non parte se l'utente non si è MAI loggato dopo il boot (caso bordo: PC sharing — non target KUIO)

## Sequenza install

1. **Check pre-requisiti** (riuso `InstallKuio.ps1` esistente)
2. **Richiesta UAC** (necessaria per registrare servizio)
3. **Download NSSM** da `https://installer.kuio.ai/nssm.exe` (~300 KB)
4. **Download `kuio.exe`** (Node SEA bundle) da `https://installer.kuio.ai/kuio-core-vX.Y.Z.exe`
5. **Verifica SHA-256** entrambi (whitelist nei manifest R2)
6. **Estrazione in `C:\Program Files\KUIO\`**
7. **Creazione `%LOCALAPPDATA%\KUIO\` con permessi corretti**
8. **Registrazione servizio NSSM:**
   ```
   nssm install KUIO "C:\Program Files\KUIO\kuio.exe"
   nssm set KUIO AppParameters "gateway run --workspace %LOCALAPPDATA%\KUIO\workspace"
   nssm set KUIO AppDirectory "C:\Program Files\KUIO"
   nssm set KUIO DisplayName "KUIO Personal Assistant"
   nssm set KUIO Description "Il tuo segretario personale digitale (kuio.ai)"
   nssm set KUIO Start SERVICE_AUTO_START
   nssm set KUIO ObjectName ".\<utente>" "<password>"   ← input cliente (UAC)
   nssm set KUIO AppStdout "%LOCALAPPDATA%\KUIO\logs\kuio-stdout.log"
   nssm set KUIO AppStderr "%LOCALAPPDATA%\KUIO\logs\kuio-stderr.log"
   nssm set KUIO AppRotateFiles 1
   nssm set KUIO AppRotateBytes 10485760    ← 10 MB log rotation
   nssm set KUIO AppExit Default Restart
   nssm set KUIO AppRestartDelay 5000        ← 5s delay tra restart
   ```
9. **Avvio:** `nssm start KUIO`
10. **Verifica:** `sc query KUIO` → STATE: RUNNING

## Sequenza uninstall

```
nssm stop KUIO
nssm remove KUIO confirm
Remove-Item "C:\Program Files\KUIO\" -Recurse -Force
# %LOCALAPPDATA%\KUIO\ resta per backup (opzionale rimozione)
```

## Update senza fermare il cliente

1. Servizio nuovo `kuio.exe` scaricato come `kuio.exe.new`
2. `nssm stop KUIO`
3. Replace: `Move-Item kuio.exe kuio.exe.old; Move-Item kuio.exe.new kuio.exe`
4. `nssm start KUIO`
5. Pausa di servizio: ~3-5 secondi totali (il cliente non se ne accorge)
6. Rollback se start fallisce: revertire ai `.old`

## Cosa manca per implementare

- [ ] Build Node SEA del fork KUIO (`kuio.exe` ~60-80 MB) — Sprint 4/5
- [ ] Upload `nssm.exe` su R2 in `installer.kuio.ai/nssm.exe` con SHA-256 in manifest
- [ ] Test del flusso completo su VM Windows pulita
- [ ] Documentazione utente "Come disinstallare KUIO" (semplice link)
