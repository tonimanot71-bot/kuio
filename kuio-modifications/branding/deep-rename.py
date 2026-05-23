#!/usr/bin/env python3
"""
KUIO deep-rename: azzera 'zeroclaw' anche nei NOMI DI MODULO e nei PERCORSI SORGENTE
che finiscono nel binario (zc_name da module_path!(), zc_file da file!()).

Rinomina in modo COERENTE i crate zeroclaw-* -> kuio-* del workspace:
  - sostituisce ogni 'zeroclaw' (minuscolo) -> 'kuio' nel CONTENUTO dei file
    sorgente/manifest (.rs, Cargo.toml, Cargo.lock, .ftl, ...)
  - rinomina cartelle/file che contengono 'zeroclaw' (es. crates/zeroclaw-log -> crates/kuio-log)

La sostituzione e' TOTALE e COERENTE (decl + usi + nomi crate insieme), quindi compila.
NON tocca: .git, target, node_modules, .github, kuio-modifications, dist.
Eseguito DOPO deep-branding.py + patcher, PRIMA di 'cargo build'.
"""
import os

REPO = os.getcwd()
SKIP_DIRS = {".git", "target", "node_modules", ".github", "kuio-modifications", "dist"}
TEXT_EXTS = (
    ".rs", ".toml", ".lock", ".ftl", ".json", ".yaml", ".yml", ".md",
    ".html", ".htm", ".css", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
    ".vue", ".svelte", ".txt", ".hbs", ".tmpl", ".sh", ".cfg", ".ron",
)
NAMED = {"Cargo.toml", "Cargo.lock"}


def _skip(root):
    rel = os.path.relpath(root, REPO)
    return rel != "." and bool(set(rel.split(os.sep)) & SKIP_DIRS)


def replace_contents():
    n = 0
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext in TEXT_EXTS or fn in NAMED:
                p = os.path.join(root, fn)
                try:
                    s = open(p, encoding="utf-8").read()
                except (UnicodeDecodeError, OSError):
                    continue
                if "zeroclaw" in s:
                    try:
                        open(p, "w", encoding="utf-8").write(s.replace("zeroclaw", "kuio"))
                        n += 1
                    except OSError:
                        pass
    return n


def rename_paths():
    n = 0
    # files first, then directories, all bottom-up
    for root, _dirs, files in os.walk(REPO, topdown=False):
        if _skip(root):
            continue
        for name in files:
            if "zeroclaw" in name:
                os.rename(os.path.join(root, name),
                          os.path.join(root, name.replace("zeroclaw", "kuio")))
                n += 1
    for root, dirs, _files in os.walk(REPO, topdown=False):
        if _skip(root):
            continue
        for d in dirs:
            if d not in SKIP_DIRS and "zeroclaw" in d:
                os.rename(os.path.join(root, d),
                          os.path.join(root, d.replace("zeroclaw", "kuio")))
                n += 1
    return n


def main():
    c = replace_contents()
    r = rename_paths()
    print("=== KUIO deep-rename: %d file aggiornati, %d cartelle/file rinominati ===" % (c, r))


if __name__ == "__main__":
    main()
