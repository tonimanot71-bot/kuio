#!/usr/bin/env python3
"""
KUIO — Applica il branding (immagini + testi) al fork ZeroClaw.

USO: eseguire dalla RADICE del clone del fork kuio (ex-zeroclaw):
    cd /percorso/del/clone/kuio
    python3 /percorso/a/kuio-modifications/branding/apply-branding.py

COSA FA:
  1. Copia icone/logo/banner KUIO al posto di quelli ZeroClaw
  2. Sostituisce "ZeroClaw" -> "KUIO" (nome prodotto) in tutti i .ftl e nel README
  3. Sostituisce il banner README remoto con quello locale KUIO
  4. Rimuove l'emoji granchio (mascotte Rust di ZeroClaw)
  5. Installa la traduzione italiana e registra "it" in locales.toml

NON TOCCA (di proposito): il comando/binario `zeroclaw` (minuscolo), il package
Cargo `zeroclawlabs`, l'org `zeroclaw-labs`, path/identificatori/codice Rust.
"""
import os
import shutil
import sys

CRAB = "\U0001F980"  # 🦀
BRANDING_DIR = os.path.dirname(os.path.abspath(__file__))
MODS_DIR = os.path.dirname(BRANDING_DIR)
REPO = os.getcwd()

REMOTE_BANNER = "https://raw.githubusercontent.com/zeroclaw-labs/zeroclaw/master/docs/assets/zeroclaw-banner.png"
LOCAL_BANNER = "docs/assets/kuio-banner.png"


def copy_if_dest_dir(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def rebrand_text(path):
    """Sostituisce ZeroClaw->KUIO, rimuove emoji granchio, sistema banner URL."""
    with open(path, "r", encoding="utf-8") as f:
        s = f.read()
    s = s.replace("ZeroClaw", "KUIO")
    s = s.replace(REMOTE_BANNER, LOCAL_BANNER)
    s = s.replace(CRAB + " ", "").replace(" " + CRAB, "").replace(CRAB, "")
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)


def main():
    print("=== KUIO branding ===")
    print(f"Branding source: {BRANDING_DIR}")
    print(f"Repo target:     {REPO}\n")

    # --- 1. IMMAGINI ---
    print("[1/3] Copio icone, logo e banner...")
    icons_dir = os.path.join(REPO, "apps/tauri/icons")
    if os.path.isdir(icons_dir):
        for root, _, files in os.walk(os.path.join(BRANDING_DIR, "apps/tauri/icons")):
            rel = os.path.relpath(root, os.path.join(BRANDING_DIR, "apps/tauri/icons"))
            for fn in files:
                dst = os.path.join(icons_dir, rel, fn) if rel != "." else os.path.join(icons_dir, fn)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(os.path.join(root, fn), dst)
        print("  icone app desktop: OK")
    src_gh_logo = os.path.join(BRANDING_DIR, ".github/assets/zeroclaw-logo.png")
    if os.path.isdir(os.path.join(REPO, ".github/assets")) and os.path.isfile(src_gh_logo):
        copy_if_dest_dir(src_gh_logo, os.path.join(REPO, ".github/assets/zeroclaw-logo.png"))
        print("  logo GitHub: OK")
    else:
        print("  logo GitHub: saltato (file non presente, non bloccante)")
    if os.path.isdir(os.path.join(REPO, "web/public")):
        copy_if_dest_dir(os.path.join(BRANDING_DIR, "web/public/logo.png"),
                         os.path.join(REPO, "web/public/logo.png"))
        print("  logo dashboard web: OK")
    copy_if_dest_dir(os.path.join(BRANDING_DIR, "docs/assets/kuio-banner.png"),
                     os.path.join(REPO, "docs/assets/kuio-banner.png"))
    print("  banner README: OK")

    # --- 2. TESTI ---
    print("\n[2/3] Sostituisco 'ZeroClaw' -> 'KUIO', banner ed emoji...")
    crates = os.path.join(REPO, "crates")
    n = 0
    if os.path.isdir(crates):
        for root, _, files in os.walk(crates):
            for fn in files:
                if fn.endswith(".ftl"):
                    rebrand_text(os.path.join(root, fn))
                    n += 1
    readme = os.path.join(REPO, "README.md")
    if os.path.isfile(readme):
        rebrand_text(readme)
    print(f"  {n} file .ftl + README aggiornati (comando 'zeroclaw' e 'zeroclaw-labs' NON toccati).")

    # --- 3. ITALIANO ---
    print("\n[3/3] Installo la traduzione italiana...")
    it_dir = os.path.join(REPO, "crates/zeroclaw-runtime/locales/it")
    os.makedirs(it_dir, exist_ok=True)
    for fn in ("cli.ftl", "tools.ftl"):
        shutil.copy2(os.path.join(MODS_DIR, "locales/it", fn), os.path.join(it_dir, fn))
    loc = os.path.join(REPO, "locales.toml")
    if os.path.isfile(loc):
        with open(loc, encoding="utf-8") as f:
            content = f.read()
        if 'code = "it"' not in content:
            shutil.copy2(os.path.join(MODS_DIR, "locales.toml"), loc)
    print("  italiano installato e registrato.")

    print("\n=== BRANDING COMPLETATO ===")
    print("Prossimi pass#!/usr/bin/env python3
"""
KUIO — Applica il branding (immagini + testi) al fork ZeroClaw.

USO: eseguire dalla RADICE del clone del fork kuio (ex-zeroclaw):
    cd /percorso/del/clone/kuio
    python3 /percorso/a/kuio-modifications/branding/apply-branding.py

COSA FA:
  1. Copia icone/logo/banner KUIO al posto di quelli ZeroClaw
  2. Sostituisce "ZeroClaw" -> "KUIO" (nome prodotto) in tutti i .ftl e nel README
  3. Sostituisce il banner README remoto con quello locale KUIO
  4. Rimuove l'emoji granchio (mascotte Rust di ZeroClaw)
  5. Installa la traduzione italiana e registra "it" in locales.toml

NON TOCCA (di proposito): il comando/binario `zeroclaw` (minuscolo), il package
Cargo `zeroclawlabs`, l'org `zeroclaw-labs`, path/identificatori/codice Rust.
"""
import os
import shutil
import sys

CRAB = "\U0001F980"  # 🦀
BRANDING_DIR = os.path.dirname(os.path.abspath(__file__))
MODS_DIR = os.path.dirname(BRANDING_DIR)
REPO = os.getcwd()

REMOTE_BANNER = "https://raw.githubusercontent.com/zeroclaw-labs/zeroclaw/master/docs/assets/zeroclaw-banner.png"
LOCAL_BANNER = "docs/assets/kuio-banner.png"


def copy_if_dest_dir(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def rebrand_text(path):
    """Sostituisce ZeroClaw->KUIO, rimuove emoji granchio, sistema banner URL."""
    with open(path, "r", encoding="utf-8") as f:
        s = f.read()
    s = s.replace("ZeroClaw", "KUIO")
    s = s.replace(REMOTE_BANNER, LOCAL_BANNER)
    s = s.replace(CRAB + " ", "").replace(" " + CRAB, "").replace(CRAB, "")
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)


def main():
    print("=== KUIO branding ===")
    print(f"Branding source: {BRANDING_DIR}")
    print(f"Repo target:     {REPO}\n")

    # --- 1. IMMAGINI ---
    print("[1/3] Copio icone, logo e banner...")
    icons_dir = os.path.join(REPO, "apps/tauri/icons")
    if os.path.isdir(icons_dir):
        for root, _, files in os.walk(os.path.join(BRANDING_DIR, "apps/tauri/icons")):
            rel = os.path.relpath(root, os.path.join(BRANDING_DIR, "apps/tauri/icons"))
            for fn in files:
                dst = os.path.join(icons_dir, rel, fn) if rel != "." else os.path.join(icons_dir, fn)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(os.path.join(root, fn), dst)
        print("  icone app desktop: OK")
    src_gh_logo = os.path.join(BRANDING_DIR, ".github/assets/zeroclaw-logo.png")
    if os.path.isdir(os.path.join(REPO, ".github/assets")) and os.path.isfile(src_gh_logo):
        copy_if_dest_dir(src_gh_logo, os.path.join(REPO, ".github/assets/zeroclaw-logo.png"))
        print("  logo GitHub: OK")
    else:
        print("  logo GitHub: saltato (file non presente, non bloccante)")
    if os.path.isdir(os.path.join(REPO, "web/public")):
        copy_if_dest_dir(os.path.join(BRANDING_DIR, "web/public/logo.png"),
                         os.path.join(REPO, "web/public/logo.png"))
        print("  logo dashboard web: OK")
    copy_if_dest_dir(os.path.join(BRANDING_DIR, "docs/assets/kuio-banner.png"),
                     os.path.join(REPO, "docs/assets/kuio-banner.png"))
    print("  banner README: OK")

    # --- 2. TESTI ---
    print("\n[2/3] Sostituisco 'ZeroClaw' -> 'KUIO', banner ed emoji...")
    crates = os.path.join(REPO, "crates")
    n = 0
    if os.path.isdir(crates):
        for root, _, files in os.walk(crates):
            for fn in files:
                if fn.endswith(".ftl"):
                    rebrand_text(os.path.join(root, fn))
                    n += 1
    readme = os.path.join(REPO, "README.md")
    if os.path.isfile(readme):
        rebrand_text(readme)
    print(f"  {n} file .ftl + README aggiornati (comando 'zeroclaw' e 'zeroclaw-labs' NON toccati).")

    # --- 3. ITALIANO ---
    print("\n[3/3] Installo la traduzione italiana...")
    it_dir = os.path.join(REPO, "crates/zeroclaw-runtime/locales/it")
    os.makedirs(it_dir, exist_ok=True)
    for fn in ("cli.ftl", "tools.ftl"):
        shutil.copy2(os.path.join(MODS_DIR, "locales/it", fn), os.path.join(it_dir, fn))
    loc = os.path.join(REPO, "locales.toml")
    if os.path.isfile(loc):
        with open(loc, encoding="utf-8") as f:
            content = f.read()
        if 'code = "it"' not in content:
            shutil.copy2(os.path.join(MODS_DIR, "locales.toml"), loc)
    print("  italiano installato e registrato.")

    print("\n=== BRANDING COMPLETATO ===")
    print("Prossimi passi: build con setup.bat --prebuilt o cargo build, poi verifica icona e lingua.")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
KUIO — Applica il branding (immagini + testi) al fork ZeroClaw.

USO: eseguire dalla RADICE del clone del fork kuio (ex-zeroclaw):
    cd /percorso/del/clone/kuio
    python3 /percorso/a/kuio-modifications/branding/apply-branding.py

COSA FA:
  1. Copia icone/logo/banner KUIO al posto di quelli ZeroClaw
  2. Sostituisce "ZeroClaw" -> "KUIO" (nome prodotto) in tutti i .ftl e nel README
  3. Sostituisce il banner README remoto con quello locale KUIO
  4. Rimuove l'emoji granchio (mascotte Rust di ZeroClaw)
  5. Installa la traduzione italiana e registra "it" in locales.toml

NON TOCCA (di proposito): il comando/binario `zeroclaw` (minuscolo), il package
Cargo `zeroclawlabs`, l'org `zeroclaw-labs`, path/identificatori/codice Rust.
"""
import os
import shutil
import sys

CRAB = "\U0001F980"  # 🦀
BRANDING_DIR = os.path.dirname(os.path.abspath(__file__))
MODS_DIR = os.path.dirname(BRANDING_DIR)
REPO = os.getcwd()

REMOTE_BANNER = "https://raw.githubusercontent.com/zeroclaw-labs/zeroclaw/master/docs/assets/zeroclaw-banner.png"
LOCAL_BANNER = "docs/assets/kuio-banner.png"


def copy_if_dest_dir(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def rebrand_text(path):
    """Sostituisce ZeroClaw->KUIO, rimuove emoji granchio, sistema banner URL."""
    with open(path, "r", encoding="utf-8") as f:
        s = f.read()
    s = s.replace("ZeroClaw", "KUIO")
    s = s.replace(REMOTE_BANNER, LOCAL_BANNER)
    s = s.replace(CRAB + " ", "").replace(" " + CRAB, "").replace(CRAB, "")
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)


def main():
    print("=== KUIO branding ===")
    print(f"Branding source: {BRANDING_DIR}")
    print(f"Repo target:     {REPO}\n")

    # --- 1. IMMAGINI ---
    print("[1/3] Copio icone, logo e banner...")
    icons_dir = os.path.join(REPO, "apps/tauri/icons")
    if os.path.isdir(icons_dir):
        for root, _, files in os.walk(os.path.join(BRANDING_DIR, "apps/tauri/icons")):
            rel = os.path.relpath(root, os.path.join(BRANDING_DIR, "apps/tauri/icons"))
            for fn in files:
                dst = os.path.join(icons_dir, rel, fn) if rel != "." else os.path.join(icons_dir, fn)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(os.path.join(root, fn), dst)
        print("  icone app desktop: OK")
    if os.path.isdir(os.path.join(REPO, ".github/assets")):
        copy_if_dest_dir(os.path.join(BRANDING_DIR, ".github/assets/zeroclaw-logo.png"),
                         os.path.join(REPO, ".github/assets/zeroclaw-logo.png"))
        print("  logo GitHub: OK")
    if os.path.isdir(os.path.join(REPO, "web/public")):
        copy_if_dest_dir(os.path.join(BRANDING_DIR, "web/public/logo.png"),
                         os.path.join(REPO, "web/public/logo.png"))
        print("  logo dashboard web: OK")
    copy_if_dest_dir(os.path.join(BRANDING_DIR, "docs/assets/kuio-banner.png"),
                     os.path.join(REPO, "docs/assets/kuio-banner.png"))
    print("  banner README: OK")

    # --- 2. TESTI ---
    print("\n[2/3] Sostituisco 'ZeroClaw' -> 'KUIO', banner ed emoji...")
    crates = os.path.join(REPO, "crates")
    n = 0
    if os.path.isdir(crates):
        for root, _, files in os.walk(crates):
            for fn in files:
                if fn.endswith(".ftl"):
                    rebrand_text(os.path.join(root, fn))
                    n += 1
    readme = os.path.join(REPO, "README.md")
    if os.path.isfile(readme):
        rebrand_text(readme)
    print(f"  {n} file .ftl + README aggiornati (comando 'zeroclaw' e 'zeroclaw-labs' NON toccati).")

    # --- 3. ITALIANO ---
    print("\n[3/3] Installo la traduzione italiana...")
    it_dir = os.path.join(REPO, "crates/zeroclaw-runtime/locales/it")
    os.makedirs(it_dir, exist_ok=True)
    for fn in ("cli.ftl", "tools.ftl"):
        shutil.copy2(os.path.join(MODS_DIR, "locales/it", fn), os.path.join(it_dir, fn))
    loc = os.path.join(REPO, "locales.toml")
    if os.path.isfile(loc):
        with open(loc, encoding="utf-8") as f:
            content = f.read()
        if 'code = "it"' not in content:
            shutil.copy2(os.path.join(MODS_DIR, "locales.toml"), loc)
    print("  italiano installato e registrato.")

    print("\n=== BRANDING COMPLETATO ===")
    print("Prossimi passi: build con 'setup.bat --prebuilt' o 'cargo build', poi verifica icona/lingua.")


if __name__ == "__main__":
    main()
