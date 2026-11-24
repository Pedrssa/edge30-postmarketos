```
 ███████╗██████╗  ██████╗ ███████╗██████╗  ██████╗
 ██╔════╝██╔══██╗██╔════╝ ██╔════╝╚════██╗██╔═████╗
 █████╗  ██║  ██║██║  ███╗█████╗   █████╔╝██║██╔██║
 ██╔══╝  ██║  ██║██║   ██║██╔══╝   ╚═══██╗████╔╝██║
 ███████╗██████╔╝╚██████╔╝███████╗██████╔╝╚██████╔╝
 ╚══════╝╚═════╝  ╚═════╝ ╚══════╝╚═════╝  ╚═════╝
   p o s t m a r k e t O S   ·   p r o j e t o   d u b a i
```

# EDGE30 · postmarketOS (`dubai`)

> De celular Android travado a **estação Linux de bolso** — Motorola Edge 30 rodando
> postmarketOS (Nura) com Phosh, kernel `sc7280` mainline, **Wi‑Fi e SSH de pé**.

Este repositório **reconstrói e documenta**, a partir dos artefatos reais, como transformamos um
**Motorola Edge 30** (`XT2203-1`, codinome `dubai`) em um computador **Linux ARM64 nativo**. Cada
afirmação é marcada por grau de confirmação — nada é pintado de verde sem evidência.

---

## 🎯 Estado real do projeto

| | |
|---|---|
| **Alvo** | Motorola Edge 30 · `XT2203-1` · `dubai` · SoC SD 778G+ (SM7325 / sc7280) · ARM64 |
| **Sistema** | postmarketOS (**Nura**, canal *edge*) · base Alpine · **Phosh** / Wayland |
| **Build** | `pmbootstrap` em VM Ubuntu (VirtualBox) · gravação por `fastboot` |
| **Comprovado** | ✅ boot em Linux · ✅ GUI Phosh · ✅ Wi‑Fi · ✅ SSH · ✅ `apk` + rollback |
| **Não testado** | ❔ áudio · modem/chamadas · dados móveis · GPU · câmera · Bluetooth · NFC · sensores · bateria |
| **Reconstruído** | ⚠️ passos de destravamento e gravação (sem log de flash capturado) |

> Legenda completa e tabela de rastreabilidade: [`docs/evidencias.md`](docs/evidencias.md).

---

## 🗂️ Organização do repositório

```
edge30-postmarketos/
├── README.md                     ← este arquivo
├── docs/
│   ├── relatorio-tecnico.md       ← relatório técnico completo  (+ .docx  + .pdf)
│   ├── guia-de-reproducao.md      ← pré-requisitos e passos (usado vs recomendado)
│   ├── evidencias.md              ← tabela ID · afirmação · evidência · local · grau
│   ├── linha-do-tempo.md          ← cronologia baseada em evidências
│   ├── pendencias.md              ← lacunas e próximos passos (com prioridade)
│   ├── roteiro-apresentacao.md    ← falas completas, slide a slide (~10 min)
│   └── processo-de-producao.md    ← skills/ferramentas usadas e sua contribuição
├── presentation/
│   ├── index.html                 ← apresentação animada (fonte canônica, offline)
│   ├── edge30-postmarketos.pptx   ← deck editável (com animações de entrada reais)
│   └── edge30-postmarketos.pdf    ← deck em PDF 16:9 (offline)
├── assets/
│   ├── diagram.png                ← diagrama de fluxo de boot (original)
│   ├── CREDITOS.md                ← fontes, licenças e marcas
│   └── preview/                   ← capturas de validação dos slides
├── evidence/                      ← evidências sanitizadas (sem segredos)
└── scripts/                       ← geradores (gen_pptx / gen_docx / gen_pdf)
```

---

## ▶️ Como abrir

- **Apresentação (recomendado):** abra [`presentation/index.html`](presentation/index.html) no navegador.
  Navegue com **↑ ↓ / ← →**, scroll ou pelos pontos à direita.
- **Para projetor/offline:** `presentation/edge30-postmarketos.pdf` (14 páginas 16:9) ou o `.pptx`.
- **Relatório:** [`docs/relatorio-tecnico.md`](docs/relatorio-tecnico.md) · também em `.docx` e `.pdf`.

## 🔁 Reproduzir os derivados

```sh
pip install python-pptx python-docx markdown pymupdf
python scripts/gen_pptx.py    # -> presentation/edge30-postmarketos.pptx
python scripts/gen_docx.py    # -> docs/relatorio-tecnico.docx
python scripts/gen_pdf.py     # -> os dois PDFs (requer Microsoft Edge)
```

---

## ⚡ Fluxo em uma imagem

```
┌─────────────┐  pmbootstrap   ┌──────────────┐  fastboot flash  ┌─────────────┐
│  VM Ubuntu  │ ─────────────► │ boot · dtbo  │ ───────────────► │  Edge 30    │
│  (build)    │                │ rootfs .img  │   [reconstruído] │  dubai      │
└─────────────┘                └──────────────┘                  └─────────────┘
       └── unlock bootloader (código Motorola) ──────────────────────┘
                                                      boot ► Phosh + Wi‑Fi + SSH ✅
```

---

## ⚠️ Avisos

- **Destravar o bootloader e gravar partições apaga o aparelho** e invalida a garantia.
- Operação feita em **hardware próprio**. Ferramentas montadas sobre o sistema são para **redes
  próprias ou autorizadas**.
- Imagens (`*.img`, ~2 GB) e a VM **não** são versionadas — ver `.gitignore` e `docs/pendencias.md`.

---

<sub>Projeto pessoal · documentação reconstruída em 2026-11-24 a partir de artefatos locais e transcrições.</sub>
