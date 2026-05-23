#!/usr/bin/env python3
"""
KUIO - Branding PROFONDO del sorgente ZeroClaw (eseguire sul clone del fork PRIMA di compilare).

Rimuove TUTTE le scritte "ZeroClaw" visibili all'utente, ovunque si trovino:
  - Sorgenti Rust (.rs): system prompt/identita', banner, messaggi di stato, help CLI
  - Template HTML/SVG/JSON inclusi nel binario (es. <title>...Gateway API</title>)
  - Sorgente dashboard web (web/**: .ts/.tsx/.js/.html/.css) e build pronta (web/dist)
  - Cargo.toml (descrizioni/banner)
  - Service label e cartella dati (.zeroclaw -> .kuio)

USO (dalla radice del clone del fork, DOPO apply-branding.py):
    python3 deep-branding.py
Poi compilare:  cargo build --release

STRATEGIA SICURA:
  Sostituiamo "ZeroClaw" SOLO quando NON e' seguito da lettera/cifra/underscore.
  Cosi' la parola visibile "ZeroClaw" diventa "KUIO", MA gli identificatori
  CamelCase interni come ZeroClawConfig (seguiti da lettera) restano intatti
  -> il codice continua a compilare. Il comando minuscolo zeroclaw, i crate
  zeroclaw_* e i path crates/zeroclaw-... (minuscoli) non vengono toccati.
"""
import os, re, sys, subprocess

REPO = os.getcwd()
SKIP_DIRS = {".git", "target", "node_modules", ".github"}

TEXT_EXTS = (
    ".rs", ".html", ".htm", ".svg", ".json", ".yaml", ".yml",
    ".css", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".vue", ".svelte",
    ".txt", ".md", ".hbs", ".tmpl",
)

WORD = re.compile(r"ZeroClaw(?![A-Za-z0-9_])")

LITERAL = {
    '"com.zeroclaw.daemon"': '"ai.kuio.daemon"',
    '.join(".zeroclaw")': '.join(".kuio")',
    '".zeroclaw"': '".kuio"',
    'join("\\.zeroclaw")': 'join(".kuio")',
    "~/.zeroclaw": "~/.kuio",
}


def process(path, do_literal=False):
    try:
        with open(path, encoding="utf-8") as f:
            s = f.read()
    except (UnicodeDecodeError, OSError):
        return False
    orig = s
    s = WORD.sub("KUIO", s)
    if do_literal:
        for old, new in LITERAL.items():
            s = s.replace(old, new)
    if s != orig:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(s)
            return True
        except OSError:
            return False
    return False


def main():
    print("=== KUIO branding PROFONDO (completo) ===")
    counts = {}
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            p = os.path.join(root, fn)
            ext = os.path.splitext(fn)[1].lower()
            if fn == "Cargo.toml":
                if process(p):
                    counts["Cargo.toml"] = counts.get("Cargo.toml", 0) + 1
            elif ext in TEXT_EXTS:
                if process(p, do_literal=(ext == ".rs")):
                    counts[ext] = counts.get(ext, 0) + 1
    if counts:
        for k in sorted(counts):
            print("  %12s : %d file aggiornati" % (k, counts[k]))
    else:
        print("  (nessun file modificato)")
    tot = sum(counts.values())
    print("\n=== BRANDING PROFONDO COMPLETATO: %d file ===" % tot)
    print("Ora 'cargo build --release' produce kuio.exe e dashboard senza 'ZeroClaw' visibile.")

    # KUIO: applica anche la patch "auto-fiducia del proprietario" per Telegram
    # (il primo utente che scrive viene autorizzato in automatico, niente /bind).
    # Sta in un file separato cosi' resta testabile da solo; lo eseguiamo qui per
    # non dover toccare il workflow di GitHub. Se fallisce, fa fallire la build.
    patcher = os.path.join(os.path.dirname(os.path.abspath(__file__)), "patch-telegram-autotrust.py")
    print("\n=== Applico patch auto-fiducia Telegram ===")
    subprocess.run([sys.executable, patcher], check=True)


if __name__ == "__main__":
    main()
