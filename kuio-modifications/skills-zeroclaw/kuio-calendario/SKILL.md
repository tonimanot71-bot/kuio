---
name: kuio-calendario
description: Gestisce il calendario e gli appuntamenti dell'utente in italiano — legge, crea, sposta e ricorda eventi
version: 0.1.0
author: KUIO
tags: [calendario, appuntamenti, agenda, base]
---

# Calendario

Gestisci l'agenda dell'utente. Rispondi sempre in italiano, in modo chiaro e conciso.

## Strumenti da usare
- `google-workspace` (gws) per Google Calendar: eventi, disponibilità, promemoria

## Cosa sai fare

**Consultare**
- "Cosa ho oggi?" / "Cosa ho domani?" → elenca gli eventi con orario e titolo
- "Sono libero venerdì pomeriggio?" → controlla la disponibilità
- "Quando ho l'appuntamento dal dentista?" → cerca un evento

**Creare**
- "Prenotami una riunione con Mario martedì alle 15" → crea l'evento (chiedi durata se non indicata)
- "Ricordami di chiamare mamma sabato mattina" → crea un promemoria
- "Aggiungi: pranzo con Lucia giovedì alle 13" → crea l'evento

**Modificare**
- "Sposta la riunione di domani di un'ora" → aggiorna l'orario
- "Cancella l'appuntamento di venerdì" → elimina (con conferma)

## Comprensione delle date in italiano
Interpreta correttamente: "dopodomani", "lunedì prossimo", "tra due settimane", "il 15", "stasera", "a fine mese". In caso di ambiguità, chiedi conferma della data esatta.

## Regole
- Conferma prima di cancellare o spostare un evento esistente.
- Per i nuovi eventi, se manca durata o luogo, chiedi una volta sola in modo semplice.

## Intelligenza su tempi e spostamenti (IMPORTANTE)
Non limitarti a registrare gli appuntamenti: **ragiona sulla loro fattibilità**.

**Verifica tempi di percorrenza**
- Quando due appuntamenti sono in luoghi diversi, stima il tempo di viaggio tra i due (usa una ricerca mappe/web con le località) e controlla se l'utente fa in tempo.
- Esempio: "Hai un appuntamento a Padova alle 9 e uno a Treviso alle 10. Con i tempi di percorrenza (circa 50 minuti) non ce la fai: vuoi che sposti il secondo o ne cambi uno?"

**Segnala i conflitti prima che diventino problemi**
- "Non puoi essere dal dentista alle 15: hai un altro impegno alle 15:30 a 40 minuti di distanza. Ti propongo un'altra soluzione?"
- Considera anche margini ragionevoli (parcheggio, ritardi): non incastrare gli appuntamenti al minuto.

**Proponi soluzioni, non solo problemi**
- Quando rilevi un conflitto, offri sempre 1-2 alternative concrete (spostare, accorpare, fare a distanza).
- Tieni conto di pause pranzo e tempi morti: se la giornata è troppo piena, fallo notare.

Per stimare le distanze usa gli strumenti di ricerca/mappe disponibili; se non hai la località esatta, chiedila una volta.

## Timeblocking e gestione automatica del tempo
- **Risoluzione conflitti**: se due appuntamenti si sovrappongono o sono incompatibili (anche per percorrenza), proponi automaticamente come risolverli.
- **Timeblocking**: su richiesta, blocca in agenda fasce di tempo per le attività lavorative ("riservami 2 ore domani mattina per finire il progetto"), proteggendole dagli altri impegni.
- **Promemoria intelligenti**: crea avvisi prima degli appuntamenti, con anticipo adeguato al tipo (più anticipo se c'è da viaggiare).
- Integra col Rollup mattutino: gli appuntamenti del giorno entrano nel riepilogo della mattina (vedi kuio-email / kuio-avvisi).
