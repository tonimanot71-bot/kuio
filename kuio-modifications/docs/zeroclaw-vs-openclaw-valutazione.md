# Valutazione: ZeroClaw vs OpenClaw come motore di KUIO

Data: 2026-05-20 — analisi del codice reale (non marketing). Repo analizzati: `openclaw/openclaw` e `zeroclaw-labs/zeroclaw`.

## Sintesi in una riga

ZeroClaw è più leggero, più semplice da distribuire, e ha GIÀ di serie le funzioni che stavamo costruendo a mano per OpenClaw. Il principale rischio è che sia ancora in beta (v0.8). **Raccomandazione: passare a ZeroClaw.**

## Confronto verificato nel codice

| Aspetto | OpenClaw | ZeroClaw | Vincitore per KUIO |
|---|---|---|---|
| Linguaggio | Node.js/TypeScript | Rust | ZeroClaw |
| RAM a riposo | centinaia di MB (richiede 1 GB+) | ~5 MB | **ZeroClaw** (PC vecchi del target) |
| Avvio | "minuti" su HW lento | millisecondi | ZeroClaw |
| Distribuzione | bundle Node 60-80 MB (da costruire con Node SEA) | singolo `.exe` self-contained (`--prebuilt`) | **ZeroClaw** |
| Servizio Windows | da fare a mano (NSSM + script custom) | **nativo**: `zeroclaw service install` | **ZeroClaw** |
| WSL2 | raccomandato upstream | non serve | ZeroClaw |
| WhatsApp + Telegram | sì | sì (`whatsapp.rs`, `telegram.rs`, +30 canali) | pari |
| Provider AI (BYOK) | molti | ~15 (anthropic, openai, gemini, ollama, openrouter, bedrock, glm, copilot, compatible…) | pari |
| Licenza | MIT | MIT OR Apache-2.0 | pari (entrambe ok commerciale) |
| Hardware economico | no (pesante) | sì (`firmware/`, gira su Raspberry/ARM) | ZeroClaw |
| Migrazione dall'altro | — | legge config/memoria OpenClaw (`migration.rs`) | ZeroClaw |
| Attività progetto | attivo | attivissimo (commit di oggi, #6072) | pari |
| **Maturità** | più maturo, collaudato | **beta v0.8.0-beta-1** | **OpenClaw** |
| Italiano pronto | sì (`it.ts` esisteva) | no (en/fr/ja/es/zh — italiano da aggiungere) | OpenClaw |
| Ecosistema skill | grande (30+ skill, ClawHub) | marketplace presente ma più giovane | OpenClaw |

## La scoperta che cambia tutto

ZeroClaw risolve NATIVAMENTE i due problemi tecnici più grossi dello Sprint 4:

1. **Singolo `.exe` self-contained** (`setup.bat --prebuilt` scarica un binario pronto, niente toolchain, niente Node). Addio bundle Node SEA da 60-80 MB.
2. **Servizio Windows nativo**: `zeroclaw service install` registra il daemon come Windows Service da solo. Addio NSSM + `InstallKuioService.ps1` custom.

In pratica, metà del lavoro tecnico che stavamo pianificando per OpenClaw **sparisce** con ZeroClaw.

## Cosa del lavoro di oggi resta valido (se passiamo a ZeroClaw)

- ✅ **Sistema licenze** (Sprint 5): indipendente dal motore — 100% riutilizzabile
- ✅ **Distribuzione R2**: identica — si carica `zeroclaw.exe` invece di `kuio.exe`. nssm.exe non serve più (risparmio).
- ✅ **Mappatura 7 skill base**: i concetti restano, cambia l'implementazione
- ✅ **Decisione runtime** (Windows invisibile): confermata, e più facile da realizzare
- ⚠️ **Fork OpenClaw**: da rifare come fork ZeroClaw (poco lavoro, eravamo all'inizio)
- ❌ **Traduzioni `it.ts` OpenClaw**: non riutilizzabili (ZeroClaw usa formato `.po`/gettext) — ma il lavoro di traduzione concettuale resta
- ❌ **`InstallKuioService.ps1` + NSSM**: in gran parte superati da `zeroclaw service install` nativo (è un guadagno: meno codice nostro da mantenere)

## Rischi (onesti)

1. **Beta v0.8.0**: non ancora 1.0. Possibili breaking changes e bug. MITIGAZIONE: progetto attivissimo (si stabilizza in fretta); KUIO è lontano dal lancio pubblico, probabilmente ZeroClaw arriverà a 1.0 prima.
2. **Italiano da aggiungere**: il sistema i18n c'è (formato `.po` standard), va popolato l'italiano. Stesso lavoro che avremmo fatto comunque per il wizard OpenClaw.
3. **Skill da riscrivere**: le skill OpenClaw (himalaya, ecc.) non sono compatibili 1:1. ZeroClaw ha il suo marketplace; le 7 skill base KUIO andranno fatte per ZeroClaw.
4. **Ecosistema più giovane**: meno skill pronte della community rispetto a OpenClaw.

## Raccomandazione

**Passare a ZeroClaw.** I vantaggi sono concreti (verificati nel codice) e colpiscono esattamente i punti deboli di KUIO con OpenClaw: peso sui PC vecchi degli utenti italiani, complessità di distribuzione, fatica del servizio Windows. Il costo dello switch è basso perché siamo all'inizio. L'unico vero rischio (beta) è gestibile dato che il progetto è attivissimo e KUIO non è ancora in vendita.

Prossimo passo proposto: forkare ZeroClaw come nuova base `kuio-core`, archiviare il fork OpenClaw, e ricostruire il piano Sprint 4 sul nuovo motore (sarà più corto perché molte cose sono native).
