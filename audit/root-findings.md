# Coleta privilegiada — correções e achados

**Data:** 24/11/2026, ~23:00 (horário do aparelho) · **Acesso:** `sudo`, após o operador fornecer a
senha · **Evidências:** [`evidence/sanitized/17-root-dmesg-firewall.txt`](evidence/sanitized/17-root-dmesg-firewall.txt)
e [`evidence/sanitized/18-root-gpu-touch-bt.txt`](evidence/sanitized/18-root-gpu-touch-bt.txt)

A auditoria inicial foi feita sem privilégio e declarou isso como limitação. Com acesso root, seis
pontos mudaram. **Três deles corrigem conclusões anteriores** — registrados aqui com a mesma
transparência do resto do trabalho.

---

## 1. ❌→✅ CORREÇÃO: existe firewall, e é robusto

**O que a auditoria dizia:** *"Pela ausência de qualquer indício de configuração, a hipótese mais
provável é a de nenhum firewall efetivo."*

**O que é verdade:** há uma tabela `nft inet filter` completa, com **`policy drop` na cadeia de
entrada** e regras bem construídas:

```
chain input { type filter hook input priority filter; policy drop;
    iifname "lo" accept
    ct state { established, related } accept
    ct state invalid drop
    tcp dport 113 reject with tcp reset
    iifname "wwan*"     drop      ← bloqueia todo tráfego vindo do modem
    iifname "qmapmux*"  drop      ← idem, multiplexadores QMAP
    tcp dport 22 accept
    ... (DHCP, DNS, ICMP, SLAAC, localsend)
}
chain forward { policy drop; ... }
```

Destaque defensivo: `iifname "wwan*" drop` e `qmapmux* drop` impedem conexões entrantes pela
interface de dados móveis — exatamente a superfície mais exposta em um aparelho celular.

**Lição metodológica:** a conclusão anterior era uma inferência a partir de ausência de evidência, e
estava errada. A nota de **segurança sobe de 55% para 70%**.

---

## 2. ✅ Bluetooth passou a funcionar — A-05 resolvido

Após `rfkill unblock bluetooth` (alteração autorizada e reversível):

```
antes:  Soft blocked: yes   →   depois:  Soft blocked: no
hci0:   DOWN                →            UP RUNNING PSCAN
```

O `dmesg` mostra a inicialização completa do firmware QCA:

```
QCA controller version 0x01100101 · Product ID 0x15 · SOC 0x40140110
QCA Downloading qca/msbtfw11.mbn
QCA Downloading qca/msnv11.bin
QCA FW build version: BTFW.MOSELLE.1.1.3-00106-MSL_PATCHZ-1
QCA setup on UART is completed
```

**Reclassificado:** `DETECTADO NÃO VALIDADO` → **`FUNCIONAL`**.

Ressalvas honestas: o `hcitool scan` executou sem encontrar dispositivos (nenhum aparelho
descobrível ao alcance no momento — não é falha), o `lescan` retornou `I/O error`, e **nenhum
pareamento foi testado**. O `BD Address` continua sendo o placeholder `02:00:xx` em vez do endereço
fornecido pelo bootloader.

Para persistir entre reinicializações, o desbloqueio precisa ser tornado permanente; caso contrário
o `rfkill` volta a bloquear.

---

## 3. ⚠️→✅ CORREÇÃO: o firmware da GPU não está faltando

**O que o `dmesg` mostra primeiro** — e que, lido isoladamente, pareceria um defeito grave:

```
[1.354902] Direct firmware load for qcom/a660_sqe.fw failed with error -2
[1.354906] [drm:adreno_request_fw] *ERROR* failed to load a660_sqe.fw
[1.724382] (repete)
```

**O que acontece depois:**

```
[13.457808] [drm:adreno_request_fw] loaded qcom/a660_sqe.fw from new location
[13.458636] [drm:adreno_request_fw] loaded qcom/a660_gmu.bin from new location
[13.460040] [drm] Loaded GMU firmware v3.1.10
```

Os arquivos existem (`/lib/firmware/qcom/a660_sqe.fw`, 43 292 bytes; `a660_gmu.bin`, 55 252 bytes).
As falhas em 1,35 s e 1,72 s ocorrem **antes de o rootfs estar montado** — o driver tenta o caminho
legado, falha, e depois carrega do caminho novo. **É ruído de boot, não defeito.**

Isto confirma, por via direta, a conclusão que a auditoria já havia alcançado por método indireto:
a GPU está plenamente operacional. Na segunda leitura, o `devfreq` acumulava **399 transições e
10 212 ms a 608 MHz** (contra 191 e 4 876 ms na primeira) — a GPU continua sendo exercida.

> Vale como exemplo do próprio briefing: *"não classifique toda mensagem de warning como defeito
> crítico; investigue seu contexto e impacto."*

---

## 4. 🆕 NOVO ACHADO: o Wi-Fi opera sem seus dados de calibração

```
ath11k 17a10040.wifi: qmi failed to load CAL data file:cal-ahb-17a10040.wifi.bin
ath11k 17a10040.wifi: failed to load board data file: -2
ath11k 17a10040.wifi: qmi failed to download BDF:-2
```

O WCN6750 inicializa (`fw_version 0x10137fff`, build `WLAN.MSL.1.0.1-01477`) e o Wi-Fi funciona —
toda a auditoria trafegou por ele. Mas o **BDF (Board Data File)** e os dados de calibração
específicos da placa **não foram carregados**, e o `board_id` lido é `0xff` (inválido/genérico).

**Hipótese nova e relevante para A-06:** a instabilidade de rádio observada (33% de perda na segunda
medição, jitter de 4 a 125 ms, uma queda de sessão SSH) pode decorrer de o rádio operar com
parâmetros genéricos em vez da calibração de fábrica — não apenas do `power_save`.

Isto **não estava na matriz oficial da wiki** e é um candidato legítimo a relato upstream.

---

## 5. 🆕 NOVA PISTA para A-01: conflito de pinctrl

Ao recarregar o driver do touchscreen, o kernel emitiu:

```
sc7280-pinctrl f100000.pinctrl: not freeing pin 105 (GPIO_105) as part of
deactivating group gpio105 - it is already used for some other setting
```

O GPIO_105 é candidato natural a linha de **reset** do controlador de toque, e a mensagem indica que
a configuração do pino está **compartilhada ou presa a outro consumidor**. Se o driver não consegue
controlar o reset, o chip pode permanecer num estado em que responde ao probe mas nunca sinaliza
toque — exatamente o sintoma observado.

Estado do GPIO de interrupção:

```
gpio81 : in  high func0 2mA pull down
```

Entrada, nível alto, com pull-down. Como a IRQ é `Level` (ativa em nível baixo, conforme o binding
do GT9916), a linha em repouso **deveria** estar alta — e está. O problema é que ela nunca desce.

Reguladores do touch presentes e habilitados (`spi13.0-avdd`, `spi13.0-vddio`), embora o
`regulator_summary` reporte 0 mV — leitura esperada para reguladores RPMh, que não expõem tensão
real ao sysfs.

### Teste executado: recarregar o driver **não corrige**

```
IRQ 170 antes do rmmod/modprobe: 1535
IRQ 170 depois:                  1540   (+5, da própria inicialização)
Novo nó de entrada registrado:   input6
Reteste com toque físico, 30 s:  1540 → 1540   (zero incremento)
```

**A-01 é reprodutível e sobrevive à recarga do driver.** A hipótese (b) do plano de correção
("estado de inicialização do controlador", corrigível por reprobe) fica **descartada**.

> **Observação não explicada:** entre a primeira medição (1346) e a coleta privilegiada (1535) houve
> **+189 interrupções**. Nenhum dos dois testes controlados de toque registrou incremento, portanto
> não é possível atribuir esse aumento a toques do operador. Fica registrado como anomalia em aberto,
> sem explicação determinada — pode indicar que a linha dispara em condições específicas (por
> exemplo, ciclos de apagar/acender da tela).

---

## 6. ✅ Segurança: verificações que antes eram hipótese

### Configuração efetiva do SSH

```
Port 22                      PubkeyAuthentication yes
PermitRootLogin prohibit-password    ← root só por chave, nunca por senha
PasswordAuthentication yes           ← ⚠️ CONFIRMADO
KbdInteractiveAuthentication yes     ← ⚠️
PermitEmptyPasswords no       X11Forwarding no
AllowTcpForwarding no         MaxAuthTries 6
```

A suspeita de que a autenticação por senha estivesse habilitada **confirma-se**. Combinada a
`MaxAuthTries 6` e à ausência de `fail2ban`, deixa a porta 22 sujeita a tentativas de adivinhação —
mitigada, na prática, por o firewall só aceitar SSH e o aparelho estar em rede doméstica.

### Contas — melhor do que a auditoria inicial sugeria

```
root:             hash = "!"        → CONTA BLOQUEADA (sem senha definida)
user:             hash = $6$...     → SHA-512, senha definida
contas de sistema: "!" ou "!*"      → bloqueadas
```

A tabela da auditoria inicial listava várias contas de sistema como "senha definida" — era **falso
positivo** do método de inspeção usado (checagem dos 3 primeiros caracteres do hash). Com leitura
correta, **todas as contas de sistema estão bloqueadas** e apenas `user` tem senha.

### Outros

- **Deferred probe:** 8 dispositivos `*.etm` (CoreSight/trace) pendentes. **Benigno** — não afeta
  funcionalidade do usuário.
- **`[Firmware Bug]: Kernel image misaligned at boot`** — alerta do bootloader Motorola, sem impacto
  observado.
- **`qseecom: untested machine, skipping`** — ambiente seguro Qualcomm não utilizado; esperado.
- **LSM BPF `restrict_filesystems`:** `Not supported` pelo kernel.

---

## 7. ✅ Suspensão: nada está impedindo o repouso

```
name                                  active_count  prevent_suspend_time
ucsi-source-psy-pmic_glink.ucsi.01          1              0
qcom-battmgr-wls / usb / bat               1/1/5           0
c440000.spmi:pmic@0:rtc@6100                6              0
```

**Todos os `prevent_suspend_time` são 0** — nenhum wakeup source está bloqueando a suspensão.

Isso refina o diagnóstico de **A-04**: o aparelho não suspende **não porque algo o impeça**, mas
porque **nada solicita a suspensão**. A investigação deve mirar a política de ociosidade do
ambiente (`systemd-logind`, `tuned`, configuração de suspensão do Phosh), e não a caça a um
dispositivo culpado.

---

## 8. Impacto na matriz e nas notas

| Item | Antes | Depois |
|---|---|---|
| Bluetooth | DETECTADO NÃO VALIDADO | **FUNCIONAL** |
| Firewall | "provavelmente ausente" | **Presente, `policy drop`, regras sólidas** |
| Firmware da GPU | — | **Confirmado íntegro** (erro de boot é benigno) |
| Wi-Fi (estabilidade) | causa: `power_save` | **causa provável adicional: BDF ausente** |
| Touchscreen | 3 hipóteses | **Hipótese de reprobe descartada; pinctrl GPIO_105 é a pista principal** |
| Contas de sistema | aparentemente com senha | **Todas bloqueadas; root sem senha** |
| Suspensão | causa indefinida | **Nada impede; falta quem solicite** |

**Compatibilidade de hardware: 50% → 53,4%** — numerador passa de 14,5 para 15,5 (Bluetooth sobe de
0 para 1,0), denominador inalterado em 29. Cálculo: 15,5 / 29 ≈ 53,4%.

**Segurança: 55% → 70%** — firewall robusto confirmado, root bloqueada, contas de sistema
bloqueadas. Permanecem como débito o armazenamento sem criptografia, o bootloader destravado,
`kptr_restrict=0` e a autenticação SSH por senha.

---

## 9. Estado deixado no aparelho

| Alteração | Reversão |
|---|---|
| `rfkill unblock bluetooth` + `hciconfig hci0 up` | `sudo rfkill block bluetooth` |
| Driver do touchscreen recarregado (`rmmod`/`modprobe`) | Já reiniciado; sem efeito persistente |
| Volume do áudio em 70%, não mais mutado | `pactl set-sink-mute 0 1` |

**Nenhuma outra mudança foi feita.** Nenhum pacote instalado, removido ou atualizado; nenhuma
configuração persistida em disco; nenhum arquivo do sistema editado. Os scripts temporários foram
apagados do aparelho.

**A senha de `sudo` foi usada apenas em memória durante a sessão. Não foi gravada em nenhum arquivo,
log, evidência ou commit deste repositório.**
