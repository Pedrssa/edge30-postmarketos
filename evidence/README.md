# evidence/ — evidências sanitizadas

Cópias **sanitizadas** de artefatos reais do projeto. Os originais ficam apenas localmente.
Nada aqui contém IMEI, número de série, tokens, senhas, `/etc/shadow` ou chaves de host.

| Arquivo | O que é | Grau |
|---|---|---|
| `SHA256SUMS` | Hashes das três imagens geradas (`boot`, `dtbo`, rootfs), datado de 2026-11-04 | CONFIRMADO |
| `netops_00-backup.sh` | Script real de snapshot só-leitura do sistema antes de qualquer mudança (exclui explicitamente segredos) | CONFIRMADO |
| `netops_10-packages.sh` | Script real que instala a camada de rede como pacote virtual removível, com simulação antes | CONFIRMADO |

> As **imagens** (`*.img`) não são versionadas (tamanho + política do GitHub) — ver `.gitignore` e
> `docs/pendencias.md` (P-07). A tabela completa de rastreabilidade está em `docs/evidencias.md`.
