#!/usr/bin/env python3
"""
KUIO - Patch: il payload del codice QR di WhatsApp Web va loggato come
attributo strutturato, non solo su stderr (perso quando KUIO gira nascosto).

PROBLEMA:
  In `crates/zeroclaw-channels/src/whatsapp_web.rs`, quando il motore riceve
  il PairingQrCode emette un INFO "WhatsApp Web QR code received ..." SENZA
  il payload, poi prova a renderizzare il QR ASCII su stderr (`eprintln!`).
  Quando KUIO gira nascosto (avvia-kuio.vbs), stderr finisce nel vuoto, quindi
  il payload effettivo del QR e' irraggiungibile via API/log.
  La Stanza italiana non riesce a mostrarlo all'utente.

SOLUZIONE:
  Subito dopo l'INFO "QR code received", aggiungiamo un secondo record! INFO
  con `qr_payload` come attributo strutturato e messaggio fisso
  "WhatsApp Web QR payload (kuio)" — cosi' /api/logs lo restituisce in modo
  affidabile e parsabile lato client (la Stanza lo cerca e disegna il QR nel
  browser con una mini libreria QR).

  Non tocca il rendering ASCII su stderr (resta come fallback).

USO: python3 kuio-modifications/branding/patch-whatsapp-qr-to-log.py
"""
import os, sys

ANCHOR = (
    "                            Event::PairingQrCode { code, .. } => {\n"
    "                                ::zeroclaw_log::record!(INFO, ::zeroclaw_log::Event::new(module_path!(), ::zeroclaw_log::Action::Note), \"WhatsApp Web QR code received (scan with WhatsApp > Linked Devices)\");\n"
)

REPLACEMENT = (
    "                            Event::PairingQrCode { code, .. } => {\n"
    "                                ::zeroclaw_log::record!(INFO, ::zeroclaw_log::Event::new(module_path!(), ::zeroclaw_log::Action::Note), \"WhatsApp Web QR code received (scan with WhatsApp > Linked Devices)\");\n"
    "                                // KUIO: log payload come attributo strutturato cosi' la Stanza italiana\n"
    "                                // lo legge da /api/logs e disegna il QR nel browser (stderr e' perso\n"
    "                                // quando il motore gira nascosto sotto avvia-kuio.vbs).\n"
    "                                ::zeroclaw_log::record!(\n"
    "                                    INFO,\n"
    "                                    ::zeroclaw_log::Event::new(module_path!(), ::zeroclaw_log::Action::Note)\n"
    "                                        .with_attrs(::serde_json::json!({\"qr_payload\": code})),\n"
    "                                    \"WhatsApp Web QR payload (kuio)\"\n"
    "                                );\n"
)

MARKER = "Stanza italiana\\n                                // lo legge da /api/logs"

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
            if "qr_payload" in s and "WhatsApp Web QR payload (kuio)" in s:
                print("whatsapp-qr-to-log: gia' applicata in " + fp)
                return
            if ANCHOR in s:
                hits.append(fp)
    if not hits:
        print(
            "ERRORE patch whatsapp-qr-to-log: ancora non trovata (Event::PairingQrCode { code, .. }).",
            file=sys.stderr,
        )
        sys.exit(1)
    for p in hits:
        s = open(p, encoding="utf-8").read().replace(ANCHOR, REPLACEMENT, 1)
        open(p, "w", encoding="utf-8").write(s)
        print("whatsapp-qr-to-log: applicata in " + p)
    print("patch whatsapp-qr-to-log: OK (%d file modificati)" % len(hits))


if __name__ == "__main__":
    main()
