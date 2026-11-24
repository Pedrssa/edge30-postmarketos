# Linux em smartphones: distribuições móveis não-Android

### Estudo de caso — porte e auditoria do Motorola Edge 30 (`dubai`) com postmarketOS

**Organização de Computadores e Sistemas Operacionais — Avaliação 3 · Tema 10**
Turma matutina · 25 de novembro de 2026

| Integrante | Matrícula |
|---|---|
| Luis Eduardo Barbosa de Menezes Junior | 12723122413 |
| Murilo Ribeiro de Lima | 12723130019 |
| Pedro Henrique Martins Mattos Paranhos Barreiros | 1272319265 |
| Ricardo Henrique da Rocha Silva | 12723114666 |
| Brunno Otavyo de Jesus Aguiar | 12725192794 |

**Repositório:** <https://github.com/Pedrssa/edge30-postmarketos>

---

## Resumo

Este trabalho investiga o estado do Linux "convencional" em smartphones — distribuições que **não**
derivam do Android — comparando postmarketOS, Mobian e Ubuntu Touch quanto a maturidade, hardware
suportado, interface e telefonia. A contribuição central não é bibliográfica: instalamos
postmarketOS em um **Motorola Edge 30 real** (XT2203-1, Snapdragon 778G+) e, em 24/11/2026,
executamos uma **auditoria técnica no aparelho por SSH**, medindo 34 subsistemas com 33 testes
instrumentados. O resultado é uma matriz de compatibilidade sustentada por evidência de comando, com
metodologia de pontuação explícita. O aparelho foi classificado no **Nível 3 — Estação Linux
portátil** (55% de compatibilidade de hardware). Relatamos também dois erros cometidos durante a
auditoria e como foram corrigidos, por entendermos que isso integra o método.

**Palavras-chave:** sistemas operacionais móveis; Linux embarcado; kernel mainline; ARM64; Wayland;
postmarketOS.

---

## i. Introdução

### i.1 O problema

Um smartphone moderno é um computador completo: SoC multinúcleo, GPU, 8 GB de RAM, armazenamento
UFS. Ainda assim, o software que roda nele é fechado em um ciclo de vida curto — fabricantes
encerram atualizações em dois a quatro anos, e o aparelho vira lixo eletrônico com hardware
plenamente funcional.

O Android é Linux no kernel, mas seu espaço de usuário (Bionic, ART, HAL, SurfaceFlinger) é
incompatível com o de um Linux de desktop. A pergunta que motiva este trabalho é direta:

> **É possível rodar um Linux *convencional* — glibc/musl, Wayland, systemd, repositório de
> pacotes — em um smartphone? E o que se perde nesse caminho?**

### i.2 Por que isso interessa a Organização de Computadores e SO

O tema exercita, em hardware real, conceitos centrais da disciplina:

| Conceito da UC | Como aparece neste trabalho |
|---|---|
| Arquitetura de processadores | ARM64 big.LITTLE: 4× Cortex-A55 + 4× Cortex-A78 em 3 domínios de frequência |
| Gerência de processos | Escalonador EEVDF; governor `schedutil` ligado ao escalonador |
| Gerência de memória | 8 GB LPDDR5 + ZRAM (swap comprimido em RAM) |
| Sistemas de arquivos | `ext4` sobre *loop device* montado a partir de uma partição UFS |
| Entrada/saída e interrupções | Diagnóstico por contagem em `/proc/interrupts` e leitura de `/dev/input/event*` |
| Drivers e Device Tree | Descrição declarativa do hardware; `compatible = "motorola,dubai"` |
| Processos e init | `systemd` como PID 1, unidades, escopo de usuário × global |
| Multiprocessamento | Quatro co-processadores Qualcomm (modem, ADSP, WPSS, CDSP) coordenados por RPC |
| Segurança de SO | ASLR, `kptr_restrict`, LSM, firewall `nftables`, autenticação por chave |
| Gerência de energia | Estados de suspensão, `devfreq`, governadores, medição de consumo |

### i.3 Objetivos

1. Comparar **postmarketOS, Mobian e Ubuntu Touch** quanto a maturidade, hardware suportado,
   interface e telefonia.
2. Explicar a **arquitetura em camadas** de um Linux móvel: kernel → userspace → Wayland → shell
   móvel → telefonia.
3. **Demonstrar em hardware real**, instalando e auditando o sistema em um Motorola Edge 30.
4. Produzir uma **matriz de compatibilidade baseada em evidência**, e não em expectativa.

---

## ii. Projeto

### ii.1 Arquitetura em camadas de um Linux móvel

```
┌──────────────────────────────────────────────────────────────┐
│  APLICAÇÕES          GNOME Apps · Firefox · terminal         │
├──────────────────────────────────────────────────────────────┤
│  SHELL MÓVEL         Phosh 0.58  (interface adaptada a toque)│
│                      Phoc        (compositor Wayland/wlroots)│
├──────────────────────────────────────────────────────────────┤
│  EXIBIÇÃO            Wayland · Mesa 26.2.6 (Freedreno/Turnip)│
│                      DRM/KMS → /dev/dri/card0 · renderD128   │
├──────────────────────────────────────────────────────────────┤
│  TELEFONIA/REDE      ModemManager (QMI sobre QRTR)           │
│                      NetworkManager · wpa_supplicant         │
├──────────────────────────────────────────────────────────────┤
│  USERSPACE           Alpine Linux (musl) · apk · systemd     │
├──────────────────────────────────────────────────────────────┤
│  KERNEL              Linux 7.2.9 mainline (família sc7280)   │
│                      Device Tree: motorola,dubai + qcom,sm7325│
├──────────────────────────────────────────────────────────────┤
│  HARDWARE            Snapdragon 778G+ · Adreno 642L · WCN6750│
│  CO-PROCESSADORES    modem (MPSS) · ADSP · WPSS · CDSP       │
└──────────────────────────────────────────────────────────────┘
```

**Por que cada camada importa:**

- **Kernel mainline.** É a diferença essencial. O Android usa um kernel *downstream* com milhares de
  patches do fabricante, que deixa de receber atualizações quando o fabricante desiste. Um kernel
  mainline recebe correções enquanto o código estiver na árvore oficial — é o que dá vida longa ao
  aparelho.
- **Device Tree.** Em x86, o firmware ACPI enumera o hardware. Em ARM não há esse mecanismo: o
  hardware é descrito em um arquivo declarativo compilado (`.dtb`) que o kernel lê no boot. Portar um
  aparelho é, em grande medida, **escrever seu Device Tree**.
- **Wayland em vez de X11.** O X11 carrega decisões de projeto dos anos 1980 e não trata bem
  rotação, densidade variável e toque. O Wayland funde servidor e compositor — no nosso caso, o
  `phoc` fala direto com o DRM/KMS.
- **Shell móvel.** Um GNOME de desktop é inutilizável em 6,5". O Phosh reorganiza a interface para
  tela estreita, toque e teclado virtual.
- **Telefonia como serviço de userspace.** O modem é um computador separado, com firmware próprio,
  que conversa por **QMI sobre QRTR**. O `ModemManager` traduz isso para D-Bus.

### ii.2 O aparelho

| Item | Especificação |
|---|---|
| Modelo | Motorola Edge 30 · XT2203-1 · codinome `dubai` |
| SoC | Qualcomm Snapdragon 778G+ (SM7325-AE) |
| CPU | 4× Cortex-A55 @1,80 GHz · 3× Cortex-A78 @2,40 GHz · 1× Cortex-A78 @2,52 GHz |
| GPU | Adreno 642L |
| RAM / Armazenamento | 8 GB LPDDR5 · 128 GB UFS 3.1 (Micron) |
| Tela | AMOLED 1080×2400, 144 Hz, painel CSOT com controlador Novatek NT37701 |
| Toque | Goodix GT9916 (SPI) |
| Wi-Fi/BT | Qualcomm WCN6750 (Wi-Fi 6) |

### ii.3 Processo de instalação

```
  [PC Windows]              [VM Ubuntu]                [Edge 30]
       │                         │                          │
       │   VirtualBox            │                          │
       ├────────────────────────>│                          │
       │                    pmbootstrap init                │
       │                    (device: dubai                  │
       │                     kernel: csot                   │
       │                     UI: phosh                      │
       │                     init: systemd)                 │
       │                         │                          │
       │                    pmbootstrap build               │
       │                         │                          │
       │                 boot.img · dtbo.img                │
       │                 motorola-dubai.img                 │
       │<────────────────────────┤                          │
       │                                                    │
       │   fastboot oem unlock  (bootloader destravado)     │
       ├───────────────────────────────────────────────────>│
       │   fastboot flash boot / dtbo / rootfs              │
       ├───────────────────────────────────────────────────>│
       │                                                    │
       │   ssh user@<ip>  (sobre Wi-Fi)                     │
       │<──────────────────────────────────────────────────>│
```

O roteiro detalhado está em [`guia-de-reproducao.md`](guia-de-reproducao.md). Uma ressalva de
honestidade: o procedimento **oficial** da wiki usa **U-Boot + USB mass storage**, não `fastboot
flash` direto — divergência documentada em
[`audit/upstream-comparison.md`](../audit/upstream-comparison.md) §4.

### ii.4 Metodologia da auditoria

A auditoria ocorreu em 24/11/2026, das 21:43 às 23:25, em duas etapas:

1. **Sem privilégio** — acesso SSH como usuário comum, somente leitura.
2. **Com privilégio** — após o operador fornecer a senha de `sudo`.

Princípios adotados:

- **Identificação positiva antes de qualquer comando.** O aparelho havia mudado de IP por DHCP;
  confirmamos a identidade comparando a **chave pública ed25519 do host** com `known_hosts`. A
  verificação de host do SSH foi mantida ativa o tempo todo.
- **Nada é aprovado sem evidência.** Cada classificação aponta para uma saída de comando arquivada.
- **Teste não realizado nunca conta como aprovado** — é excluído do denominador, não reprovado.
- **Sanitização obrigatória.** Nenhuma evidência publicada contém IMEI, número de série, MAC, IP
  privado, SSID ou chave.

---

## iii. Resultados

### iii.1 Comparativo das três distribuições

| Critério | **postmarketOS** | **Mobian** | **Ubuntu Touch** |
|---|---|---|---|
| Base | Alpine Linux (musl) | Debian (glibc) | Ubuntu + Halium |
| Interface | Phosh / Plasma Mobile | Phosh | Lomiri (ex-Unity 8) |
| Servidor de exibição | Wayland | Wayland | Mir → Wayland |
| Telefonia | ModemManager | ModemManager | oFono |
| Dispositivos | 300+ (maioria `testing`) | Poucos, bem suportados | ~111 no catálogo |
| Kernel | Mainline quando possível | Mainline | Downstream + Halium |
| Gerenciador de pacotes | `apk` | `apt` | `apt` + click/snap |
| **Forte em** | Alcance e compromisso com mainline | Estabilidade do ecossistema Debian | UX coesa e telefonia madura |
| **Fraco em** | Maturidade varia muito por aparelho | Base de aparelhos pequena | Depende de blobs Android (Halium) |

**Leitura crítica.** A diferença mais profunda não é a interface, é o **kernel**. Ubuntu Touch usa
Halium, uma camada que reaproveita o kernel e os drivers Android do fabricante: funciona rápido em
muitos aparelhos, mas herda o kernel congelado — o problema que se queria resolver. postmarketOS e
Mobian apostam em mainline: mais trabalho por aparelho, porém vida longa real.

Mobian é a mais estável das três, mas concentra-se em hardware pensado para Linux (PinePhone,
PineTab). Para um aparelho de mercado como o Edge 30, **postmarketOS era a única opção com port
existente** — critério que decidiu nossa escolha.

**Nenhuma das outras duas roda no Edge 30**, o que torna a comparação necessariamente parcial: é
comparação de projetos, não de três sistemas no mesmo hardware.

### iii.2 Matriz de compatibilidade — 34 subsistemas

| Classificação | Qtd. | Subsistemas |
|---|---|---|
| **FUNCIONAL** | 14 | CPU, GPU Adreno 642L, Display, **Touchscreen**, Wi-Fi, Bluetooth, Áudio, Microfone, Bateria, Botões, UFS, Memória/ZRAM, Térmico, Remote processors |
| **PARCIALMENTE FUNCIONAL** | 4 | Estabilidade do Wi-Fi, Volume inicial, Codec de headset, USB-C |
| **DETECTADO, NÃO VALIDADO** | 5 | Câmera traseira, Flash, Acelerômetro, Luz ambiente, Proximidade |
| **DETECTADO E BLOQUEADO** | 1 | Modem (sem SIM — não é defeito) |
| **NÃO TESTADO** | 4 | Telefonia, Dados móveis, GPS, Carregamento |
| **NÃO SUPORTADO** | 5 | Câmera frontal, Câmera principal OV50A, NFC, Vibração, Biometria |
| **NÃO FUNCIONAL** | 1 | **Suspensão** |

### iii.3 Metodologia da pontuação

- Pesos: `FUNCIONAL = 1,0` · `PARCIAL = 0,5` · `DETECTADO E BLOQUEADO = 0,5` · demais `= 0`.
- Denominador: 34 − 4 `NÃO TESTADO` = **30 subsistemas avaliáveis**.
- Numerador: (14 × 1,0) + (4 × 0,5) + (1 × 0,5) = **16,5**.

> **Compatibilidade de hardware = 16,5 / 30 = 55%**

| Dimensão | Nota | Justificativa |
|---|---|---|
| Compatibilidade de hardware | 55% | Cálculo acima |
| Estabilidade | 65% | 0 serviços em falha, sem panic; descontado pela suspensão que trava |
| Desempenho | 85% | 97–98% de CPU ociosa; 499 MB/s de escrita; GPU escalando |
| Segurança | 78% | ASLR, firewall `policy drop`, root bloqueada; sem criptografia de disco |
| Eficiência energética | 35% | Suspensão não funciona; 1,12 W em repouso |
| Manutenibilidade | 80% | `apk` operante, 1326 pacotes, repositórios assinados |
| Reprodutibilidade | 60% | Guia existe, mas diverge do oficial; sem log de flash |
| Experiência de uso | 70% | Toque, GPU acelerada, áudio e Bluetooth operantes |

**Nível de maturidade: 3 de 5 — Estação Linux portátil.**

O aparelho é usável localmente como computador Linux de bolso. O que impede o Nível 4 (plataforma
móvel funcional) é, em parte, ausência de validação (sem SIM, sem libcamera, sensores bloqueados por
polkit) e, em parte, um defeito real: **a suspensão não funciona**, requisito para uso móvel diário.

### iii.4 Evidências selecionadas

**Aceleração gráfica (prova indireta, depois confirmada).** Sem acesso à sessão Wayland, provamos a
aceleração por duas vias independentes: o compositor `phoc` mantinha **5 descritores abertos em
`/dev/dri/renderD128`** (render node — existe só para submeter comandos à GPU), e o `devfreq`
registrou **399 transições com 10 212 ms na frequência máxima de 608 MHz**. Uma GPU em renderização
por software ficaria travada no mínimo. O `dmesg` com root confirmou depois:
`[drm] Loaded GMU firmware v3.1.10`.

**Bateria.** 20 amostras em 8 minutos: −225 mA a 3,958 V (**0,89 W**), temperatura constante em
33,0 °C, `STATE_OF_HEALTH = 100`, resistência interna 148 mΩ. **Nenhuma autonomia foi estimada** — a
janela cobre um único estado e a suspensão nunca funcionou.

**Suspensão (defeito novo).** Em modo `deep`, aborta com `Wakeup pending. Abort CPU freeze`. Em
`s2idle`, **trava o aparelho e força reinicialização**, com `dwc3-qcom: port-1 HS-PHY not in L2` e
`Non-boot CPUs are not disabled`. Esse defeito **não consta da matriz oficial do dispositivo** e é
candidato a contribuição upstream.

**Wi-Fi sem calibração.** O `ath11k` registra `qmi failed to download BDF:-2` e `board_id 0xff`: o
rádio opera com parâmetros genéricos. Mesmo após desligar o `power_save` — o que derrubou a latência
média de 70 ms para 15 ms — a perda de pacotes permaneceu em 17%, indicando causa adicional.

### iii.5 Correções aplicadas

| ID | Problema | Resultado |
|---|---|---|
| A-02 | PulseAudio e PipeWire simultâneos | ✅ PipeWire desabilitado; áudio validado por audição |
| A-05 | Bluetooth bloqueado por `rfkill` | ✅ `UP RUNNING`; persistiu após reboot |
| A-06 | `power_save` do Wi-Fi | ⚠️ Latência 70→15 ms, mas perda ainda 17%; custo de +26% de consumo |
| A-07 | `kptr_restrict=0`, LLMNR, senha SSH | ✅ Corrigidos e persistentes |
| A-03 | Sem criptografia de disco | ⏸️ Exige reinstalação destrutiva — não executado |
| A-04 | Suspensão | ❌ Não corrigível: é defeito de kernel |

### iii.6 Dois erros nossos — e por que os registramos

Entendemos que uma auditoria honesta precisa auditar também a si mesma.

**Erro 1 — concluímos que não havia firewall.** Sem acesso root, não conseguimos ler as regras e
inferimos, *da ausência de indícios*, que provavelmente não haveria filtragem. Com root, descobrimos
uma tabela `nftables` robusta, com `policy drop` e bloqueio de tráfego entrante do modem
(`iifname "wwan*" drop`). **Ausência de evidência não é evidência de ausência.**

**Erro 2 — classificamos o touchscreen como quebrado.** Medíamos a contagem de interrupções durante
15–30 s enquanto pedíamos que o operador tocasse a tela. O contador não subia, e concluímos falha
**CRÍTICA**. Estava errado: o operador estava lendo a instrução no computador, não com o dedo na
tela — a janela de medição não coincidia com o estímulo.

O teste correto — ler `/dev/input/event3` por 45 s — capturou **6942 eventos** com coordenadas
reais:

```
03 00 39 00 53 00 00 00   → EV_ABS  ABS_MT_TRACKING_ID = 0x53
03 00 35 00 9e 01 00 00   → EV_ABS  ABS_MT_POSITION_X  = 414
03 00 36 00 c4 05 00 00   → EV_ABS  ABS_MT_POSITION_Y  = 1476
```

Pior: tínhamos a evidência contrária e a ignoramos. A contagem crescia continuamente entre medições
(1346 → 1540 → 3686 → 6395 → 8619) e registramos isso como "anomalia sem explicação" em vez de
deixar que refutasse a hipótese. **Esse erro sozinho mudava o nível de maturidade de 3 para 2.**

A lição metodológica: concluir a partir da *ausência* de um evento exige provar que o estímulo
ocorreu **dentro** da janela de medição.

---

## iv. Conclusão

**Linux convencional em smartphone funciona — com ressalvas que precisam ser ditas com precisão.**

O Motorola Edge 30 inicializa em Linux mainline, sobe interface gráfica acelerada por GPU, responde
ao toque, conecta em Wi-Fi 6, toca áudio, captura do microfone e gerencia bateria com telemetria
completa. Tudo isso com **zero serviços em falha** e os quatro co-processadores Qualcomm operando.
Como estação Linux portátil, **o aparelho entrega**.

Como *substituto de smartphone*, não entrega ainda. A suspensão trava o sistema, o que inviabiliza
uso móvel diário. Câmera frontal, NFC, vibração e leitor biométrico não têm driver. Telefonia não
pôde ser validada por falta de SIM — e a wiki oficial adverte que funções avançadas de chamada
(mudo, viva-voz, áudio por Bluetooth) não funcionam.

O gargalo **não é o SoC**: o Snapdragon 778G+ é bem suportado upstream. É o conjunto de periféricos
cujos drivers dependem de trabalho voluntário ainda não mesclado. Isso explica a assimetria do
projeto: o que o kernel mainline cobre funciona bem; o que depende de um driver específico do
aparelho, não.

Quanto às três distribuições, a escolha é um trade-off claro: **Ubuntu Touch** entrega a melhor
experiência imediata ao custo de depender de blobs Android via Halium — perpetuando a obsolescência
que se queria combater. **Mobian** oferece a estabilidade do Debian, mas para poucos aparelhos.
**postmarketOS** aposta em mainline e alcance: mais trabalho por aparelho, maturidade desigual, e a
única das três capaz de rodar neste Edge 30.

### iv.1 Trabalhos futuros

1. **Reportar o travamento da suspensão upstream** — defeito reprodutível, ausente da matriz
   oficial, com diagnóstico pronto.
2. **Investigar o BDF ausente do Wi-Fi** (`board_id 0xff`), provável causa da perda residual de 17%.
3. **Validar telefonia com SIM inserido**, observando que a wiki exige provider `pipewire` para
   chamadas — o que conflita com nossa correção A-02.
4. **Reinstalar com criptografia de disco (FDE)**, suportada segundo a wiki e hoje ausente.
5. **Medir autonomia real** em ciclo de descarga completo, impossível enquanto a suspensão falhar.

---

## v. Anexos

### Anexo A — Slides da apresentação

- `presentation/edge30-postmarketos.pptx` — 17 slides, 16:9, com transições
- `presentation/edge30-postmarketos.pdf` — versão imprimível
- `presentation/index.html` — versão animada, offline (fonte canônica)
- `docs/roteiro-apresentacao.md` — falas slide a slide

### Anexo B — Roteiro de instalação e configuração

- `docs/guia-de-reproducao.md` — pré-requisitos e passos
- `audit/scripts/collect-diagnostics.sh` — coletor de diagnóstico reutilizável, testado no aparelho

### Anexo C — Prompt e LLM utilizada

**Ferramenta:** Claude Code (CLI da Anthropic)
**Modelo:** **Claude Opus 5** (`claude-opus-5`)
**Período:** 4, 18 e 24 de novembro de 2026

**Forma de uso.** A LLM foi usada como **par técnico operando o aparelho**, não como geradora de
texto. Executou comandos via SSH, interpretou saídas, levantou e descartou hipóteses, e redigiu a
documentação a partir das evidências coletadas. Toda afirmação técnica deste artigo tem origem em
uma saída de comando arquivada em `audit/evidence/sanitized/`.

**Prompt principal da auditoria (resumido):**

> Atue como uma equipe multidisciplinar de engenheiros seniores em Linux embarcado, kernel, ARM64,
> drivers Qualcomm e segurança. Conecte-se ao Motorola Edge 30 (`dubai`, XT2203-1, SM7325) na rede
> Wi-Fi local, realize uma auditoria real e determine o nível de maturidade do port.
> Faça uma auditoria inicial **somente leitura**. Levante inventário do SO, kernel e drivers.
> Monte uma matriz de compatibilidade classificando cada subsistema como FUNCIONAL, PARCIALMENTE
> FUNCIONAL, DETECTADO MAS NÃO VALIDADO, NÃO FUNCIONAL, NÃO SUPORTADO ou NÃO TESTADO.
> **Não confunda a existência de um dispositivo em `/dev` ou `/sys` com funcionamento comprovado.**
> **Não classifique toda mensagem de warning como defeito crítico.**
> **Testes não realizados não podem ser contabilizados como aprovados.**
> Qualquer pontuação percentual deve apresentar metodologia, pesos e critérios explícitos.
> Não publique IPs privados, MACs, IMEI ou números de série.
> Separe diagnóstico, proposta de correção e execução. Não aplique correções automaticamente.

O prompt integral está versionado no repositório.

**Restrições que impusemos à LLM:**

- Modo somente leitura na primeira etapa; alterações apenas com autorização explícita.
- Proibido desativar a verificação de chave de host do SSH.
- Proibido publicar dados sensíveis; sanitização verificada programaticamente.
- Obrigatório declarar limitações e separar o que foi medido do que foi inferido.

**Avaliação crítica do uso de LLM.** O ganho foi de velocidade e cobertura: 33 testes em ~100
minutos, com documentação simultânea. Mas a LLM **errou duas vezes de forma relevante** (§iii.6), e
em ambos os casos o erro foi de *raciocínio sobre evidência*, não de execução: inferiu ausência de
firewall a partir de ausência de dados, e concluiu falha de hardware a partir de uma janela de
medição mal sincronizada. O segundo erro só foi descoberto porque **um integrante do grupo
contestou o resultado** com base no uso cotidiano do aparelho. É o argumento prático mais forte
deste trabalho a favor da verificação humana: a ferramenta acelera, mas não dispensa quem conhece o
objeto.

### Anexo D — Arquivos de configuração e evidências

| Caminho | Conteúdo |
|---|---|
| `audit/hardware-compatibility.csv` | Matriz dos 34 subsistemas |
| `audit/system-inventory.json` | Inventário completo legível por máquina |
| `audit/test-results.json` | 33 testes com método, resultado e evidência |
| `audit/evidence/sanitized/` | Saídas brutas de comando, sanitizadas |
| `audit/dashboard.html` | Painel offline com gráficos e matriz visual |
| `audit/fixes-applied.md` | Correções executadas, com rollback |
| `docs/evidencias.md` | Rastreabilidade: afirmação → evidência → grau |

**Configurações aplicadas ao aparelho:**

```sh
/etc/sysctl.d/99-audit-hardening.conf          # kernel.kptr_restrict = 2
/etc/systemd/resolved.conf.d/99-audit-no-llmnr.conf   # LLMNR=no, MulticastDNS=no
/etc/ssh/sshd_config.d/99-audit-nopassword.conf       # PasswordAuthentication no
/etc/NetworkManager/conf.d/wifi-powersave-off.conf    # wifi.powersave = 2
```

### Anexo E — Referências

1. postmarketOS. *Motorola Edge 30 (motorola-dubai)*. Wiki oficial do dispositivo. Acesso: 24 nov. 2026.
2. postmarketOS. *pmaports* e documentação do `pmbootstrap`. Acesso: 24 nov. 2026.
3. Linaro. *Input: add initial support for Goodix Berlin touchscreen IC* — série de patches v1–v15, linux-input. Acesso: 24 nov. 2026.
4. LKML. *arm64: dts: qcom: Add Motorola edge 30 (dubai) DTS* — mar. 2026. Acesso: 24 nov. 2026.
5. Linux Kernel Driver DataBase. *CONFIG_TOUCHSCREEN_GOODIX_BERLIN_SPI*. Acesso: 24 nov. 2026.
6. Mobian Project. Documentação oficial. Acesso: 24 nov. 2026.
7. UBports Foundation. *Ubuntu Touch* — documentação e catálogo de dispositivos. Acesso: 24 nov. 2026.
8. Wikipedia. *Comparison of mobile operating systems* e *List of open-source mobile phones*. Acesso: 24 nov. 2026.
9. Alpine Linux. Documentação do `apk` e do sistema base. Acesso: 24 nov. 2026.
10. Mesa 3D. Documentação dos drivers Freedreno e Turnip. Acesso: 24 nov. 2026.

---

<sub>Documento gerado em 24/11/2026. Evidências e histórico de revisão em
<https://github.com/Pedrssa/edge30-postmarketos> · auditoria completa no diretório `audit/`.</sub>
