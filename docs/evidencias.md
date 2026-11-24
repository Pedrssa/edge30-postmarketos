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
