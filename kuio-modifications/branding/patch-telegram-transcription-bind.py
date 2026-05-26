#!/usr/bin/env python3
"""
KUIO - Patch: il manager di trascrizione del canale Telegram va LEGATO al
provider configurato, altrimenti i messaggi vocali falliscono SEMPRE.

PROBLEMA:
  In `crates/zeroclaw-channels/src/telegram.rs::with_transcription`, dopo aver
  creato il `TranscriptionManager` da `TranscriptionConfig`, il manager NON
  viene mai bound a un provider tramite `with_agent_transcription_provider`.
  Risultato: il suo `agent_transcription_provider` resta vuoto e, all'arrivo
  di un voice message, `manager.transcribe()` bailè con
  "Agent has no transcription_provider configured ... Set
  agent.<alias>.transcription_provider = \"<type>.<alias>\" ...".
  Il config TOML e' irrilevante: il bug e' nel codice del canale.

  Il canale Line (`line.rs:663-674`) gia' fa il binding corretto in modo
  auto-detect: guarda quale provider e' presente in `config.*` e fa
  `with_agent_transcription_provider("<tipo>")` con la chiave bare con cui
  il manager registra il provider (groq/openai/deepgram/assemblyai/google/
  local_whisper). Telegram dovrebbe fare lo stesso. Questa patch lo aggiunge.

SOLUZIONE (chirurgica, una sola modifica):
  Subito dopo che il manager viene creato con successo, lo legchiamo al
  provider configurato esattamente come line.rs. Cosi' i voice message di
  Telegram vengono trascritti dal provider scelto (ad es. local_whisper).
  Non tocca altri canali (slack, qq, ecc. hanno il loro stesso bug ma
  Antonio non li usa: li sistemeremo se servirà).

COME:
  Cerca l'ancora esatta del blocco Ok(m) => { ... transcription_manager =
  Some(Arc::new(m)) ... } in telegram.rs e inserisce il binding auto-detect.
  Idempotente (marker) e fail-loud se l'ancora manca.

USO: python3 kuio-modifications/branding/patch-telegram-transcription-bind.py
"""
import os, sys

ANCHOR = (
    "        match super::transcription::TranscriptionManager::new(&config) {\n"
    "            Ok(m) => {\n"
    "                self.transcription_manager = Some(std::sync::Arc::new(m));\n"
    "                self.transcription = Some(config);\n"
    "            }"
)

REPLACEMENT = (
    "        match super::transcription::TranscriptionManager::new(&config) {\n"
    "            Ok(m) => {\n"
    "                // KUIO: lega il manager al provider configurato (single-instance),\n"
    "                // come fa line.rs. Senza questo, transcribe() bailè con\n"
    "                // \"Agent has no transcription_provider configured\" perché il\n"
    "                // manager creato qui non viene mai bound nel flusso Telegram\n"
    "                // (a differenza del media_pipeline nell'orchestrator).\n"
    "                let m = if config.local_whisper.is_some() {\n"
    "                    m.with_agent_transcription_provider(\"local_whisper\")\n"
    "                } else if config.openai.is_some() {\n"
    "                    m.with_agent_transcription_provider(\"openai\")\n"
    "                } else if config.deepgram.is_some() {\n"
    "                    m.with_agent_transcription_provider(\"deepgram\")\n"
    "                } else if config.assemblyai.is_some() {\n"
    "                    m.with_agent_transcription_provider(\"assemblyai\")\n"
    "                } else if config.google.is_some() {\n"
    "                    m.with_agent_transcription_provider(\"google\")\n"
    "                } else {\n"
    "                    m.with_agent_transcription_provider(\"groq\")\n"
    "                };\n"
    "                self.transcription_manager = Some(std::sync::Arc::new(m));\n"
    "                self.transcription = Some(config);\n"
    "            }"
)

MARKER = "KUIO: lega il manager al provider configurato (single-instance)"

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
                print("telegram-transcription-bind: gia' applicata in " + fp)
                return
            if ANCHOR in s:
                hits.append(fp)
    if not hits:
        print(
            "ERRORE patch telegram-transcription-bind: ancora "
            "(match TranscriptionManager::new(&config) ... transcription_manager = Some(Arc::new(m)))"
            " non trovata.",
            file=sys.stderr,
        )
        sys.exit(1)
    for p in hits:
        s = open(p, encoding="utf-8").read().replace(ANCHOR, REPLACEMENT, 1)
        open(p, "w", encoding="utf-8").write(s)
        print("telegram-transcription-bind: applicata in " + p)
    print("patch telegram-transcription-bind: OK (%d file modificati)" % len(hits))


if __name__ == "__main__":
    main()
