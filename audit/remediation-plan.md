# Plano de correção

> **Nada deste plano foi aplicado ao aparelho.** Diagnóstico, proposta e execução estão
> deliberadamente separados. Cada item exige autorização explícita, verificação de compatibilidade e
> plano de recuperação antes de qualquer execução.

Gravidade: **CRÍTICO** (impede o uso) · **ALTO** (compromete função central) · **MÉDIO** (degrada
experiência) · **BAIXO** (endurecimento desejável).

---

## A-01 · ~~Touchscreen não emite eventos~~ — ✅ FALSO POSITIVO (corrigido em 24/11/2026)

> **Este problema não existe.** O touchscreen **funciona**.
>
> **Teste definitivo:** leitura direta de `/dev/input/event3` com janela de 45 segundos, executada
> com root. Resultado: **6942 eventos capturados** e **delta de +2224 interrupções** na IRQ 170. Os
> bytes decodificam como eventos multitouch legítimos:
>
> ```
> 03 00 39 00 53 00 00 00   → EV_ABS  ABS_MT_TRACKING_ID = 0x53
> 03 00 35 00 9e 01 00 00   → EV_ABS  ABS_MT_POSITION_X  = 414
> 03 00 36 00 c4 05 00 00   → EV_ABS  ABS_MT_POSITION_Y  = 1476
> ```
>
> **Causa do erro:** sincronização entre a janela de medição e a ação física. Os testes anteriores
> observavam a contagem de IRQ por 15–30 segundos enquanto pediam o toque, mas o operador estava
> lendo a instrução no computador em vez de tocar a tela naquele intervalo exato. **Ausência de
> estímulo foi interpretada como falha de hardware.**
>
> **Sinal ignorado:** a contagem da IRQ cresceu de forma contínua entre as medições
> (1346 → 1540 → 3686 → 6395 → 8619). Esse crescimento foi registrado como "anomalia sem
> explicação" quando deveria ter refutado a hipótese de falha.
>
> **Lição de método:** medir uma janela estreita e concluir a partir da ausência de evento exige
> confirmar que o estímulo ocorreu *dentro* da janela. A leitura direta do event node, com janela
> ampla, é o teste correto — a contagem de interrupção é apenas um indicador indireto.
>
> O aviso de pinctrl (`not freeing pin 105 (GPIO_105)`) observado na recarga do driver é **benigno**
> e não tem relação com funcionalidade.

---

## A-02 · PulseAudio e PipeWire em execução simultânea — ALTO

| Campo | Conteúdo |
|---|---|
| **Subsistema** | Áudio / ALSA + servidores de som |
| **Evidência** | `pulseaudio` (PID 3445), `pipewire` (5231) e `wireplumber` (5232) ativos ao mesmo tempo. Pacotes `postmarketos-base-ui-audio-backend-pulseaudio`, `soc-qcom-pulseaudio` **e** `pipewire`/`wireplumber` instalados. Log: `pipewire-pulse.socket: Socket service pipewire-pulse.service not loaded, refusing` e `pulseaudio: Daemon already running` (3 ocorrências no boot). |
| **Diagnóstico** | Dois servidores de áudio disputam o mesmo dispositivo ALSA. O PulseAudio venceu a disputa — o sink funciona —, mas a configuração é instável e contraria o provider oficial. |
| **Causa provável** | Instalação feita com provider `pulseaudio` enquanto algum pacote de UI arrastou PipeWire como dependência, ou troca de provider sem remoção do anterior. |
| **Impacto real** | Áudio de mídia funciona (validado). O risco recai sobre **chamadas telefônicas**: a wiki oficial exige explicitamente `pipewire` no `pmbootstrap init` "to have working phone calls". A configuração atual tende a quebrar roteamento de chamada, troca para viva-voz e áudio por Bluetooth. |
| **Correção recomendada** | Escolher **um** backend. Para alinhar ao oficial: migrar para PipeWire removendo `postmarketos-base-ui-audio-backend-pulseaudio` e `soc-qcom-pulseaudio`, instalando o equivalente PipeWire e habilitando `pipewire-pulse.socket`. Alternativa conservadora: manter PulseAudio e **desabilitar** as units de usuário do PipeWire. |
| **Dependências** | Root. Decisão prévia sobre a prioridade de telefonia. |
| **Risco da correção** | **Médio-alto.** Trocar o backend pode deixar o aparelho sem áudio algum até a reconfiguração do UCM. Executar com o aparelho acessível fisicamente. |
| **Rollback** | Registrar `apk info -v | grep -E 'pipewire|pulseaudio' > audio-baseline.txt` antes; reinstalar o conjunto anterior e reiniciar. |
| **Critério de aceite** | Apenas um servidor de áudio em execução; `wpctl status` (ou `pactl info`) responde sem erro; tom de teste audível; nenhuma mensagem de recusa de socket no boot. |
| **Validação** | Reiniciar, conferir `pgrep -a pulseaudio pipewire`, repetir o `speaker-test` de 440 Hz. |

---

## A-03 · Armazenamento sem criptografia com bootloader destravado — ALTO

| Campo | Conteúdo |
|---|---|
| **Subsistema** | Segurança / integridade de dados |
| **Evidência** | `lsblk` não revela nenhum mapeamento LUKS. Linha de comando do kernel: `androidboot.verifiedbootstate=orange`, `vbmeta.device_state=unlocked`. A wiki declara `FDE: Works` para este device. |
| **Diagnóstico** | O rootfs (227 GB em `loop0p2` sobre `sde27`) está em texto claro. Com o bootloader destravado, qualquer pessoa com acesso físico pode inicializar um sistema externo e ler tudo. |
| **Causa provável** | Instalação realizada sem habilitar *full disk encryption*. |
| **Impacto real** | Perda ou furto do aparelho expõe integralmente chaves SSH, credenciais, histórico e dados pessoais. É o risco de segurança mais concreto do conjunto. |
| **Correção recomendada** | Não há como cifrar in-place. Exige **reinstalação** com FDE habilitado no `pmbootstrap init`. Mitigação imediata sem reinstalar: remover segredos de alto valor do aparelho e reduzir a superfície (ver A-07). |
| **Dependências** | Backup completo; aparelho fisicamente presente; cabo USB; host com `pmbootstrap`. |
| **Risco da correção** | **Alto — destrutivo.** Apaga todo o conteúdo. |
| **Rollback** | Apenas por backup prévio. Preservar `boot.img`, `dtbo.img` e o rootfs atual com `sha256sum` conferido antes de qualquer gravação. |
| **Critério de aceite** | `lsblk` exibe mapeamento `crypt` e o boot solicita a senha de desbloqueio. |
| **Validação** | Reiniciar e confirmar o prompt de desbloqueio. |

---

## A-04 · Suspensão nunca exercida e consumo ocioso elevado — MÉDIO

| Campo | Conteúdo |
|---|---|
| **Subsistema** | Gerenciamento de energia |
| **Evidência** | `/sys/power/suspend_stats/success = 0` e `fail = 0`. `/sys/power/state` oferece `freeze mem`; `mem_sleep = s2idle [deep]`. Consumo medido em repouso: **−225 mA a 3,958 V ≈ 0,89 W**, estável ao longo de 20 amostras em 8 minutos, temperatura constante em 33,0 °C. |
| **Diagnóstico** | O aparelho nunca entrou em suspensão desde o boot. O consumo observado é compatível com um sistema sempre acordado. |
| **Causa provável** | ⚠️ **Refinado com root.** A leitura de `/sys/kernel/debug/wakeup_sources` mostra **`prevent_suspend_time = 0` em todas as fontes** — nada está impedindo a suspensão. O aparelho não suspende porque **nada solicita a suspensão**, e não porque algo a bloqueie. A investigação deve mirar a política de ociosidade (`systemd-logind`, `tuned`, configuração do Phosh). Quanto ao consumo em si, a wiki atribui mais da metade aos motores de foco da câmera sempre ligados, com **correção já integrada no kernel near-to-mainline** — coerente com `ak7375` e `wl2864c` carregados. |
| **Impacto real** | Autonomia reduzida. **Não é possível quantificar o impacto a partir desta medição** — 8 minutos em repouso não sustentam estimativa de autonomia. |
| **Correção recomendada** | Aguardar o release do kernel com a correção upstream e atualizar. Enquanto isso, testar a suspensão manualmente **com o aparelho em mãos**, usando `rtcwake` para garantir o despertar automático. |
| **Dependências** | Root. Aparelho fisicamente acessível. |
| **Risco da correção** | **Médio.** A suspensão pode derrubar o Wi-Fi e encerrar o único canal de acesso; pode também não retornar, exigindo reinício pelo botão físico. |
| **Rollback** | Pressionar o botão de power; em último caso, desligamento forçado. |
| **Critério de aceite** | `suspend_stats/success` incrementa, o aparelho retorna com a rede operante e o consumo em suspensão cai de forma mensurável. |
| **Validação** | Medir `current_now` antes, durante e depois de um ciclo de suspensão. |

---

## A-05 · Bluetooth bloqueado por rfkill — ✅ RESOLVIDO (24/11/2026)

> **Executado e validado.** Com acesso root, `rfkill unblock bluetooth` seguido de
> `hciconfig hci0 up` levou o controlador a `UP RUNNING PSCAN`. O `dmesg` confirma a carga completa
> do firmware QCA (`msbtfw11.mbn`, `msnv11.bin`, `BTFW.MOSELLE.1.1.3`) e `QCA setup on UART is
> completed`. Reclassificado para **FUNCIONAL**.
>
> **Pendências menores:** tornar o desbloqueio persistente entre reinicializações; investigar o
> `BD Address` placeholder (`02:00:xx`); testar um pareamento real. Ver
> [`root-findings.md` §2](root-findings.md).

### Registro original do diagnóstico

| Campo | Conteúdo |
|---|---|
| **Subsistema** | Conectividade / `btqca` em `hci0` (UART) |
| **Evidência** | `rfkill`: `Soft blocked: yes`, `Hard blocked: no`. `bluetoothctl show`: `Powered: no`, `PowerState: off-blocked`. `hciconfig`: `DOWN`, porém **1781 comandos HCI trocados com 0 erros**, o que indica que o transporte e o firmware estão operantes. `bluetoothctl power on` falhou com `org.bluez.Error.Failed`; descoberta falhou com `NotReady`. Observação adicional: o `BD Address` é `02:00:xx` (placeholder), e não o endereço fornecido pelo bootloader — sinal de que o MAC real não foi aplicado. |
| **Diagnóstico** | O hardware responde; o bloqueio é de software (`rfkill`), não de rádio. |
| **Causa provável** | Bloqueio persistido entre reinicializações, ou falha na aplicação do MAC do bootloader levando o BlueZ a recusar a ativação. |
| **Impacto real** | Bluetooth indisponível. Secundariamente, elimina o caminho mais prático de contornar A-01 por teclado/mouse sem fio. |
| **Correção recomendada** | `sudo rfkill unblock bluetooth` e, em seguida, `bluetoothctl power on`. Se persistir, investigar a aplicação do MAC (`btmgmt public-addr`) e revisar o `pwrseq_qcom_wcn`. |
| **Dependências** | Root. |
| **Risco da correção** | **Baixo** e plenamente reversível. |
| **Rollback** | `sudo rfkill block bluetooth`. |
| **Critério de aceite** | `hci0` em `UP RUNNING`, `Powered: yes` e varredura retornando ao menos um dispositivo próximo. |
| **Validação** | `bluetoothctl scan on` por 15 s com um dispositivo conhecido ao alcance. |

---

## A-06 · Power save do Wi-Fi degradando a estabilidade — MÉDIO

| Campo | Conteúdo |
|---|---|
| **Subsistema** | Rede / WCN6750 |
| **Evidência** | `iw dev wlan0 get power_save` → `Power save: on`. Primeira medição: 20 pacotes, 0% de perda, média 70 ms, **pico 125 ms** contra mínimo de 4 ms. Segunda medição: **33% de perda**, média 121 ms. Uma sessão SSH caiu por timeout; o `uptime` posterior (31 min) confirma que **não houve reboot** — foi perda de enlace. |
| **Diagnóstico** | O modo de economia do rádio introduz latência e descarte de pacotes. A variação de 4 ms a 125 ms é assinatura típica desse comportamento, não de congestionamento. |
| **Causa provável** | `power_save` habilitado por padrão. ⚠️ **Hipótese adicional descoberta com root:** o `ath11k` registra `qmi failed to download BDF:-2`, `failed to load board data file: -2` e `board_id 0xff` — o rádio opera **sem os dados de calibração específicos da placa**, com parâmetros genéricos. Isso pode contribuir tanto quanto o `power_save` para a instabilidade observada, e não consta da matriz oficial da wiki. |
| **Impacto real** | Sessões SSH instáveis e jitter alto. Relevante porque o SSH é, hoje, o **único** meio de operar o aparelho (ver A-01). |
| **Correção recomendada** | `sudo iw dev wlan0 set power_save off` para diagnóstico. Para persistir, configurar `wifi.powersave=2` no NetworkManager. **Contrapartida explícita:** aumenta o consumo em repouso, agravando A-04. Recomenda-se desligar apenas enquanto o touchscreen estiver inoperante. |
| **Dependências** | Root. |
| **Risco da correção** | **Baixo**, reversível, com custo energético conhecido. |
| **Rollback** | `sudo iw dev wlan0 set power_save on`. |
| **Critério de aceite** | 100 pings com perda 0% e desvio padrão da latência abaixo de 20 ms. |
| **Validação** | Comparar 100 pings antes e depois, registrando também `current_now` para medir o custo energético. |

---

## A-07 · Endurecimento do kernel e da superfície de rede — BAIXO

| Campo | Conteúdo |
|---|---|
| **Subsistema** | Segurança |
| **Evidência** | `kptr_restrict=0` (ponteiros de kernel expostos). LSM ativos: `lockdown,capability,yama,bpf` — **sem SELinux ou AppArmor**. `nft` instalado mas o conjunto de regras não pôde ser lido sem root. Portas em escuta: 22 (SSH), 5353 (mDNS/Avahi), 5355 (LLMNR), 67 (DHCP em `usb0`), 53 (resolved, apenas loopback). Pontos positivos já presentes: `randomize_va_space=2`, `dmesg_restrict=1`, `unprivileged_bpf_disabled=1`, login direto de root por SSH negado, repositórios com chaves Alpine e `build.postmarketos.org` instaladas, `/etc/shadow` inacessível a usuário comum. |
| **Diagnóstico** | Postura razoável para um aparelho de desenvolvimento, com arestas desnecessárias. |
| **Causa provável** | Padrões de distribuição. |
| **Impacto real** | Baixo na rede doméstica atual. `kptr_restrict=0` facilita a exploração de uma eventual falha de kernel; 5353/5355 expõem o nome do host na LAN. |
| **Correção recomendada** | Definir `kernel.kptr_restrict=2` via `sysctl.d`; desabilitar LLMNR no `systemd-resolved`; restringir o Avahi se a descoberta mDNS não for necessária; confirmar e documentar as regras `nft` com root. |
| **Dependências** | Root. |
| **Risco da correção** | **Baixo.** Desligar mDNS pode quebrar a descoberta do aparelho por nome na rede — manter o acesso por IP garantido antes. |
| **Rollback** | Remover os arquivos de `sysctl.d` e reabilitar os serviços. |
| **Critério de aceite** | `cat /proc/sys/kernel/kptr_restrict` retorna 2 e `ss -tulnp` não lista 5355. |
| **Validação** | Reexecutar a seção de segurança do `scripts/collect-diagnostics.sh` e comparar com a linha de base desta auditoria. |

---

## Ordem de execução sugerida

1. **A-05** e **A-06** — risco baixo, reversíveis, e ambos ampliam a capacidade de diagnosticar o resto.
2. **A-01** — é o bloqueio central; atacar após garantir Bluetooth (teclado sem fio como contingência).
3. **A-02** — exige decisão de arquitetura sobre o backend de áudio.
4. **A-07** — endurecimento, sem urgência.
5. **A-04** — depende majoritariamente de um release upstream.
6. **A-03** — por último, por ser destrutivo e exigir reinstalação planejada com backup validado.
