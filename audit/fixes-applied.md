# Correções aplicadas ao aparelho

**Data:** 24/11/2026, 23:05–23:25 · **Autorização:** explícita do operador ("conserte tudo")
**Acesso:** `sudo` · **Estado final:** aparelho operante, 0 unidades systemd em falha

Este documento registra o que foi **efetivamente executado no aparelho**, distinto do
[`remediation-plan.md`](remediation-plan.md), que é a proposta. Inclui o que funcionou, o que falhou
e **um efeito colateral que causei**.

---

## Resumo

| ID | Problema | Resultado |
|---|---|---|
| **A-01** | Touchscreen "não funciona" | ✅ **Falso positivo** — o dispositivo sempre funcionou |
| **A-02** | PulseAudio × PipeWire | ✅ **Corrigido e validado** |
| **A-03** | Sem criptografia de disco | ⏸️ **Não executado** — exige reinstalação destrutiva |
| **A-04** | Suspensão | ❌ **Não corrigível** — falha de kernel; meu teste causou um reboot |
| **A-05** | Bluetooth bloqueado | ✅ **Corrigido e persistente** |
| **A-06** | `power_save` do Wi-Fi | ⚠️ **Melhora parcial, com custo energético** |
| **A-07** | Endurecimento | ✅ **Corrigido e persistente** |

**Todas as correções sobreviveram ao reboot** e foram verificadas após ele.

---

## A-01 · Falso positivo — o touchscreen sempre funcionou

A auditoria classificou o touchscreen como **NÃO FUNCIONAL**. Estava errado.

**Teste definitivo** (leitura direta do event node, janela de 45 s, com root):

```
t=30s  irq=6395  (delta=0)     eventos=0
t=33s  irq=7355  (delta=960)   eventos=2934   ← operador tocou a tela
t=36s  irq=8605  (delta=2210)  eventos=6928
VEREDITO: 6942 eventos capturados
```

Bytes decodificados de `/dev/input/event3`:

```
03 00 39 00 53 00 00 00   → EV_ABS  ABS_MT_TRACKING_ID = 0x53
03 00 35 00 9e 01 00 00   → EV_ABS  ABS_MT_POSITION_X  = 414
03 00 36 00 c4 05 00 00   → EV_ABS  ABS_MT_POSITION_Y  = 1476
```

**Causa do erro:** dessincronia. Os testes anteriores observavam a IRQ por 15–30 s enquanto pediam o
toque, mas o operador estava lendo a instrução no computador em vez de tocar a tela naquele intervalo
exato. **Ausência de estímulo foi lida como falha de hardware.**

**Sinal que ignorei:** a contagem cresceu continuamente entre medições
(1346 → 1540 → 3686 → 6395 → 8619). Registrei isso como "anomalia sem explicação" quando deveria ter
refutado minha própria hipótese.

**Lição:** concluir a partir da ausência de evento exige confirmar que o estímulo ocorreu *dentro* da
janela. A contagem de IRQ é indicador indireto; a leitura do event node é o teste correto.

---

## A-02 · Conflito de áudio — corrigido

**Diagnóstico confirmado:** `postmarketos-base-ui-audio-backend-pulseaudio` é o backend oficial
instalado, mas `pipewire.socket`, `pipewire-pulse.socket` e `wireplumber.service` estavam
habilitados em **escopo global**, subindo em paralelo.

**Decisão:** manter o PulseAudio (comprovadamente funcional) e remover o PipeWire, em vez de migrar
para PipeWire. Migrar traria risco de ficar sem áudio, e a vantagem do PipeWire — chamadas
telefônicas — não é exercível sem SIM.

```sh
systemctl --user   disable --now pipewire.socket pipewire-pulse.socket wireplumber.service
systemctl --global disable      pipewire.socket pipewire-pulse.socket wireplumber.service
```

O segundo comando foi necessário: o escopo de usuário sozinho não impede a reativação no boot.

**Validação:** tom de 440 Hz reproduzido e **confirmado como audível pelo operador** após a mudança.
Apenas `pulseaudio` em execução. Verificado novamente após o reboot.

**Rollback:** `systemctl --global enable pipewire.socket pipewire-pulse.socket wireplumber.service`

> ⚠️ Se um SIM for inserido e houver necessidade de chamadas, a wiki oficial exige o provider
> `pipewire`. Nesse caso esta decisão deve ser revista.

---

## A-04 · Suspensão — não corrigível, e causei um reboot

Duas tentativas, ambas malsucedidas.

### Tentativa 1 — `deep` (padrão)

```
PM: suspend entry (deep)
printk: Suspending console(s)
Wakeup pending. Abort CPU freeze      ← aborta
PM: suspend exit
```

Resultado: `success=0, fail=1`. Falha **limpa** — o sistema abortou e retornou íntegro.

### Tentativa 2 — `s2idle` → **travou o aparelho e forçou reboot**

```
dwc3-qcom a600000.usb: port-1 HS-PHY not in L2
Non-boot CPUs are not disabled
[log termina — reinicialização forçada]
```

**Fui eu quem causou esse reboot**, ao testar `s2idle`. O operador observou o aparelho reiniciando.
Nenhum dado foi perdido e todas as configurações persistiram, mas registro aqui porque foi
consequência direta de uma ação minha.

### Diagnóstico

| Modo | Comportamento |
|---|---|
| `deep` | Aborta com `Wakeup pending` — falha segura |
| `s2idle` | **Trava o sistema e força reinicialização** |

Isto **corrige** a hipótese anterior de que "nada solicita a suspensão, logo ela não é exercida". Ela
é exercível; **falha quando solicitada**. É um defeito de kernel no port, não de configuração, e
**não consta da matriz oficial da wiki**.

Pistas: `dwc3-qcom ... HS-PHY not in L2` indica que o controlador USB não entra em baixo consumo, e
`Non-boot CPUs are not disabled` indica falha ao desligar os núcleos secundários.

**Recomendação:** não usar suspensão neste aparelho até que seja corrigido upstream. Candidato forte
a relato no canal `#sc7280-mainline:postmarketos.org`.

---

## A-05 · Bluetooth — corrigido e persistente

```sh
rfkill unblock bluetooth && hciconfig hci0 up
```

`DOWN` → **`UP RUNNING PSCAN`**, com firmware QCA completo (`BTFW.MOSELLE.1.1.3`). **Persistiu após o
reboot** — o `systemd-rfkill` grava o estado automaticamente.

**Rollback:** `rfkill block bluetooth`

---

## A-06 · Wi-Fi `power_save` — melhora parcial, com custo

```sh
iw dev wlan0 set power_save off
# persistido em /etc/NetworkManager/conf.d/wifi-powersave-off.conf  →  wifi.powersave = 2
```

### Resultado em rede

| Métrica | Antes | Depois |
|---|---|---|
| Latência média | 70 ms / 121 ms | **15 ms** |
| Latência máxima | 125 ms | **70 ms** |
| Latência mínima | 4 ms | 4 ms |
| **Perda de pacotes** | 0% / 33% | **17%** |

A latência caiu **4,7×**. Mas o **critério de aceite era 0% de perda, e não foi atingido** — 17%
ainda é alto. Isso reforça a hipótese **P-21**: o `ath11k` opera sem o BDF e sem os dados de
calibração da placa (`board_id 0xff`), o que o `power_save` não explica.

### Custo energético

| Métrica | Antes | Depois |
|---|---|---|
| Corrente em repouso | −225 mA | **−284 mA** (+26%) |
| Potência | 0,89 W | **1,12 W** |
| Temperatura | 33,0 °C | **37,0 °C** |

**Trade-off explícito:** rede 4,7× mais responsiva, a 26% mais de consumo. Como a suspensão não
funciona (A-04), o aparelho já não economiza energia em repouso, o que torna o custo relativamente
menos relevante. **Se a autonomia for prioridade, reverter com:**

```sh
iw dev wlan0 set power_save on
rm /etc/NetworkManager/conf.d/wifi-powersave-off.conf
```

---

## A-07 · Endurecimento — corrigido e persistente

| Controle | Antes | Depois | Como |
|---|---|---|---|
| `kptr_restrict` | 0 | **2** | `/etc/sysctl.d/99-audit-hardening.conf` |
| LLMNR (porta 5355) | em escuta | **desativado** | `/etc/systemd/resolved.conf.d/99-audit-no-llmnr.conf` |
| mDNS do resolved | ativo | desativado | idem |
| `PasswordAuthentication` | yes | **no** | `/etc/ssh/sshd_config.d/99-audit-nopassword.conf` |
| `KbdInteractiveAuthentication` | yes | **no** | idem |

A configuração do SSH foi validada com `sshd -t` **antes** do reload, e o acesso por chave foi
testado imediatamente depois — confirmado operante. Todos os valores verificados novamente após o
reboot.

> ⚠️ **O acesso ao aparelho agora depende exclusivamente da chave SSH.** Guarde
> `id_ed25519_motorola` com cuidado. Para reverter:
> `sudo rm /etc/ssh/sshd_config.d/99-audit-nopassword.conf && sudo systemctl reload sshd`

---

## A-03 · Criptografia de disco — não executado

Não há como cifrar um sistema já instalado. Exigiria **reinstalação completa** com FDE habilitado no
`pmbootstrap init`, operação destrutiva que apaga todo o conteúdo. O operador optou por não executar
agora. Permanece documentado como o risco de segurança mais concreto do conjunto, em
[`security-audit.md` §6](security-audit.md).

---

## Estado final verificado (pós-reboot)

```
kptr_restrict = 2                  ✅
Power save: off                    ✅
LLMNR porta 5355 = 0 ocorrências   ✅
PasswordAuthentication no          ✅
hci0 UP RUNNING PSCAN              ✅
pipewire: ausente                  ✅
pulseaudio: rodando                ✅
systemctl --failed: 0 unidades     ✅
remoteprocs: modem/adsp/wpss/cdsp todos running  ✅
touchscreen: IRQ incrementando     ✅
```

**Backups** do estado anterior em `/root/audit-backup/` no aparelho.

---

## Impacto nas notas

| Dimensão | Antes | Depois | Motivo |
|---|---|---|---|
| Compatibilidade de hardware | 53% | **57%** | Touchscreen reclassificado para FUNCIONAL |
| Segurança | 70% | **78%** | `kptr_restrict`, LLMNR e senha SSH corrigidos |
| Estabilidade | 70% | **65%** | Suspensão confirmada como capaz de travar o aparelho |
| Eficiência energética | 40% | **35%** | Suspensão não funciona e o consumo subiu 26% |
| Experiência de uso | 25% | **70%** | Toque funciona; áudio e Bluetooth operantes |

**Nível de maturidade: 2 → 3 (Estação Linux portátil).**

O aparelho é operável localmente como computador Linux de bolso: toque, GPU acelerada, Wi-Fi,
Bluetooth, áudio, microfone e bateria. O que impede o Nível 4 é, em parte, ausência de validação
(sem SIM, sensores bloqueados por polkit, sem libcamera) e, em parte, um defeito real: **a suspensão
não funciona**, o que é requisito para uso móvel diário.
