# Mappatura skill base KUIO ↔ skill OpenClaw esistenti

Data: 2026-05-20 — Sprint 4

Le 7 skill base promesse a Antonio dal Master Brief vs cosa offre già il fork OpenClaw.

| # | Skill KUIO | Copertura OpenClaw | Stato | Azione richiesta |
|---|---|---|---|---|
| 1 | **Email** | `himalaya` (IMAP/SMTP completo) | ✅ Pronta | Wrapper italiano + onboarding account |
| 2 | **Calendario** | nessuna nativa | ❌ Da creare | Skill nuova: CalDAV o Google Calendar API (scheletro creato) |
| 3 | **Documenti** | `notion`, `obsidian`, `apple-notes`, `bear-notes`, `nano-pdf`, `summarize` | ✅ Più alternative | Decidere quali abilitare di default per il cliente italiano |
| 4 | **Ricerca** | `weather`, `github`, `gh-issues`, `summarize` (URL/YouTube/PDF) | ⚠️ Parziale | Aggiungere skill "ricerca web generica" (Brave Search API o DDG) |
| 5 | **Scrittura** | nessuna (capability nativa del LLM) | ⚠️ Wrapper sottile | Creare skill con prompt templates italiani (scheletro creato) |
| 6 | **Lingue** | nessuna nativa | ❌ Da creare | Skill traduzione/correzione (scheletro creato) |
| 7 | **Comandi Vocali** | `openai-whisper`(local STT), `openai-whisper-api`, `sherpa-onnx-tts` (local TTS offline), `sag` (ElevenLabs cloud), `voice-call` | ✅ Stack completo | Scegliere combinazione default: consigliato whisper+sherpa-onnx (entrambi locali, no cloud) |

## Skill bonus rilevanti (oltre le 7 base)

- `taskflow` — orchestrazione task multi-step durabili (essenziale per agente AI)
- `wacli` — WhatsApp CLI per messaggi/sync (canale primario KUIO)
- `summarize` — riepiloga URL, video YouTube, podcast, articoli, PDF locali

## Stack tecnico raccomandato per il cliente italiano

- **Email:** himalaya su account IMAP del cliente
- **Calendario:** Google Calendar API (la maggior parte ha Gmail)
- **Documenti:** notion+obsidian come default (Apple Notes solo se Mac)
- **Ricerca:** web (Brave) + summarize (per leggere e riassumere)
- **Scrittura:** template prompt italiani in skill dedicata
- **Lingue:** wrapper LLM con prompt strutturati (traduzione, riformulazione, correzione grammaticale)
- **Vocali:** openai-whisper (locale, offline) per STT + sherpa-onnx-tts (locale) per TTS

## Skill che NON ci servono (eliminare/disabilitare)

Per snellire il pacchetto KUIO e ridurre superficie d'attacco:
- 1password, apple-notes, apple-reminders, bear-notes (Mac-only)
- discord, slack (non target KUIO Italia)
- coding-agent, gh-issues, github, node-inspect-debugger (per developer, non per cliente finale)
- gog, goplaces, spike, songsee (niche)
- camsnap, meme-maker, weather (non prioritari)

Restano: himalaya, notion, obsidian, nano-pdf, summarize, taskflow, voice-call, wacli, openai-whisper, sherpa-onnx-tts, + 3 nuove KUIO.
