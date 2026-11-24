# Relatório de desempenho

**Protocolo:** benchmarks curtos e controlados, compatíveis com dispositivo móvel. Nenhum teste de
estresse prolongado, nenhum benchmark destrutivo de armazenamento, nenhuma carga capaz de provocar
superaquecimento. O limite de interrupção foi definido em **45 °C** em qualquer zona térmica; esse
limite **nunca foi aproximado** (máximo observado: 37,2 °C).

---

## 1. Linha de base em repouso

| Métrica | Valor |
|---|---|
| Load average (1/5/15 min) | 0,15 / 0,16 / 0,18 |
| CPU ociosa | **97–98%** (`vmstat`) |
| Memória total | 7 368 MB |
| Memória em uso | **637 MB (8,6%)** |
| Buff/cache | 940 MB |
| Memória disponível | 6 136 MB |
| Swap (ZRAM) | 11 052 MB totais, **0 MB em uso** |
| Processos / threads | 575 |
| Temperatura máxima | 37,2 °C (`cpu4-thermal`) |

Um sistema com shell gráfico completo consumindo 8,6% da RAM e mantendo 97% de CPU ociosa está
**bem dimensionado** para o hardware.

---

## 2. CPU

Topologia confirmada (SM7325, 8 núcleos em 3 clusters):

| Policy | Núcleos | CPU part | Microarquitetura | Faixa | Governor |
|---|---|---|---|---|---|
| `policy0` | 0–3 | `0xd05` | Cortex-A55 (eficiência) | 300 MHz – **1,80 GHz** | `schedutil` |
| `policy4` | 4–6 | `0xd41` | Cortex-A78 (desempenho) | 691 MHz – **2,40 GHz** | `schedutil` |
| `policy7` | 7 | `0xd41` | Cortex-A78 (prime) | 806 MHz – **2,52 GHz** | `schedutil` |

`schedutil` é o governor correto para este perfil: integrado ao escalonador, responde à demanda sem
a latência dos governors legados. **Escalonamento confirmado em operação** — no momento da leitura,
`policy4` estava em 1,65 GHz e `policy0` em 1,32 GHz, ambos acima do mínimo, o que demonstra
resposta ativa à carga.

Referência externa: a wiki oficial do device registra **Unixbench 9626,6** para este aparelho.
Esse valor **não foi reproduzido** nesta auditoria (exigiria carga prolongada) e é citado apenas
como referência de terceiros.

---

## 3. Processos de maior consumo

Nenhum processo anômalo. Os dez maiores por RSS somam menos de 90 MB:

| PID | Usuário | RSS | Processo |
|---|---|---|---|
| 3739 | user | 9 352 KB | `gsd-color` |
| 3690 | user | 9 128 KB | `gvfs-udisks2-volume-monitor` |
| 3353 | user | 9 100 KB | `gnome-session-initialized` |
| 987 | polkitd | 8 984 KB | `polkitd` |
| 3770 | user | 8 584 KB | `gsd-sharing` |
| 3749 | user | 8 396 KB | `gsd-housekeeping` |
| 3421 | user | 8 372 KB | `feedbackd` |
| 3785 | user | 8 188 KB | `gsd-usb-protection` |
| 1019 | root | 8 072 KB | `wpa_supplicant` |
| 3254 | user | 7 796 KB | `gnome-keyring-daemon` |

Observação: há uma quantidade considerável de daemons `gsd-*` (GNOME Settings Daemon) para um
dispositivo móvel. Não representam problema de desempenho no estado atual, mas contribuem para o
consumo ocioso discutido em [`battery-analysis.md`](battery-analysis.md).

---

## 4. Armazenamento

**Hardware:** Micron UFS 3.1 (`MT128GAXAT2U3165`), controlador `1d84000.ufshc`.

| Teste | Resultado | Observação |
|---|---|---|
| Escrita sequencial no `/` com `fsync` | **499,4 MB/s** | 128 MiB, `dd ... conv=fsync` — medida confiável |
| Escrita sequencial em `/tmp` (tmpfs) | 1,7 GB/s | ⚠️ **Não é disco** — `/tmp` é tmpfs em RAM |
| Leitura de `/tmp` | 4,2 GB/s | ⚠️ **Não é disco** — leitura de RAM/cache |

> **Ressalva metodológica importante:** apenas o primeiro número mede armazenamento real. Os outros
> dois refletem desempenho de memória e **não devem ser citados como desempenho de UFS**. Nenhum
> teste de leitura direta do UFS com cache invalidado foi executado, porque isso exigiria
> `drop_caches` (root) ou leitura de dispositivo bruto (risco desnecessário).

499 MB/s de escrita com `fsync` é um resultado consistente com UFS 3.1 através de uma camada
`loop` + `ext4`, e indica que **a pilha de armazenamento não é gargalo**.

**Ocupação:** rootfs de 227 GB com 5,9 GB usados (**3%**); `/boot` com 133,5 MB de 478,8 MB (28%).

---

## 5. Memória e ZRAM

`zram0` provê **10,8 GB** de swap comprimido — configuração generosa sobre 7,3 GB de RAM física.
Com **0 bytes em uso**, o subsistema nunca foi exercido, o que confirma folga de memória
confortável no uso atual. `systemd-oomd` está ativo como rede de proteção.

---

## 6. Rede

| Métrica | 1ª medição (22:05) | 2ª medição (22:14) |
|---|---|---|
| Pacotes | 20 | 3 |
| Perda | **0%** | **33%** |
| Latência mínima | 4 ms | 101 ms |
| Latência média | 70 ms | 121 ms |
| Latência máxima | **125 ms** | 141 ms |

**Enlace Wi-Fi:** 5 GHz (canal 5180 MHz), Wi-Fi 6 (HE), RX 206,4 Mbit/s (40 MHz, HE-MCS 4, NSS 2),
TX 432,3 Mbit/s (160 MHz, HE-MCS 2, NSS 2), sinal −66 dBm.

A amplitude de 4 ms a 125 ms em uma rede local não se explica por congestionamento. A causa
identificada é `power_save = on` no rádio (ver [`remediation-plan.md` § A-06](remediation-plan.md)).

---

## 7. Estabilidade da conexão SSH

| Evento | Registro |
|---|---|
| Duração da auditoria | ~40 minutos de sessão quase contínua |
| Quedas | **1** — `Connection timed out` por volta das 22:13 |
| Recuperação | Imediata na tentativa seguinte |
| Reboot associado | **Nenhum** — `uptime` posterior de 31 min confirma continuidade |

A queda foi de **enlace**, não de sistema. Isso é um dado relevante de confiabilidade: o sistema
operacional permaneceu estável; o que falhou foi a camada de rádio sob economia de energia.

---

## 8. Comportamento sob carga moderada

A carga aplicada foi a do próprio uso: compositor Phosh ativo, reprodução de áudio, captura de
microfone, escrita de 128 MiB com `fsync` e a sessão SSH.

| Observação | Resultado |
|---|---|
| Temperaturas durante a carga | Sem variação perceptível — faixa mantida em 32,8–37,2 °C |
| GPU sob carga do compositor | Escalou a 608 MHz (máximo) por 4 876 ms acumulados |
| Comportamento anormal | **Nenhum** — nenhum teste precisou ser interrompido |
| Throttling térmico | Não observado |

**Não foi executado** nenhum teste de estresse multi-core prolongado, conforme a restrição de
protocolo. Portanto, **o comportamento térmico sob carga sustentada permanece desconhecido** e não
pode ser inferido destes resultados.

---

## 9. Síntese

| Dimensão | Avaliação |
|---|---|
| CPU | ✅ Excelente — topologia correta, governor adequado, 97% ociosa |
| Memória | ✅ Excelente — 8,6% de uso, ZRAM intocado |
| Armazenamento | ✅ Bom — 499 MB/s, não é gargalo |
| GPU | ✅ Acelerada e escalando (ver [`graphics-analysis.md`](graphics-analysis.md)) |
| Térmico | ✅ Saudável em repouso; **não caracterizado sob carga sustentada** |
| Rede | ⚠️ Degradada por `power_save` — jitter e perda intermitente |
| Fluidez da interface | ❓ **Não avaliável** — bloqueada pela falha do touchscreen |
