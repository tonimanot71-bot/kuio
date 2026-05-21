#!/usr/bin/env python3
"""
KUIO — Branding PROFONDO del sorgente ZeroClaw (da eseguire sul clone del fork PRIMA di compilare).

Sostituisce i nomi tecnici "ZeroClaw" che restano cablati nel binario compilato:
  - Nome servizio Windows:  "ZeroClaw Daemon" -> "KUIO"
  - Service label:          "com.zeroclaw.daemon" -> "ai.kuio.daemon"
  - Cartella dati utente:   ".zeroclaw" -> ".kuio"

USO (dalla radice del clone del fork, DOPO apply-branding.py):
    python3 deep-branding.py
Poi compilare:  setup.bat --full   (o cargo build --release)

NB: cambiare la cartella dati (.zeroclaw -> .kuio) è giusto per un prodotto NUOVO.
NON tocca: nomi di funzioni Rust, namespace dei crate (zeroclaw_config ecc.),
l'utente di sistema Linux 'zeroclaw' (irrilevante su Windows), import.
Questi non sono visibili al cliente e cambiarli romperebbe la compilazione.
"""
import os, re, sys

REPO = os.getcwd()

# Sostituzioni MIRATE (stringa esatta -> nuova). Solo nomi visibili all'utente.
LITERAL = {
    '"ZeroClaw Daemon"': '"KUIO"',
    '"com.zeroclaw.daemon"': '"ai.kuio.daemon"',
    '.join(".zeroclaw")': '.join(".kuio")',
    '".zeroclaw"': '".kuio"',
    'join("\\.zeroclaw")': 'join(".kuio")',
}

changed = 0
for root, _, files in os.walk(os.path.join(REPO, "crates")):
    for fn in files:
        if not fn.endswith(".rs"):
            continue
        p = os.path.join(root, fn)
        with open(p, encoding="utf-8") as f:
            s = f.read()
        orig = s
        for old, new in LITERAL.items():
            s = s.replace(old, new)
        if s != orig:
            with open(p, "w", encoding="utf-8") as f:
                f.write(s)
            changed += 1

print(f"Branding profondo applicato a {changed} file sorgente.")
print("Ora compila il fork (setup.bat --full) per ottenere kuio.exe completamente brandizzato.")
print("Verifica residui visibili:  grep -rn '\"ZeroClaw Daemon\"\\|\\.zeroclaw' crates/")
