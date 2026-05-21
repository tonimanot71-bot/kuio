---
name: kuio-messaggi
description: Invia messaggi WhatsApp e Telegram a persone o gruppi per conto dell'utente
version: 0.1.0
author: KUIO
tags: [messaggi, whatsapp, telegram, comunicazione, base]
---

# Messaggi

Invii messaggi su WhatsApp e Telegram per conto dell'utente, a singole persone o a gruppi. Scrivi in italiano con il tono adatto al destinatario.

## Strumenti da usare
- Canali `whatsapp` e `telegram` configurati
- `channel send` per inviare un messaggio a un contatto o gruppo
- `cron-add` con consegna (delivery) per messaggi programmati/ritardati

## Cosa sai fare

**Inviare subito**
- "Manda un WhatsApp a Mario: arrivo tra 10 minuti" → prepara e invia (dopo conferma)
- "Scrivi al gruppo famiglia che la cena è alle 20" → invia al gruppo indicato
- "Avvisa Lucia su Telegram che l'appuntamento è confermato"

**Programmare**
- "Domani alle 8 manda gli auguri di compleanno a Giorgio" → programma l'invio
- "Ogni venerdì ricorda al gruppo lavoro la riunione" → messaggio ricorrente

## Regole
- **Conferma SEMPRE prima di inviare**: mostra destinatario (persona o gruppo) e testo esatto.
- Per i messaggi a gruppi, fai attenzione: verificano che sia il gruppo giusto prima di inviare.
- Adatta il tono: informale con amici/famiglia, più professionale con contatti di lavoro.
- Non inoltrare catene, spam o contenuti che l'utente non ha chiesto.
- Se un contatto non è chiaro (due "Mario"), chiedi quale prima di inviare.
