#!/usr/bin/env python3
"""
KUIO - Patch: il canale email (IMAP/TLS) deve fidarsi ANCHE dei certificati
NATIVI del sistema operativo, non solo dei root Mozilla a bordo (webpki).

PROBLEMA:
  connect_imap() costruisce il RootCertStore SOLO con webpki_roots::TLS_SERVER_ROOTS.
  Se un antivirus o un proxy aziendale intercetta la connessione IMAP (MITM con un
  proprio certificato), quel root NON e' tra quelli Mozilla -> errore
  "invalid peer certificate: UnknownIssuer" -> l'email non si collega finche'
  l'utente non disattiva la scansione email dell'antivirus.

SOLUZIONE:
  Aggiungere al RootCertStore anche i certificati nativi del SO (rustls-native-certs),
  dove l'antivirus/proxy installa il proprio root. E' additivo: i root Mozilla restano.

DOVE:
  crates/zeroclaw-channels/src/email_channel.rs  (funzione connect_imap)
  crates/zeroclaw-channels/Cargo.toml            (dipendenza rustls-native-certs)

USO: python3 kuio-modifications/branding/patch-imap-nativecerts.py
  (eseguito da deep-branding.py PRIMA di deep-rename.py, quando il crate si chiama
   ancora zeroclaw-channels).

Esce != 0 (fa fallire la build di proposito) se non trova i punti di aggancio.
"""
import os, re, sys

RS = os.path.join("crates", "zeroclaw-channels", "src", "email_channel.rs")
TOML = os.path.join("crates", "zeroclaw-channels", "Cargo.toml")
MARKER = "rustls_native_certs::load_native_certs"


def fail(msg):
    print("ERRORE patch IMAP native-certs: " + msg, file=sys.stderr)
    sys.exit(1)


# --- 1) email_channel.rs: aggiungi i certificati nativi al RootCertStore ---
if not os.path.isfile(RS):
    fail("file non trovato: " + RS)
with open(RS, encoding="utf-8") as f:
    src = f.read()

if MARKER in src:
    print("patch IMAP native-certs: gia' applicata a email_channel.rs (ok)")
else:
    pat = re.compile(
        r"let\s+certs\s*=\s*RootCertStore\s*\{\s*roots:\s*webpki_roots::TLS_SERVER_ROOTS\.into\(\)\s*,?\s*\}\s*;",
        re.S,
    )
    if not pat.search(src):
        fail("anchor RootCertStore/webpki_roots non trovato in " + RS)
    replacement = (
        "let mut certs = RootCertStore { roots: webpki_roots::TLS_SERVER_ROOTS.into() };\n"
        "        // KUIO: aggiunge i certificati nativi del sistema operativo (Windows/macOS/Linux)\n"
        "        // ai root affidabili, cosi' vengono accettati i certificati di antivirus/proxy\n"
        "        // aziendali che intercettano la connessione IMAP/TLS (causa di UnknownIssuer).\n"
        "        {\n"
        "            let native = rustls_native_certs::load_native_certs();\n"
        "            for cert in native.certs {\n"
        "                let _ = certs.add(cert);\n"
        "            }\n"
        "        }"
    )
    src = pat.sub(replacement, src, count=1)
    with open(RS, "w", encoding="utf-8") as f:
        f.write(src)
    print("patch IMAP native-certs: email_channel.rs aggiornato")

# --- 2) Cargo.toml: aggiungi la dipendenza rustls-native-certs ---
if not os.path.isfile(TOML):
    fail("file non trovato: " + TOML)
with open(TOML, encoding="utf-8") as f:
    toml = f.read()

if "rustls-native-certs" in toml:
    print("patch IMAP native-certs: dipendenza gia' presente in Cargo.toml (ok)")
else:
    m = re.search(r"(?m)^\[dependencies\]\s*$", toml)
    if not m:
        fail("sezione [dependencies] non trovata in " + TOML)
    insert_at = m.end()
    dep_line = '\nrustls-native-certs = "0.8"'
    toml = toml[:insert_at] + dep_line + toml[insert_at:]
    with open(TOML, "w", encoding="utf-8") as f:
        f.write(toml)
    print("patch IMAP native-certs: dipendenza rustls-native-certs aggiunta a Cargo.toml")

print("patch IMAP native-certs: OK")
