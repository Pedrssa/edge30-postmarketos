```
 ┌─ AUDIT ─────────────────────────────────────────────────┐
 │  auditoria técnica executada no aparelho real            │
 │  motorola-dubai · 24 nov 2026 · ssh · somente leitura    │
 └──────────────────────────────────────────────────────────┘
```

# Auditoria técnica — Motorola Edge 30 (`dubai`)

Esta pasta contém uma auditoria **executada no aparelho físico**, por SSH sobre Wi-Fi, em
24 de novembro de 2026. Não é uma revisão documental: cada classificação abaixo está amarrada a uma
saída de comando reproduzível, arquivada em [`evidence/sanitized/`](evidence/sanitized/).

> **Veredito: NÍVEL 3 — Estação Linux portátil.**
> Aparelho operável localmente: toque, GPU acelerada, Wi-Fi 6, Bluetooth, áudio, microfone e
> bateria. O que impede o Nível 4 é parte ausência de validação (sem SIM, sem libcamera, sensores
> bloqueados por polkit) e parte um defeito real: **a suspensão não funciona.**
>
> ⚠️ **Correção registrada:** a primeira versão desta auditoria classificou o touchscreen como
> NÃO FUNCIONAL. **Era falso positivo** — erro de método, não defeito do aparelho. Ver
> [`fixes-applied.md` §A-01](fixes-applied.md).

---

## O que esta auditoria mudou no projeto

| Antes | Depois |
|---|---|
| E23: matriz de hardware `AUSENTE` | **34 subsistemas classificados com evidência** |
| P-02: kernel `7.2.9 [RELATADO]` | **Confirmado por leitura direta** |
| P-04: wiki bloqueada por Anubis | **Matriz oficial obtida e comparada** |
| "Sistema é postmarketOS com OpenRC" | **É Nura edge, com systemd** |
| "GPU não testada" | **Aceleração por hardware comprovada** |
| "Áudio não testado" | **Alto-falante e microfone validados** |
| E11: bootloader destravado `RECONSTRUÍDO` | **`CONFIRMADO` pelo cmdline do kernel** |

---

## Conteúdo

| Arquivo | O que traz |
|---|---|
| [`executive-summary.md`](executive-summary.md) | Veredito, metodologia de pontuação, falhas priorizadas, limites |
| [`hardware-compatibility.csv`](hardware-compatibility.csv) | Matriz dos 34 subsistemas: classificação, evidência, método, comparação com a wiki |
| [`kernel-analysis.md`](kernel-analysis.md) | Kernel, remoteprocs, módulos, erros reais do boot, o caso do touchscreen |
| [`graphics-analysis.md`](graphics-analysis.md) | Prova de aceleração por hardware sem acesso à sessão Wayland |
| [`security-audit.md`](security-audit.md) | Proteções de kernel, superfície de rede, dados em repouso, bootloader |
| [`performance-report.md`](performance-report.md) | CPU, memória, armazenamento, rede, comportamento sob carga |
| [`battery-analysis.md`](battery-analysis.md) | 20 amostras de consumo e por que **nenhuma autonomia é estimada** |
| [`upstream-comparison.md`](upstream-comparison.md) | Matriz oficial × auditoria, divergências, oportunidades de contribuição |
| [`remediation-plan.md`](remediation-plan.md) | 7 problemas com causa, risco, rollback e critério de aceite |
| [`fixes-applied.md`](fixes-applied.md) | **O que foi efetivamente corrigido, com resultados e efeitos colaterais** |
| [`fixes-applied.md`](fixes-applied.md) | **O que foi efetivamente corrigido no aparelho, com resultados** |
| [`root-findings.md`](root-findings.md) | **Coleta privilegiada: 3 correções de conclusões anteriores + novos achados** |
| [`manual-validation-checklist.md`](manual-validation-checklist.md) | O que só pode ser testado com o aparelho em mãos |
| [`system-inventory.json`](system-inventory.json) | Inventário completo, legível por máquina |
| [`test-results.json`](test-results.json) | 30 testes com método, resultado e evidência |
| [`dashboard.html`](dashboard.html) | Painel offline com gráficos e a matriz visual |
| [`scripts/collect-diagnostics.sh`](scripts/collect-diagnostics.sh) | Coletor reutilizável, testado no aparelho |
| [`evidence/sanitized/`](evidence/sanitized/) | Saídas brutas, sanitizadas |

---

## Resumo dos 34 subsistemas

```
FUNCIONAL                 ██████████████ 14  CPU · GPU · Display · TOUCHSCREEN · Wi-Fi · Bluetooth
                                             Áudio · Mic · Bateria · Botões · UFS · RAM · Térmico · RPROCs
DETECTADO NÃO VALIDADO    █████          5   Câmera · Flash · Accel · Luz · Prox
NÃO SUPORTADO             █████          5   Câm. frontal · OV50A · NFC · Vibração · Biometria
PARCIALMENTE FUNCIONAL    ████           4   Estab. Wi-Fi · Volume · Codec headset · USB-C
NÃO TESTADO               ████           4   Telefonia · Dados · GPS · Carregamento
DETECTADO E BLOQUEADO     █              1   Modem (sem SIM — não é defeito)
NÃO FUNCIONAL             █              1   ◄── SUSPENSÃO (deep aborta, s2idle trava)
```

**Compatibilidade de hardware: 55%** — metodologia, pesos e denominador explícitos em
[`executive-summary.md` §4](executive-summary.md). Testes não realizados **não** são contados como
aprovados.

---

## Problemas encontrados

| ID | Gravidade | Problema |
|---|---|---|
| ~~A-01~~ | ✅ **FALSO POSITIVO** | O touchscreen funciona; erro de método na medição |
| ~~A-02~~ | ✅ **RESOLVIDO** | PipeWire desabilitado; PulseAudio validado |
| A-03 | 🟠 ALTO | Armazenamento sem criptografia com bootloader destravado |
| A-04 | 🟠 **ALTO** | Suspensão falha: `deep` aborta, `s2idle` trava o aparelho |
| ~~A-05~~ | ✅ **RESOLVIDO** | Bluetooth desbloqueado; controlador `UP RUNNING` |
| A-06 | 🟡 MÉDIO | `power_save` off: latência 70→15 ms, mas perda ainda 17% |
| ~~A-07~~ | ✅ **RESOLVIDO** | kptr_restrict=2, LLMNR off, senha SSH desabilitada |

> **Correções aplicadas em 24/11/2026**, com autorização explícita do operador. O que foi
> efetivamente executado, com resultados e efeitos colaterais — incluindo **um reboot que meu teste
> de suspensão causou** — está em [`fixes-applied.md`](fixes-applied.md).

---

## Como reexecutar

```sh
# no computador — copiar o coletor para o aparelho
scp audit/scripts/collect-diagnostics.sh user@<ip-do-aparelho>:/tmp/

# no aparelho — coletar com redação de dados sensíveis
ssh user@<ip-do-aparelho>
sh /tmp/collect-diagnostics.sh /tmp/diag --sanitize

# de volta no computador — recuperar
scp -r user@<ip-do-aparelho>:/tmp/diag ./nova-coleta/
```

O script foi **testado neste aparelho**: roda como usuário comum, não altera estado, e registra em
`manifest.txt` o código de saída de cada seção — inclusive as que falham por falta de privilégio
(`dmesg`) ou de ferramenta (`eglinfo`, `vulkaninfo`).

---

## Metodologia e limites

**Como o aparelho foi identificado:** a chave pública ed25519 do host foi comparada com a entrada
previamente registrada em `known_hosts` e mostrou-se idêntica, confirmando o mesmo aparelho sob IP
novo (DHCP). A verificação de host do SSH **foi mantida ativa durante toda a auditoria**.

**Natureza:** somente leitura. As únicas alterações de estado foram o ajuste de volume do sink de
áudio (de 0% mutado para 70%) e tentativas de reivindicação de sensores via D-Bus (negadas por
polkit) — ambas reversíveis e autorizadas.

**Duas etapas:** a auditoria foi feita primeiro **sem privilégio**, e depois complementada com uma
**coleta privilegiada** quando o operador forneceu a senha de `sudo`. Essa segunda etapa **corrigiu
três conclusões** da primeira — todas registradas em [`root-findings.md`](root-findings.md) em vez
de reescritas silenciosamente.

**Limites declarados:**
- **Sem SIM inserido** — telefonia, dados móveis e GPS não são verificáveis.
- **Sem libcamera** — nenhuma captura de imagem foi possível.
- **Sessão Wayland inacessível por SSH** — `eglinfo`/`vulkaninfo` não executáveis; a aceleração foi
  provada por via indireta.
- **Bateria amostrada por 7 min 41 s em repouso** — insuficiente para estimar autonomia, e nenhuma
  estimativa é feita.
- **Sem teste de estresse prolongado** — o comportamento térmico sob carga sustentada permanece
  desconhecido.

**Sanitização:** nenhuma evidência publicada contém IMEI, número de série, endereço MAC, IP privado,
SSID, chave SSH ou senha. A redação foi verificada programaticamente após a geração.
