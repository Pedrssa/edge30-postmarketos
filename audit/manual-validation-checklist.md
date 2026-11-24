# Checklist de validação manual

Itens que **não podem ser validados por SSH** e exigem o aparelho em mãos, acesso root ou um SIM
inserido. Cada item traz o procedimento, o resultado esperado e onde registrar.

Marque: `[x]` aprovado · `[!]` falhou · `[-]` não executado

---

## A. Requer apenas o aparelho em mãos

### A1 · Rotação automática de tela (acelerômetro)
- [ ] Abrir qualquer aplicativo no Phosh e **girar o aparelho 90°**.
- **Esperado:** a interface rotaciona para paisagem.
- **Por que importa:** resolveria a classificação "detectado, não validado" do acelerômetro. A
  auditoria confirmou `HasAccelerometer=true`, mas a reivindicação por SSH foi negada por polkit.
- **Observação:** se a rotação estiver desativada nas configurações do Phosh, habilitá-la antes.

### A2 · Sensor de proximidade
- [ ] Com uma chamada ou o app de câmera aberto, **cobrir a área superior da tela com a mão**.
- **Esperado:** a tela apaga enquanto coberta.
- **Alternativa:** em Configurações → Sensores, se houver leitura ao vivo.

### A3 · Sensor de luz ambiente
- [ ] Ativar o brilho automático e **cobrir/descobrir o sensor** alternando entre ambiente escuro e
      claro.
- **Esperado:** o backlight varia. Verificável também por `cat /sys/class/backlight/ae94000.dsi.0/brightness`.

### A4 · Flash da câmera
- [ ] Abrir o app de câmera e **acionar a lanterna**.
- **Esperado:** os dois LEDs brancos acendem (`white:flash` e `white:flash_1`).

### A5 · Captura de imagem
- [ ] Abrir o app de câmera e tentar **tirar uma foto com a câmera traseira**.
- **Esperado:** incerto. A wiki classifica a câmera como `Partial`; o sensor principal (OV50A) não
  tem driver, mas o ultrawide (S5KJN1) e o de profundidade (GC02M1B) têm.
- **Registrar:** qual câmera aparece no app e se a imagem é gerada.

### A6 · Carregamento
- [ ] **Conectar o carregador USB-C** e aguardar 1 minuto.
- **Verificar por SSH:**
  ```sh
  cat /sys/class/power_supply/qcom-battmgr-bat/status        # esperado: Charging
  cat /sys/class/power_supply/qcom-battmgr-usb/online        # esperado: 1
  cat /sys/class/power_supply/qcom-battmgr-bat/current_now   # esperado: valor POSITIVO
  cat /sys/class/power_supply/ucsi-source-psy-*/usb_type     # negociação PD
  ```

### A7 · USB OTG / modo host
- [ ] Conectar um pendrive por adaptador USB-C OTG.
- **Esperado:** aparece em `lsblk`. A auditoria encontrou `udc` em `not attached`.

### A8 · Teclado USB como contorno do A-01
- [ ] Conectar um teclado USB-C e verificar se aparece em `/proc/bus/input/devices`.
- **Por que importa:** confirmaria se o aparelho é operável localmente apesar do touchscreen.

---

## B. Requer acesso root

> Execute `su -` ou `sudo -i` **no próprio aparelho** (o `sudo` exige senha interativa, que não
> funciona em sessão SSH não interativa).

### B1 · `dmesg` completo — prioridade máxima
- [ ] ```sh
      dmesg | grep -iE 'goodix|berlin|spi13|firmware|-517|defer' > /tmp/goodix.log
      ```
- **Por que importa:** é a informação que falta para fechar o diagnóstico de **A-01**. Procurar por
  `request_firmware`, falha de carregamento de configuração do painel ou timeout de reset.

### B2 · Recarregar o driver do touchscreen
- [ ] ```sh
      grep goodix /proc/interrupts                 # anotar o contador
      rmmod goodix_berlin_spi && modprobe goodix_berlin_spi
      sleep 3
      grep goodix /proc/interrupts                 # tocar a tela e comparar
      ```
- **Esperado se corrigir:** o contador passa a incrementar ao toque.
- **Rollback:** reiniciar o aparelho.

### B3 · Eventos de entrada brutos
- [ ] ```sh
      apk add evtest && evtest /dev/input/event3
      ```
- **Esperado:** eventos `ABS_MT_POSITION_X` / `ABS_MT_POSITION_Y` ao tocar.
- **Nota:** instala um pacote — fora do escopo somente-leitura da auditoria, por isso não foi feito.

### B4 · Desbloquear o Bluetooth (A-05)
- [ ] ```sh
      rfkill unblock bluetooth
      bluetoothctl power on
      bluetoothctl scan on        # aguardar 15 s
      ```
- **Esperado:** `hci0` em `UP RUNNING` e dispositivos próximos detectados.
- **Rollback:** `rfkill block bluetooth`.

### B5 · Teste de suspensão (A-04) — ⚠️ com o aparelho em mãos
- [ ] ```sh
      cat /sys/class/power_supply/qcom-battmgr-bat/current_now    # antes
      rtcwake -m mem -s 60                                        # desperta sozinho em 60 s
      cat /sys/power/suspend_stats/success                        # esperado: 1
      ```
- **Risco:** pode derrubar o Wi-Fi e encerrar o SSH. Use `rtcwake` (com despertar automático), nunca
  `echo mem > /sys/power/state` sem temporizador.
- **Rollback:** botão de power.

### B6 · Wakeup sources
- [ ] ```sh
      grep -v '	0	0' /sys/kernel/debug/wakeup_sources
      ```
- **Por que importa:** identifica o que impede o repouso.

### B7 · Firewall e SSH efetivo
- [ ] ```sh
      nft list ruleset
      sshd -T | grep -iE 'permitrootlogin|passwordauthentication|pubkeyauthentication'
      ```
- **Por que importa:** fecha as duas lacunas de [`security-audit.md`](security-audit.md).

### B8 · Desligar o power save do Wi-Fi (A-06)
- [ ] ```sh
      iw dev wlan0 set power_save off
      ```
- **Validar do computador:** `ping -n 100 <ip>` e comparar perda e jitter com a linha de base
  (0–33% de perda, 4–125 ms).
- **Rollback:** `iw dev wlan0 set power_save on`.
- **Contrapartida:** aumenta o consumo ocioso.

---

## C. Requer um chip SIM

### C1 · Inicialização do modem
- [ ] Inserir o SIM, reiniciar e executar `mmcli -m 0`.
- **Esperado:** estado deixa de ser `failed/sim-missing` e passa a `registered`.

### C2 · Chamada de voz
- [ ] Fazer e receber uma chamada.
- **Atenção:** a wiki exige provider `pipewire` para chamadas funcionais, e o aparelho usa
  PulseAudio (**A-02**). Este teste provavelmente **expõe o problema de áudio**.
- **Registrar:** se há áudio nos dois sentidos, e se viva-voz e mudo funcionam (a wiki informa que
  essas funções avançadas **não** funcionam).

### C3 · SMS
- [ ] Enviar e receber uma mensagem.

### C4 · Dados móveis
- [ ] Desligar o Wi-Fi e navegar.
- **Verificar:** `nmcli device status` deve mostrar `qrtr0` como `connected`.

### C5 · GPS
- [ ] Abrir um app de mapas ao ar livre e aguardar o fixo.
- **Nota:** não há dispositivo GNSS dedicado; a localização vem do modem via QMI. O ModemManager
  tentou carregar SUPL e dados de assistência, o que indica a capacidade.

---

## D. Após qualquer correção

- [ ] Reexecutar `sh collect-diagnostics.sh /tmp/diag-pos --sanitize`.
- [ ] Comparar com a linha de base em [`evidence/sanitized/collect-run/`](evidence/sanitized/collect-run/).
- [ ] Atualizar [`hardware-compatibility.csv`](hardware-compatibility.csv) com as novas classificações.
- [ ] Registrar em `docs/evidencias.md` com data e grau de confirmação.
- [ ] Confirmar que nenhuma evidência nova contém IMEI, serial, MAC, IP privado ou chave.
