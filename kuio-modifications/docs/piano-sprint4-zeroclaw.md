# Piano Sprint 4 — su ZeroClaw (rivisto dopo il cambio motore)

Data: 2026-05-20. Motore: ZeroClaw (Rust). Fork: `github.com/tonimanot71-bot/kuio`.

## Perché è più corto del piano OpenClaw

ZeroClaw fa nativamente 2 cose che su OpenClaw richiedevano lavoro manuale:
- **Servizio Windows**: `zeroclaw service install` (niente più NSSM né script custom)
- **Binario pronto**: GitHub Releases offre `.exe` self-contained con `setup.bat --prebuilt` (niente più build Node SEA)

## Flusso di installazione cliente (nuovo, semplificato)

1. Cliente lancia `InstallKuio.bat` (esistente, fa i 7 check di sistema)
2. Lo script scarica `kuio.exe` (= binario ZeroClaw brandizzato) dal tuo R2 `installer.kuio.ai`
3. `kuio.exe service install` → registra il servizio Windows invisibile (nativo)
4. `kuio.exe onboard` → wizard in italiano: chiede codice licenza, provider AI (BYOK), bot Telegram/WhatsApp
5. Fatto — il segretario è attivo e parte ad ogni avvio

## Passi del nuovo Sprint 4

### 1. Branding ZeroClaw → KUIO
- Sostituire "ZeroClaw" → "KUIO" SOLO nelle stringhe user-facing (file `.ftl` in `crates/zeroclaw-runtime/locales/` + README + banner)
- NON rinominare il package Rust `zeroclawlabs` né il comando interno (rischio rottura; il cliente non li vede)
- Logo/banner: sostituire con `Logo_transparent.png` di KUIO

### 2. Italiano
- Creare `crates/zeroclaw-runtime/locales/it/` copiando da `en/` e traducendo:
  - `cli.ftl` (messaggi a riga di comando)
  - `tools.ftl` (descrizioni strumenti)
  - eventuali altri `.ftl`
- Registrare "it" tra le lingue disponibili (`locales.toml`)
- Tradurre la doc onboarding (`docs/book/po/it.po`) — priorità bassa

### 3. Config di default KUIO
- Preparare un `kuio.toml` di default con: provider AI placeholder (BYOK), canali Telegram + WhatsApp pre-impostati, workspace path
- Definire COSA è "base" e COSA è "Plus" (per il sistema licenze)

### 4. Le 7 skill base
- ZeroClaw ha un repo skill separato: `github.com/zeroclaw-labs/zeroclaw-skills` (marketplace)
- Verificare quali delle 7 (Email, Calendario, Documenti, Ricerca, Scrittura, Lingue, Vocali) esistono già lì
- Creare le mancanti nel formato skill ZeroClaw (da studiare — diverso da OpenClaw)

### 5. Binario su R2
- Ottenere `kuio.exe`: due strade
  - (a) Scaricare il prebuilt da GitHub Releases di ZeroClaw e rinominarlo → veloce per partire
  - (b) Compilare il nostro fork brandizzato → per la versione vera con branding KUIO
- Calcolare SHA-256 (con `Genera-Manifest.ps1` già pronto), aggiornare `manifest.json`, caricare su R2
- `nssm.exe` NON serve più (rimuovere dal manifest e dallo script servizio)

### 6. Aggiornare InstallKuio.ps1
- Scaricare `kuio.exe` da R2 (al posto del bundle Node)
- Chiamare `kuio.exe service install` invece dello script NSSM custom
- Rimuovere i riferimenti a WSL2 e Node (non più necessari)

### 7. Test end-to-end
- VM Windows pulita: InstallKuio.bat → download → service install → onboard → primo messaggio su Telegram

## Cosa resta valido dal lavoro precedente

- ✅ Sistema licenze (`licensing/`, `docs/sistema-licenze-architettura.md`) — invariato
- ✅ Distribuzione R2 + `Genera-Manifest.ps1` + `manifest.json` — invariati (cambia il binario)
- ✅ Decisione runtime Windows invisibile — confermata e più facile
- ✅ Mappatura concettuale 7 skill base (`skills-mapping.md`)

## Cosa è da archiviare/non più valido

- ❌ `InstallKuioService.ps1` + NSSM → sostituiti da `zeroclaw service install` nativo
- ❌ Traduzioni `it.ts` OpenClaw (formato diverso, ZeroClaw usa `.ftl`)
- ❌ Scheletri SKILL.md OpenClaw (formato skill diverso in ZeroClaw)
- ❌ Vecchio fork `tonimanot71-bot/kuio-core` (OpenClaw) → archiviare/cancellare

## Stima

Più corto del piano OpenClaw: ~1-2 sessioni (il servizio Windows e il binario, prima i pezzi più pesanti, ora sono quasi gratis).
