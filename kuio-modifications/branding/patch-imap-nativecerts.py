#!/usr/bin/env python3
"""
KUIO - Patch: il canale email deve fidarsi ANCHE dei certificati NATIVI del SO,
non solo dei root Mozilla a bordo (webpki). Vale per la posta in ARRIVO (IMAP,
rustls) E in USCITA (SMTP, libreria lettre).

PROBLEMA:
  Un antivirus/proxy aziendale che intercetta la posta (MITM con un proprio
  certificato) NON ha il suo root tra quelli Mozilla -> "invalid peer certificate:
  UnknownIssuer" -> l'email non si collega (IMAP) e/o non si invia (SMTP) finche'
  l'utente non disattiva la scansione email dell'antivirus.

SOLUZIONE:
  Aggiungere i certificati nativi del SO (rustls-native-certs) sia al RootCertStore
  IMAP, sia ai root della connessione TLS SMTP (lettre add_root_certificate). Additivo.

DOVE:
  crates/zeroclaw-channels/src/email_channel.rs  (connect_imap + create_smtp_transport)
  crates/zeroclaw-channels/Cargo.toml            (dipendenza rustls-native-certs)

USO: python3 kuio-modifications/branding/patch-imap-nativecerts.py
  (da deep-branding.py, PRIMA di deep-rename.py, quando il crate e' ancora zeroclaw-channels)
Esce != 0 (fa fallire la build) se non trova i punti di aggancio.
"""
import os, re, sys

RS = os.path.join("crates", "zeroclaw-channels", "src", "email_channel.rs")
TOML = os.path.join("crates", "zeroclaw-channels", "Cargo.toml")


def fail(msg):
    print("ERRORE patch IMAP/SMTP native-certs: " + msg, file=sys.stderr)
    sys.exit(1)


if not os.path.isfile(RS):
    fail("file non trovato: " + RS)
with open(RS, encoding="utf-8") as f:
    src = f.read()

# --- 1) IMAP: RootCertStore + certificati nativi ---
if "let mut certs = RootCertStore" in src:
    print("IMAP: gia' applicata (ok)")
else:
    imap_pat = re.compile(
        r"let\s+certs\s*=\s*RootCertStore\s*\{\s*roots:\s*webpki_roots::TLS_SERVER_ROOTS\.into\(\)\s*,?\s*\}\s*;",
        re.S,
    )
    if not imap_pat.search(src):
        fail("anchor IMAP (RootCertStore/webpki_roots) non trovato")
    imap_repl = (
        "let mut certs = RootCertStore { roots: webpki_roots::TLS_SERVER_ROOTS.into() };\n"
        "        // KUIO: aggiunge i certificati nativi del SO (antivirus/proxy che intercettano IMAP/TLS).\n"
        "        {\n"
        "            let native = rustls_native_certs::load_native_certs();\n"
        "            for cert in native.certs {\n"
        "                let _ = certs.add(cert);\n"
        "            }\n"
        "        }"
    )
    src = imap_pat.sub(imap_repl, src, count=1)
    print("IMAP: applicata")

# --- 2) SMTP: TLS lettre + certificati nativi ---
if "smtp_tls_params" in src:
    print("SMTP: gia' applicata (ok)")
else:
    smtp_pat = re.compile(
        r"let\s+transport\s*=\s*if\s+self\.config\.smtp_tls\s*\{\s*"
        r"SmtpTransport::relay\(&self\.config\.smtp_host\)\?\s*"
        r"\.port\(self\.config\.smtp_port\)\s*"
        r"\.credentials\(creds\)\s*"
        r"\.build\(\)\s*\}\s*else\s*\{",
        re.S,
    )
    if not smtp_pat.search(src):
        fail("anchor SMTP (SmtpTransport::relay smtp_tls) non trovato")
    smtp_repl = (
        "let transport = if self.config.smtp_tls {\n"
        "            // KUIO: TLS SMTP con i certificati nativi del SO (antivirus/proxy che intercettano SMTP).\n"
        "            let mut smtp_tls_builder = ::lettre::transport::smtp::client::TlsParameters::builder(self.config.smtp_host.clone());\n"
        "            for cert in rustls_native_certs::load_native_certs().certs {\n"
        "                if let Ok(c) = ::lettre::transport::smtp::client::Certificate::from_der(cert.as_ref().to_vec()) {\n"
        "                    smtp_tls_builder = smtp_tls_builder.add_root_certificate(c);\n"
        "                }\n"
        "            }\n"
        "            let smtp_tls_params = smtp_tls_builder.build()?;\n"
        "            SmtpTransport::relay(&self.config.smtp_host)?\n"
        "                .port(self.config.smtp_port)\n"
        "                .tls(::lettre::transport::smtp::client::Tls::Wrapper(smtp_tls_params))\n"
        "                .credentials(creds)\n"
        "                .build()\n"
        "        } else {"
    )
    src = smtp_pat.sub(smtp_repl, src, count=1)
    print("SMTP: applicata")

with open(RS, "w", encoding="utf-8") as f:
    f.write(src)

# --- 3) Cargo.toml: dipendenza rustls-native-certs ---
if not os.path.isfile(TOML):
    fail("file non trovato: " + TOML)
with open(TOML, encoding="utf-8") as f:
    toml = f.read()
if "rustls-native-certs" in toml:
    print("Cargo.toml: dipendenza gia' presente (ok)")
else:
    m = re.search(r"(?m)^\[dependencies\]\s*$", toml)
    if not m:
        fail("sezione [dependencies] non trovata in Cargo.toml")
    toml = toml[:m.end()] + '\nrustls-native-certs = "0.8"' + toml[m.end():]
    with open(TOML, "w", encoding="utf-8") as f:
        f.write(toml)
    print("Cargo.toml: dipendenza rustls-native-certs aggiunta")

print("patch IMAP/SMTP native-certs: OK")
