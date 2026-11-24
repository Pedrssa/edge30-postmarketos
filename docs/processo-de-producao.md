# Processo de produção — skills, ferramentas e contribuição concreta

Registro honesto de **o que foi efetivamente usado** para produzir esta entrega, e onde cada coisa
contribuiu. Onde uma skill ideal não estava disponível ou não se aplicou, há a alternativa e a limitação.

## Skills / habilidades aplicadas

| Skill / habilidade | Usada? | Contribuição concreta |
|---|---|---|
| **`construtor-apresentacoes`** (do ZIP `criar-apresentacoes-skill.zip`) | ✅ Sim | Li integralmente `skill.md`, `references/design-system.md`, `references/slide-templates.md` e `assets/template.html`. Apliquei a **estrutura** (scroll-snap, navegação por teclado e por pontos, animação por `IntersectionObserver`, tipos de slide: título, grade, comparação, diagrama, estatísticas, etapas, CTA) no deck `presentation/index.html`. **Substituí** a paleta e as fontes do template pela identidade *hacking* pedida (ver abaixo). |
| **Pesquisa web (WebSearch)** | ✅ Sim | Confirmei: `dubai` = Motorola Edge 30 (pmOS/LineageOS); fluxo oficial do `pmbootstrap` (flasher `flash_kernel`/`flash_rootfs`/`flash_dtbo`); rebrand postmarketOS→Nura (set/2026); patch LKML do DTS do Edge 30. Fontes e datas em `relatorio-tecnico.md §14`. |
| **Agente de fetch web** | ⚠️ Parcial | Tentei ler a página oficial do device. A wiki redireciona para `wiki.nura.eco` e está atrás de **proteção anti-bot (Anubis)** — não foi possível extrair a matriz completa. Limitação registrada em `pendencias.md` (P-04). |
| **Geração de DOCX** | ✅ Sim (alternativa) | Não usei uma skill de alto nível; gerei com **`python-docx`** via `scripts/gen_docx.py` (converte o relatório MD → DOCX legível para impressão). É o mesmo mecanismo que as skills de documento usam por baixo. |
| **Geração de PPTX** | ✅ Sim (alternativa) | **`python-pptx`** via `scripts/gen_pptx.py`. Cada slide é a **arte renderizada do HTML** (com as ilustrações) + **transição de fade real** entre slides (XML `p:transition`, que o PowerPoint toca de forma confiável). A animação plena — scanline, digitação, contadores — vive no **HTML**, que é a fonte canônica; o PPTX é um derivado visualmente idêntico para quem precisa do formato. |
| **Geração de PDF** | ✅ Sim | **Microsoft Edge headless (Chromium)** via `scripts/gen_pdf.py`: imprime o deck (`index.html`) em PDF 16:9 e o relatório (MD→HTML tema claro) em PDF A4. |
| **Diagramas / ilustrações** | ✅ Sim | Originais em **SVG/CSS** dentro do deck: celular com terminal de boot + **scanline** e barras (slides 1/4/14), montanhas Alpine + chip ARM64 (slide 3), diagrama de fluxo de boot com setas animadas (`stroke-dashoffset`, slide 7), checks que se desenham na matriz, linha do tempo que cresce, **contadores que contam** (slide 11) e terminal que **digita sozinho** (slides 1/6). |
| **Validação visual** | ✅ Sim | Rasterizei slides com **PyMuPDF** (`assets/preview/`) e inspecionei: abertura, diagrama e matriz. Conferência de contraste (hook de design) aplicada. |
| **Git** | ✅ Sim | Repositório local inicializado e versionado. Publicação no GitHub conforme `README` / bloco final da conversa (autenticação existente; sem colar tokens). |
| **Design (hook Impeccable)** | ✅ Sim | O hook sinalizou 12 pontos de baixo contraste; corrigi os reais (textos esmaecidos, comentário de terminal) elevando opacidades/cores. Legibilidade em projetor priorizada. |

## Identidade visual aplicada (substituições documentadas)

- **Paleta** (conforme brief): `#090D12` grafite · `#151C25` superfície · `#A6FF4D` verde terminal (destaque) ·
  `#22D3EE` ciano (secundária) · `#E8EEF5`→`#B4C3D0` leitura · âmbar/vermelho só para alertas.
- **Fontes** (trocadas do template, todas no Google Fonts):
  - Títulos: **Space Grotesk** (era Chakra Petch).
  - Corpo: **Inter**.
  - Código/labels: **JetBrains Mono**.
- **Tom**: terminal / engenharia reversa, com grids discretos, etiquetas técnicas, numeração e blocos de
  terminal — sem chuva de caracteres nem neon excessivo.

## Reprodutibilidade

```sh
pip install python-pptx python-docx markdown pymupdf
python scripts/gen_pptx.py    # -> presentation/edge30-postmarketos.pptx
python scripts/gen_docx.py    # -> docs/relatorio-tecnico.docx
python scripts/gen_pdf.py     # -> deck.pdf + relatorio.pdf (precisa do Microsoft Edge)
```

> O HTML (`presentation/index.html`) é a fonte canônica da apresentação animada e é **offline** (só busca
> Google Fonts). PPTX e PDF são derivados para distribuição.
