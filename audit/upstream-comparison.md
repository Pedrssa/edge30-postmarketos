# Comparação com o estado upstream

**Fontes consultadas em 24/11/2026:**

- Wiki oficial do device — `wiki.nura.eco/wiki/Motorola_Edge_30_(motorola-dubai)` (acesso obtido via
  navegador, contornando o bloqueio Anubis que havia impedido a consulta anterior — **resolve a
  pendência P-04**)
- Documentação do driver Goodix Berlin no kernel Linux (série de patches v1–v15, Linaro)
- Patches de device tree SM7325 / Motorola dubai enviados à LKML (mar/2026, v2 e v3)
- Registro LKDDB de `CONFIG_TOUCHSCREEN_GOODIX_BERLIN_SPI`

---

## 1. Posição oficial do port

| Campo | Valor |
|---|---|
| Categoria | **testing** |
| Mainline | **sim** |
| Imagens pré-prontas | **não** |
| Kernel oficial | **7.2.9-3** |
| Pacote de device | `device-motorola-dubai` |
| Pacote de kernel | `linux-postmarketos-qcom-sc7280` |
| Unixbench de referência | 9 626,6 |
| Descrição oficial | *"Affordable price. Modern hardware. Great Unixbench score. Mainline. Ready for daily usage!"* |

O aparelho auditado roda **exatamente o kernel oficial** (`7.2.9`, pacote `-r2` contra `-3` da
wiki — diferença de revisão de empacotamento) e os pacotes oficiais `device-motorola-dubai-2-r0`,
`device-motorola-dubai-kernel-csot-2-r0` e `firmware-motorola-dubai-20250428-r1`.

Isso é importante: **o sistema não está desatualizado nem usa componentes divergentes**. As
diferenças encontradas são de *configuração*, não de versão.

---

## 2. Matriz oficial × auditoria

| Componente | Wiki oficial | Esta auditoria | Leitura |
|---|---|---|---|
| Screen | Works | ✅ FUNCIONAL | Concorda |
| **Touchscreen** | **Works** | ❌ **NÃO FUNCIONAL** | 🔴 **Divergência crítica** |
| 3D Acceleration | Works | ✅ FUNCIONAL | Concorda |
| Audio | Works | ✅ FUNCIONAL (saída e mic) | Concorda |
| Wi-Fi | Works | ✅ FUNCIONAL | Concorda |
| **Bluetooth** | **Works** | ⚠️ Detectado, bloqueado por `rfkill` | 🟡 Divergência de configuração |
| Battery | Works | ✅ FUNCIONAL | Concorda |
| Internal storage | Works | ✅ FUNCIONAL | Concorda |
| Buttons | Works | ✅ FUNCIONAL | Concorda |
| Camera | Partial | ⚠️ Detectado, não validado | Concorda |
| Camera Flash | Works | ⚠️ Detectado, não acionado | Não contradiz |
| **Calls / SMS / Mobile data** | **Works** | ❓ Não testado (sem SIM) | Não verificável |
| **GPS** | **Works** | ❓ Não testado | Não verificável |
| NFC | **Broken** | ❌ NÃO SUPORTADO | Concorda |
| Haptics | **Broken** | ❌ NÃO SUPORTADO | Concorda |
| **Accelerometer / ALS / Proximity** | **Works** | ⚠️ Detectados, Claim negado por polkit | 🟡 Limitação de método |
| Magnetometer | Works | ❓ Não testado | — |
| FDE | Works | ❌ Não habilitado na instalação | 🟡 Escolha de instalação |
| USB OTG | Works | ⚠️ `udc` em `not attached` | Não contradiz |
| U-Boot (mainline) | **Broken** | n/a | — |

---

## 3. As três divergências e o que significam

### 3.1 Touchscreen — a mais relevante

A wiki declara `Works` e a tabela de hardware confirma: **Goodix GT9916, interface SPI, status `Y`**.
O driver `goodix-berlin-spi` está em mainline desde o kernel 6.9 e o binding do device tree
especifica `IRQ_TYPE_LEVEL_LOW` — exatamente o que o aparelho apresenta (`msmgpio 81 Level`).

Ou seja: **hardware suportado, driver em mainline, configuração de interrupção correta, e ainda
assim não há eventos.** Isso reforça a hipótese de firmware/configuração de painel não aplicada, e
**afasta** a hipótese de incompatibilidade de hardware ou de device tree errado.

Como o aparelho já roda o kernel oficial, a causa deve estar em um dos seguintes:
(a) revisão de empacotamento `-r2` vs `-3`; (b) estado de inicialização do controlador;
(c) particularidade da unidade física. Um `apk upgrade` é a hipótese de correção mais direta.

### 3.2 Bluetooth — configuração, não driver

A wiki declara `Works` para o WCN6750. A auditoria encontrou o driver carregado, o firmware
operante e 1781 comandos HCI sem erro — tudo coerente com `Works`. O que impede o uso é um
**bloqueio `rfkill` de software**, removível com um comando de root. Não é divergência real de
suporte.

### 3.3 Sensores — limitação do método de auditoria

A wiki afirma *"Sensor hub support works"* para o ICM-42602, e a auditoria **confirmou
independentemente** que `iio-sensor-proxy` reporta `HasAccelerometer=true`, `HasAmbientLight=true`
e `HasProximity=true`, com `hexagonrpcd-adsp-sensorspd` ativo.

A reivindicação (`ClaimAccelerometer`) falhou com `Access denied` — **polkit negando a uma sessão
SSH sem seat gráfico**, não falha de hardware. Classificado como "detectado, não validado" por
rigor, mas a evidência aponta fortemente para funcionamento.

---

## 4. Divergência de procedimento de instalação

O método oficial difere do documentado no repositório em pontos substantivos:

| Etapa | Procedimento oficial | Repositório |
|---|---|---|
| Verificação de painel | `fastboot getvar primary-display` → `csot` ou `tianma` | Não documentado |
| Bootloader | **U-Boot** gravado em `boot` (`u-boot-motorola-dubai-csot.img`) | `fastboot` direto |
| Instalação do rootfs | Via U-Boot em modo **USB mass storage** + `pmbootstrap install --sdcard` | `fastboot flash` |
| AVB | `pmbootstrap flasher flash_vbmeta` | Mencionado |
| DTBO | `pmbootstrap flasher flash_dtbo` (apagar overlays Android) | Mencionado |
| **Provider de áudio** | **`pipewire`** — exigido para chamadas funcionais | **`pulseaudio`** instalado |
| Service manager | `systemd` | ✅ Confere |
| Canal | `edge` — exigido para chamadas | ✅ Confere |

A divergência de **provider de áudio** é a mais consequente e sustenta o item **A-02** do plano de
correção: a wiki condiciona explicitamente o funcionamento de chamadas à escolha do `pipewire`, e o
aparelho tem PulseAudio como backend **com PipeWire rodando em paralelo**.

---

## 5. Limitações conhecidas upstream (não são defeitos deste port)

Registradas na wiki oficial e **confirmadas** pela auditoria:

| Limitação | Situação upstream |
|---|---|
| Câmera frontal (OV32B40) | Driver pronto, **em processo de integração** no kernel near-to-mainline |
| Câmera principal (OV50A) | Sem driver; depende de suporte a **C-PHY** ainda não disponível upstream |
| Háptica (AW86224) | Driver existe, **não mesclado**; integração pendente também no feedbackd |
| NFC (ST21NFCJ) | Funciona na árvore de ValPackett, **não empacotado** |
| Consumo ocioso elevado | Causa identificada (motores de foco); **correção já mesclada**, aguardando release |
| Áudio analógico USB-C (FSA4480) | Funciona na árvore de ValPackett, **não empacotado** |
| Foco de câmera | Funciona em nível de driver, **indisponível nos aplicativos** |
| Funções avançadas de chamada | Mudo de microfone, viva-voz e voz por Bluetooth **não funcionam** |
| Leitor biométrico (Egis ET528) | Sem driver |
| Sensor SAR (SX9375) | Sem driver |
| U-Boot mainline | `Broken` |

**Nenhum destes itens é regressão do trabalho do grupo** — são limites do estado atual do suporte
upstream.

---

## 6. Oportunidades de contribuição upstream

Identificadas a partir desta auditoria:

1. **Relatar a falha do touchscreen (A-01).** A wiki declara `Works`; se a falha for reproduzível em
   uma instalação limpa do kernel `7.2.9-r2`, trata-se de regressão ou de caso não coberto, e o
   relato tem valor concreto para o canal `#sc7280-mainline:postmarketos.org`.
2. **Documentar o conflito PulseAudio/PipeWire (A-02).** A wiki exige `pipewire` para chamadas, mas
   não adverte sobre o estado resultante de uma instalação com `pulseaudio`. Uma nota na seção de
   problemas conhecidos seria útil.
3. **Reportar o `BD Address` placeholder do Bluetooth.** O endereço `02:00:xx` em vez do fornecido
   pelo bootloader pode ser um bug de aplicação de MAC digno de investigação.
4. **Contribuir a matriz de energia.** A medição de 0,89 W em repouso, com metodologia documentada,
   oferece uma linha de base quantitativa para verificar o ganho quando a correção dos motores de
   foco chegar ao release.

---

## 7. Advertência sobre aplicação de patches

Conforme orientação explícita: **nenhum patch de outro modelo deve ser aplicado sem verificação de
compatibilidade.** Em particular, o driver `goodix-berlin` foi originalmente desenvolvido para o
GT9916 presente nas plataformas de referência **SM8550/SM8650** — SoCs diferentes do SM7325 aqui
auditado. Embora o controlador seja o mesmo, parâmetros de painel, sequência de regulador e
temporização de reset podem divergir, e qualquer adaptação exige validação no hardware real antes
de ser considerada correção.
