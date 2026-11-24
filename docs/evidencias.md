# Evidências

Tabela de rastreabilidade. Cada afirmação importante do projeto, a evidência que a sustenta, onde ela
está e o grau de confirmação.

**Graus:** `CONFIRMADO` (verificado em arquivo/transcrição) · `RELATADO` (dito em prompt/anotação, não
verificado de forma independente) · `RECONSTRUÍDO` (inferido de fluxo + artefatos) · `AUSENTE` (sem
evidência) · `EXTERNO` (doc de terceiros, não prova sobre o nosso aparelho).

> Caminhos pessoais aparecem relativos a `C:\Users\Phmmp\`. Nenhum IMEI, número de série, token ou
> senha é reproduzido aqui (ver `docs/pendencias.md` sobre sanitização).

| ID | Afirmação | Evidência | Localização | Grau |
|----|-----------|-----------|-------------|------|
| E01 | O aparelho é um Motorola Edge 30, codinome `dubai` | rootfs nomeado `motorola-dubai.img`; hostname `motorola-dubai:~$` | `Downloads/Edge30-postmarketOS/`; transcrição 2026-11-18 | CONFIRMADO |
| E02 | Variante `XT2203-1` | Descrição do ambiente no prompt do projeto | Sessão 2026-11-04 (prompt NETOPS/BLACKBOX) | RELATADO |
| E03 | Sistema é postmarketOS (Nura), base Alpine | Trio de imagens no padrão pmbootstrap; uso de `apk`; prompts citam "Nura Linux edge" | `Downloads/Edge30-postmarketOS/`; scripts `edge30-netops-lab/` | CONFIRMADO |
| E04 | Interface Phosh/Wayland | Prompt descreve Phosh 0.58; captura da UI enviada do aparelho | Sessão 2026-11-04 | RELATADO (versão) / CONFIRMADO (UI existe) |
| E05 | Kernel 7.2.9 linha mainline | Prompt ("confirmar novamente"); família `sc7280` no pacote pmOS | Sessão 2026-11-04; wiki pmOS | RELATADO / EXTERNO |
| E06 | Imagens `boot/dtbo/rootfs` geradas e íntegras | `SHA256SUMS` + reconferência `sha256sum` | `Downloads/Edge30-postmarketOS/SHA256SUMS` | CONFIRMADO |
| E07 | `boot.img` = 27,2 MiB, sha256 `d101233…fa23b7` | `sha256sum` / `ls -la` | idem | CONFIRMADO |
| E08 | `dtbo.img` = 24,0 MiB, sha256 `95aeaae0…f8369` | `sha256sum` / `ls -la` | idem | CONFIRMADO |
| E09 | `motorola-dubai.img` = 2,04 GiB, sha256 `874374ce…51b842` | `sha256sum` / `ls -la` | idem | CONFIRMADO |
| E10 | Build feito em VM Ubuntu com pmbootstrap | `postmarketOS-Build.vbox` (`Ubuntu25_64`, 4096 MB); logs 2026-11-04 | `VirtualBox VMs/postmarketOS-Build/` | CONFIRMADO (VM) / RECONSTRUÍDO (comandos) |
| E11 | Bootloader destravado | O aparelho roda imagens custom (só possível destravado) | inferência | RECONSTRUÍDO |
| E12 | Gravação por fastboot das partições | Imagens existem e o device bootou; sem log de flash capturado | — | RECONSTRUÍDO |
| E13 | Aparelho inicializa em Linux com GUI | Captura da UI Phosh (1080×2400) enviada do aparelho | Sessão 2026-11-04 | CONFIRMADO |
| E14 | Wi-Fi funcional | SSH sobre Wi-Fi; referências a `wlan0` | Sessões 2026-11-04 / 2026-11-18 | CONFIRMADO |
| E15 | SSH funcional | Conexões `ssh user@172.70.8.137`; prompt remoto | Sessões 2026-11-04 / 2026-11-18 | CONFIRMADO |
| E16 | `apk` operante; pacotes de rede instalados e revertidos | Scripts `00-backup.sh`/`10-packages.sh`; "rollback idêntico ao backup" | `edge30-netops-lab/deploy/`; sessão 2026-11-04 | CONFIRMADO |
| E17 | 18 testes passaram no aparelho | Relato da sessão após rodar a suíte no device | Sessão 2026-11-04 | RELATADO |
| E18 | Parsers de rede (iw/ping/ss/nmap/tshark) escritos e testados | Código-fonte local com testes | `edge30-cyberlab/cyberlab/*.py`, `tests/` | CONFIRMADO (código) |
| E19 | Ferramentas ofensivas (wifipumpkin3, bettercap) executadas no device | Comandos no histórico da sessão | Sessão 2026-11-18 | CONFIRMADO (execução) / AUSENTE (resultado/efeito) |
| E20 | `dubai` é *testing* no pmOS, sem imagem pré-pronta | Resultado de busca na wiki | web, 2026-11-24 | EXTERNO |
| E21 | Kernel sc7280-mainline tem relato de baixa responsividade | Resultado de busca na wiki | web, 2026-11-24 | EXTERNO |
| E22 | DTS do Edge 30 enviado ao kernel em mar/2026; display via `simplefb` | Patch LKML | web, 2026-11-24 | EXTERNO |
| E23 | Áudio, modem, dados, GPU, câmera, BT, NFC, sensores, bateria | — nenhuma verificação | — | AUSENTE |
| E24 | Sessões sobre `boot.img`/Magisk eram do **Moto G9 (CEBU/XT2091)** | Logs citam `CEBU_RETAIL…XT2091`, fastboot `cebu` | Sessão 2026-10-28; `Documents/projeto-root-moto-g9/` | CONFIRMADO (⚠️ não confundir com o Edge 30) |

## Nota metodológica

A busca foi dirigida por nomes: *postmarketOS, pmbootstrap, Motorola, Edge, dubai, fastboot, adb, boot,
kernel, device tree*. Priorizei `Downloads/` e as pastas de projeto reveladas pela busca
(`edge30-netops-lab/`, `edge30-cyberlab/`, `VirtualBox VMs/postmarketOS-Build/`) e as transcrições de
sessão em `.claude/projects/`. Não houve varredura indiscriminada de arquivos pessoais.

**Correção importante (E24):** material de *root* via `boot.img`/Magisk/firmware `CEBU…XT2091`
pertence ao **Moto G9**, projeto distinto. Ele **não** é evidência do port do Edge 30 e foi separado
para não contaminar a narrativa.

---

## Auditoria no aparelho — 24/11/2026

Evidências obtidas por acesso SSH ao aparelho físico. Saídas completas e sanitizadas em
[`audit/evidence/sanitized/`](../audit/evidence/sanitized/); matriz em
[`audit/hardware-compatibility.csv`](../audit/hardware-compatibility.csv).

| ID | Afirmação | Evidência | Localização | Grau |
|----|-----------|-----------|-------------|------|
| E25 | O sistema instalado é **Nura edge**, não postmarketOS puro | `/etc/os-release`: `ID=nura`, `ID_LIKE=alpine`, repos `mirror.nura.eco` | `audit/evidence/sanitized/01-base.txt` | CONFIRMADO |
| E26 | O init é **systemd**, não OpenRC | `/sbin/init -> ../lib/systemd/systemd`; 37 serviços systemd ativos | `audit/evidence/sanitized/02-os.txt` | CONFIRMADO |
| E27 | Kernel **7.2.9** `#3-postmarketos-qcom-sc7280`, clang 23.1.3, build 17/10/2026 | `uname -a` e `/proc/version` lidos no aparelho — **substitui o "[RELATADO]" de E05 e encerra P-02** | `audit/evidence/sanitized/01-base.txt` | CONFIRMADO |
| E28 | Hardware reconhecido como `Motorola Edge 30 (CSOT)` / `motorola,dubai` / `qcom,sm7325` | Device tree em `/sys/firmware/devicetree/base/model` e `compatible` | `audit/evidence/sanitized/01-base.txt` | CONFIRMADO |
| E29 | **Bootloader destravado** | `cmdline`: `verifiedbootstate=orange`, `vbmeta.device_state=unlocked` — **eleva E11 de RECONSTRUÍDO a CONFIRMADO** | `audit/evidence/sanitized/02-os.txt` | CONFIRMADO |
| E30 | **Aceleração gráfica por hardware ativa** | `phoc` com 5 fds em `/dev/dri/renderD128`; `libgallium-26.2.6`, `libEGL`, `libGLESv2`, `libvulkan` mapeadas; devfreq da GPU com 191 transições e 4876 ms a 608 MHz | `audit/evidence/sanitized/07-perf.txt`, `09-extra.txt` | CONFIRMADO |
| E31 | **Áudio de saída funcional** | Sink `HiFi__Speaker__sink` em RUNNING a 48 kHz; tom de 440 Hz confirmado como audível pelo operador | `audit/evidence/sanitized/13-audio-test.txt` | CONFIRMADO |
| E32 | **Microfone funcional** | `parecord` capturou 1 042 600 bytes em 4 s com sinal não nulo; áudio descartado após medição de nível | `audit/evidence/sanitized/12-input-audio.txt` | CONFIRMADO |
| E33 | **Touchscreen NÃO funcional** | IRQ 170 (`goodix-berlin`) imóvel em 1346 durante 30 s de toque físico, com `dpms=On` e backlight 1079; `spurious=0` | `audit/evidence/sanitized/14-goodix.txt` | CONFIRMADO |
| E34 | **Botões físicos funcionais** | IRQ 117 (`pmic_resin`) subiu de 0 para 4 após pressionamento físico | `audit/evidence/sanitized/12-input-audio.txt` | CONFIRMADO |
| E35 | Modem inicializado, bloqueado por **ausência de SIM** | `mmcli`: firmware MPSS carregado, QMI sobre `qrtr0` operante, suporta 5gnr; `failed reason: sim-missing`. Ausência de SIM confirmada pelo operador | `audit/evidence/sanitized/10-faults.txt` | CONFIRMADO |
| E36 | Wi-Fi funcional em **Wi-Fi 6 / 5 GHz** | TX 432,3 Mbit/s, RX 206,4 Mbit/s, −66 dBm; SSH sustentado por ~40 min | `audit/evidence/sanitized/05-devices.txt` | CONFIRMADO |
| E37 | Bluetooth detectado, **bloqueado por rfkill** | 1781 comandos HCI sem erro, porém `Soft blocked: yes` e `power on` falhou | `audit/evidence/sanitized/11-bt-test.txt` | CONFIRMADO (bloqueio) / AUSENTE (função) |
| E38 | Bateria funcional, **0,89 W em repouso** | 20 amostras: −225 mA médios a 3,958 V, 33,0 °C constante, SOH 100 | `audit/evidence/sanitized/08-battery-samples.txt` | CONFIRMADO |
| E39 | **Suspensão nunca exercida** | `/sys/power/suspend_stats/success = 0` e `fail = 0` | `audit/evidence/sanitized/05-devices.txt` | CONFIRMADO |
| E40 | **Conflito PulseAudio × PipeWire** | Ambos em execução; log: `pipewire-pulse.socket: refusing` e `Daemon already running` | `audit/evidence/sanitized/10-faults.txt` | CONFIRMADO |
| E41 | **Armazenamento sem criptografia** | Nenhum mapeamento LUKS em `lsblk`; rootfs ext4 de 227 GB em claro | `audit/evidence/sanitized/06-sec.txt` | CONFIRMADO |
| E42 | Matriz oficial do device obtida da wiki | Página `wiki.nura.eco` acessada por navegador, contornando o Anubis — **encerra P-04** | `audit/upstream-comparison.md` | EXTERNO |
| E43 | Sensores presentes no hub ADSP, não validados | `iio-sensor-proxy`: `HasAccelerometer/HasAmbientLight/HasProximity = true`; `Claim` negado por polkit em sessão SSH | `audit/evidence/sanitized/15-sensors.txt`, `16-accel.txt` | CONFIRMADO (presença) / AUSENTE (função) |

**Efeito sobre E23:** a afirmação "áudio, modem, dados, GPU, câmera, BT, NFC, sensores, bateria —
nenhuma verificação", antes `AUSENTE`, está **substituída** por E30–E43 e pela matriz completa de
34 subsistemas.
