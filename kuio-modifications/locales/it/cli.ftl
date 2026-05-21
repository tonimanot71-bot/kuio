cli-about = L'assistente AI più veloce e più leggero.
cli-no-command-provided = Nessun comando specificato.
cli-try-onboard = Prova `zeroclaw onboard` per inizializzare il tuo spazio di lavoro.

cli-onboard-about = Inizializza lo spazio di lavoro e la configurazione
cli-agent-about = Avvia il ciclo dell'agente AI
cli-gateway-about = Gestisci il server gateway (webhook, websocket)
cli-acp-about = Avvia il server ACP (JSON-RPC 2.0 su stdio)
cli-daemon-about = Avvia il daemon autonomo a esecuzione continua
cli-service-about = Gestisci il ciclo di vita del servizio di sistema (servizio utente launchd/systemd)
cli-doctor-about = Esegui la diagnostica su daemon/scheduler/aggiornamento canali
cli-status-about = Mostra lo stato del sistema (dettagli completi)
cli-estop-about = Attiva, ispeziona e ripristina gli stati di arresto di emergenza
cli-cron-about = Configura e gestisci le attività pianificate
cli-models-about = Gestisci i cataloghi dei modelli dei provider
cli-providers-about = Elenca i provider AI supportati
cli-channel-about = Gestisci i canali di comunicazione
cli-integrations-about = Sfoglia oltre 50 integrazioni
cli-skills-about = Gestisci le skill (funzionalità definite dall'utente)
cli-sop-about = Gestisci le procedure operative standard (SOP)
cli-migrate-about = Migra i dati da altri runtime di agenti
cli-auth-about = Gestisci i profili di autenticazione degli abbonamenti dei provider
cli-hardware-about = Rileva e ispeziona l'hardware USB
cli-peripheral-about = Gestisci le periferiche hardware
cli-memory-about = Gestisci le voci di memoria dell'agente
cli-config-about = Gestisci la configurazione di KUIO
cli-update-about = Controlla e applica gli aggiornamenti di KUIO
cli-self-test-about = Esegui i test diagnostici automatici
cli-completions-about = Genera gli script di completamento per la shell
cli-desktop-about = Avvia l'app desktop companion di KUIO

cli-config-schema-about = Esporta lo schema JSON completo della configurazione su stdout
cli-config-list-about = Elenca tutte le proprietà di configurazione con i valori attuali
cli-config-get-about = Ottieni il valore di una proprietà di configurazione
cli-config-set-about = Imposta una proprietà di configurazione (i campi segreti richiedono input mascherato automaticamente)
cli-config-init-about = Inizializza le sezioni non configurate con i valori predefiniti (enabled=false)
cli-config-migrate-about = Migra config.toml alla versione corrente dello schema su disco (preserva i commenti)

cli-service-install-about = Installa l'unità di servizio del daemon per avvio automatico e riavvio
cli-service-start-about = Avvia il servizio del daemon
cli-service-stop-about = Arresta il servizio del daemon
cli-service-restart-about = Riavvia il servizio del daemon per applicare l'ultima configurazione
cli-service-status-about = Controlla lo stato del servizio del daemon
cli-service-uninstall-about = Disinstalla l'unità di servizio del daemon
cli-service-logs-about = Mostra in tempo reale i log del servizio del daemon

cli-channel-list-about = Elenca tutti i canali configurati
cli-channel-start-about = Avvia tutti i canali configurati
cli-channel-doctor-about = Esegui i controlli di salute sui canali configurati
cli-channel-add-about = Aggiungi una nuova configurazione di canale
cli-channel-remove-about = Rimuovi una configurazione di canale
cli-channel-send-about = Invia un messaggio singolo a un canale configurato
cli-wechat-pairing-required = 🔐 Abbinamento WeChat richiesto. Codice di collegamento monouso: {$code}
cli-wechat-send-bind-command = Invia `{$command} <codice>` da WeChat.
cli-wechat-qr-login = 📱 Accesso WeChat tramite QR ({$attempt}/{$max})
cli-wechat-scan-to-connect = Scansiona con WeChat per connetterti.
cli-wechat-qr-url = URL del QR: {$url}
cli-wechat-qr-expired-giving-up = Il codice QR di WeChat è scaduto {$max} volte, rinuncio.
cli-wechat-qr-fetch-failed = Impossibile recuperare il codice QR di WeChat.
cli-wechat-qr-fetch-status-failed = Recupero del codice QR di WeChat fallito ({$status}): {$body}
cli-wechat-missing-response-field = Campo {$field} mancante nella risposta di WeChat.
cli-wechat-scanned-confirm = 👀 Scansionato! Conferma sul telefono...
cli-wechat-qr-expired-refreshing = ⏳ Codice QR scaduto, aggiornamento in corso...
cli-wechat-login-confirmed-missing-field = Accesso confermato ma campo {$field} mancante.
cli-wechat-connected = ✅ WeChat connesso!
cli-wechat-bound-success = ✅ Account WeChat collegato con successo. Ora puoi parlare con KUIO.
cli-wechat-invalid-bind-code = ❌ Codice di collegamento non valido. Riprova.

cli-skills-list-about = Elenca tutte le skill installate
cli-skills-audit-about = Verifica una cartella sorgente di una skill o il nome di una skill installata
cli-skills-install-about = Installa una nuova skill da un URL o da un percorso locale
cli-skills-remove-about = Rimuovi una skill installata
cli-skills-test-about = Esegui la validazione TEST.sh per una skill (o per tutte)
cli-skills-install-start = Installazione della skill da: {$source}
cli-skills-install-resolving-registry = { "  " }Risoluzione di '{$source}' dal registro delle skill...
cli-skills-install-installed-audited = { "  " }{$status} Skill installata e verificata: {$path} ({$files} file analizzati)
cli-skills-install-security-audit-completed = { "  " }Verifica di sicurezza completata con successo.
cli-skills-install-tier-official = Installazione di {$name} v{$version} — Ufficiale (gestita da zeroclaw-labs)
cli-skills-install-tier-community =
    Installazione di {$name} v{$version} — Contributo della community
    Questa skill non è verificata da KUIO. Controlla il contenuto della skill
    ed esegui `zeroclaw skills audit {$name}` prima di concedere qualsiasi
    permesso o di usarla in produzione.

cli-skills-add-scaffolded = Skill {$target} creata in {$dir}

cli-skills-bundle-add-prompt =
    Per creare il bundle di skill '{$alias}' con la cartella '{$dir}', esegui:
      zeroclaw config map-key skill-bundles {$alias}
      zeroclaw config set skill-bundles.{$alias}.directory {$dir}

    (La creazione diretta del bundle tramite `zeroclaw skills bundle add` duplicherebbe la superficie di modifica della configurazione.)

cli-skills-bundle-remove-prompt =
    Per rimuovere il bundle di skill '{$alias}', esegui:
      zeroclaw config map-key-delete skill-bundles {$alias}

    (Rimuove la voce di configurazione; la cartella del bundle su disco rimane al suo posto.)

cli-skills-bundle-list-empty =
    Nessun bundle di skill configurato.
      Creane uno: zeroclaw config set skill-bundles.default.directory shared/skills/default
cli-skills-bundle-list-header = Bundle di skill ({$count}):
cli-skills-bundle-entry = {$alias} -> {$dir}
cli-skills-bundle-include = includi: {$values}
cli-skills-bundle-exclude = escludi: {$values}
cli-skills-bundle-show-no-skills = (nessuna skill installata)
cli-skills-bundle-show-skills-header = skill ({$count}):
cli-skills-bundle-show-skill = {$name}: {$description}

cli-cron-list-about = Elenca tutte le attività pianificate
cli-cron-add-about = Aggiungi una nuova attività pianificata ricorrente
cli-cron-add-at-about = Aggiungi un'attività singola che si attiva a un preciso istante UTC
cli-cron-add-every-about = Aggiungi un'attività che si ripete a intervalli fissi
cli-cron-once-about = Aggiungi un'attività singola che si attiva dopo un ritardo da adesso
cli-cron-remove-about = Rimuovi un'attività pianificata
cli-cron-update-about = Aggiorna uno o più campi di un'attività pianificata esistente
cli-cron-pause-about = Metti in pausa un'attività pianificata
cli-cron-resume-about = Riprendi un'attività in pausa

cli-auth-login-about = Accedi con OAuth (OpenAI Codex o Gemini)
cli-auth-refresh-about = Aggiorna il token di accesso di OpenAI Codex usando il refresh token
cli-auth-logout-about = Rimuovi il profilo di autenticazione
cli-auth-use-about = Imposta il profilo attivo per un provider
cli-auth-list-about = Elenca i profili di autenticazione
cli-auth-status-about = Mostra lo stato dell'autenticazione con il profilo attivo e la scadenza del token

cli-memory-list-about = Elenca le voci di memoria con filtri opzionali
cli-memory-get-about = Ottieni una specifica voce di memoria tramite chiave
cli-memory-stats-about = Mostra le statistiche e lo stato del backend di memoria
cli-memory-clear-about = Cancella le memorie per categoria, per chiave, o cancella tutto

cli-estop-status-about = Mostra lo stato attuale dell'arresto di emergenza
cli-estop-resume-about = Riprendi da un livello di arresto di emergenza attivo

cli-models-refresh-about = Aggiorna e memorizza nella cache i modelli del provider
cli-models-list-about = Elenca i modelli in cache per un provider
cli-models-set-about = Imposta il modello predefinito nella configurazione
cli-models-status-about = Mostra la configurazione attuale del modello e lo stato della cache

cli-doctor-models-about = Sonda i cataloghi dei modelli tra i provider e segnala la disponibilità
cli-doctor-traces-about = Interroga gli eventi di traccia del runtime (diagnostica strumenti e risposte dei modelli)

cli-hardware-discover-about = Elenca i dispositivi USB e mostra le schede conosciute
cli-hardware-introspect-about = Ispeziona un dispositivo tramite il suo numero di serie o percorso
cli-hardware-info-about = Ottieni informazioni sul chip via USB usando probe-rs su ST-Link

cli-peripheral-list-about = Elenca le periferiche configurate
cli-peripheral-add-about = Aggiungi una periferica per tipo di scheda e percorso di trasporto
cli-peripheral-flash-about = Carica il firmware KUIO su una scheda Arduino

cli-sop-list-about = Elenca le SOP caricate
cli-sop-validate-about = Valida le definizioni delle SOP
cli-sop-show-about = Mostra i dettagli di una SOP

cli-migrate-openclaw-about = Importa la memoria da uno spazio di lavoro OpenClaw in questo spazio di lavoro KUIO

cli-agent-long-about =
    Avvia il ciclo dell'agente AI.

    Avvia una sessione di chat interattiva con il provider AI configurato. Usa --message per richieste singole senza entrare in modalità interattiva.

    Esempi:
      zeroclaw agent                              # sessione interattiva
      zeroclaw agent -m "Riassumi i log di oggi"  # messaggio singolo
      zeroclaw agent -p anthropic --model claude-sonnet-4-20250514
      zeroclaw agent --peripheral nucleo-f401re:/dev/ttyACM0

cli-gateway-long-about =
    Gestisci il server gateway (webhook, websocket).

    Avvia, riavvia o ispeziona il gateway HTTP/WebSocket che accetta gli eventi webhook in arrivo e le connessioni WebSocket.

    Esempi:
      zeroclaw gateway start              # avvia il gateway
      zeroclaw gateway restart            # riavvia il gateway
      zeroclaw gateway get-paircode       # mostra il codice di abbinamento

cli-acp-long-about =
    Avvia il server ACP (JSON-RPC 2.0 su stdio).

    Avvia un server JSON-RPC 2.0 su stdin/stdout per l'integrazione con IDE e strumenti. Supporta la gestione delle sessioni e lo streaming delle risposte dell'agente come notifiche.

    Metodi: initialize, session/new, session/prompt, session/stop.

    Esempi:
      zeroclaw acp                        # avvia il server ACP
      zeroclaw acp --max-sessions 5       # limita le sessioni concorrenti

cli-daemon-long-about =
    Avvia il daemon autonomo a esecuzione continua.

    Avvia il runtime completo di KUIO: server gateway, tutti i canali configurati (Telegram, Discord, Slack, ecc.), monitoraggio heartbeat e scheduler cron. Questo è il modo consigliato per eseguire KUIO in produzione o come assistente sempre attivo.

    Usa 'zeroclaw service install' per registrare il daemon come servizio di sistema (systemd/launchd) per l'avvio automatico al boot.

    Esempi:
      zeroclaw daemon                   # usa i valori predefiniti della configurazione
      zeroclaw daemon -p 9090           # gateway sulla porta 9090
      zeroclaw daemon --host 127.0.0.1  # solo localhost

cli-cron-long-about =
    Configura e gestisci le attività pianificate.

    Pianifica attività ricorrenti, singole o a intervalli usando espressioni cron, timestamp RFC 3339, durate o intervalli fissi.

    Le espressioni cron usano il formato standard a 5 campi: 'min ora giorno mese giorno-settimana'. Il fuso orario predefinito è UTC; sovrascrivilo con --tz e un nome di fuso orario IANA.

    Esempi:
      zeroclaw cron list
      zeroclaw cron add '0 9 * * 1-5' 'Buongiorno' --tz America/New_York --agent
      zeroclaw cron add '*/30 * * * *' 'Controlla lo stato del sistema' --agent
      zeroclaw cron add '*/5 * * * *' 'echo ok'
      zeroclaw cron add-at 2025-01-15T14:00:00Z 'Invia promemoria' --agent
      zeroclaw cron add-every 60000 'Ping heartbeat'
      zeroclaw cron once 30m 'Esegui backup tra 30 minuti' --agent
      zeroclaw cron pause TASK_ID
      zeroclaw cron update TASK_ID --expression '0 8 * * *' --tz Europe/London

cli-channel-long-about =
    Gestisci i canali di comunicazione.

    Aggiungi, rimuovi, elenca, invia ed esegui controlli di salute sui canali che collegano KUIO alle piattaforme di messaggistica. Tipi di canale supportati: telegram, discord, slack, whatsapp, matrix, imessage, email.

    Esempi:
      zeroclaw channel list
      zeroclaw channel doctor
      zeroclaw channel add telegram '{ "{" }"bot_token":"...","name":"my-bot"{ "}" }'
      zeroclaw channel remove my-bot
      zeroclaw channel bind-telegram zeroclaw_user
      zeroclaw channel send 'Allarme!' --channel-id telegram --recipient 123456789

cli-hardware-long-about =
    Rileva e ispeziona l'hardware USB.

    Elenca i dispositivi USB connessi, identifica le schede di sviluppo conosciute (STM32 Nucleo, Arduino, ESP32) e recupera le informazioni sul chip tramite probe-rs / ST-Link.

    Esempi:
      zeroclaw hardware discover
      zeroclaw hardware introspect /dev/ttyACM0
      zeroclaw hardware info --chip STM32F401RETx

cli-peripheral-long-about =
    Gestisci le periferiche hardware.

    Aggiungi, elenca, carica firmware e configura schede hardware che espongono strumenti all'agente (GPIO, sensori, attuatori). Schede supportate: nucleo-f401re, rpi-gpio, esp32, arduino-uno.

    Esempi:
      zeroclaw peripheral list
      zeroclaw peripheral add nucleo-f401re /dev/ttyACM0
      zeroclaw peripheral add rpi-gpio native
      zeroclaw peripheral flash --port /dev/cu.usbmodem12345
      zeroclaw peripheral flash-nucleo

cli-memory-long-about =
    Gestisci le voci di memoria dell'agente.

    Elenca, ispeziona e cancella le voci di memoria salvate dall'agente. Supporta il filtraggio per categoria e sessione, la paginazione e la cancellazione in blocco con conferma.

    Esempi:
      zeroclaw memory stats
      zeroclaw memory list
      zeroclaw memory list --category core --limit 10
      zeroclaw memory get KEY
      zeroclaw memory clear --category conversation --yes

cli-config-long-about =
    Gestisci la configurazione di KUIO.

    Visualizza, imposta o inizializza le proprietà di configurazione tramite percorso puntato. Usa 'schema' per esportare lo schema JSON completo del file di configurazione.

    Le proprietà sono indirizzate tramite percorso puntato (es. channels.matrix.mention-only).
    I campi segreti (chiavi API, token) usano automaticamente l'input mascherato.
    I campi enum offrono la selezione interattiva quando il valore viene omesso.

    Esempi:
      zeroclaw config list                                  # elenca tutte le proprietà
      zeroclaw config list --secrets                        # elenca solo i segreti
      zeroclaw config list --filter channels.matrix         # filtra per prefisso
      zeroclaw config get channels.matrix.mention-only      # ottieni un valore
      zeroclaw config set channels.matrix.mention-only true # imposta un valore
      zeroclaw config set channels.matrix.access-token      # segreto: input mascherato
      zeroclaw config set channels.matrix.stream-mode       # enum: selezione interattiva
      zeroclaw config init channels.matrix                  # inizializza la sezione con i valori predefiniti
      zeroclaw config schema                                # stampa lo schema JSON su stdout
      zeroclaw config schema > schema.json

    Il completamento automatico del percorso delle proprietà è incluso automaticamente in `zeroclaw completions <shell>`.

cli-update-long-about =
    Controlla e applica gli aggiornamenti di KUIO.

    Per impostazione predefinita, scarica e installa l'ultima versione con una pipeline a 6 fasi: verifica preliminare, download, backup, validazione, sostituzione e test di funzionamento. Ripristino automatico in caso di errore.

    Usa --check per controllare solo gli aggiornamenti senza installarli.
    Usa --force per saltare la richiesta di conferma.
    Usa --version per puntare a una versione specifica invece dell'ultima.

    Esempi:
      zeroclaw update                      # scarica e installa l'ultima versione
      zeroclaw update --check              # controlla soltanto, non installare
      zeroclaw update --force              # installa senza conferma
      zeroclaw update --version 0.6.0      # installa una versione specifica

cli-self-test-long-about =
    Esegui i test diagnostici automatici per verificare l'installazione di KUIO.

    Per impostazione predefinita, esegue la suite completa di test inclusi i controlli di rete (salute del gateway, andata e ritorno della memoria). Usa --quick per saltare i controlli di rete e una validazione offline più rapida.

    Esempi:
      zeroclaw self-test             # suite completa
      zeroclaw self-test --quick     # solo controlli rapidi (senza rete)

cli-skills-install-suggestion =
    Sembra che questa richiesta abbia bisogno della skill `{$name}`, ma non è installata.

    Funzionalità corrispondente: {$matched}
    Successivo: Esegui `{$install_command}` per installarla.

cli-completions-long-about =
    Genera gli script di completamento della shell per `zeroclaw`.

    Lo script viene stampato su stdout in modo da poter essere caricato direttamente:

    Esempi:
      source <(zeroclaw completions bash)
      zeroclaw completions zsh > ~/.zfunc/_zeroclaw
      zeroclaw completions fish > ~/.config/fish/completions/zeroclaw.fish

cli-desktop-long-about =
    Avvia l'app desktop companion di KUIO.

    L'app companion è una leggera applicazione nella barra dei menu / area di notifica che si connette allo stesso gateway della CLI. Fornisce accesso rapido alla dashboard, al monitoraggio dello stato e all'abbinamento dei dispositivi.

    Usa --install per scaricare l'app companion precompilata per la tua piattaforma.

    Esempi:
      zeroclaw desktop              # avvia l'app companion
      zeroclaw desktop --install    # scaricala e installala

# Risposta lato canale emessa quando l'invio della chat viene rifiutato perché il
# gateway non ha un modello configurato. Usata dai gestori webhook dei canali
# del crate gateway (WhatsApp, Linq, WATI, Nextcloud Talk).
channel-needs-onboarding-reply = Questo agente non è ancora completamente configurato. L'operatore deve completare la configurazione iniziale prima che io possa rispondere.

channel-whatsapp-web-feature-missing-warning =   ⚠ WhatsApp Web è configurato ma la funzionalità 'whatsapp-web' non è compilata.
channel-whatsapp-web-feature-missing-build =     Compila/esegui con: cargo build --features whatsapp-web
channel-whatsapp-web-feature-missing-install =     Se installato nel PATH, reinstalla con: cargo install --path . --force --locked --features whatsapp-web
channel-whatsapp-web-feature-missing-error = Il canale WhatsApp Web richiede la funzionalità 'whatsapp-web'. Abilitala con: cargo build --features whatsapp-web (oppure, se installato nel PATH: cargo install --path . --force --locked --features whatsapp-web)
