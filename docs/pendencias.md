# Pendências, lacunas e próximos passos

Prioridade: **P0** (bloqueia a precisão da história) · **P1** (valor alto) · **P2** (desejável).

| ID | Pendência | Prioridade | Critério de validação |
|----|-----------|------------|------------------------|
| P-01 | **Levantar a matriz de funcionalidades no próprio aparelho**: áudio, modem/chamadas/SMS, dados móveis, GPU, câmera, Bluetooth, NFC, sensores, bateria/carga | P0 | Saída de comandos no device (ex.: `pactl list`, `mmcli -L`, `bluetoothctl show`, `cat /sys/class/power_supply/*/*`) colada em `evidence/` com data |
| P-02 | **Confirmar a versão do kernel** por leitura direta | P0 | `uname -a` e `cat /proc/version` do aparelho (substitui o "7.2.9 [RELATADO]") |
| P-03 | **Capturar um log de regravação limpa** (fastboot/pmbootstrap flasher) para transformar os passos [RECONSTRUÍDO] em [CONFIRMADO] | P1 | Transcript/arquivo de log da sessão de flash |
| P-04 | **Ler a matriz oficial do device** na wiki (bloqueada por Anubis em `wiki.nura.eco`) | P1 | Abrir em navegador normal e colar as seções em `docs/relatorio-tecnico.md §3/§14` |
| P-05 | **Documentar o rollback real** para o Android (ferramenta e passos usados) | P1 | Passo a passo com evidência do retorno |
| P-06 | **Medir o impacto da baixa responsividade** relatada no kernel sc7280-mainline | P2 | Observação com método (ex.: latência de toque, logs de erro do kernel) |
| P-07 | **Imagens fora do Git** (2 GB) — definir destino (release com LFS? armazenamento externo?) | P2 | Decisão registrada; link se publicado |
| P-08 | **Separar/arquivar o material do Moto G9** para não se misturar a este projeto | P2 | Pasta/relatório próprio do G9 |

## Observações de sanitização (antes de publicar)

- **Não** subir: IMEI, número de série (ex.: aparece `getvar`/serial em logs de projetos correlatos),
  tokens, senhas, IPs internos sensíveis, `/etc/shadow`, chaves SSH de host.
- As imagens (`*.img`, `*.vdi`, `*.vbox`) estão no `.gitignore`.
- Os trechos em `evidence/` são **cópias sanitizadas**; os originais ficam só localmente.
