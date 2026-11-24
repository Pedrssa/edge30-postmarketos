# Análise gráfica

**Pergunta central:** a interface está usando a GPU ou caindo em renderização por software?

**Resposta: está usando a GPU.** A aceleração por hardware foi comprovada por duas linhas de
evidência independentes, obtidas sem acesso à sessão Wayland.

---

## 1. O problema do método

`eglinfo`, `glxinfo` e `vulkaninfo` **não estão instalados** no aparelho, e instalá-los violaria a
natureza somente-leitura desta auditoria. Além disso, mesmo instalados, executá-los por SSH fora da
sessão Wayland produziria falha de acesso ao display — que, conforme o próprio briefing adverte,
**não deve ser confundida com ausência de aceleração**.

Foram então usadas duas provas indiretas, ambas independentes de sessão gráfica.

---

## 2. Prova 1 — o compositor mantém o render node aberto

O processo `phoc` (PID 3281), compositor Wayland do Phosh, mantém **dez descritores de arquivo**
abertos em nós DRM:

```
17 -> /dev/dri/card0        21 -> /dev/dri/renderD128
18 -> /dev/dri/card0        22 -> /dev/dri/card0
19 -> /dev/dri/renderD128   23 -> /dev/dri/renderD128
20 -> /dev/dri/renderD128   24 -> /dev/dri/card0
                            25 -> /dev/dri/card0
                            26 -> /dev/dri/renderD128
```

A distinção importa: `card0` é o nó de *modesetting* (usado mesmo em software), mas **`renderD128`
é o render node** — existe exclusivamente para submissão de comandos à GPU. Um compositor em
renderização por software não teria motivo para abri-lo, muito menos cinco vezes.

As bibliotecas mapeadas no espaço de endereçamento de `phoc` confirmam:

```
libgallium-26.2.6.so      ← driver Mesa (freedreno para Adreno)
libEGL.so.1.0.0           ← EGL
libGLESv2.so.2.0.0        ← OpenGL ES 2
libvulkan.so.1.4.360      ← carregador Vulkan
```

## 3. Prova 2 — a GPU efetivamente escalou de frequência

Esta é a evidência decisiva. O `devfreq` de `3d00000.gpu` registra o histórico real de transições:

| Frequência | Tempo acumulado |
|---|---|
| 315 MHz (mínimo) | 31 376 ms |
| 450 MHz | 120 ms |
| 550 MHz | 0 ms |
| **608 MHz (máximo)** | **4 876 ms** |

**Total de transições: 191**, com 93 saltos diretos de 315 MHz para 608 MHz.

Uma GPU ociosa permaneceria travada na frequência mínima. O padrão observado — quase 5 segundos na
frequência máxima e 191 transições sob governor `simple_ondemand` — só ocorre quando há carga real
de renderização sendo submetida. **Isso é incompatível com renderização por software.**

---

## 4. Pilha gráfica identificada

| Camada | Componente | Versão / estado |
|---|---|---|
| Hardware | Adreno 642L (`3d00000.gpu`) | Operacional, governor `simple_ondemand` |
| Firmware | `a660_zap.mbn` | Presente em `/lib/firmware/qcom/sm7325/` |
| DRM/KMS | `qcom,sc7280-dpu` | `card0` + `card0-DSI-1` + `card0-Writeback-1` |
| Driver 3D | Mesa **26.2.6** — `mesa-dri-gallium` (Freedreno) | Instalado |
| Vulkan | `mesa-vulkan-freedreno` 26.2.6 (**Turnip**) + `soc-qcom-vulkan-14-r0` | Instalado, carregador 1.4.360 mapeado em `phoc` |
| EGL / GLES | `mesa-egl`, `mesa-gles`, `mesa-gl`, `mesa-gbm` 26.2.6 | Instalados |
| Compositor | `phoc` 0.58.0 | Ativo (PID 3281) |
| Shell | `phosh` 0.58.0 | Ativo (PID 3382) |
| Teclado virtual | `phosh-osk-stevia` | Ativo, após 6 falhas de inicialização |
| Portal | `xdg-desktop-portal-phosh` | Ativo |
| Greeter | `greetd` | Ativo desde 21:43:31 |

Sessão de login confirmada: `loginctl` lista a sessão `c3` em `seat0`, `tty7`, classe `user`.

---

## 5. Display

| Parâmetro | Valor |
|---|---|
| Conector | `card0-DSI-1` — `connected`, `enabled`, `dpms = On` |
| Resolução | 1080×2400 |
| Painel | CSOT com controlador Novatek NT37701 (do `cmdline`) |
| Backlight | `ae94000.dsi.0` — 1079 de 3514 (≈ 31%) |
| Writeback | `card0-Writeback-1` disponível |
| Taxa de atualização | **Não verificada.** O hardware suporta 48/60/90/120/144 Hz; o modo em uso não foi lido. A wiki registra que o driver do painel ainda é WIP. |

---

## 6. Confirmação direta com acesso root

A comprovação indireta acima foi **validada pelo `dmesg` completo**, obtido depois com privilégio:

```
[ 1.316405] msm_dpu ae01000.display-controller: bound ae94000.dsi (ops dsi_ops)
[ 1.346506] msm_dpu ae01000.display-controller: bound 3d00000.gpu (ops a3xx_ops)
[ 1.349286] [drm:dpu_kms_hw_init] dpu hardware revision: 0x70020000
[ 1.354708] [drm] Initialized msm 1.13.0 for ae01000.display-controller on minor 0
[13.457808] [drm:adreno_request_fw] loaded qcom/a660_sqe.fw from new location
[13.458636] [drm:adreno_request_fw] loaded qcom/a660_gmu.bin from new location
[13.460040] [drm] Loaded GMU firmware v3.1.10
```

⚠️ **Um alerta que parecia defeito e não é.** Antes dessas linhas, o log registra duas vezes:

```
Direct firmware load for qcom/a660_sqe.fw failed with error -2
[drm:adreno_request_fw] *ERROR* failed to load a660_sqe.fw
```

Lido isoladamente, isso sugeriria microcódigo da GPU ausente. Mas os arquivos existem
(`a660_sqe.fw`, 43 292 bytes; `a660_gmu.bin`, 55 252 bytes) e as falhas ocorrem em 1,35 s e 1,72 s,
**antes de o rootfs estar montado**; em 13,45 s o carregamento é bem-sucedido. É **ruído de boot**.

Na segunda leitura do `devfreq`, a GPU acumulava **399 transições e 10 212 ms a 608 MHz** (contra
191 e 4 876 ms na primeira), confirmando uso contínuo.

---

## 7. Ressalvas honestas

- **Não foi possível determinar a versão de OpenGL ES nem o perfil Vulkan efetivamente exposto.**
  Isso exigiria `eglinfo`/`vulkaninfo` dentro da sessão Wayland.
- **O desempenho gráfico não foi medido.** Nenhum benchmark de GPU foi executado; a comprovação é
  de *uso* da GPU, não de *quão bem* ela rende.
- **A fluidez da interface não pôde ser avaliada**, porque o touchscreen não responde (ver
  [`remediation-plan.md` § A-01](remediation-plan.md)) e a observação remota não permite julgar
  suavidade de animação.
- A presença do carregador Vulkan mapeado em `phoc` indica disponibilidade da biblioteca, **não**
  que o compositor esteja renderizando via Vulkan — o Phoc usa GLES por padrão.
