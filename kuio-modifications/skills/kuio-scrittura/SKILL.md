---
name: kuio-scrittura
description: "Assistenza alla scrittura in italiano — bozze email, lettere, post, riepiloghi, parafrasi, correzioni con tono adatto al contesto."
homepage: https://kuio.ai
metadata:
  {
    "openclaw":
      {
        "emoji": "✍️",
        "language": "it",
      },
  }
---

# Scrittura KUIO

Wrapper di prompt italiani sopra il modello AI scelto dall'utente (BYOK). Non richiede binari esterni — usa direttamente il provider AI configurato.

## Modalità

### Bozza email
- "Scrivi una mail a Mario per chiedere uno sconto sulla fornitura"
- Output: bozza con apertura, corpo, chiusura — tono modulabile (formale/cordiale/informale)

### Lettera ufficiale
- "Scrivi una raccomandata al condominio per il guasto al cancello"
- Output: struttura italiana standard (intestazione, oggetto, riferimenti, firma)

### Post social
- "Scrivi un post Facebook per il compleanno di mia moglie"
- Output: tono caloroso, lunghezza adatta a FB/IG

### Riepilogo / sintesi
- "Riassumi questa email in 3 righe"
- Output: riepilogo conciso preservando informazioni chiave

### Parafrasi / riformulazione
- "Riformula questa frase più gentile"
- Output: alternative con tono diverso

### Correzione
- "Correggi grammatica e punteggiatura di questo testo"
- Output: testo corretto + lista correzioni applicate

## Stato implementazione

⚠️ **Scheletro — da implementare in Sprint 4-5.** Necessita:
- [ ] Libreria di prompt templates italiani (uno per modalità)
- [ ] Detector di tono (formale/informale) e contesto (business/personale)
- [ ] Integrazione con provider AI configurato dall'utente
- [ ] Memoria stile dell'utente (impara come scrive l'utente per replicare il tono)

## Note culturali

- Distinguere "tu/Lei" in base al destinatario
- Saluti italiani standard ("Cordiali saluti", "Distinti saluti", "Un abbraccio", "Ciao")
- Apertura formale italiana ("Egregio Dott.", "Gentile Sig.ra", non "Caro" se contesto business)
