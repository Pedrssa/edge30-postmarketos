# Análise de bateria e energia

**Janela de observação:** 24/11/2026, 21:58:15 → 22:05:56 (**7 min 41 s**)
**Amostras:** 20 válidas, em intervalos de 20 s
**Condição:** repouso — sessão Phosh ativa, tela ligada (backlight em 31%), Wi-Fi associado, sem
carga de usuário, sem cabo conectado

---

## 1. Subsistema identificado

A bateria é gerenciada pelo **ADSP via `pmic-glink`** (`qcom,sm7325-pmic-glink`), não por um
driver de PMIC direto. Três fontes de energia são expostas:

| Fonte | Tipo | Estado |
|---|---|---|
| `qcom-battmgr-bat` | Battery | `Discharging` |
| `qcom-battmgr-usb` | USB | `ONLINE=0` (sem cabo) |
| `qcom-battmgr-wls` | Wireless | `ONLINE=0` |
| `ucsi-source-psy-pmic_glink.ucsi.01` | USB-C / UCSI | `Not charging`, suporta `PD` e `PD_PPS` |

A wiki oficial registra: *"ADSP battmgr, it just works, profile/calibration already loaded"* — o que
a auditoria confirma: o perfil está carregado e os valores são coerentes.

---

## 2. Estado da bateria

| Parâmetro | Valor |
|---|---|
| Capacidade | **58% → 57%** durante a janela |
| Tensão atual | 3,950 V → 3,952 V |
| Tensão de circuito aberto (OCV) | 4,237 V |
| Tensão máxima de projeto | 4,480 V |
| Tecnologia | Li-ion |
| Saúde reportada | `Good` |
| **State of health** | **100** |
| Resistência interna | 148 mΩ |
| Contador de carga | 2 328 868 µAh |
| Ciclos | `0` — ⚠️ **não reportado pelo firmware**, não significa bateria nova |
| Temperatura | **33,0 °C**, constante nas 20 amostras |

O **SOH de 100 e a resistência interna de 148 mΩ** indicam uma célula em bom estado. A capacidade
de projeto do Edge 30 é de 4 020 mAh; o `CHARGE_COUNTER` de 2 329 mAh a 58% é consistente com isso
(≈ 4 015 mAh projetados a 100%), o que sugere **degradação mínima**.

---

## 3. Consumo medido

| Estatística | Corrente |
|---|---|
| Mínima | −200 mA |
| **Média** | **≈ −225 mA** |
| Mediana | −220 mA |
| Máxima | −311 mA (primeira amostra, transitória) |

**Potência média em repouso: 0,225 A × 3,958 V ≈ 0,89 W.**

A estabilidade é notável: descontada a primeira amostra (ainda sob efeito da coleta anterior), a
corrente permaneceu entre −200 mA e −255 mA ao longo de todo o período, com `load average` entre
0,01 e 0,26. A proximidade entre média (225 mA) e mediana (220 mA) confirma que não houve
outliers relevantes.

---

## 4. O que estes dados **não** permitem concluir

Esta seção existe por rigor metodológico.

> **Nenhuma estimativa de autonomia é feita neste relatório.**

Dividir 4 020 mAh por 225 mA produziria "≈ 18 horas", mas esse número seria **enganoso**, porque:

1. A janela de 7 min 41 s cobre **um único estado** (repouso com tela ligada). Uso real alterna
   entre tela apagada, carga de CPU, rádio ativo e suspensão.
2. A **suspensão nunca foi exercida** (§5), então o estado de menor consumo do aparelho jamais foi
   medido.
3. A descarga de 58% para 57% em 8 minutos reflete o cruzamento de um limiar de arredondamento do
   medidor, **não** uma taxa de descarga de 1%/8min.
4. O campo `TIME_TO_EMPTY_AVG` reportava 50 564 s (≈ 14 h), mas trata-se de **estimativa do próprio
   firmware**, não de medição independente — e é citada aqui apenas como dado bruto.

Uma estimativa de autonomia confiável exigiria pelo menos um ciclo de descarga completo, com perfil
de uso representativo.

---

## 5. Suspensão — o achado central

| Item | Valor |
|---|---|
| Estados disponíveis (`/sys/power/state`) | `freeze mem` |
| Modos de `mem_sleep` | `s2idle` **[deep]** (deep é o padrão selecionado) |
| **Suspensões bem-sucedidas** | **0** |
| **Suspensões falhas** | **0** |

`success = 0` **e** `fail = 0` significam que o aparelho **nunca tentou suspender** desde o boot.
Isso é a explicação mais direta para o consumo ocioso: sem deep idle, o SoC permanece acordado
integralmente.

O teste de suspensão **não foi executado**, conforme a instrução explícita de não suspender
automaticamente o aparelho quando isso pode interromper o único canal de acesso SSH. O procedimento
seguro proposto (com `rtcwake` e o aparelho em mãos) está em
[`remediation-plan.md` § A-04](remediation-plan.md).

**Wakeup sources:** `/sys/kernel/debug/wakeup_sources` é inacessível sem root, portanto **não foi
possível identificar quais processos ou dispositivos impediriam o repouso**.

---

## 6. Causa provável do consumo elevado

A wiki oficial do device é explícita quanto a isto:

> "Mais da metade do consumo ocioso é causado pelos motores de foco da câmera permanentemente
> ligados. A solução foi integrada ao kernel near-to-mainline e estará disponível no próximo
> release."

Isso é **coerente com o que a auditoria observou de forma independente**: os módulos `ak7375` (VCM
de autofoco) e `wl2864c` (PMIC de câmera) estão carregados, e a zona `camera0-thermal` registrava
35,9 °C — acima de várias zonas do SoC em repouso, o que sugere componente energizado sem uso.

Se a atribuição da wiki estiver correta, o consumo de ~0,89 W cairia para a ordem de 0,4 W apenas
com a atualização do kernel — sem nenhuma alteração de configuração local.

---

## 7. Governadores e economia de energia

| Mecanismo | Estado |
|---|---|
| Governor de CPU | `schedutil` nas três policies ✅ |
| Frequências mínimas | 300 MHz (A55) / 691 MHz (A78) / 806 MHz (prime) |
| Governor de GPU | `simple_ondemand`, ociosa em 315 MHz ✅ |
| `tuned` / `tuned-ppd` | Ativos — gerenciamento dinâmico de perfil de energia presente |
| ZRAM | 10,8 GB configurados, 0 em uso |
| Wi-Fi `power_save` | `on` — economiza energia, mas degrada a rede (ver A-06) |
| **Suspensão** | ❌ **Nunca exercida** |

Há uma **tensão real entre dois achados**: desligar o `power_save` do Wi-Fi (A-06) resolveria a
instabilidade do SSH, mas aumentaria o consumo já elevado (A-04). A recomendação é desligá-lo
apenas enquanto o touchscreen estiver inoperante e o SSH for o único meio de operação.

---

## 8. Síntese

| Aspecto | Avaliação |
|---|---|
| Driver de bateria | ✅ **Funcional e completo** — tensão, corrente, temperatura, SOH, perfil calibrado |
| Saúde da célula | ✅ Excelente — SOH 100, 148 mΩ, degradação mínima |
| Estabilidade térmica | ✅ 33,0 °C constante, sem variação |
| Medição de consumo | ✅ Obtida — 0,89 W em repouso, estável |
| Eficiência energética | ⚠️ **Deficiente** — sem suspensão, com causa raiz provável já corrigida upstream |
| Carregamento | ❓ **Não testado** — cabo não conectado durante a auditoria |
| Autonomia | ❓ **Não estimável** com os dados disponíveis |
