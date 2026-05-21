---
name: kuio-lingue
description: "Traduzione, correzione grammaticale, analisi e spiegazione di testi in italiano e tra italiano e altre lingue (EN/FR/ES/DE)."
homepage: https://kuio.ai
metadata:
  {
    "openclaw":
      {
        "emoji": "🌍",
        "language": "it",
      },
  }
---

# Lingue KUIO

Servizi linguistici per l'utente italiano. Wrapper LLM con prompt strutturati — usa il provider AI scelto (BYOK), nessun servizio esterno.

## Operazioni

### Traduzione
- "Traduci in inglese: ..." → traduzione formale/informale
- "Cosa significa 'serendipity'?" → spiegazione + traduzione + esempi d'uso
- "Come si dice 'beccare qualcuno con le mani nel sacco' in inglese?" → idiomatico, non letterale

### Correzione grammaticale (italiano)
- "Correggi: ho andato al mare ieri" → "Sono andato al mare ieri" + spiegazione regola
- Distinguere errori di ortografia, grammatica, sintassi, registro

### Riformulazione di registro
- "Rendi più formale questa frase"
- "Rendi più semplice questa frase" (per leggibilità anziana o non-madrelingua)

### Spiegazione
- "Spiega cosa vuol dire 'conditio sine qua non'"
- "Spiega questa parola: 'epistemologico'"
- Output: definizione + etimologia + esempio + sinonimi

### Analisi di testo
- "Che tono ha questa mail?" (formale/informale/aggressiva/ironica/etc)
- "Riassumi questo testo lungo in 5 punti"

## Lingue supportate

Italiano (madre) ↔ Inglese, Francese, Spagnolo, Tedesco (le 5 lingue dell'UI KUIO).

## Stato implementazione

⚠️ **Scheletro — da implementare in Sprint 4-5.** Necessita:
- [ ] Prompt templates per ciascuna operazione
- [ ] Detector automatico della lingua sorgente
- [ ] Glossario terminologia italiana specifica (giuridica, medica, tecnica) come opzione
- [ ] Memoria di traduzioni precedenti per coerenza terminologica

## Limiti

- Per testi legali/medici critici, raccomandare revisione umana professionale (output disclaimer)
- Nessuna garanzia su trascrizioni perfette di dialetti italiani regionali
