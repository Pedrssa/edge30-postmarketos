# Linha do tempo

Reconstruída a partir de datas de arquivo, logs de VM e carimbos das transcrições de sessão.
Datas sem evidência não foram inventadas — marcadas como aproximadas quando necessário.

| Data | Evento | Evidência | Grau |
|------|--------|-----------|------|
| **2026-10-26** | Pesquisa inicial sobre instalar Linux em celular; conclusão de que o **LG K62+ não tem suporte**; recomendação de usar aparelho oficialmente suportado | Transcrição da sessão (carimbo 2026-10-26) | CONFIRMADO |
| **2026-10-28** | Trabalho de desbloqueio/root no **Moto G9 (CEBU, XT2091)** — *projeto separado*, não é o Edge 30 | Transcrição 2026-10-28; `Documents/projeto-root-moto-g9/` | CONFIRMADO |
| **2026-11-04** (dia) | **Build do postmarketOS** para o `dubai` na VM `postmarketOS-Build`; geração de `boot.img`, `dtbo.img`, `motorola-dubai.img` e `SHA256SUMS` | `mtime` das imagens = 2026-11-04 13:05; logs da VM 2026-11-04 | CONFIRMADO |
| **2026-11-04** (noite) | Aparelho **já em Linux**, acessível por SSH; construção do scaffolding "NETOPS LAB / CYBERLAB / BLACKBOX"; 18 testes no device; instalação `.netops-lab` e **rollback verificado** | Transcrição 2026-11-04 (19h+); scripts locais | CONFIRMADO (resultado) |
| **2026-11-09** | Dúvidas de operação (sudo/doas; reconexão) | Transcrição 2026-11-09 | CONFIRMADO |
| **2026-11-18** | Tentativas de reconexão (IP mudou de rede); execução de `wifipumpkin3`/`bettercap` no aparelho | Transcrição 2026-11-18 | CONFIRMADO |
| **2026-11-24** | **Esta entrega**: investigação, reconstrução, documentação, relatório (DOCX/PDF), apresentação (HTML/PPTX/PDF) e repositório | Esta sessão | CONFIRMADO |

> **Momento exato do flash:** não há transcrição capturando a gravação por `fastboot`/`pmbootstrap flasher`
> **do Edge 30**. Pela data das imagens e dos logs da VM, o build e a gravação concentram-se em **2026-11-04**,
> antes da sessão da noite em que o aparelho já respondia em Linux. O passo em si é **[RECONSTRUÍDO]**.
