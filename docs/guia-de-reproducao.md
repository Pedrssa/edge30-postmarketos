# Guia de reprodução

> ⚠️ **Leia primeiro.** Destravar o bootloader e gravar partições **apaga o aparelho** e **invalida a
> garantia**. Este guia separa o que foi **comprovadamente usado** no nosso projeto do que é apenas
> **procedimento recomendado** (fluxo oficial, ainda não validado neste aparelho). Não é um tutorial
> "validado de ponta a ponta" — é uma reconstrução honesta.

## Pré-requisitos

- Um **Motorola Edge 30** (`XT2203-1`, `dubai`) que você possa apagar.
- **PC com Linux** (ou VM) para rodar `pmbootstrap`. No nosso caso: **VM VirtualBox Ubuntu 25, 4 GB RAM**. **[CONFIRMADO]**
- **Android platform-tools** (`adb` + `fastboot`) no host. **[CONFIRMADO]**
- Conta Motorola para obter o **código de desbloqueio** do bootloader.
- Backup da **firmware de fábrica** (rollback). **[RELATADO]**

---

## Parte A — Procedimento recomendado (fluxo oficial) · **[RECONSTRUÍDO]**

> Confirme cada comando na página do `motorola-dubai` antes de executar; alvos de partição variam por device.

### 1. Destravar o bootloader *(destrutivo)*

1. No Android: *Opções do desenvolvedor* → ativar **Desbloqueio de OEM**.
2. Reiniciar em fastboot e obter os dados de desbloqueio:
   ```sh
   adb reboot bootloader
   fastboot oem get_unlock_data
   ```
3. Colar os dados no site oficial da Motorola; o código chega por e-mail.
4. Aplicar o código:
   ```sh
   fastboot oem unlock <CÓDIGO>
   ```

### 2. Build do sistema (na VM Linux)

```sh
pmbootstrap init         # device: motorola-dubai · UI: phosh
pmbootstrap install      # gera o rootfs + kernel (adicione --fde para disco criptografado)
```

### 3. Gravar no aparelho (em fastboot)

```sh
pmbootstrap flasher flash_kernel   # boot.img  -> partição boot
pmbootstrap flasher flash_dtbo     # dtbo.img  -> partição dtbo (device usa overlay)
pmbootstrap flasher flash_rootfs   # rootfs    -> userdata (padrão desde pmbootstrap 2.0)
```

Alternativa manual equivalente:
```sh
fastboot flash boot boot.img
fastboot flash dtbo dtbo.img
fastboot flash userdata motorola-dubai.img
fastboot reboot
```

### 4. Primeiro boot

Deixe inicializar (o primeiro boot é mais lento). Deve subir o **Phosh**. **[CONFIRMADO: resultado]**

---

## Parte B — Comprovadamente usado por nós · **[CONFIRMADO]**

### Conferir integridade das imagens
```sh
sha256sum -c SHA256SUMS
```

### Acessar o aparelho já em Linux (SSH sobre Wi-Fi)
```sh
# Descobrir o IP no próprio aparelho (terminal do celular):
ip -4 addr show wlan0
# Do PC:
ssh user@<ip-do-aparelho>
```

### Camada de rede como pacote virtual removível (simular antes de instalar)
```sh
apk add -s -t .netops-lab tshark iw mtr iperf3 nmap bind-tools curl   # -s = simulação
apk add    -t .netops-lab tshark iw mtr iperf3 nmap bind-tools curl   # instala de fato
apk del .netops-lab                                                    # remove tudo de uma vez
```

> O backup do estado do sistema antes de qualquer mudança está em `edge30-netops-lab/deploy/00-backup.sh`
> (snapshot só-leitura de pacotes, `world`, firewall, serviços e `/etc`, sem segredos).

---

## Recuperação (voltar ao Android)

Restaurar a firmware de fábrica guardada (ex.: *Rescue and Smart Assistant* / *LMSA* da Motorola, ou
`fastboot`/flashfile oficial). **[RELATADO — procedimento não capturado nesta entrega]**

---

## O que este guia **não** garante

- Não há log de execução do flash **deste** aparelho — a Parte A é reconstrução do fluxo-padrão.
- Funcionamento de áudio, modem, dados móveis, GPU, câmera, Bluetooth, NFC, sensores e bateria **não
  foi testado** e não é prometido aqui. **[AUSENTE]**
