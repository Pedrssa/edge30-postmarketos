#!/bin/sh
# EDGE30 NETOPS LAB - snapshot do estado do sistema antes de qualquer alteracao.
# Idempotente: cada execucao cria um diretorio novo. So le o sistema; so escreve
# em /var/backups/netops. Roda como root.
set -eu
TS=$(date +%Y%m%d-%H%M%S)
D=/var/backups/netops/$TS
umask 077
mkdir -p "$D"

cp /etc/apk/world "$D/apk-world"
apk info -v 2>/dev/null | sort > "$D/apk-packages"
nft list ruleset > "$D/nft-ruleset" 2>/dev/null || true
systemctl list-unit-files --no-legend > "$D/unit-files"
systemctl list-units --type=service --state=running --no-legend | awk '{print $1}' | sort > "$D/services-running"
ip -br addr > "$D/ip-addr"
ip route > "$D/ip-route"
getcap -r /usr/bin /usr/sbin 2>/dev/null | sort > "$D/file-caps" || true
getent group > "$D/group"
getent passwd > "$D/passwd"
ls -la /etc/sudoers.d > "$D/sudoers-d" 2>/dev/null || true
# /etc completo fica so no aparelho (root 0600). Segredos ficam de fora.
tar czf "$D/etc.tar.gz" -C / \
    --exclude=etc/shadow --exclude=etc/shadow- --exclude=etc/gshadow \
    --exclude=etc/NetworkManager/system-connections --exclude='etc/ssh/ssh_host_*_key' \
    etc 2>/dev/null || true
ln -sfn "$D" /var/backups/netops/latest
echo "$D"
