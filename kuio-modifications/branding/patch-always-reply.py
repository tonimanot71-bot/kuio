#!/usr/bin/env python3
"""
KUIO - Patch: KUIO deve rispondere SEMPRE ai messaggi diretti 1:1.

PROBLEMA:
  L'agente usa un classificatore REPLY/NO_REPLY che a volte SALTA messaggi
  diretti dell'utente giudicandoli "gia' risposti / informational" (es. stessa
  domanda ripetuta, anche in giorni diversi). Per un segretario e' inaccettabile:
  ogni messaggio diretto dell'utente deve ricevere risposta.

SOLUZIONE (a basso rischio):
  Rafforza il PROMPT del classificatore (una stringa di testo) aggiungendo una
  direttiva: un messaggio diretto 1:1 dell'utente e' SEMPRE call-to-action ->
  sempre REPLY, mai NO_REPLY. NON tocca la logica del codice, quindi non puo'
  rompere la compilazione.

COME:
  Cerca in tutti i .rs sotto crates/ la frase esatta del prompt del classificatore
  (presa dal binario) e vi inserisce la direttiva subito dopo. Fail-loud se non la
  trova (meglio build fallita che patch silenziosamente non applicata).

USO: python3 kuio-modifications/branding/patch-always-reply.py
"""
import os, sys

ANCHOR = "system broadcasts, or content the embedded system prompt explicitly tells the assistant to ignore."
ADD = " A direct one-to-one message from the user (a private direct chat, or an email addressed to you) is NEVER in this category: it is ALWAYS a call to action and MUST ALWAYS receive REPLY, even when it is identical or very similar to an earlier message, and even if you believe you already answered it before. NEVER emit NO_REPLY for a direct one-to-one message from the user; NO_REPLY is only for group chatter between other people or for system broadcasts."
MARKER = "is NEVER in this category"


EXTS = (".rs", ".ftl", ".txt", ".md", ".toml", ".json", ".yaml", ".yml", ".hbs", ".tmpl")
SKIP = {".git", "target", "node_modules"}

def main():
    targets = []
    for dirpath, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for fn in files:
            if fn.endswith(EXTS):
                fp = os.path.join(dirpath, fn)
                try:
                    s = open(fp, encoding="utf-8").read()
                except Exception:
                    continue
                if ANCHOR in s:
                    targets.append(fp)
    if not targets:
        print("ERRORE patch always-reply: frase del prompt classificatore non trovata in nessun .rs", file=sys.stderr)
        sys.exit(1)
    changed = 0
    for p in targets:
        s = open(p, encoding="utf-8").read()
        if MARKER in s:
            print("always-reply: gia' applicata in " + p)
            continue
        s = s.replace(ANCHOR, ANCHOR + ADD, 1)
        open(p, "w", encoding="utf-8").write(s)
        print("always-reply: applicata in " + p)
        changed += 1
    print("patch always-reply: OK (%d file modificati, %d totali con anchor)" % (changed, len(targets)))


if __name__ == "__main__":
    main()
