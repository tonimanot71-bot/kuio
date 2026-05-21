# Architettura — Sistema di licenze KUIO

Decisioni prese da Antonio il 2026-05-20:
- **Verifica online** sul server Cloudflare
- **1 licenza = 1 PC, trasferibile** dal cliente (limite trasferimenti/anno)
- **Mancato pagamento Plus** → funzioni base restano, Plus si spegne

## Come appare al cliente

1. Compra la chiavetta KUIO (49€). Dentro c'è un codice tipo `KUIO-965E3-KNVTW`.
2. Installa KUIO. Al primo avvio il programma chiede: "Inserisci il tuo codice KUIO".
3. Digita il codice → attesa di 2 secondi → "Attivazione completata, benvenuto!"
4. Se il codice è sbagliato o già usato: messaggio chiaro ("Codice non valido" / "Codice già attivo su un altro PC").

## Il codice di licenza

- Formato: `KUIO-XXXXX-XXXXX` — 10 caratteri visibili.
- Alfabeto senza caratteri ambigui (niente 0/O, 1/I/L) → facile da leggere e digitare.
- Gli ultimi 3 caratteri sono una **firma crittografica** (HMAC-SHA256): impediscono a un truffatore di inventarsi codici validi.
- Generati in lotti con lo script `licensing/genera_licenze.py`.

## La chiave segreta (punto critico di sicurezza)

- Esiste UNA chiave segreta che firma tutti i codici.
- Sta **SOLO sul server Cloudflare**. Mai dentro il programma installato sul PC del cliente, mai su GitHub.
- Se trapela, chiunque può generare codici validi → andrebbe rigenerata e invaliderebbe i codici vecchi.

## Cosa serve costruire (stack Cloudflare già esistente)

| Pezzo | Strumento Cloudflare | Note |
|---|---|---|
| Database licenze | KV o D1 | Gratis nel piano base. Una riga per codice: stato, PC legato, data attivazione, abbonamento |
| Server di attivazione | Worker su `api.kuio.ai/activate` | Riceve codice + impronta PC, valida, risponde sì/no |
| Generatore codici | `genera_licenze.py` (già fatto, PoC) | Antonio genera lotti quando servono |
| Pannello licenze (futuro) | Worker + pagina protetta | Per vedere/sospendere/sbloccare codici |

## Stati di una licenza

```
created    → codice generato, non ancora usato (caricato nel DB)
active     → attivato e legato a un PC (impronta hardware registrata)
suspended  → sospeso (es. codice rubato, segnalato da Antonio)
transferred→ in trasferimento verso un nuovo PC
expired    → abbonamento Plus scaduto (funzioni base restano, Plus off)
```

## Flusso di attivazione (tecnico, riassunto)

1. KUIO calcola un'**impronta del PC** (hash di identificatori hardware Windows).
2. Manda `{codice, impronta}` a `api.kuio.ai/activate`.
3. Il Worker: verifica firma del codice → cerca nel DB → controlla che sia `created` o legato a questa stessa impronta → se ok, segna `active` + salva impronta + risponde "ok + token di sessione".
4. KUIO salva il token e parte.
5. Periodicamente (heartbeat) KUIO richiama il server per sapere se l'abbonamento Plus è attivo → accende/spegne le funzioni Plus.

## Flusso di trasferimento su nuovo PC

- Il cliente sul vecchio PC: "Disattiva qui" → il server libera la licenza.
- Sul nuovo PC: reinserisce lo stesso codice → si rilega alla nuova impronta.
- Limite: es. 2 trasferimenti/anno (configurabile lato server) per evitare abusi.

## Cosa manca per implementare (1-2 sessioni)

- [ ] Generare la chiave segreta vera e custodirla (Cloudflare secret)
- [ ] Creare il database licenze (KV/D1)
- [ ] Scrivere il Worker `api.kuio.ai/activate` (validazione + stati)
- [ ] Configurare il sottodominio `api.kuio.ai`
- [ ] Integrare la richiesta del codice nel wizard di onboarding KUIO
- [ ] Implementare l'impronta PC lato KUIO (Windows MachineGuid + altri)
- [ ] Pannello per Antonio (vedere/sospendere/sbloccare codici)
- [ ] Definire COSA è "base" e COSA è "Plus" (lista funzioni)
