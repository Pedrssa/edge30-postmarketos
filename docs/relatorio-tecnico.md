# Relatório Técnico — Motorola Edge 30 com postmarketOS (`dubai`)

> **Classificação das afirmações.** Ao longo deste relatório cada informação é marcada:
> **[CONFIRMADO]** evidência local ou de transcrição que eu mesmo verifiquei ·
> **[RELATADO]** afirmado em anotações/prompts do projeto, ainda não verificado de forma independente ·
> **[RECONSTRUÍDO]** procedimento inferido do fluxo-padrão + artefatos, sem log de execução capturado ·
> **[AUSENTE]** não há evidência · **[EXTERNO]** documentação de terceiros (não é prova sobre o nosso aparelho).

---

## 1. Resumo executivo

Transformamos um **Motorola Edge 30** (`XT2203-1`, codinome `dubai`) de Android de fábrica
para **Linux ARM64 nativo** rodando **postmarketOS** (projeto rebatizado **Nura** em setembro de 2026),
com interface **Phosh** sobre Wayland.

As imagens do sistema (`boot.img`, `dtbo.img` e o rootfs `motorola-dubai.img`) foram **geradas
localmente com `pmbootstrap`** dentro de uma VM Ubuntu e existem no computador, com hashes SHA-256
registrados. **[CONFIRMADO]**

Ao final, o aparelho **inicializou em Linux, com interface gráfica, Wi-Fi e acesso SSH ativos** —
evidenciado por sessões em que o celular respondeu por SSH sobre Wi-Fi (`user@172.70.8.137`, prompt
`motorola-dubai:~$`) e por uma captura da UI Phosh enviada do próprio aparelho. **[CONFIRMADO]**

Componentes como **áudio, modem/chamadas/SMS, dados móveis, aceleração de GPU, câmera, Bluetooth,
NFC e sensores NÃO foram verificados** neste trabalho e não são declarados como funcionais. **[AUSENTE]**

---

## 2. Objetivo e escopo

**Objetivo.** Substituir o Android por um sistema Linux desktop-like no Edge 30, utilizável como
estação portátil de engenharia/redes, mantendo a possibilidade de rollback.

**No escopo deste relatório.** Reconstruir, a partir das evidências, o *como* do port: aparelho,
ambiente de build, artefatos, fluxo de gravação, o que ficou comprovadamente de pé e o que não foi testado.

**Fora do escopo.** As camadas construídas *em cima* do sistema (laboratórios "NETOPS/CYBERLAB/BLACKBOX")
aparecem apenas como contexto na linha do tempo — não são o foco e não tiveram suas funções de rede validadas aqui.

---

## 3. Dispositivo e ambiente

### 3.1 Aparelho **[CONFIRMADO / RELATADO]**

| Item | Valor | Grau |
|---|---|---|
| Modelo | Motorola Edge 30 | CONFIRMADO (codinome `dubai` = Edge 30 nas wikis pmOS/LineageOS) |
| Variante | `XT2203-1` | RELATADO (prompts do projeto) |
| Codinome | `dubai` | CONFIRMADO (rootfs `motorola-dubai.img`; hostname `motorola-dubai`) |
| SoC | Qualcomm Snapdragon 778G+ 5G (SM7325, família SC7280) | EXTERNO (specs do aparelho + pacote de kernel pmOS `…-sc7280`) |
| Arquitetura | ARM64 / aarch64 | CONFIRMADO (prompt + natureza do rootfs) |

### 3.2 Sistema no aparelho

| Item | Valor | Grau |
|---|---|---|
| Distribuição | postmarketOS / **Nura**, canal *edge* (base Alpine Linux) | CONFIRMADO (artefatos pmbootstrap; prompts; `apk`) |
| Interface | Phosh 0.58.0 / Phoc 0.58.0, Wayland, touchscreen | RELATADO (prompt); UI CONFIRMADA por captura |
| Kernel | 7.2.9, linha *mainline* `sc7280` (não o kernel de fábrica) | RELATADO ("confirmar novamente"); família de pacote EXTERNO |
| Gerenciador de pacotes | `apk` | CONFIRMADO (scripts e testes) |

### 3.3 Ambiente de build **[CONFIRMADO]**

| Item | Valor |
|---|---|
| Host de build | VM VirtualBox `postmarketOS-Build`, `Ubuntu25_64`, 4 GB RAM, disco VDI |
| Ferramenta | `pmbootstrap` (toolchain oficial do postmarketOS) |
| Host físico | Windows 11, com `adb`/`fastboot` (platform-tools) para a gravação |

> Evidência: `C:\Users\Phmmp\VirtualBox VMs\postmarketOS-Build\postmarketOS-Build.vbox`
> (`OSType="Ubuntu25_64"`, `RAMSize="4096"`) e logs de 2026-11-04.

---

## 4. Materiais e ferramentas

- **`pmbootstrap`** — monta o rootfs e o kernel do postmarketOS para o `dubai`. **[CONFIRMADO: artefatos]**
- **Android platform-tools** (`adb`, `fastboot`, v37.0.1) — reinício em bootloader e gravação de partições. **[CONFIRMADO: presença/uso em projetos correlatos]**
- **Imagens geradas** — `boot.img`, `dtbo.img`, `motorola-dubai.img` + `SHA256SUMS`. **[CONFIRMADO]**

### 4.1 Artefatos e integridade **[CONFIRMADO]**

| Arquivo | Tamanho | Partição alvo | SHA-256 |
|---|---|---|---|
| `boot.img` | 28.549.120 B (27,2 MiB) | `boot` | `d101233411355fa33cec8d27eff6b1e9d8900842ae6569ea7678960a41fa23b7` |
| `dtbo.img` | 25.165.824 B (24,0 MiB) | `dtbo` | `95aeaae03b56c171cf88753c821630a3c24f1fcf406cec3e17d56781aa3f8369` |
| `motorola-dubai.img` | 2.189.179.340 B (2,04 GiB) | `userdata` (rootfs) | `874374ceb107745eca7c0d97b6d1f9f358d3de2df6580eac3cfbe7856eb51b42` |

> `SHA256SUMS` original datado de **2026-11-04**; hashes reconferidos em 2026-11-24 e idênticos. As imagens
> **não** são versionadas no Git (tamanho + política do GitHub) — ver `.gitignore` e `docs/pendencias.md`.

---

## 5. Metodologia

1. **Viabilidade.** Confirmar que o `dubai` tem suporte no postmarketOS e que o bootloader é destravável. **[CONFIRMADO: pesquisa]**
2. **Build.** Em VM Linux, usar `pmbootstrap init` (device `motorola-dubai`, UI Phosh) e `pmbootstrap install` para gerar rootfs + kernel. **[RECONSTRUÍDO]**
3. **Destravamento.** Habilitar *OEM unlock*, obter o código no site da Motorola e destravar o bootloader (operação destrutiva). **[RECONSTRUÍDO para o `dubai`]**
4. **Gravação.** Com o aparelho em `fastboot`, gravar `boot`, `dtbo` e o rootfs (`userdata`). **[RECONSTRUÍDO]**
5. **Primeiro boot e verificação.** Subir o Phosh, conectar Wi-Fi, habilitar SSH e validar acesso remoto. **[CONFIRMADO: resultado]**
6. **Rollback.** Guardar a firmware de fábrica para retorno ao Android. **[RELATADO]**

> **Honestidade de evidência.** Não há, nas transcrições capturadas, o log exato da gravação por
> `fastboot`/`pmbootstrap flasher` **deste** aparelho — o passo foi feito fora do assistente, muito
> provavelmente na VM. Por isso os passos 2–4 são **[RECONSTRUÍDO]** a partir do fluxo oficial do
> pmbootstrap e dos artefatos presentes, não de um registro de execução.

---

## 6. Arquitetura e fluxo de inicialização

```
   [ VM Ubuntu + pmbootstrap ]                 [ Motorola Edge 30 "dubai" ]
            │                                            │
   pmbootstrap init  ───────────┐                        │
   pmbootstrap install          │  gera                  │
            │                    ▼                        │
     boot.img (kernel+initramfs) ─┐                       │
     dtbo.img (device-tree overlay)│   fastboot flash     ▼
     motorola-dubai.img (rootfs) ──┼────────────────►  partições boot / dtbo / userdata
            │                      │                      │
   SHA256SUMS (integridade)  ◄─────┘                 primeiro boot
                                                          │
                                            kernel sc7280-mainline
                                                          │
                                              initramfs → rootfs (Alpine)
                                                          │
                                               Phosh / Wayland (GUI)
                                                          │
                                        Wi-Fi (wlan0) + sshd  →  acesso SSH
```

O `dtbo.img` (*device-tree overlay*) é necessário em aparelhos cujo boot depende de overlays de
árvore de dispositivo; sem ele o sistema pode não inicializar. **[EXTERNO: docs pmbootstrap]**

---

## 7. Etapas efetivamente realizadas (com grau)

| # | Etapa | Grau | Base da evidência |
|---|---|---|---|
| 1 | Pesquisa de viabilidade (device suportado, bootloader destravável) | CONFIRMADO | Sessões 2026-10-26 |
| 2 | Build do rootfs/kernel com pmbootstrap em VM | CONFIRMADO (resultado) / RECONSTRUÍDO (comandos) | VM + imagens datadas 2026-11-04 |
| 3 | Destravamento do bootloader do `dubai` | RECONSTRUÍDO | Aparelho aceita imagens custom ⇒ destravado; passos não capturados |
| 4 | Gravação das partições por fastboot | RECONSTRUÍDO | Imagens existem; sem log de flash capturado |
| 5 | Primeiro boot em Linux + Phosh | CONFIRMADO | Captura da UI enviada do aparelho |
| 6 | Wi-Fi + SSH ativos | CONFIRMADO | SSH sobre Wi-Fi; prompt `motorola-dubai:~$` |
| 7 | Camadas de rede por cima (pacotes `.netops-lab`, parsers) | CONFIRMADO (instalação) | Scripts locais + sessão 2026-11-04 |

---

## 8. Comandos e configurações relevantes

> **Comprovadamente usados** no projeto (capturados):

```sh
# Conferência de integridade das imagens (feita neste repositório)
sha256sum -c SHA256SUMS

# Acesso ao aparelho já em Linux, por SSH sobre Wi-Fi
ssh user@<ip-do-aparelho>          # ex. observado: 172.70.8.137 / 192.168.137.8

# Camada de rede instalada como pacote virtual removível (sessão 2026-11-04)
apk add -s -t .netops-lab tshark iw mtr iperf3 nmap bind-tools curl   # -s = simulação primeiro
```

> **Recomendados / reconstruídos** (fluxo oficial pmbootstrap — confirmar na wiki do device antes de usar):

```sh
# Na VM de build
pmbootstrap init                    # escolher device 'motorola-dubai' e UI 'phosh'
pmbootstrap install                 # gera rootfs + kernel

# Com o aparelho em fastboot (bootloader destravado)
pmbootstrap flasher flash_kernel    # grava boot.img
pmbootstrap flasher flash_dtbo      # grava dtbo.img (quando o device usa overlay)
pmbootstrap flasher flash_rootfs    # grava o rootfs no userdata (padrão desde pmbootstrap 2.0)
```

⚠️ A gravação e o destravamento **apagam o aparelho**. Os nomes/alvos de partição variam por device;
confira a página do `motorola-dubai` antes de executar. **[EXTERNO]**

---

## 9. Problemas encontrados e evidências

| Problema | Evidência | Status |
|---|---|---|
| `dubai` é categoria *testing* no pmOS, **sem imagem pronta** → precisávamos **buildar** | Wiki pmOS (busca) | Contornado pelo build local |
| Kernel `sc7280-mainline` com relatos de **baixa responsividade** | Wiki pmOS (busca) | Risco conhecido; impacto no nosso aparelho **não medido** [AUSENTE] |
| Shell do Windows não processou um bloco grande → nada foi enviado numa etapa | Sessão 2026-11-04 | Resolvido enviando a árvore por script de upload/SFTP |
| Codificação: `UnicodeEncodeError` (`cp1252`) ao gerar texto com sinais `−` | Sessão 2026-11-04 | Resolvido forçando UTF-8 |
| Reconexão posterior falhou (IP mudou de rede) | Sessão 2026-11-18 | Resolvido obtendo o IP atual no próprio aparelho |

---

## 10. Resultados

- **[CONFIRMADO]** O aparelho **inicializa em postmarketOS** com **GUI Phosh**.
- **[CONFIRMADO]** **Wi-Fi** sobe (`wlan0`) e o **SSH** funciona — base para trabalho remoto.
- **[CONFIRMADO]** `apk` opera e pacotes de rede foram instalados/revertidos com rollback idêntico ao backup.
- **[CONFIRMADO]** Integridade das imagens reproduzível por SHA-256.

---

## 11. Limitações

- **Não verificados:** áudio, modem/chamadas/SMS, dados móveis, GPU, câmera, Bluetooth, NFC, sensores, bateria/carga. **[AUSENTE]**
- **Sem log de gravação capturado** para o `dubai` — passos de build/flash são **[RECONSTRUÍDO]**.
- **Versão de kernel (7.2.9)** é **[RELATADO]**, não reconfirmada por leitura direta nesta entrega.
- **Matriz oficial do device** não pôde ser lida: a wiki (`wiki.nura.eco`) está atrás de proteção anti-bot (Anubis). **[EXTERNO/bloqueado]**

---

## 12. Riscos e cuidados

- Destravar o bootloader e gravar partições é **destrutivo e perde a garantia**.
- Operar as ferramentas de rede montadas por cima é restrito a **redes próprias ou autorizadas**.
- Guardar a firmware de fábrica é o que viabiliza o **retorno ao Android**.

---

## 13. Conclusão e próximos passos

O port é **real e funcional no essencial** (boot, GUI, Wi-Fi, SSH). O que falta é **medir o aparelho**:
levantar a matriz de funcionalidades diretamente no device (`uname -a`, estado de áudio/modem/BT/sensores),
capturar o log de uma regravação limpa e confirmar a versão de kernel. Ver `docs/pendencias.md`.

---

## 14. Referências

- postmarketOS — página do dispositivo *Motorola Edge 30 (motorola-dubai)*. Acesso em 2026-11-24 (redireciona para `wiki.nura.eco`; conteúdo atrás de proteção anti-bot). <https://wiki.postmarketos.org/wiki/Motorola_Edge_30_(motorola-dubai)>
- postmarketOS — *Installation using pmbootstrap*. Acesso em 2026-11-24. <https://wiki.postmarketos.org/wiki/Installation/Using_pmbootstrap>
- pmbootstrap — *Usage* (flasher: `flash_kernel`, `flash_rootfs`, `flash_dtbo`; padrão `userdata` desde 2.0). Acesso em 2026-11-24. <https://docs.postmarketos.org/pmbootstrap/usage.html>
- LKML — *[PATCH] arm64: dts: qcom: Add Motorola edge 30 (dubai) DTS* (março/2026; display via `simplefb`). Acesso em 2026-11-24. <https://lkml.iu.edu/hypermail/linux/kernel/2603.3/10844.html>
- Linuxiac — *postmarketOS Is Now Nura After Major Project Rebrand* (set/2026; domínio `nura.eco`). Acesso em 2026-11-24. <https://linuxiac.com/postmarketos-is-now-nura-after-major-project-rebrand/>
- LineageOS — *Devices: dubai* (confirma `dubai` = Motorola Edge 30). Acesso em 2026-11-24. <https://wiki.lineageos.org/devices/dubai/>

---

<sub>Relatório reconstruído a partir de artefatos locais e transcrições de sessão. Fatos, hipóteses e lacunas marcados explicitamente conforme a legenda do topo.</sub>
