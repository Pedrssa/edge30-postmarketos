#!/bin/sh
# collect-diagnostics.sh — coleta de diagnóstico para Motorola Edge 30 (dubai)
# postmarketOS / Nura edge · kernel sc7280 mainline · systemd · BusyBox ash
#
# Projetado para rodar NO APARELHO, como usuário comum. Não altera estado do sistema.
# Compatível com Alpine/BusyBox: não assume bash, GNU coreutils, OpenRC nem systemd-only tools.
#
# Uso:
#   sh collect-diagnostics.sh [diretorio-de-saida]
#   sh collect-diagnostics.sh --sanitize   # redige IMEI, seriais, MACs, IPs e SSIDs
#
# Saída: um diretório com um arquivo .txt por seção + manifest.txt com códigos de retorno.

set -u

OUTDIR="${1:-diagnostics-$(date +%Y%m%d-%H%M%S)}"
SANITIZE=0
for a in "$@"; do
    [ "$a" = "--sanitize" ] && SANITIZE=1
done
[ "${OUTDIR}" = "--sanitize" ] && OUTDIR="diagnostics-$(date +%Y%m%d-%H%M%S)"

if ! mkdir -p "$OUTDIR" 2>/dev/null; then
    echo "ERRO: não foi possível criar '$OUTDIR'" >&2
    exit 1
fi

MANIFEST="$OUTDIR/manifest.txt"
: > "$MANIFEST"

log() { printf '%s\n' "$*" >&2; }

# run <arquivo-de-saida> <rotulo> <comando...>
# Registra comando, código de saída e horário. Nunca aborta o script.
run() {
    out="$1"; label="$2"; shift 2
    {
        printf '\n===== %s =====\n' "$label"
        printf '$ %s\n' "$*"
    } >> "$OUTDIR/$out"

    if ! command -v "$1" >/dev/null 2>&1 && [ ! -e "$1" ]; then
        printf '[AUSENTE] ferramenta "%s" não encontrada\n' "$1" >> "$OUTDIR/$out"
        printf '%-28s %-44s AUSENTE\n' "$out" "$label" >> "$MANIFEST"
        return 0
    fi

    "$@" >> "$OUTDIR/$out" 2>&1
    rc=$?
    printf '[exit=%d]\n' "$rc" >> "$OUTDIR/$out"
    printf '%-28s %-44s exit=%d\n' "$out" "$label" "$rc" >> "$MANIFEST"
    return 0
}

# readfiles <arquivo-de-saida> <rotulo> <caminhos...>
readfiles() {
    out="$1"; label="$2"; shift 2
    printf '\n===== %s =====\n' "$label" >> "$OUTDIR/$out"
    for f in "$@"; do
        if [ -r "$f" ]; then
            printf -- '--- %s ---\n' "$f" >> "$OUTDIR/$out"
            cat "$f" >> "$OUTDIR/$out" 2>&1
            printf '\n' >> "$OUTDIR/$out"
        else
            printf -- '--- %s --- [ilegível ou inexistente]\n' "$f" >> "$OUTDIR/$out"
        fi
    done
    printf '%-28s %-44s lidos\n' "$out" "$label" >> "$MANIFEST"
}

log "Coletando em: $OUTDIR"
printf 'Coleta iniciada em %s\n' "$(date -u '+%Y-%m-%d %H:%M:%S UTC')" >> "$MANIFEST"
printf '%s\n\n' "----------------------------------------------------------------" >> "$MANIFEST"

# ---------------------------------------------------------------- 1. sistema
log "[1/9] sistema"
readfiles 01-system.txt "identificação" /etc/os-release /proc/version /proc/cmdline
run 01-system.txt "uname"        uname -a
run 01-system.txt "uptime"       uptime
run 01-system.txt "hostname"     hostname
readfiles 01-system.txt "device tree" /sys/firmware/devicetree/base/model
run 01-system.txt "init"         ls -l /sbin/init

# ------------------------------------------------------------- 2. recursos
log "[2/9] recursos"
run 02-resources.txt "memória"      free -m
run 02-resources.txt "disco"        df -h
run 02-resources.txt "blocos"       lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT
run 02-resources.txt "loop"         losetup -a
run 02-resources.txt "montagens"    mount
run 02-resources.txt "carga"        cat /proc/loadavg
run 02-resources.txt "processos"    ps -eo pid,user,rss,comm

# --------------------------------------------------------------- 3. pacotes
log "[3/9] pacotes e serviços"
run 03-packages.txt "repositórios"  cat /etc/apk/repositories
run 03-packages.txt "chaves apk"    ls /etc/apk/keys/
run 03-packages.txt "pacotes"       apk info -v
if command -v systemctl >/dev/null 2>&1; then
    run 03-packages.txt "unidades falhas"  systemctl --failed --no-pager
    run 03-packages.txt "serviços ativos"  systemctl list-units --type=service --state=running --no-pager
elif command -v rc-status >/dev/null 2>&1; then
    run 03-packages.txt "openrc"           rc-status
fi

# ---------------------------------------------------------------- 4. kernel
log "[4/9] kernel e drivers"
run 04-kernel.txt "módulos"      lsmod
run 04-kernel.txt "interrupções" cat /proc/interrupts
if command -v journalctl >/dev/null 2>&1; then
    run 04-kernel.txt "erros do boot"  journalctl -b -p err --no-pager
    run 04-kernel.txt "kernel"         journalctl -k -b --no-pager
fi
run 04-kernel.txt "dmesg"        dmesg
readfiles 04-kernel.txt "deferred probe" /sys/kernel/debug/devices_deferred

printf '\n===== remoteprocs =====\n' >> "$OUTDIR/04-kernel.txt"
for d in /sys/class/remoteproc/*/; do
    [ -d "$d" ] || continue
    printf '%s: %s -> %s\n' "$(basename "$d")" \
        "$(cat "$d/name" 2>/dev/null)" "$(cat "$d/state" 2>/dev/null)" \
        >> "$OUTDIR/04-kernel.txt"
done

printf '\n===== zonas térmicas =====\n' >> "$OUTDIR/04-kernel.txt"
for z in /sys/class/thermal/thermal_zone*/; do
    [ -d "$z" ] || continue
    printf '%s %s %s\n' "$(basename "$z")" \
        "$(cat "$z/type" 2>/dev/null)" "$(cat "$z/temp" 2>/dev/null)" \
        >> "$OUTDIR/04-kernel.txt"
done

# -------------------------------------------------------------- 5. gráficos
log "[5/9] gráficos"
run 05-graphics.txt "nós DRM"     ls -l /dev/dri/
run 05-graphics.txt "conectores"  ls /sys/class/drm/
readfiles 05-graphics.txt "painel" /sys/class/drm/card0-DSI-1/status /sys/class/drm/card0-DSI-1/modes /sys/class/drm/card0-DSI-1/enabled

printf '\n===== devfreq (GPU) =====\n' >> "$OUTDIR/05-graphics.txt"
for g in /sys/class/devfreq/*/; do
    [ -d "$g" ] || continue
    printf -- '--- %s ---\ngovernor=%s cur_freq=%s\n' "$(basename "$g")" \
        "$(cat "$g/governor" 2>/dev/null)" "$(cat "$g/cur_freq" 2>/dev/null)" \
        >> "$OUTDIR/05-graphics.txt"
    cat "$g/trans_stat" >> "$OUTDIR/05-graphics.txt" 2>/dev/null
done

# Prova indireta de aceleração: quem mantém o render node aberto.
printf '\n===== clientes do render node =====\n' >> "$OUTDIR/05-graphics.txt"
for p in $(pgrep -f 'phoc|phosh|gnome-shell|sway|weston' 2>/dev/null); do
    [ -d "/proc/$p/fd" ] || continue
    n=$(ls -l "/proc/$p/fd" 2>/dev/null | grep -c 'renderD')
    printf 'pid=%s comm=%s fds_renderD=%s\n' "$p" \
        "$(cat /proc/$p/comm 2>/dev/null)" "$n" >> "$OUTDIR/05-graphics.txt"
done

run 05-graphics.txt "drivers mesa"  ls /usr/lib/dri/
run 05-graphics.txt "eglinfo"       eglinfo
run 05-graphics.txt "vulkaninfo"    vulkaninfo --summary

# ------------------------------------------------------------- 6. hardware
log "[6/9] hardware"
run 06-hardware.txt "entradas"   cat /proc/bus/input/devices
run 06-hardware.txt "leds"       ls /sys/class/leds/
run 06-hardware.txt "v4l2"       ls /sys/class/video4linux/
run 06-hardware.txt "typec"      ls /sys/class/typec/
run 06-hardware.txt "udc"        ls /sys/class/udc/

printf '\n===== dispositivos i2c =====\n' >> "$OUTDIR/06-hardware.txt"
for d in /sys/bus/i2c/devices/*/; do
    [ -r "$d/name" ] || continue
    printf '%s: %s\n' "$(basename "$d")" "$(cat "$d/name")" >> "$OUTDIR/06-hardware.txt"
done

printf '\n===== dispositivos spi =====\n' >> "$OUTDIR/06-hardware.txt"
for d in /sys/bus/spi/devices/*/; do
    [ -r "$d/modalias" ] || continue
    printf '%s: %s\n' "$(basename "$d")" "$(cat "$d/modalias")" >> "$OUTDIR/06-hardware.txt"
done

printf '\n===== iio =====\n' >> "$OUTDIR/06-hardware.txt"
for i in /sys/bus/iio/devices/*/; do
    [ -r "$i/name" ] || continue
    printf '%s: %s\n' "$(basename "$i")" "$(cat "$i/name")" >> "$OUTDIR/06-hardware.txt"
done

# ---------------------------------------------------------------- 7. energia
log "[7/9] energia"
printf '===== power supply =====\n' >> "$OUTDIR/07-power.txt"
for p in /sys/class/power_supply/*/; do
    [ -r "$p/uevent" ] || continue
    printf -- '--- %s ---\n' "$(basename "$p")" >> "$OUTDIR/07-power.txt"
    grep -v 'SERIAL' "$p/uevent" >> "$OUTDIR/07-power.txt" 2>/dev/null
done

printf '\n===== cpufreq =====\n' >> "$OUTDIR/07-power.txt"
for c in /sys/devices/system/cpu/cpufreq/policy*/; do
    [ -d "$c" ] || continue
    printf '%s gov=%s cur=%s min=%s max=%s\n' "$(basename "$c")" \
        "$(cat "$c/scaling_governor" 2>/dev/null)" \
        "$(cat "$c/scaling_cur_freq" 2>/dev/null)" \
        "$(cat "$c/cpuinfo_min_freq" 2>/dev/null)" \
        "$(cat "$c/cpuinfo_max_freq" 2>/dev/null)" >> "$OUTDIR/07-power.txt"
done

readfiles 07-power.txt "suspensão" /sys/power/state /sys/power/mem_sleep \
    /sys/power/suspend_stats/success /sys/power/suspend_stats/fail
readfiles 07-power.txt "wakeup sources" /sys/kernel/debug/wakeup_sources

# ----------------------------------------------------------------- 8. rede
log "[8/9] rede"
run 08-network.txt "interfaces"   ip -br addr
run 08-network.txt "rotas"        ip route
run 08-network.txt "escuta"       ss -tulnp
run 08-network.txt "nmcli"        nmcli -t device status
run 08-network.txt "wifi link"    iw dev wlan0 link
run 08-network.txt "power save"   iw dev wlan0 get power_save
run 08-network.txt "modem"        mmcli -L
run 08-network.txt "bluetooth"    bluetoothctl show
run 08-network.txt "rfkill"       rfkill list

# ------------------------------------------------------------ 9. segurança
log "[9/9] segurança"
readfiles 09-security.txt "sysctl" /proc/sys/kernel/randomize_va_space \
    /proc/sys/kernel/kptr_restrict /proc/sys/kernel/dmesg_restrict \
    /proc/sys/kernel/unprivileged_bpf_disabled /sys/kernel/security/lsm
run 09-security.txt "usuários"      awk -F: '$3>=1000||$3==0 {print $1,$3,$7}' /etc/passwd
run 09-security.txt "grupos admin"  getent group wheel sudo adm
run 09-security.txt "suid"          find /usr/bin /usr/sbin /bin /sbin -perm -4000 -type f
run 09-security.txt "sshd config"   grep -vE '^#|^$' /etc/ssh/sshd_config

printf '\n===== vulnerabilidades de cpu =====\n' >> "$OUTDIR/09-security.txt"
for v in /sys/devices/system/cpu/vulnerabilities/*; do
    [ -r "$v" ] || continue
    printf '%s: %s\n' "$(basename "$v")" "$(cat "$v")" >> "$OUTDIR/09-security.txt"
done

# ------------------------------------------------------------- sanitização
if [ "$SANITIZE" -eq 1 ]; then
    log "Sanitizando (IMEI, seriais, MACs, IPs, SSIDs)..."
    for f in "$OUTDIR"/*.txt; do
        [ -f "$f" ] || continue
        sed -E \
            -e 's/\b[0-9]{15}\b/<IMEI-REDIGIDO>/g' \
            -e 's/([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}/<MAC-REDIGIDO>/g' \
            -e 's/androidboot\.serialno=[^ ]*/androidboot.serialno=<REDIGIDO>/g' \
            -e 's/wifimacaddr=[^ ]*/wifimacaddr=<REDIGIDO>/g' \
            -e 's/androidboot\.btmacaddr=[^ ]*/androidboot.btmacaddr=<REDIGIDO>/g' \
            -e 's/vbmeta\.digest=[^ ]*/vbmeta.digest=<REDIGIDO>/g' \
            -e 's/\b(10|192\.168)\.[0-9]{1,3}\.[0-9]{1,3}\b/<IP-PRIVADO-REDIGIDO>/g' \
            -e 's/SSID: .*/SSID: <REDIGIDO>/g' \
            -e 's/^([a-z0-9]+):(wifi|ethernet|gsm|loopback|wifi-p2p):([a-z]+):.*/\1:\2:\3:<SSID-REDIGIDO>/g' \
            -e 's/(GENERAL\.CONNECTION|connection\.id|Connection):[[:space:]]*.*/\1: <SSID-REDIGIDO>/g' \
            -e 's/Connected to ([0-9a-f]{2}:){5}[0-9a-f]{2}/Connected to <MAC-REDIGIDO>/g' \
            "$f" > "$f.tmp" && mv "$f.tmp" "$f"
    done
    printf '\nSanitização aplicada.\n' >> "$MANIFEST"
fi

printf '\nColeta concluída em %s\n' "$(date -u '+%Y-%m-%d %H:%M:%S UTC')" >> "$MANIFEST"

log ""
log "Concluído. Arquivos em: $OUTDIR"
log "Seções sem ferramenta disponível:"
grep 'AUSENTE' "$MANIFEST" >&2 || log "  (nenhuma)"
log ""
log "ATENÇÃO: sem --sanitize a saída contém IMEI, seriais, MACs e IPs."
