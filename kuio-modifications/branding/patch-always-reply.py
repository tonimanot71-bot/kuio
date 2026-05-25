#!/usr/bin/env python3
"""
KUIO - Patch: KUIO deve rispondere SEMPRE ai messaggi diretti 1:1.

PROBLEMA (due cause distinte, risolte qui):
  1) Il classificatore REPLY/NO_REPLY (mini-chiamata AI) a volte SALTA messaggi
     diretti dell'utente giudicandoli "gia' risposti". Per un segretario e'
     inaccettabile: ogni messaggio diretto deve ricevere risposta.
  2) Anche scavalcato il classificatore, il MODELLO principale a volte produce
     come "risposta" il marker tecnico "[No reply sent: ...]". Lo fa perche'
     quei marker (segnaposto interni dei mancati-risposta) finiscono nello
     STORICO della conversazione passato al modello, e il modello li IMITA e li
     rimanda all'utente. Si auto-avvelena ogni volta che ne produce uno.

SOLUZIONE (deterministica, a livello di LOGICA, indipendente dal modello e
dallo stato del database):
  EDIT 1 - Scavalca il classificatore per TUTTI i messaggi diretti 1:1.
     Il motore ha gia' questo scavalcamento per il canale ACP; lo estendiamo ai
     DM (Telegram privato / email personale) riusando `is_group_chat`. I gruppi
     restano gestiti dal classificatore.
  EDIT 2 - Togli i marker "[No reply sent ...]" dallo storico PRIMA di costruirlo.
     Cosi' ne' il classificatore ne' l'agente li vedono mai: il modello non puo'
     piu' imitarli. Neutralizza anche i marker gia' presenti nel database (non
     serve azzerare la cronologia).

  NON tocca il testo dei prompt (fragile): cambia poche righe di logica. Le
  parentesi attorno a `(is_acp_channel || kuio_is_direct_message)` sono
  necessarie (precedenza + let-chain), quindi clippy non le segnala.

COME:
  Per ogni EDIT cerca un'ancora esatta nei .rs sotto crates/. Idempotente
  (marker) e fail-loud se un'ancora non c'e' (meglio build rossa che patch non
  applicata).

USO: python3 kuio-modifications/branding/patch-always-reply.py
"""
import os, sys

# (descrizione, ancora, sostituzione, marker_idempotenza)
EDITS = [
    (
        "EDIT1 override classificatore per i messaggi diretti",
        (
            "    let reply_intent = if is_acp_channel\n"
            "        && let AssistantChannelOutcome::NoReply {"
        ),
        (
            "    // KUIO: ogni messaggio diretto 1:1 (DM Telegram / email privata) e' una richiesta\n"
            "    // del proprietario e DEVE sempre ricevere risposta. Come per ACP, scavalca il\n"
            "    // classificatore quando vota NO_REPLY su un messaggio diretto. I gruppi restano\n"
            "    // gestiti dal classificatore (chiacchiere tra altre persone -> NO_REPLY consentito).\n"
            "    // Riusa `is_group_chat` gia' calcolato sopra (== is_group_reply_target(reply_target)).\n"
            "    let kuio_is_direct_message = !is_group_chat;\n"
            "    let reply_intent = if (is_acp_channel || kuio_is_direct_message)\n"
            "        && let AssistantChannelOutcome::NoReply {"
        ),
        "kuio_is_direct_message",
    ),
    (
        "EDIT2 togli i marker [No reply sent] dallo storico",
        (
            "    let mut history = vec![ChatMessage::system(system_prompt)];\n"
            "    history.extend(prior_turns);"
        ),
        (
            "    // KUIO: i marker tecnici \"[No reply sent ...]\" sono segnaposto interni dei\n"
            "    // mancati-risposta, NON messaggi reali dell'assistente. Se finiscono nello storico\n"
            "    // passato al modello, questo li imita e li rimanda all'utente come fossero una\n"
            "    // risposta. Li togliamo prima di costruire lo storico: ne' il classificatore ne'\n"
            "    // l'agente li vedono mai (neutralizza anche quelli gia' salvati nel database).\n"
            "    prior_turns.retain(|turn| !turn.content.trim_start().starts_with(\"[No reply sent\"));\n"
            "    let mut history = vec![ChatMessage::system(system_prompt)];\n"
            "    history.extend(prior_turns);"
        ),
        "prior_turns.retain(|turn| !turn.content.trim_start().starts_with(\"[No reply sent\")",
    ),
]

SKIP = {".git", "target", "node_modules"}


def all_rs_files():
    out = []
    for dirpath, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for fn in files:
            if fn.endswith(".rs"):
                out.append(os.path.join(dirpath, fn))
    return out


def apply_edit(desc, anchor, replacement, marker):
    files = all_rs_files()
    # idempotenza: se il marker c'e' gia' da qualche parte, edit gia' applicata
    for fp in files:
        try:
            if marker in open(fp, encoding="utf-8").read():
                print("always-reply [%s]: gia' applicata" % desc)
                return
        except Exception:
            continue
    hits = []
    for fp in files:
        try:
            if anchor in open(fp, encoding="utf-8").read():
                hits.append(fp)
        except Exception:
            continue
    if not hits:
        print(
            "ERRORE patch always-reply [%s]: ancora non trovata in nessun .rs" % desc,
            file=sys.stderr,
        )
        sys.exit(1)
    for p in hits:
        s = open(p, encoding="utf-8").read().replace(anchor, replacement, 1)
        open(p, "w", encoding="utf-8").write(s)
        print("always-reply [%s]: applicata in %s" % (desc, p))


def main():
    for desc, anchor, replacement, marker in EDITS:
        apply_edit(desc, anchor, replacement, marker)
    print("patch always-reply: OK")


if __name__ == "__main__":
    main()
