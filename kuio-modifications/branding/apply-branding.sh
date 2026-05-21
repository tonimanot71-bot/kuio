#!/usr/bin/env bash
# KUIO — wrapper che lancia lo script di branding Python.
# Eseguire dalla RADICE del clone del fork kuio:
#   cd /percorso/del/clone/kuio
#   bash /percorso/a/kuio-modifications/branding/apply-branding.sh
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$DIR/apply-branding.py" "$@"
