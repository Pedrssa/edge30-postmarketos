# Auditoria de segurança

**Escopo:** avaliação **defensiva** do próprio aparelho, com verificações exclusivamente não
destrutivas. Nenhuma vulnerabilidade foi explorada, nenhuma persistência foi instalada e nenhum
teste foi dirigido a outros dispositivos da rede.

**Sanitização:** nenhum IMEI, número de série, endereço MAC, IP privado, chave SSH, senha ou token
é reproduzido neste documento ou nas evidências publicadas.

---

## 1. Postura geral

| Área | Avaliação |
|---|---|
| Proteções de kernel | **Boa**, com uma lacuna |
| Autenticação e acesso | **Boa** |
| Superfície de rede | **Aceitável**, reduzível |
| Cadeia de pacotes | **Boa** |
| Proteção de dados em repouso | **Deficiente** — principal risco |
| Integridade de boot | **Comprometida por decisão de projeto** (bootloader destravado) |

---

## 2. Proteções de kernel

| Controle | Valor | Avaliação |
|---|---|---|
| `randomize_va_space` (ASLR) | **2** | ✅ ASLR completo, incluindo heap |
| `dmesg_restrict` | **1** | ✅ Log de kernel negado a usuário comum |
| `unprivileged_bpf_disabled` | **1** | ✅ BPF não privilegiado desabilitado |
| `kptr_restrict` | **0** | ⚠️ **Ponteiros de kernel expostos** — facilita exploração de falhas de memória |
| LSM ativos | `lockdown,capability,yama,bpf` | ⚠️ Sem SELinux ou AppArmor — nenhum controle de acesso obrigatório |

### Mitigações de CPU especulativa

Todas as mitigações aplicáveis ao ARM64 estão presentes, e as demais não se aplicam a esta
arquitetura:

- `spectre_v1`: Mitigation — `__user` pointer sanitization
- `spectre_v2`: Mitigation — CSV2, BHB
- `spec_store_bypass`: Mitigation — desabilitado via `prctl`
- `meltdown`, `l1tf`, `mds`, `retbleed`, `srbds`, `tsx_async_abort`, `mmio_stale_data`,
  `gather_data_sampling`, `itlb_multihit`, `ghostwrite`, `vmscape`, `indirect_target_selection`,
  `reg_file_data_sampling`, `old_microcode`, `spec_rstack_overflow`, `tsa`: **Not affected**

---

## 3. Acesso e autenticação

| Item | Situação |
|---|---|
| Usuários com shell | `root` (uid 0, `/bin/sh`) e `user` (uid 10000, `/bin/ash`) |
| Grupo administrativo | `wheel: root, user` |
| Login root direto por SSH | ❌ **Negado** — tentativa retornou `Permission denied` |
| Logins `pmos` / `alpine` | ❌ Negados (contas inexistentes) |
| `sudo` sem senha | ❌ **Não permitido** — exige autenticação interativa |
| `/etc/shadow` | ✅ Inacessível a usuário comum |
| Autenticação usada nesta auditoria | Chave ed25519, `BatchMode=yes`, sem senha em disco |
| Verificação de host SSH | ✅ **Mantida ativa** — `StrictHostKeyChecking=yes` em todas as conexões |

### Identificação do host

O aparelho mudou de IP (`.170` → `.171`) por DHCP. A identificação foi feita por **comparação da
chave pública ed25519 do host**, que se mostrou idêntica byte a byte à registrada em `known_hosts`.
Nenhuma verificação foi desativada em momento algum.

### Configuração do SSH

Legível apenas em parte (sem root para `sshd -T`). Do arquivo:

```
AllowTcpForwarding no      ✅ reduz uso do aparelho como pivô de rede
GatewayPorts no            ✅
X11Forwarding no           ✅
AuthorizedKeysFile .ssh/authorized_keys
Subsystem sftp internal-sftp
```

⚠️ **Não verificável sem root:** `PermitRootLogin`, `PasswordAuthentication` e
`KbdInteractiveAuthentication` efetivos. O banner de erro de login (`publickey,password,
keyboard-interactive`) sugere que **autenticação por senha está habilitada** — o que, combinado à
exposição na LAN, é um ponto a confirmar e provavelmente a restringir.

---

## 4. Superfície de rede

Portas em escuta (saída sanitizada de `ss -tulnp`):

| Porta | Protocolo | Alcance | Serviço | Avaliação |
|---|---|---|---|---|
| **22** | TCP | `0.0.0.0` + `[::]` | OpenSSH **10.6** | Necessário; é o único canal de operação do aparelho |
| 5353 | UDP | `0.0.0.0` + `*` | Avahi (mDNS) | Expõe o nome do host na LAN |
| **5355** | TCP+UDP | `0.0.0.0` + `[::]` | LLMNR (systemd-resolved) | ⚠️ Desnecessário; protocolo com histórico de abuso para *spoofing* de nomes |
| 67 | UDP | `0.0.0.0` | `unudhcpd@usb0` | Restrito à rede USB; aceitável |
| 53 | TCP+UDP | `127.0.0.53`, `127.0.0.54` | systemd-resolved | ✅ Apenas loopback |

**Firewall:** `nft` está instalado, mas o conjunto de regras **não pôde ser lido sem root**.
Não é possível afirmar se há filtragem ativa. Pela ausência de qualquer indício de configuração,
a hipótese mais provável é a de **nenhum firewall efetivo**, com o aparelho dependendo da fronteira
da rede local.

---

## 5. Cadeia de pacotes

| Item | Situação |
|---|---|
| Repositórios | `mirror.nura.eco` (systemd + main) e `dl-cdn.alpinelinux.org` (main, community, **testing**) |
| Transporte | ✅ Todos em HTTPS |
| Chaves de assinatura | 18 chaves Alpine + `build.postmarketos.org.rsa.pub` |
| Verificação | ✅ `apk` valida assinaturas por padrão |

⚠️ O repositório **`testing` do Alpine está habilitado**, junto ao canal `edge`. Isso é esperado
para um port em desenvolvimento, mas significa que o aparelho recebe pacotes sem garantia de
estabilidade — relevante ao avaliar o risco de qualquer `apk upgrade` (ver
[`remediation-plan.md` § A-01](remediation-plan.md)).

### Binários SUID

12 binários com bit SUID, **todos padrão de distribuição**, nenhum anômalo:

```
su  sudo  suexec  passwd  chfn  chsh  chage  gpasswd
mount  umount  fusermount3  pkexec
```

Nenhum binário SUID em caminho incomum ou de origem não identificada.

---

## 6. Dados em repouso e integridade de boot — principal risco

| Item | Situação |
|---|---|
| Criptografia de disco | ❌ **Ausente** — nenhum mapeamento LUKS em `lsblk` |
| Rootfs | `ext4` em texto claro, 227 GB (`loop0p2` sobre `sde27`) |
| Bootloader | 🔓 **Destravado** — `vbmeta.device_state=unlocked` |
| Verified boot | `verifiedbootstate=orange` (verificação desabilitada) |
| `veritymode` | `enforcing` no cmdline, porém sem efeito prático com AVB desabilitado |

**Risco concreto:** qualquer pessoa com acesso físico ao aparelho pode inicializar um sistema
externo via fastboot e ler integralmente o rootfs — incluindo chaves SSH, credenciais, histórico de
comandos e dados pessoais. Nenhuma senha de usuário impede isso.

Este é um **efeito colateral necessário** do port: sem destravar o bootloader, não há como executar
Linux no aparelho. O que é evitável é a ausência de criptografia — a wiki oficial do device registra
**`FDE: Works`**, ou seja, a criptografia de disco completa é suportada e simplesmente não foi
habilitada na instalação.

---

## 7. Riscos associados ao bootloader destravado

1. **Perda da cadeia de confiança.** Qualquer imagem pode ser gravada; não há verificação
   criptográfica do que inicializa.
2. **Exposição física total**, conforme §6.
3. **Ataque de "evil maid"**: com acesso físico temporário, é possível gravar um kernel modificado
   sem deixar indício perceptível ao usuário.
4. **Garantia e atestação**: funções que dependem de atestação de integridade (pagamentos, DRM,
   bancos) deixam de funcionar — irrelevante neste uso, mas registrado para completude.

Mitigação realista: habilitar FDE em reinstalação (§A-03), tratar o aparelho como dispositivo
confiável apenas sob custódia física, e não armazenar nele segredos de longo prazo.

---

## 8. Vulnerabilidades conhecidas aplicáveis

As versões instaladas são **muito recentes** — canal `edge`, com OpenSSH 10.6, kernel 7.2.9 e Mesa
26.2.6, todos de outubro/novembro de 2026. Não foi identificado nenhum componente em versão
notoriamente vulnerável.

**Ressalva metodológica honesta:** não foi executado nenhum scanner de CVE contra o inventário de
1326 pacotes. Uma afirmação de "ausência de vulnerabilidades conhecidas" seria irresponsável sem
esse cruzamento. O que se pode afirmar é que **não há componentes desatualizados** — o risco
residual concentra-se em falhas recém-divulgadas ainda sem correção no canal `edge`.

---

## 9. Recomendações priorizadas

| Prioridade | Ação | Referência |
|---|---|---|
| **ALTA** | Habilitar FDE em reinstalação planejada | A-03 |
| **ALTA** | Confirmar e, se habilitada, desativar autenticação SSH por senha | §3 |
| MÉDIA | Definir `kernel.kptr_restrict=2` | A-07 |
| MÉDIA | Desabilitar LLMNR (porta 5355) | A-07 |
| MÉDIA | Verificar e documentar o conjunto de regras `nft` | A-07 |
| BAIXA | Restringir Avahi/mDNS se a descoberta por nome não for necessária | A-07 |
| BAIXA | Executar cruzamento de CVE sobre o inventário de pacotes | §8 |
