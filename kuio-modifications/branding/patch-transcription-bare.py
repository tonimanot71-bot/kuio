#!/usr/bin/env python3
"""
KUIO - Patch: accetta nel config il nome bare del provider di trascrizione.

PROBLEMA:
  Il validator del config (schema.rs) richiede formato "<tipo>.<alias>" per
  `agents.<x>.transcription_provider`, e verifica che esista una mappa
  `providers.transcription.<tipo>.<alias>`. Ma il TranscriptionManager runtime
  (transcription.rs) registra i provider single-instance (groq, openai,
  deepgram, assemblyai, google, local_whisper) con chiavi HashMap BARE
  ("local_whisper", "openai", ...). Quindi:
    - Se l'utente scrive "local_whisper" (bare) -> validator fallisce
      [invalid_format], il valore viene scartato e il runtime bailè con
      "Agent has no transcription_provider configured".
    - Se l'utente scrive "local_whisper.default" -> validator e' contento solo
      se esiste anche [providers.transcription.local_whisper.default], e
      comunque la lookup runtime fa MISS perche' la chiave HashMap e' bare
      "local_whisper".
  Risultato: i provider single-instance sono di fatto NON configurabili in
  modo coerente.

SOLUZIONE:
  Patch chirurgico al validator: accetta il bare "groq" | "openai" |
  "deepgram" | "assemblyai" | "google" | "local_whisper" come valore valido
  di `transcription_provider`, senza richiedere il suffisso ".<alias>".
  Cosi' il valore arriva intatto al runtime, che lo trova nella HashMap.

  Una sola riga aggiunta nel loop di validazione. Non cambia la lookup
  runtime; non cambia la struttura del config. NON tocca tts_provider
  (che usa il vero schema aliasato `[providers.tts.<tipo>.<alias>]`).

COME:
  Cerca nel sorgente l'ancora esatta del controllo (dopo "if value.is_empty()
  { continue; }" e prima di "match value.split_once('.')") e vi inserisce la
  nuova clausola. Idempotente (marker) e fail-loud se l'ancora manca.

USO: python3 kuio-modifications/branding/patch-transcription-bare.py
"""
import os, sys

ANCHOR = (
    "                if value.is_empty() {\n"
    "                    continue;\n"
    "                }\n"
    "                match value.split_once('.') {"
)

REPLACEMENT = (
    "                if value.is_empty() {\n"
    "                    continue;\n"
    "                }\n"
    "                // KUIO: i provider transcription single-instance (groq, openai, deepgram,\n"
    "                // assemblyai, google, local_whisper) hanno chiavi HashMap BARE nel\n"
    "                // TranscriptionManager runtime. Accettiamo quindi anche il solo \"<tipo>\"\n"
    "                // (senza \".<alias>\") nel config: il manager runtime fa la lookup esatta\n"
    "                // su quella chiave bare. Altrimenti l'utente sarebbe costretto a scrivere\n"
    "                // \"<tipo>.<alias>\" ma il runtime farebbe MISS.\n"
    "                if *field == \"transcription_provider\"\n"
    "                    && matches!(*value, \"groq\" | \"openai\" | \"deepgram\" | \"assemblyai\" | \"google\" | \"local_whisper\")\n"
    "                {\n"
    "                    continue;\n"
    "                }\n"
    "                match value.split_once('.') {"
)

MARKER = "TranscriptionManager runtime. Accettiamo quindi anche il solo"

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
                print("transcription-bare: gia' applicata in " + fp)
                return
            if ANCHOR in s:
                hits.append(fp)
    if not hits:
        print(
            "ERRORE patch transcription-bare: ancora del validator "
            "(if value.is_empty() ... match value.split_once('.')) non trovata.",
            file=sys.stderr,
        )
        sys.exit(1)
    for p in hits:
        s = open(p, encoding="utf-8").read().replace(ANCHOR, REPLACEMENT, 1)
        open(p, "w", encoding="utf-8").write(s)
        print("transcription-bare: applicata in " + p)
    print("patch transcription-bare: OK (%d file modificati)" % len(hits))


if __name__ == "__main__":
    main()
