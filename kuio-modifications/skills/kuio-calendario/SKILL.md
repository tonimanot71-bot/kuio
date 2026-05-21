---
name: kuio-calendario
description: "Gestione calendario per KUIO — leggi, crea, modifica, cancella eventi su Google Calendar o iCloud Calendar. Promemoria, ricerca eventi, free/busy."
homepage: https://kuio.ai
metadata:
  {
    "openclaw":
      {
        "emoji": "📅",
        "requires": { "env": ["KUIO_CALENDAR_PROVIDER", "KUIO_CALENDAR_TOKEN"] },
        "language": "it",
      },
  }
---

# Calendario KUIO

Gestione del calendario personale dell'utente tramite Google Calendar (default) o iCloud (CalDAV).

## Provider supportati

- `google` — Google Calendar API (OAuth, scope: calendar.events)
- `icloud` — iCloud Calendar via CalDAV (app password)
- `caldav` — Server CalDAV generico (es. Nextcloud, FastMail)

Configurazione: `~/.kuio/calendario.toml`

## Operazioni base

### Leggere eventi

- "Cosa ho oggi?" → eventi delle prossime 24h
- "Cosa ho la prossima settimana?" → eventi prossimi 7 giorni
- "Cerca riunione con Marco" → ricerca per partecipante/titolo

### Creare eventi

- "Prenotami una riunione con Marco domani alle 15"
- "Aggiungi appuntamento dentista venerdì 11"
- "Mettimi un promemoria per chiamare mamma sabato"

### Modificare/cancellare

- "Sposta la riunione di domani di un'ora"
- "Cancella l'appuntamento dentista"

## Stato implementazione

⚠️ **Scheletro — da implementare in Sprint 4-5.** Necessita:
- [ ] Modulo OAuth Google Calendar (riuso del provider OAuth interno OpenClaw se esiste)
- [ ] Wrapper TypeScript per le 6 operazioni base
- [ ] Test con calendario di test
- [ ] Prompts italiani per disambiguazione date ("dopodomani", "lunedì prossimo", "tra due settimane")

## Sicurezza

- Token Google in `~/.kuio/secrets/` (file permission 600)
- Mai loggare token o ID eventi sensibili
- Confermare prima di cancellare eventi
