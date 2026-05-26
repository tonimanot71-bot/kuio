#!/usr/bin/env python3
"""
KUIO - Branding PROFONDO del sorgente ZeroClaw (eseguire sul clone del fork PRIMA di compilare).

Rimuove TUTTE le scritte "ZeroClaw" visibili all'utente (sorgenti .rs, template
HTML/SVG/JSON, dashboard web, Cargo.toml, service label, cartella dati .zeroclaw->.kuio)
e brandizza anche gli ESEMPI DI COMANDO minuscoli ("zeroclaw onboard" -> "kuio onboard")
senza toccare crate/module/path (zeroclaw_log, crates/zeroclaw-channels, zeroclaw::...)
cosi' il codice continua a compilare. Alla fine applica la patch auto-fiducia Telegram.

USO (dalla radice del clone del fork, DOPO apply-branding.py):  python3 deep-branding.py
"""
import os, re, sys, subprocess

REPO = os.getcwd()
SKIP_DIRS = {".git", "target", "node_modules", ".github"}

TEXT_EXTS = (
    ".rs", ".html", ".htm", ".svg", ".json", ".yaml", ".yml",
    ".css", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".vue", ".svelte",
    ".txt", ".md", ".hbs", ".tmpl",
)

# "ZeroClaw" maiuscolo visibile -> KUIO (ma non gli identificatori CamelCase tipo ZeroClawConfig).
WORD = re.compile(r"ZeroClaw(?![A-Za-z0-9_])")

# 'zeroclaw' minuscolo: SOLO quando e' PRECEDUTO DA UN BACKTICK (esempi di comando dentro i
# messaggi/help, es. `zeroclaw channel ...`) e seguito da spazio/tab. Cosi' "`zeroclaw onboard`" ->
# "`kuio onboard`" ma identificatori/variabili/crate (zeroclaw_log, let mut zeroclaw =, name="zeroclaw")
# NON vengono toccati e il codice compila.
CMD = re.compile(r"(?<=`)zeroclaw(?=[ 	])")

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
    s = CMD.sub("kuio", s)
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

    # KUIO: applica anche la patch "auto-fiducia del proprietario" Telegram (niente /bind).
    # Sta in un file separato (testabile da solo); eseguito qui per non toccare il workflow.
    # Se fallisce, fa fallire la build (check=True).
    patcher = os.path.join(os.path.dirname(os.path.abspath(__file__)), "patch-telegram-autotrust.py")
    print("\n=== Applico patch auto-fiducia Telegram ===")
    subprocess.run([sys.executable, patcher], check=True)

    # KUIO: patch certificati nativi per IMAP/email (email funziona con antivirus/proxy attivi).
    imap_patcher = os.path.join(os.path.dirname(os.path.abspath(__file__)), "patch-imap-nativecerts.py")
    print("\n=== Applico patch certificati nativi IMAP (email) ===")
    subprocess.run([sys.executable, imap_patcher], check=True)

    # KUIO: patch "rispondi sempre" (classificatore non deve saltare messaggi diretti).
    ar_patcher = os.path.join(os.path.dirname(os.path.abspath(__file__)), "patch-always-reply.py")
    print("\n=== Applico patch rispondi-sempre (classificatore) ===")
    subprocess.run([sys.executable, ar_patcher], check=True)

    # KUIO: patch validator transcription_provider (accetta nomi bare per i single-instance).
    tb_patcher = os.path.join(os.path.dirname(os.path.abspath(__file__)), "patch-transcription-bare.py")
    print("\n=== Applico patch transcription_provider bare (voce in entrata) ===")
    subprocess.run([sys.executable, tb_patcher], check=True)

    # KUIO: lega il TranscriptionManager del canale Telegram al provider configurato
    # (bug strutturale: senza binding i voice message falliscono SEMPRE).
    tt_patcher = os.path.join(os.path.dirname(os.path.abspath(__file__)), "patch-telegram-transcription-bind.py")
    print("\n=== Applico patch telegram transcription bind (voce in entrata) ===")
    subprocess.run([sys.executable, tt_patcher], check=True)

    # KUIO: rinomina i crate zeroclaw-* -> kuio-* (azzera zeroclaw nei nomi modulo/percorsi del binario).
    renamer = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deep-rename.py")
    print("\n=== Deep-rename crate zeroclaw-* -> kuio-* ===")
    subprocess.run([sys.executable, renamer], check=True)


if __name__ == "__main__":
    main()
