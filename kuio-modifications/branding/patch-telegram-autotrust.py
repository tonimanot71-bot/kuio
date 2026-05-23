#!/usr/bin/env python3
"""
KUIO - Patch "auto-fiducia del proprietario" per il canale Telegram.

PROBLEMA (ZeroClaw di default):
  Al primo contatto, il bot Telegram pretende l'"approvazione operatore":
  l'utente deve eseguire `/bind <codice>` o un comando da terminale. Per
  l'utente finale di KUIO (spesso anziano, non tecnico) e' impensabile.

SOLUZIONE (questa patch):
  Se la allowlist e' ANCORA VUOTA (nessun utente autorizzato = primissimo
  contatto in assoluto) e il messaggio arriva da una chat privata 1:1,
  il PRIMO utente che scrive viene autorizzato e salvato AUTOMATICAMENTE
  come proprietario. Gli utenti successivi restano da approvare (la allowlist
  non e' piu' vuota), quindi NON e' un "bot aperto a tutti".

  Cosi' l'utente finale: installa -> collega Telegram -> scrive "ciao" ->
  funziona. Nessun /bind, nessun comando.

DOVE AGISCE:
  crates/zeroclaw-channels/src/telegram.rs, nel ciclo di dispatch, subito
  PRIMA di `let msg = if let Some(m) = self.parse_update_message(update)`.
  Dopo aver salvato il proprietario, lo stesso messaggio supera il controllo
  di autorizzazione e viene gestito normalmente (il bot risponde subito).

USO (dalla radice del clone del fork, nel workflow di build, dopo deep-branding.py):
    python3 kuio-modifications/branding/patch-telegram-autotrust.py

Esce con codice != 0 (fa fallire la build, di proposito) se non trova il
punto di aggancio: meglio una build fallita che un binario senza la patch.
"""
import os
import sys

TARGET = os.path.join("crates", "zeroclaw-channels", "src", "telegram.rs")

ANCHOR = "                    let msg = if let Some(m) = self.parse_update_message(update) {"

MARKER = "KUIO: primo contatto auto-autorizzato come proprietario"

# Blocco inserito PRIMA dell'ANCHOR. Indentazione = 20 spazi (come l'ANCHOR).
# Usa solo costrutti gia' presenti nel file: let-chains, serde_json::Value::as_*,
# Self::normalize_identity, self.persist_allowed_identity (async), zeroclaw_log::record!.
PATCH = '''                    // KUIO auto-fiducia del proprietario: se non c'e' ancora
                    // nessun utente autorizzato (allowlist vuota = primo contatto
                    // in assoluto) e il messaggio arriva da una chat privata 1:1,
                    // autorizza e salva automaticamente il PRIMO utente come
                    // proprietario. Cosi' l'utente finale non deve mai eseguire
                    // /bind ne' comandi da terminale. Gli utenti successivi restano
                    // da approvare (la allowlist non e' piu' vuota).
                    if update
                        .get("message")
                        .and_then(|m| m.get("chat"))
                        .and_then(|c| c.get("type"))
                        .and_then(serde_json::Value::as_str)
                        == Some("private")
                        && (self.peer_resolver)().is_empty()
                    {
                        let owner_identity = update
                            .get("message")
                            .and_then(|m| m.get("from"))
                            .and_then(|from| {
                                from.get("id")
                                    .and_then(serde_json::Value::as_i64)
                                    .map(|id| id.to_string())
                                    .or_else(|| {
                                        from.get("username")
                                            .and_then(serde_json::Value::as_str)
                                            .map(Self::normalize_identity)
                                    })
                            })
                            .filter(|s| !s.is_empty() && s.as_str() != "unknown");
                        if let Some(identity) = owner_identity {
                            match Box::pin(self.persist_allowed_identity(&identity)).await {
                                Ok(()) => {
                                    ::zeroclaw_log::record!(
                                        INFO,
                                        ::zeroclaw_log::Event::new(
                                            module_path!(),
                                            ::zeroclaw_log::Action::Note
                                        )
                                        .with_attrs(::serde_json::json!({"identity": identity})),
                                        "KUIO: primo contatto auto-autorizzato come proprietario identity="
                                    );
                                }
                                Err(e) => {
                                    ::zeroclaw_log::record!(
                                        WARN,
                                        ::zeroclaw_log::Event::new(
                                            module_path!(),
                                            ::zeroclaw_log::Action::Note
                                        )
                                        .with_outcome(::zeroclaw_log::EventOutcome::Unknown)
                                        .with_attrs(::serde_json::json!({"e": e.to_string()})),
                                        "KUIO: auto-fiducia primo contatto fallita"
                                    );
                                }
                            }
                        }
                    }

'''


def main():
    if not os.path.isfile(TARGET):
        print("ERRORE: non trovo %s (CWD=%s)" % (TARGET, os.getcwd()))
        sys.exit(1)

    with open(TARGET, encoding="utf-8") as f:
        src = f.read()

    if MARKER in src:
        print("Patch auto-fiducia gia' presente: salto.")
        return

    count = src.count(ANCHOR)
    if count != 1:
        print("ERRORE: punto di aggancio trovato %d volte (atteso 1)." % count)
        print("Il sorgente upstream e' cambiato: aggiornare l'ANCHOR.")
        sys.exit(1)

    patched = src.replace(ANCHOR, PATCH + ANCHOR, 1)

    if patched == src or MARKER not in patched:
        print("ERRORE: inserzione non riuscita.")
        sys.exit(1)

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(patched)

    print("OK: patch auto-fiducia del proprietario applicata a %s" % TARGET)


if __name__ == "__main__":
    main()
