# Pendências, lacunas e próximos passos

Prioridade: **P0** (bloqueia a precisão da história) · **P1** (valor alto) · **P2** (desejável).

> **Atualizado em 24/11/2026** após a auditoria técnica executada no aparelho
> (ver [`audit/`](../audit/)). Pendências encerradas foram mantidas no registro, marcadas como
> **RESOLVIDA**, para preservar a cronologia do projeto.

## Pendências originais

| ID | Pendência | Prioridade | Situação |
|----|-----------|------------|----------|
| P-01 | **Levantar a matriz de funcionalidades no próprio aparelho** | P0 | ✅ **RESOLVIDA (24/11/2026)** — 34 subsistemas classificados com evidência em [`audit/hardware-compatibility.csv`](../audit/hardware-compatibility.csv). Restam 5 itens `NÃO TESTADO` que dependem de SIM ou acesso físico (ver P-09). |
| P-02 | **Confirmar a versão do kernel** por leitura direta | P0 | ✅ **RESOLVIDA** — `7.2.9 #3-postmarketos-qcom-sc7280`, clang 23.1.3, build 17/10/2026. Evidência E27. |
| P-03 | **Capturar um log de regravação limpa** (fastboot/pmbootstrap flasher) | P1 | ⏳ **Em aberto.** A auditoria não envolveu regravação. Ganhou relevância: o método oficial usa **U-Boot + USB mass storage**, não `fastboot flash` direto (ver [`audit/upstream-comparison.md` §4](../audit/upstream-comparison.md)). |
| P-04 | **Ler a matriz oficial do device** na wiki (bloqueada por Anubis) | P1 | ✅ **RESOLVIDA** — página obtida por navegador e comparada item a item em [`audit/upstream-comparison.md`](../audit/upstream-comparison.md). Evidência E42. |
| P-05 | **Documentar o rollback real** para o Android | P1 | ⏳ **Em aberto.** A wiki documenta recuperação por **EDL** (PID 9008) com a Motorola Unbrick Tool, e há ponto de teste EDL confirmado. |
| P-06 | **Medir o impacto da baixa responsividade** relatada no kernel sc7280-mainline | P2 | 🔄 **Reformulada.** A causa provável foi identificada: **o touchscreen não entrega eventos** (A-01). O que se relatava como "baixa responsividade" pode ser ausência total de resposta ao toque. |
| P-07 | **Imagens fora do Git** (2 GB) — definir destino | P2 | ⏳ **Em aberto.** |
| P-08 | **Separar/arquivar o material do Moto G9** | P2 | ⏳ **Em aberto.** |

## Pendências abertas pela auditoria

| ID | Pendência | Prioridade | Critério de validação |
|----|-----------|------------|------------------------|
| ~~P-09~~ | ~~Corrigir o touchscreen~~ | ✅ **CANCELADA (24/11)** | **Falso positivo.** O touchscreen sempre funcionou: 6942 eventos capturados de `/dev/input/event3`. O erro foi de método — janela de medição dessincronizada do toque físico. |
| ~~P-10~~ | ~~Resolver o conflito PulseAudio × PipeWire~~ | ✅ **RESOLVIDA (24/11)** | PipeWire desabilitado em escopo global; PulseAudio mantido e áudio validado por audição. ⚠️ Se um SIM for inserido e houver necessidade de chamadas, revisar — a wiki exige `pipewire`. |
| ~~P-11~~ | ~~Obter `dmesg` completo com root~~ | ✅ **RESOLVIDA (24/11)** | `dmesg` coletado. O driver do touch **não emite nenhuma mensagem** além do registro do input; a pista passou a ser o conflito de pinctrl no GPIO_105. Ver [`audit/root-findings.md`](../audit/root-findings.md). |
| ~~P-12~~ | ~~Validar Bluetooth após remover o bloqueio `rfkill`~~ | ✅ **RESOLVIDA (24/11)** | `hci0` subiu para `UP RUNNING PSCAN` com firmware QCA completo. Resta tornar o desbloqueio persistente e testar um pareamento. |
| **P-13** | **Validar sensores fora de sessão SSH** — `iio-sensor-proxy` os reporta presentes, mas polkit negou a reivindicação | P1 | Rotação automática de tela ao girar o aparelho (ver [`audit/manual-validation-checklist.md` §A1](../audit/manual-validation-checklist.md)). |
| **P-14** | **Testar telefonia, dados móveis e GPS com SIM inserido** | P1 | `mmcli -m 0` em `registered`; chamada com áudio nos dois sentidos; SMS; navegação sem Wi-Fi. |
| **P-15** | **Suspensão não funciona (A-04)** — testada: `deep` aborta com `Wakeup pending`; `s2idle` **trava o aparelho e força reboot** | **P0** ⬆️ | `suspend_stats/success` incrementa e o aparelho retorna íntegro. Defeito de kernel, **não consta da wiki** — candidato a relato upstream. |
| **P-16** | **Avaliar FDE em reinstalação planejada (A-03)** — armazenamento hoje em texto claro com bootloader destravado | P1 | `lsblk` exibe mapeamento `crypt` e o boot solicita desbloqueio. **Operação destrutiva — exige backup validado.** |
| **P-17** | **Validar a câmera com libcamera** | P2 | Captura real com o sensor ultrawide (S5KJN1). Observar que o sensor principal (OV50A) e o frontal (OV32B40) não têm driver disponível. |
| ~~P-18~~ | ~~Endurecimento de segurança~~ | ✅ **RESOLVIDA (24/11)** | `kptr_restrict=2`, LLMNR desativado e `PasswordAuthentication no` aplicados e persistentes após reboot. ⚠️ O acesso agora depende **exclusivamente** da chave SSH. |
| **P-19** | **Contribuir os achados upstream** | P2 | Relato da falha do touchscreen no canal `#sc7280-mainline:postmarketos.org`, já que a wiki declara `Works`. |
| **P-20** | **Cruzar CVEs** contra o inventário de 1326 pacotes | P2 | Relatório de scanner sobre a lista de `apk info -v`. |
| **P-21** | **Investigar o BDF ausente do Wi-Fi** — reforçado: mesmo com `power_save` desligado a perda permanece em 17% — `ath11k` reporta `qmi failed to download BDF:-2` e `board_id 0xff`, operando sem a calibração de fábrica | P1 | `dmesg` sem erro de board data e melhora mensurável na estabilidade do enlace. Candidato a relato upstream. |

## Observações de sanitização (antes de publicar)

- **Não** subir: IMEI, número de série, tokens, senhas, IPs internos sensíveis, `/etc/shadow`,
  chaves SSH de host.
- As imagens (`*.img`, `*.vdi`, `*.vbox`) estão no `.gitignore`.
- Os trechos em `evidence/` são **cópias sanitizadas**; os originais ficam só localmente.
- **As evidências da auditoria** em [`audit/evidence/sanitized/`](../audit/evidence/sanitized/)
  passaram por redação automatizada de IMEI, número de série, endereços MAC, IPs privados e SSID,
  com verificação programática posterior. O script
  [`collect-diagnostics.sh`](../audit/scripts/collect-diagnostics.sh) oferece a flag `--sanitize`
  para reproduzir essa redação em coletas futuras.
