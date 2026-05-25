#!/usr/bin/env python3
"""
KUIO - Patch: KUIO deve rispondere SEMPRE ai messaggi diretti 1:1.

PROBLEMA:
  L'agente usa un classificatore REPLY/NO_REPLY che a volte SALTA messaggi
  diretti dell'utente giudicandoli "gia' risposti / informational" (es. stessa
  domanda ripetuta, anche in giorni diversi). Per un segretario e' inaccettabile:
  ogni messaggio diretto del proprietario deve ricevere risposta.

SOLUZIONE (deterministica, a livello di LOGICA, non di prompt):
  Il motore ha gia' uno scavalcamento del classificatore per il canale ACP:
  se il classificatore vota NO_REPLY, su ACP viene forzato REPLY. Estendiamo
  quello stesso scavalcamento a TUTTI i messaggi diretti 1:1 (DM Telegram,
  email privata): se non e' un gruppo, si risponde sempre. I gruppi restano
  gestiti dal classificatore (chiacchiere tra altre persone -> NO_REPLY ok).

  Si appoggia a `is_group_reply_target(&msg.reply_target)` gia' presente nello
  stesso modulo: e' True solo per i gruppi (WhatsApp @g.us o prefisso "group:").
  Quindi `!is_group_reply_target(...)` == messaggio diretto.

  NON tocca il testo del prompt (fragile): cambia una sola condizione `if`.
  Le parentesi attorno a `(is_acp_channel || kuio_is_direct_message)` sono
  necessarie (precedenza + let-chain), quindi clippy non le segnala come ridondanti.

COME:
  Cerca nei .rs sotto crates/ l'ancora esatta del blocco di scavalcamento e
  inserisce la variabile + estende la condizione. Idempotente (marker) e
  fail-loud se l'ancora non c'e' (meglio build rossa che patch non applicata).

USO: python3 kuio-modifications/branding/patch-always-reply.py
"""
import os, sys

ANCHOR = (
    "    let reply_intent = if is_acp_channel\n"
    "        && let AssistantChannelOutcome::NoReply {"
)

REPLACEMENT = (
    "    // KUIO: ogni messaggio diretto 1:1 (DM Telegram / email privata) e' una richiesta\n"
    "    // del proprietario e DEVE sempre ricevere risposta. Come per ACP, scavalca il\n"
    "    // classificatore quando vota NO_REPLY su un messaggio diretto. I gruppi restano\n"
    "    // gestiti dal classificatore (chiacchiere tra altre persone -> NO_REPLY consentito).\n"
    "    // Riusa `is_group_chat` gia' calcolato sopra (== is_group_reply_target(reply_target)).\n"
    "    let kuio_is_direct_message = !is_group_chat;\n"
    "    let reply_intent = if (is_acp_channel || kuio_is_direct_message)\n"
    "        && let AssistantChannelOutcome::NoReply {"
)

MARKER = "kuio_is_direct_message"

SKIP = {".git", "target", "node_modules"}


def main():
    hits = []
    for dirpath, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for fn in files:
            if not fn.endswith(".rs"):
                continue
            fp = os.path.join(dirpath, fn)
            try:
                s = open(fp, encoding="utf-8").read()
            except Exception:
                continue
            if MARKER in s:
                print("always-reply: gia' applicata in " + fp)
                return
            if ANCHOR in s:
                hits.append(fp)
    if not hits:
        print(
            "ERRORE patch always-reply: ancora del blocco di scavalcamento "
            "(let reply_intent = if is_acp_channel ...) non trovata in nessun .rs",
            file=sys.stderr,
        )
        sys.exit(1)
    for p in hits:
        s = open(p, encoding="utf-8").read()
        s = s.replace(ANCHOR, REPLACEMENT, 1)
        open(p, "w", encoding="utf-8").write(s)
        print("always-reply: applicata in " + p)
    print("patch always-reply: OK (%d file modificati)" % len(hits))


if __name__ == "__main__":
    main()
