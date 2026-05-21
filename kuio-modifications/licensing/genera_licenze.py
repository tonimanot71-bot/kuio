#!/usr/bin/env python3
"""
KUIO - Generatore di codici licenza firmati.

Ogni codice ha formato KUIO-XXXXX-XXXXX (10 caratteri visibili).
Gli ultimi 3 caratteri sono una FIRMA crittografica (HMAC-SHA256):
nessuno puo' inventarsi codici validi senza conoscere la chiave segreta.

USO:
    python genera_licenze.py 100        # genera 100 codici
    python genera_licenze.py 100 > lotto.csv

IMPORTANTE:
- La CHIAVE_SEGRETA qui sotto e' un PLACEHOLDER di esempio.
  Quella vera va generata una sola volta, tenuta SEGRETA e messa SOLO
  sul server Cloudflare (mai nel programma installato sul PC del cliente).
- I codici generati vanno caricati nel database licenze (Cloudflare KV/D1)
  con stato iniziale "created".
"""
import hashlib
import hmac
import secrets
import sys

# Alfabeto SENZA caratteri ambigui (niente 0/O, 1/I/L) - facili da leggere/digitare
ALFABETO = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # 31 caratteri

# PLACEHOLDER - la chiave vera sta SOLO sul server, generata una volta sola
CHIAVE_SEGRETA = b"DEMO-CHIAVE-NON-USARE-IN-PRODUZIONE-genera-la-tua-vera"

def _map_to_alfabeto(data: bytes, n: int) -> str:
    """Mappa byte sull'alfabeto sicuro, n caratteri."""
    out = []
    for i in range(n):
        out.append(ALFABETO[data[i] % len(ALFABETO)])
    return "".join(out)

def genera_codice() -> str:
    # 7 caratteri casuali (la parte "univoca")
    corpo = "".join(secrets.choice(ALFABETO) for _ in range(7))
    # 3 caratteri di firma HMAC (la parte "anti-falsificazione")
    firma_raw = hmac.new(CHIAVE_SEGRETA, corpo.encode(), hashlib.sha256).digest()
    firma = _map_to_alfabeto(firma_raw, 3)
    grezzo = corpo + firma  # 10 caratteri
    # Formato leggibile KUIO-XXXXX-XXXXX
    return f"KUIO-{grezzo[:5]}-{grezzo[5:]}"

def verifica_codice(codice: str) -> bool:
    """Il server usa questa per validare un codice (check firma)."""
    try:
        pulito = codice.replace("KUIO-", "").replace("-", "").upper()
        if len(pulito) != 10:
            return False
        corpo, firma = pulito[:7], pulito[7:]
        firma_raw = hmac.new(CHIAVE_SEGRETA, corpo.encode(), hashlib.sha256).digest()
        firma_attesa = _map_to_alfabeto(firma_raw, 3)
        return hmac.compare_digest(firma, firma_attesa)
    except Exception:
        return False

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    for _ in range(n):
        print(genera_codice())
