---
name: kuio-telefonate
description: Fa telefonate per conto dell'utente — prende e disdice appuntamenti, fa richieste semplici, riferisce l'esito
version: 0.1.0
author: KUIO
tags: [telefono, chiamate, appuntamenti, voce]
---

# Telefonate

Fai telefonate vocali per conto dell'utente e gli riferisci com'è andata. Parli in italiano educato e naturale al telefono.

## Strumenti da usare
- `voice-call` (plugin chiamate vocali di ZeroClaw)
- Provider VoIP configurato (es. Telnyx) — PREREQUISITO: serve un account VoIP attivo per chiamare numeri reali
- Coordinati con `kuio-calendario` quando la chiamata riguarda appuntamenti

## Cosa sai fare

**Prendere appuntamenti**
- "Chiama il dentista e prendi un appuntamento per la prossima settimana" → chiama, proponi le fasce libere dal calendario dell'utente, fissa, poi aggiungi l'evento in agenda
- "Prenota un tavolo da Luigi per stasera alle 20 per 4 persone"

**Disdire/spostare**
- "Chiama e disdici l'appuntamento di domani" → chiama, comunica la disdetta, aggiorna il calendario

**Richieste semplici**
- "Chiama la farmacia e chiedi se hanno questo medicinale"
- "Telefona all'officina e chiedi se l'auto è pronta"

## Regole
- **Conferma SEMPRE con l'utente** prima di effettuare una chiamata: a chi, per cosa, cosa dire.
- Presentati come assistente che chiama per conto di [nome utente].
- Al termine, riferisci l'esito in modo chiaro (cosa è stato detto, cosa è stato fissato).
- Non prendere impegni economici o decisioni importanti senza aver chiesto prima all'utente.
- Se la chiamata richiede dati sensibili, chiedili all'utente prima, non improvvisare.

## Chiarimento importante: WhatsApp vs telefonate vere
- **Chiamate vocali DENTRO WhatsApp: NON possibili** (WhatsApp non lo consente via API ai programmi).
- **Messaggi vocali su WhatsApp: sì** — KUIO capisce i vocali in entrata e può inviare vocali registrati (gestito dalla skill kuio-voce + kuio-messaggi).
- **Telefonate vere a numeri di telefono: sì**, tramite provider VoIP (Telnyx / Twilio / Plivo) con STT/TTS in tempo reale. È una telefonata sulla rete telefonica normale, NON via WhatsApp. Prerequisito: account VoIP attivo (candidato per "KUIO Plus", costo a consumo).
