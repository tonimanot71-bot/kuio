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
    # Sostituzione a livello di BYTE (indipendente dalla codifica): cattura anche file
    # con qualche byte non-UTF8 che altrimenti verrebbero saltati. Tre varianti:
    #   zeroclaw -> kuio (minuscolo, nomi crate/moduli/default)
    #   ZEROCLAW -> KUIO (maiuscolo, nomi di variabili d'ambiente; nessuno script esterno le usa)
    # NB: NON tocchiamo "ZeroClaw" CamelCase qui: ci pensa gia' deep-branding.py con i confini
    #     di parola (cosi' identificatori come ZeroClawConfig restano coerenti). Nel binario il
    #     capital risulta gia' 0.
    n = 0
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext in TEXT_EXTS or fn in NAMED:
                fp = os.path.join(root, fn)
                try:
                    with open(fp, "rb") as f:
                        b = f.read()
                except OSError:
                    continue
                if b"zeroclaw" in b or b"Zeroclaw" in b or b"ZEROCLAW" in b:
                    b = b.replace(b"zeroclaw", b"kuio").replace(b"Zeroclaw", b"Kuio").replace(b"ZEROCLAW", b"KUIO")
                    try:
                        with open(fp, "wb") as f:
                            f.write(b)
                        n += 1
                    except OSError:
                        pass
    return n


def rename_paths():
    n = 0
    # files first (bottom-up); if a kuio-named target already exists (es. asset
    # gia' brandizzato da apply-branding), rimuovi l'orfano zeroclaw invece di crashare.
    for root, _dirs, files in os.walk(REPO, topdown=False):
        if _skip(root):
            continue
        for name in files:
            if "zeroclaw" not in name:
                continue
            src = os.path.join(root, name)
            dst = os.path.join(root, name.replace("zeroclaw", "kuio"))
            try:
                if os.path.exists(dst):
                    os.remove(src)
                else:
                    os.rename(src, dst)
                n += 1
            except OSError:
                pass
    # then directories (bottom-up)
    for root, dirs, _files in os.walk(REPO, topdown=False):
        if _skip(root):
            continue
        for d in dirs:
            if d in SKIP_DIRS or "zeroclaw" not in d:
                continue
            src = os.path.join(root, d)
            dst = os.path.join(root, d.replace("zeroclaw", "kuio"))
            try:
                if not os.path.exists(dst):
                    os.rename(src, dst)
                    n += 1
            except OSError:
                pass
    return n


def main():
    c = replace_contents()
    r = rename_paths()
    print("=== KUIO deep-rename: %d file aggiornati, %d cartelle/file rinominati ===" % (c, r))


if __name__ == "__main__":
    main()
