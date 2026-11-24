# Análise de kernel e drivers

**Kernel:** `7.2.9 #3-postmarketos-qcom-sc7280 SMP PREEMPT`
**Compilador:** Alpine Clang 23.1.3 / LLD 23.1.3
**Build:** 17 de outubro de 2026, 01:53:13 UTC
**Pacote:** `linux-postmarketos-qcom-sc7280-7.2.9-r2`
**Arquitetura:** aarch64 · **Modelo em DT:** `Motorola Edge 30 (CSOT)` · **Compatible:** `motorola,dubai` + `qcom,sm7325`

Isto resolve a pendência **P-02**, que registrava a versão do kernel como `[RELATADO]`.

---

## 1. Saúde geral

| Indicador | Resultado |
|---|---|
| Kernel panic | **Nenhum** |
| Oops | **Nenhum** |
| Segmentation fault em serviços | **Nenhum** |
| Unidades systemd em falha | **0** (`systemctl --failed` vazio) |
| Reboots inesperados | Nenhum — uptime contínuo durante toda a auditoria |
| `dmesg` completo | **Inacessível** (`dmesg_restrict=1`, sem root) |
| `devices_deferred` | **Inacessível** (debugfs restrito) |

A análise de erros foi feita por `journalctl -b -p err`, que é legível pelo usuário comum. A
ausência de acesso a `dmesg` é a maior limitação desta seção e deve ser considerada ao ler as
conclusões: **falhas de probe silenciosas não seriam visíveis por este método.**

---

## 2. Remote processors — todos operacionais

Este é o indicador mais forte de maturidade do port. Os quatro co-processadores do SM7325 estão em
execução:

| Nó | Processador | Estado |
|---|---|---|
| `remoteproc0` | modem (MPSS) | `running` |
| `remoteproc1` | adsp | `running` |
| `remoteproc2` | wpss (Wi-Fi) | `running` |
| `remoteproc3` | cdsp | `running` |

Os serviços de suporte correspondentes estão ativos: `rmtfs` (remote filesystem), `tqftpserv` (QRTR
TFTP), `qcom_pd_mapper`, `hexagonrpcd-adsp-rootpd` e `hexagonrpcd-adsp-sensorspd`.

Firmware presente em `/lib/firmware/qcom/sm7325/`: `a660_zap.mbn` (GPU), `adsp.mbn`, `cdsp.mbn`,
`modem.mbn`, `aw88261_acf.bin` (amplificadores de áudio), além dos arquivos `.jsn` de configuração e
um diretório específico `motorola/dubai`. Pacote `firmware-motorola-dubai-20250428-r1`.

---

## 3. Subsistemas Qualcomm verificados

- **RPMh / reguladores / clocks:** operacionais por inferência — sem eles nenhum dos remoteprocs
  subiria, o display não acenderia e o UFS não responderia. Não inspecionados diretamente
  (`debugfs` restrito).
- **IOMMU:** não inspecionável sem root; a operação de CAMSS e GPU sugere funcionamento.
- **Gerenciamento térmico:** **39 zonas** ativas, cobrindo `cpu0`–`cpu11`, `cpuss0/1`, `gpuss0/1`,
  `nspss0/1`, `mdmss0`–`mdmss3`, `ddr`, `camera0`, `pm7325`, `pm8350c`, `pm7250b`, `qcom-battmgr-bat`,
  `chg-skin`, `conn`, `xo`, `quiet`, `cam-flash`, `sdm-skin`, `pa-1`. Em repouso, todas entre
  **32,8 °C e 37,2 °C** — perfil térmico saudável.
- **PMIC / pmic-glink:** `qcom,sm7325-pmic-glink` ativo, fornecendo bateria, USB-C/UCSI e wireless.
- **Armazenamento:** `1d84000.ufshc` (UFS 3.1 Micron). O rootfs está em `ext4` sobre `loop0p2`,
  mapeado a partir de `sde27` — layout em que a partição `userdata` hospeda a imagem.
- **IPA:** `1e40000.ipa` presente, provendo `rmnet_ipa0` para dados móveis.

---

## 4. Módulos carregados — leitura dirigida

Agrupamento dos módulos relevantes de `lsmod`:

| Grupo | Módulos | Leitura |
|---|---|---|
| Áudio | `snd_soc_sm8250`, `snd_soc_qcom_common`, `snd_soc_qcom_sdw`, `q6voice`, `q6voice_dai`, `q6cvs`, `q6mvm`, `q6cvp`, `q6usb`, `soc_usb` | Pilha de áudio Qualcomm completa, **incluindo o caminho de voz** (`q6voice*` existe para chamadas) |
| Câmera | `qcom_camss` (679 KB), `s5kjn1`, `gc02m1b`, `at24`, `videobuf2_dma_contig` | CAMSS e dois sensores com driver |
| Vídeo | `qcom_iris` | Decodificação de vídeo por hardware disponível |
| Bluetooth | `bluetooth` (987 KB), `hci_uart`, `btqca`, `btbcm`, `rfcomm`, `bnep`, `ecdh_generic`, `ecc` | Pilha completa; o bloqueio é de `rfkill`, não de driver |
| USB-C | `fsa4480`, `pwrseq_qcom_wcn` | Comutador de áudio analógico USB-C presente |
| RPC | `fastrpc` | Canal para ADSP/CDSP (sensores) |

---

## 5. Erros efetivamente registrados no boot

Única família de erros de kernel encontrada em `journalctl -b -p err`:

```
wcd937x_codec audio-codec: ASoC error (-16): at soc_component_read_no_lock()
                           on audio-codec for register: [0x00003125]   (x12)
wcd937x_codec audio-codec: wcd_measure_adc_once: adc complete: 0, adc timeout: 1   (x2)
wcd937x_codec audio-codec: Impedance detect ramp error, c1=0, x1=0x0   (x4)
```

**Interpretação:** `-16` é `EBUSY`. O codec WCD9375 falha na rotina de detecção de impedância do
conector de headset durante a inicialização. Conforme orientado, isto **não** é tratado como falha
crítica: o caminho de áudio principal foi validado como funcional (tom audível pelos alto-falantes)
e o microfone captura normalmente. O impacto provável restringe-se à **detecção automática de fones
e ao áudio analógico por USB-C** — coerente com a wiki oficial, que classifica o WCD9375 como
parcial (`P`) e registra "USB-C analog pending".

Erros de espaço de usuário no boot (não de kernel):

- `pulseaudio: Daemon already running` (×3) e `pipewire-pulse.socket: refusing` — ver **A-02**.
- `Failed to start Stevia, a user friendly on screen keyboard` (×6) — o teclado virtual falhou
  repetidamente, mas acabou subindo (PID 3731 ativo). Consequência plausível de **A-01**: sem
  touchscreen, o teclado na tela não tem como operar normalmente.
- `gkr-pam: unable to locate daemon control file` — benigno, do GNOME Keyring.

**Não foram encontrados:** probe failures, `-517` (deferred probe), firmware ausente, timeouts de
I/O, erros de UFS ou incompatibilidades de device tree.

---

## 6. O caso do touchscreen (detalhe técnico)

| Fato | Valor |
|---|---|
| Driver | `goodix-berlin-spi` |
| Barramento | SPI — `spi13.0` em `/soc@0/ac0000.geniqup/a94000.spi` |
| Modalias | `spi:gt9916` |
| Vinculação | Efetivada (`/sys/bus/spi/drivers/goodix-berlin-spi/spi13.0`) |
| Registro de entrada | `input3`, às 21:43:29, **sem mensagem de erro** |
| Capacidades | `PROP=2` (direct), `EV=b`, `KEY=400`, `ABS=261800000000003` (slots multitouch) |
| IRQ | 170 — `msmgpio 81 Level` |
| Contagem | **1346, imóvel** ao longo de 30 s de toque físico contínuo |
| `spurious` / `unhandled` | 0 / 0 |

O driver está corretamente vinculado e o dispositivo de entrada foi criado com as capacidades
esperadas. O tipo de interrupção (`Level`) corresponde ao que o binding upstream do GT9916
especifica (`IRQ_TYPE_LEVEL_LOW`), portanto **não há erro de configuração de borda/nível**.

A conclusão é que o controlador **não gera interrupções em operação**, apesar de responder durante o
probe. A hipótese mais provável é a de firmware/configuração do painel não aplicada, deixando o chip
em modo bootloader. O diagnóstico completo, com hipóteses ordenadas e plano de verificação, está em
[`remediation-plan.md` § A-01](remediation-plan.md).

---

## 7. Linha de comando do kernel (sanitizada)

```
quiet splash plymouth.ignore-serial-consoles plymouth.prefer-fbcon
pmos_boot_uuid=<REDIGIDO> pmos_root_uuid=<REDIGIDO> pmos_rootfsopts=defaults
androidboot.verifiedbootstate=orange androidboot.vbmeta.device_state=unlocked
androidboot.veritymode=enforcing androidboot.bootdevice=1d84000.ufshc
androidboot.device=dubai androidboot.hardware.sku=XT2203-1
androidboot.bootloader=MBM-3.0-dubai_g-... androidboot.slot_suffix=_b
msm_drm.dsi_display0=qcom,mdss_dsi_mot_csot_nt37701_655_1080x2400_dsc_cmd_v1
rootwait ro init=/init androidboot.force_normal_boot=1
```

Três leituras relevantes:

1. `verifiedbootstate=orange` + `vbmeta.device_state=unlocked` confirmam o **bootloader
   destravado** — isto eleva E11 de `RECONSTRUÍDO` para `CONFIRMADO`.
2. O painel declarado é **CSOT NT37701**, coerente com o pacote `device-motorola-dubai-kernel-csot`
   instalado. A variante de painel, portanto, **está correta** e não explica A-01 isoladamente.
3. `slot_suffix=_b` indica inicialização pelo slot B do esquema A/B.
