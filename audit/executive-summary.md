# Sumário executivo — Auditoria do Motorola Edge 30 (`dubai`)

**Data da auditoria:** 24 de novembro de 2026, 21:43–22:20 (horário do aparelho, GMT)
**Auditor:** sessão assistida por LLM (Claude Opus 5 / Claude Code) conduzida por Pedro H. M. M. P. Barreiros
**Alvo:** Motorola Edge 30 `XT2203-1` · `motorola-dubai` · SM7325 (Snapdragon 778G+) · ARM64
**Acesso:** SSH sobre Wi-Fi, usuário não privilegiado `user`, chave ed25519
**Natureza:** somente leitura, com duas exceções reversíveis explicitamente autorizadas (volume de áudio e reivindicação de sensores)

---

## 1. Veredito

O aparelho **não é um protótipo de boot**. É um sistema Linux ARM64 em operação contínua, com
systemd, 1326 pacotes, **zero unidades de serviço em falha**, os quatro co-processadores Qualcomm
(modem, ADSP, WPSS, CDSP) em `running` e **aceleração gráfica por hardware comprovadamente ativa**.

Com o touchscreen confirmado como funcional, o aparelho é **operável localmente como um computador
Linux de bolso**: interface Phosh acelerada por GPU, toque, Wi-Fi 6, Bluetooth, áudio, microfone e
bateria com gestão completa.

> **Nível de maturidade atribuído: NÍVEL 3 — Estação Linux portátil.**
> O que impede o Nível 4 (plataforma móvel funcional) não é defeito, mas ausência de validação:
> telefonia, dados móveis e GPS não foram testados por falta de SIM; os sensores não puderam ser
> reivindicados por SSH; a câmera não tem libcamera instalada; e a suspensão nunca foi exercida.

> ⚠️ **CORREÇÃO IMPORTANTE (A-01).** A primeira versão desta auditoria classificou o touchscreen
> como **NÃO FUNCIONAL**. **Isso estava errado.** O teste definitivo — leitura direta de
> `/dev/input/event3` com janela de 45 s — capturou **6942 eventos multitouch** e um delta de
> **+2224 interrupções**. A causa do falso positivo foi **sincronização**: as janelas de medição de
> 15–30 s não coincidiam com o momento em que o operador tocava a tela, e a ausência de estímulo foi
> lida como falha de hardware. Relato completo em [`root-findings.md` §10](root-findings.md).
>
> **Outras revisões da coleta privilegiada:** o Bluetooth passou a funcionar após `rfkill unblock`;
> confirmou-se um firewall robusto (a auditoria havia inferido o contrário); e o aparente firmware
> faltante da GPU revelou-se ruído de boot.

---

## 2. Correção de premissas do projeto

A auditoria contradisse três afirmações que constavam da documentação do repositório:

| Afirmação anterior | Constatação |
|---|---|
| "Sistema é postmarketOS" | O sistema é **Nura edge** (`ID=nura`, `ID_LIKE=alpine`), um derivado que consome `mirror.nura.eco` além dos repositórios Alpine. O postmarketOS é a base, não a distribuição instalada. |
| "Init é OpenRC" (implícito no uso de `rc-status`) | O init é **systemd** (`/sbin/init -> ../lib/systemd/systemd`). Nenhum comando OpenRC se aplica. |
| Kernel "7.2.9 [RELATADO]" | **Confirmado por leitura direta:** `7.2.9 #3-postmarketos-qcom-sc7280`, compilado com Clang 23.1.3 em 17/10/2026. Resolve a pendência **P-02**. |

Também foi resolvida a pendência **P-04** (matriz oficial da wiki, antes bloqueada por Anubis) e, em
grande parte, a **P-01** (matriz de funcionalidades no próprio aparelho), que constava como
evidência `AUSENTE` (E23).

---

## 3. Matriz consolidada — 34 subsistemas

| Classificação | Qtd. | Subsistemas |
|---|---|---|
| **FUNCIONAL** | 14 | CPU, GPU Adreno 642L, Display, **Touchscreen**, Wi-Fi, **Bluetooth**, Áudio (saída), Microfone, Bateria, Botões físicos, UFS, Memória/ZRAM, Térmico, Remote processors |
| **PARCIALMENTE FUNCIONAL** | 4 | Estabilidade do Wi-Fi, Configuração de volume, Codec de headset (WCD9375), USB-C |
| **DETECTADO, NÃO VALIDADO** | 5 | Câmera traseira, Flash, Acelerômetro, Luz ambiente, Proximidade |
| **DETECTADO E BLOQUEADO** | 1 | Modem (bloqueado por ausência de SIM, não por defeito) |
| **NÃO TESTADO** | 4 | Telefonia, Dados móveis, GPS, Carregamento |
| **NÃO SUPORTADO** | 5 | Câmera frontal, Câmera principal OV50A, NFC, Vibração, Biometria |
| **NÃO FUNCIONAL** | 1 | **Suspensão** — testada após as correções: `deep` aborta e `s2idle` trava o aparelho |

---

## 4. Metodologia da pontuação

Critério explícito, conforme exigido: **nenhum teste não realizado é contabilizado como aprovado.**

- Pesos por subsistema: `FUNCIONAL = 1,0` · `PARCIALMENTE FUNCIONAL = 0,5` · `DETECTADO E BLOQUEADO = 0,5`
  (o modem comprovou inicialização completa do firmware e da pilha QMI) · `DETECTADO NÃO VALIDADO = 0`
  · `NÃO SUPORTADO = 0` · `NÃO FUNCIONAL = 0`.
- **Denominador:** 34 subsistemas − 4 `NÃO TESTADO` = **30 subsistemas avaliáveis**. Os itens não
  testados são excluídos do cálculo em vez de reprovados, para não penalizar o que não foi medido.
- **Numerador:** (14 × 1,0) + (4 × 0,5) + (1 × 0,5) = **16,5**.

**Compatibilidade de hardware = 16,5 / 30 = 55%.**

Esse número é deliberadamente conservador: os 6 subsistemas "detectados, não validados" pontuam
zero, embora haja forte indício de que ao menos Bluetooth e sensores funcionem (a wiki oficial os
declara `Works`, e as falhas observadas foram de *permissão* — `rfkill` e polkit — não de hardware).
Com acesso root, a pontuação realista subiria de forma significativa.

### Avaliação por dimensão

| Dimensão | Nota | Justificativa baseada em evidência |
|---|---|---|
| Compatibilidade de hardware | **55%** | Cálculo acima. Penalizada sobretudo pelos 5 itens sem driver e pelos 5 sem validação. |
| Estabilidade | **65%** | Zero unidades falhas, uptime contínuo sem reboot, nenhum panic/oops. Descontado por uma queda de sessão SSH e 33% de perda de pacotes na segunda medição. |
| Desempenho | **85%** | 97–98% de CPU ociosa em repouso, 499 MB/s de escrita, GPU escalando até 608 MHz, 637 MB de 7,3 GB em uso. Unixbench oficial do device: 9626,6. |
| Segurança | **78%** | ASLR completo, `dmesg_restrict`, BPF não privilegiado desabilitado, repositórios assinados e — confirmado com root — **firewall `nft` com `policy drop`**, conta root bloqueada e contas de sistema sem senha. Descontado por bootloader destravado, ausência de criptografia de disco, `kptr_restrict=0` e autenticação SSH por senha habilitada. |
| Eficiência energética | **35%** | ~0,89 W em repouso (−225 mA a 3,958 V). Suspensão **nunca exercida** (`success=0`), e a wiki atribui mais da metade do consumo ocioso aos motores de foco da câmera sempre ligados. |
| Manutenibilidade | **80%** | `apk` operante, 1326 pacotes, repositórios assinados, pacotes de device versionados (`device-motorola-dubai-2-r0`). |
| Reprodutibilidade | **60%** | Guia de reprodução existe, mas o procedimento documentado no repositório diverge do oficial (ver §5) e não há log de flash capturado (pendência P-03). |
| Experiência de uso | **70%** | Phosh com GPU acelerada, **toque funcional**, áudio e Bluetooth operantes. Descontado por ausência de háptica, teclado virtual instável no boot e falta de telefonia validada. |

---

## 5. Divergências entre o sistema instalado e o suporte oficial

A wiki oficial declara `Works` para touchscreen, Bluetooth, sensores, telefonia e GPS. Após os
retestes, **touchscreen e Bluetooth foram confirmados como funcionais**, em acordo com a wiki. Os
demais permanecem sem validação por falta de SIM e por restrição de polkit — não por defeito
observado. **Não há mais divergência de suporte entre esta instalação e o upstream.**

Diferença relevante de procedimento: o método oficial recomendado usa **U-Boot** com instalação via
*USB mass storage* e, no `pmbootstrap init`, exige escolher **`pipewire`** como provider para ter
chamadas funcionais. O aparelho auditado usa **PulseAudio** (`postmarketos-base-ui-audio-backend-pulseaudio`
e `soc-qcom-pulseaudio` instalados) **com PipeWire e WirePlumber rodando simultaneamente** — uma
configuração conflitante que o próprio log registra (`pipewire-pulse.socket: refusing`).

---

## 6. Falhas priorizadas

| ID | Subsistema | Gravidade | Resumo |
|---|---|---|---|
| ~~A-01~~ | Touchscreen | ✅ **FALSO POSITIVO** | Reteste definitivo capturou 6942 eventos. O dispositivo **funciona**; o erro foi de método. |
| ~~A-02~~ | Áudio | ✅ **RESOLVIDO** | PipeWire desabilitado; PulseAudio mantido e áudio validado. |
| **A-03** | Segurança | **ALTO** | Armazenamento sem criptografia com bootloader destravado: acesso físico expõe todos os dados. |
| **A-04** | Energia | **ALTO** ⬆️ | **Suspensão falha**: `deep` aborta com `Wakeup pending`; `s2idle` **trava o aparelho e força reboot**. Gravidade elevada após o teste. |
| ~~A-05~~ | Bluetooth | ✅ **RESOLVIDO** | Desbloqueado e persistente após reboot. |
| **A-06** | Rede | **MÉDIO** | `power_save` desligado: latência 70→15 ms, mas **perda ainda em 17%** e consumo +26%. Critério de aceite não atingido. |
| ~~A-07~~ | Segurança | ✅ **RESOLVIDO** | `kptr_restrict=2`, LLMNR desativado, senha SSH desabilitada. Persistente. |

O plano de correção está em [`remediation-plan.md`](remediation-plan.md); **o que foi efetivamente
executado no aparelho**, com resultados e efeitos colaterais, está em
[`fixes-applied.md`](fixes-applied.md).

---

## 7. Limites desta auditoria

Declarados de forma explícita para que nada seja lido como mais conclusivo do que é:

- **Sem acesso root.** `sudo` exigiu autenticação interativa, o que impediu `dmesg` completo
  (`dmesg_restrict=1`), leitura de `wakeup_sources`, inspeção de regras `nft`, `sshd -T` efetivo,
  remoção do bloqueio `rfkill` e teste de suspensão.
- **Sem SIM inserido**, o que torna telefonia, dados móveis e GPS não verificáveis.
- **Sem libcamera instalada**, impedindo qualquer captura de imagem real.
- **Sessão gráfica inacessível por SSH**, o que impediu `eglinfo`/`vulkaninfo`. A aceleração foi
  comprovada por via indireta (descritores de `renderD128` + escalonamento de devfreq), método
  sólido mas que não substitui a consulta direta ao driver.
- A medição de bateria cobriu **8 minutos em repouso**. Isso **não permite estimar autonomia**, e
  nenhuma projeção de duração é feita neste relatório.
