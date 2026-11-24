#!/bin/sh
# Instala o conjunto minimo como pacote virtual: `apk del .netops-lab` remove tudo.
# Idempotente. Aborta se a simulacao indicar upgrade ou remocao de pacote existente.
set -eu
PKGS="tshark iw mtr iperf3 nmap bind-tools curl"
SIM=$(apk add -s -t .netops-lab $PKGS 2>&1)
printf '%s\n' "$SIM" | tail -3
if printf '%s\n' "$SIM" | grep -E '^\([ 0-9/]+\) (Upgrading|Downgrading|Replacing|Purging|Removing)'; then
    echo "ABORTADO: a simulacao mexeria em pacotes existentes." >&2
    exit 3
fi
if [ "${1:-}" = "--simulate" ]; then exit 0; fi
apk add -t .netops-lab $PKGS 2>&1 | tail -3
for b in dumpcap tshark iw mtr iperf3 nmap dig curl; do
    command -v "$b" >/dev/null || { echo "FALTA: $b" >&2; exit 4; }
done
echo "pacotes OK"
