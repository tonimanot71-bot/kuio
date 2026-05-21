# Descrizioni degli strumenti in italiano
#
# Le chiavi seguono il modello: tool-{nome-con-trattini}
# es. "file_read" → "tool-file-read", "web_search_tool" → "tool-web-search-tool"
#
# Le { e } letterali nei valori devono essere protette come {"{"}  e  {"}"} rispettivamente.

tool-backup = Crea, elenca, verifica e ripristina i backup dello spazio di lavoro

tool-browser = Automazione web/browser con backend modulari (agent-browser, rust-native, computer_use). Supporta azioni sul DOM più azioni opzionali a livello di sistema operativo (mouse_move, mouse_click, mouse_drag, key_type, key_press, screen_capture) tramite un sidecar computer-use. Usa 'snapshot' per mappare gli elementi interattivi ai riferimenti (@e1, @e2). Applica browser.allowed_domains per le azioni di apertura.

tool-browser-delegate = Delega le attività basate su browser a una CLI dotata di browser per interagire con applicazioni web come Teams, Outlook, Jira, Confluence

tool-browser-open = Apri un URL HTTPS approvato nel browser di sistema. Vincoli di sicurezza: solo domini nella lista consentita, nessun host locale/privato, nessuno scraping.

tool-cloud-ops = Strumento di consulenza per la trasformazione cloud. Analizza i piani IaC, valuta i percorsi di migrazione, esamina i costi e verifica l'architettura rispetto ai pilastri del Well-Architected Framework. Sola lettura: non crea né modifica risorse cloud.

tool-cloud-patterns = Libreria di pattern cloud. Data la descrizione di un carico di lavoro, suggerisce i pattern architetturali cloud-native applicabili (containerizzazione, serverless, modernizzazione dei database, ecc.).

tool-composio = Esegui azioni su oltre 1000 app tramite Composio (Gmail, Notion, GitHub, Slack, ecc.). Usa action='list' per vedere le azioni disponibili (inclusi i nomi dei parametri). action='execute' con action_name/tool_slug e params per eseguire un'azione. Se non sei sicuro dei parametri esatti, passa invece 'text' con una descrizione in linguaggio naturale di ciò che vuoi (Composio risolverà i parametri corretti tramite NLP). action='list_accounts' o action='connected_accounts' per elencare gli account collegati via OAuth. action='connect' con app/auth_config_id per ottenere l'URL OAuth. connected_account_id viene risolto automaticamente se omesso.

tool-content-search = Cerca nel contenuto dei file tramite pattern regex all'interno dello spazio di lavoro. Supporta ripgrep (rg) con fallback su grep. Modalità di output: 'content' (righe corrispondenti con contesto), 'files_with_matches' (solo percorsi dei file), 'count' (numero di corrispondenze per file). Esempio: pattern='fn main', include='*.rs', output_mode='content'.

tool-cron-add = Crea un'attività cron pianificata (shell o agente) con pianificazioni cron/at/every. Usa job_type='agent' con un prompt per eseguire l'agente AI a orario. Per consegnare l'output a un canale (Discord, Telegram, Slack, Mattermost, Matrix), imposta delivery={"{"}"mode":"announce","channel":"discord","to":"<id_canale_o_id_chat>"{"}"}. Questo è lo strumento preferito per inviare messaggi pianificati/ritardati agli utenti tramite i canali.

tool-cron-list = Elenca tutte le attività cron pianificate

tool-cron-remove = Rimuovi un'attività cron tramite id

tool-cron-run = Forza l'esecuzione immediata di un'attività cron e registra la cronologia delle esecuzioni

tool-cron-runs = Elenca la cronologia recente delle esecuzioni di un'attività cron

tool-cron-update = Modifica un'attività cron esistente (pianificazione, comando, prompt, abilitazione, consegna, modello, ecc.)

tool-data-management = Conservazione dei dati dello spazio di lavoro, eliminazione e statistiche di archiviazione

tool-delegate = Delega un'attività secondaria a un agente specializzato. Usa quando: un'attività trae beneficio da un modello diverso (es. riassunto rapido, ragionamento approfondito, generazione di codice). L'agente secondario esegue un singolo prompt per impostazione predefinita; con agentic=true può iterare con un ciclo di chiamate a strumenti filtrato.

tool-file-edit = Modifica un file sostituendo una corrispondenza esatta di stringa con un nuovo contenuto

tool-file-read = Leggi il contenuto di un file con i numeri di riga. Supporta la lettura parziale tramite offset e limit. Estrae il testo dai PDF; gli altri file binari vengono letti con conversione UTF-8 con perdita.

tool-file-write = Scrivi contenuti in un file nello spazio di lavoro

tool-git-operations = Esegui operazioni Git strutturate (status, diff, log, branch, commit, add, checkout, stash). Fornisce output JSON analizzato e si integra con la policy di sicurezza per i controlli di autonomia.

tool-glob-search = Cerca file che corrispondono a un pattern glob all'interno dello spazio di lavoro. Restituisce un elenco ordinato di percorsi di file corrispondenti relativi alla radice dello spazio di lavoro. Esempi: '**/*.rs' (tutti i file Rust), 'src/**/mod.rs' (tutti i mod.rs in src).

tool-google-workspace = Interagisci con i servizi di Google Workspace (Drive, Gmail, Calendar, Sheets, Docs, ecc.) tramite la CLI gws. Richiede che gws sia installato e autenticato.

tool-hardware-board-info = Restituisce le informazioni complete sulla scheda (chip, architettura, mappa di memoria) per l'hardware connesso. Usa quando: l'utente chiede 'info sulla scheda', 'che scheda ho', 'hardware connesso', 'info sul chip', 'che hardware', o 'mappa di memoria'.

tool-hardware-memory-map = Restituisce la mappa di memoria (intervalli di indirizzi flash e RAM) per l'hardware connesso. Usa quando: l'utente chiede 'indirizzi di memoria superiori e inferiori', 'mappa di memoria', 'spazio di indirizzamento', o 'indirizzi leggibili'. Restituisce gli intervalli flash/RAM dai datasheet.

tool-hardware-memory-read = Leggi i valori effettivi di memoria/registri da Nucleo via USB. Usa quando: l'utente chiede di 'leggere i valori dei registri', 'leggere la memoria a un indirizzo', 'dump della memoria', 'memoria inferiore 0-126', o 'fornisci indirizzo e valore'. Restituisce un dump esadecimale. Richiede Nucleo connesso via USB e la funzionalità probe. Parametri: address (esadecimale, es. 0x20000000 per l'inizio della RAM), length (byte, predefinito 128).

tool-http-request = Effettua richieste HTTP verso API esterne. Supporta i metodi GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS. Vincoli di sicurezza: solo domini nella lista consentita, nessun host locale/privato, timeout e limiti sulla dimensione delle risposte configurabili.

tool-image-info = Leggi i metadati di un file immagine (formato, dimensioni, peso) e, opzionalmente, restituisci i dati codificati in base64.

tool-jira = Interagisci con Jira: ottieni ticket con livello di dettaglio configurabile, cerca problemi con JQL e aggiungi commenti con supporto per menzioni e formattazione.

tool-knowledge = Gestisci un grafo di conoscenza di decisioni architetturali, pattern di soluzione, lezioni apprese ed esperti. Azioni: capture, search, relate, suggest, expert_find, lessons_extract, graph_stats.

tool-linkedin = Gestisci LinkedIn: crea post, elenca i tuoi post, commenta, reagisci, elimina post, visualizza l'engagement, ottieni informazioni sul profilo e leggi la strategia di contenuti configurata. Richiede le credenziali LINKEDIN_* nel file .env.

tool-discord-search = Cerca nella cronologia dei messaggi Discord salvata in discord.db. Usalo per trovare messaggi passati, riassumere l'attività di un canale o consultare ciò che gli utenti hanno detto. Supporta la ricerca per parola chiave e filtri opzionali: channel_id, since, until.

tool-memory-forget = Rimuovi una memoria tramite chiave. Usalo per eliminare fatti obsoleti o dati sensibili. Restituisce se la memoria è stata trovata e rimossa.

tool-memory-recall = Cerca nella memoria a lungo termine fatti, preferenze o contesto pertinenti. Restituisce risultati con punteggio ordinati per rilevanza. Ometti la query o passa un semplice * per restituire le memorie recenti.

tool-memory-store = Salva un fatto, una preferenza o una nota nella memoria a lungo termine. Usa la categoria 'core' per i fatti permanenti, 'daily' per le note di sessione, 'conversation' per il contesto della chat, o un nome di categoria personalizzato.

tool-microsoft365 = Integrazione con Microsoft 365: gestisci la posta di Outlook, i messaggi di Teams, gli eventi del Calendario, i file di OneDrive e la ricerca in SharePoint tramite l'API Microsoft Graph

tool-model-routing-config = Gestisci le impostazioni del modello predefinito, le rotte provider/modello basate su scenari, le regole di classificazione e i profili agente con alias

tool-notion = Interagisci con Notion: interroga i database, leggi/crea/aggiorna pagine e cerca nello spazio di lavoro.

tool-pdf-read = Estrai testo semplice da un file PDF nello spazio di lavoro. Restituisce tutto il testo leggibile. I PDF solo immagine o crittografati restituiscono un risultato vuoto. Richiede la funzionalità di build 'rag-pdf'.

tool-project-intel = Intelligence sulla consegna dei progetti: genera report di stato, rileva rischi, redige aggiornamenti per i clienti, riassume gli sprint e stima l'impegno. Strumento di analisi in sola lettura.

tool-proxy-config = Gestisci le impostazioni proxy di KUIO (ambito: environment | zeroclaw | services), inclusa l'applicazione dell'ambiente di runtime e di processo

tool-pushover = Invia una notifica Pushover al tuo dispositivo. Richiede PUSHOVER_TOKEN e PUSHOVER_USER_KEY nel file .env.

tool-schedule = Gestisci attività pianificate solo-shell. Azioni: create/add/once/list/get/cancel/remove/pause/resume. ATTENZIONE: Questo strumento crea attività shell il cui output viene solo registrato, NON consegnato ad alcun canale. Per inviare un messaggio pianificato a Discord/Telegram/Slack/Matrix, usa lo strumento cron_add con job_type='agent' e una configurazione di consegna come {"{"}"mode":"announce","channel":"discord","to":"<id_canale>"{"}"}.

tool-screenshot = Cattura uno screenshot dello schermo attuale. Restituisce il percorso del file e i dati PNG codificati in base64.

tool-security-ops = Strumento per le operazioni di sicurezza per servizi di cybersecurity gestiti. Azioni: triage_alert (classifica/prioritizza gli avvisi), run_playbook (esegui i passi di risposta agli incidenti), parse_vulnerability (analizza i risultati delle scansioni), generate_report (crea report sullo stato di sicurezza), list_playbooks (elenca i playbook disponibili), alert_stats (riassumi le metriche degli avvisi).

tool-shell = Esegui un comando shell nella cartella dello spazio di lavoro

tool-sop-advance = Segnala il risultato del passo SOP corrente e avanza al passo successivo. Fornisci il run_id, se il passo è riuscito o fallito, e un breve riepilogo dell'output.

tool-sop-approve = Approva un passo SOP in sospeso in attesa dell'approvazione dell'operatore. Restituisce l'istruzione del passo da eseguire. Usa sop_status per vedere quali esecuzioni sono in attesa.

tool-sop-execute = Attiva manualmente una Procedura Operativa Standard (SOP) per nome. Restituisce l'ID dell'esecuzione e l'istruzione del primo passo. Usa sop_list per vedere le SOP disponibili.

tool-sop-list = Elenca tutte le Procedure Operative Standard (SOP) caricate con i loro trigger, priorità, numero di passi e numero di esecuzioni attive. Filtra facoltativamente per nome o priorità.

tool-sop-status = Interroga lo stato di esecuzione di una SOP. Fornisci run_id per un'esecuzione specifica, o sop_name per elencare le esecuzioni di quella SOP. Senza argomenti, mostra tutte le esecuzioni attive.

tool-tool-search = Recupera le definizioni complete dello schema per gli strumenti MCP differiti in modo da poterli chiamare. Usa "select:nome1,nome2" per la corrispondenza esatta o parole chiave per cercare.

tool-web-fetch = Recupera una pagina web e restituisce il suo contenuto come testo semplice e pulito. Le pagine HTML vengono convertite automaticamente in testo leggibile. Le risposte JSON e in testo semplice vengono restituite così come sono. Solo richieste GET; segue i reindirizzamenti. Sicurezza: solo domini nella lista consentita, nessun host locale/privato.

tool-web-search-tool = Cerca informazioni sul web. Restituisce risultati di ricerca pertinenti con titoli, URL e descrizioni. Usalo per trovare informazioni attuali, notizie o argomenti di ricerca.

tool-workspace = Gestisci spazi di lavoro multi-cliente. Sottocomandi: list, switch, create, info, export. Ogni spazio di lavoro fornisce memoria, audit, segreti e restrizioni sugli strumenti isolati.

tool-weather = Ottieni le condizioni meteo attuali e le previsioni per qualsiasi località nel mondo. Supporta nomi di città (in qualsiasi lingua o alfabeto), codici aeroportuali IATA (es. 'LAX'), coordinate GPS (es. '51.5,-0.1'), codici postali e geolocalizzazione basata su dominio. Restituisce temperatura, temperatura percepita, umidità, velocità/direzione del vento, precipitazioni, visibilità, pressione, indice UV e copertura nuvolosa. Previsioni opzionali da 0 a 3 giorni con dettaglio orario. Le unità sono metriche per impostazione predefinita (°C, km/h, mm) ma possono essere impostate su imperiali (°F, mph, pollici) per ogni richiesta. Nessuna chiave API richiesta.
