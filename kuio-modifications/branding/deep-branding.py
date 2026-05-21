#!/usr/bin/env python3
"""
KUIO — Branding PROFONDO del sorgente ZeroClaw (da eseguire sul clone del fork PRIMA di compilare).

Sostituisce TUTTE le scritte "ZeroClaw" visibili all'utente che restano cablate
nel binario compilato e nella dashboard web:
  - System prompt / identita' dell'assistente ("You are ZeroClaw...", "I am ZeroClaw...")
  - Banner, messaggi di stato, testi di aiuto della CLI
  - Titolo/strings della Gateway API e della dashboard web (web/dist)
  - Nome servizio Windows ("ZeroClaw Daemon"), service label, cartella dati (.zeroclaw)

USO (dalla radice del clone del fork, DOPO apply-branding.py):
    python3 deep-branding.py
Poi compilare:  cargo build --release

STRATEGIA SICURA:
  Nei sorgenti .rs sostituiamo "ZeroClaw" SOLO quando NON e' seguito da una
  lettera/cifra/underscore. Cosi' la parola visibile "ZeroClaw" (seguita da
  spazio, punteggiatura, /, <, ", ecc.) diventa "KUIO", MA gli identificatori
  CamelCase interni come `ZeroClawConfig` (seguiti da una lettera) restano
  intatti -> il codice continua a compilare.
  NON tocca: il comando/binario `zeroclaw` minuscolo, i crate `zeroclaw_*`,
  i path `crates\\zeroclaw-...`, perche' sono tutti minuscoli.
"""
import os, re

REPO = os.getcwd()
SKIP_DIRS = {".git", "target", "node_modules", ".github"}

# Regex: "ZeroClaw" NON seguito da lettera/cifra/underscore (parola visibile, non identificatore).
WORD = re.compile(r"ZeroClaw(?![A-Za-z0-9_])")

# Sostituzioni MIRATE aggiuntive (interni tecnici visibili all'utente).
LITERAL = {
    '"com.zeroclaw.daemon"': '"ai.kuio.daemon"',
    '.join(".zeroclaw")': '.join(".kuio")',
    '".zeroclaw"': '".kuio"',
    'join("\\.zeroclaw")': 'join(".kuio")',
    "~/.zeroclaw": "~/.kuio",
}


def process(path, do_word=True):
    try:
        with open(path, encoding="utf-8") as f:
            s = f.read()
    except (UnicodeDecodeError, OSError):
        return False
    orig = s
    if do_word:
        s = WORD.sub("KUIO", s)
    for old, new in LITERAL.items():
        s = s.replace(old, new)
    if s != orig:
        with open(path, "w", encoding="utf-8") as f:
            f.write(s)
        return True
    return False


def walk(exts, do_word=True):
    n = 0
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if fn.endswith(exts) or fn == "Cargo.toml":
                if process(os.path.join(root, fn), do_word=do_word):
                    n += 1
    return n


def main():
    print("=== KUIO branding PROFONDO ===")

    # 1) Sorgenti Rust + Cargo.toml (descrizioni/banner). Regex sicura sulle parole visibili.
    rs = 0
    cargo = 0
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            p = os.path.join(root, fn)
            if fn.endswith(".rs"):
                if process(p, do_word=True):
                    rs += 1
            elif fn == "Cargo.toml":
                # Solo parola visibile (la descrizione); i name= sono minuscoli e non vengono toccati.
                if process(p, do_word=True):
                    cargo += 1
    print(f"  sorgenti .rs aggiornati: {rs}")
    print(f"  Cargo.toml aggiornati:   {cargo}")

    # 2) Dashboard web gia' compilata (web/dist): testi visibili. Sostituzione piena (sono string literal).
    web = 0
    web_root = os.path.join(REPO, "web", "dist")
    if os.path.isdir(web_root):
        for root, _, files in os.walk(web_root):
            for fn in files:
                if fn.endswith((".js", ".html", ".css", ".json")):
                    p = os.path.join(root, fn)
                    try:
                        with open(p, encoding="utf-8") as f:
                            s = f.read()
                    except (UnicodeDecodeError, OSError):
                        continue
                    if "ZeroClaw" in s:
                        with open(p, "w", encoding="utf-8") as f:
                            f.write(s.replace("ZeroClaw", "KUIO"))
                        web += 1
    print(f"  file dashboard web aggiornati: {web}")

    print("\n=== BRANDING PROFONDO COMPLETATO ===")
    print("Ora 'cargo build --release' produce un kuio.exe senza 'ZeroClaw' visibile.")


if __name__ == "__main__":
    main()
