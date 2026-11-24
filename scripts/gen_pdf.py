#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera os PDFs via Microsoft Edge headless (Chromium):
  - presentation/edge30-postmarketos.pdf  (deck 16:9, a partir do index.html)
  - docs/relatorio-tecnico.pdf             (relatório, a partir do .md -> HTML)
Uso: python scripts/gen_pdf.py
"""
import os, subprocess, tempfile, pathlib, markdown

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
import glob as _glob
_cands = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
          r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
          r"C:\Program Files\Google\Chrome\Application\chrome.exe"]
_cands += sorted(_glob.glob(r"C:\Program Files (x86)\Microsoft\EdgeCore\*\msedge.exe"), reverse=True)
EDGE = next((c for c in _cands if os.path.exists(c)), _cands[0])

def win(p): return str(pathlib.Path(p).resolve())
def url(p): return pathlib.Path(p).resolve().as_uri()

def edge_pdf(src_url, out_path):
    tmp = tempfile.mkdtemp(prefix="edgepdf_")
    cmd = [EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           f"--user-data-dir={tmp}", "--run-all-compositor-stages-before-draw",
           "--virtual-time-budget=6000", f"--print-to-pdf={win(out_path)}", src_url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    ok = os.path.exists(out_path) and os.path.getsize(out_path) > 1000
    print(("OK  " if ok else "FAIL"), out_path, "" if ok else (r.stderr or r.stdout)[:300])
    return ok

# 1) Deck — montado a partir das PNGs renderizadas (1 slide por pagina).
# Gerar o PDF direto do index.html produz paginacao errada: o scroll-snap faz o
# Chromium cortar slides entre paginas. Renderizar cada slide e empilhar e deterministico.
def deck_pdf():
    import glob as _g
    pngs = sorted(_g.glob(str(ROOT/"assets"/"slides"/"slide_*.png")))
    if not pngs:
        print("FAIL deck: nenhuma PNG em assets/slides/ — rode o renderizador de slides antes")
        return False
    try:
        from PIL import Image
    except ImportError:
        print("FAIL deck: Pillow ausente (pip install pillow)")
        return False
    ims = [Image.open(p).convert("RGB") for p in pngs]
    out = ROOT/"presentation"/"edge30-postmarketos.pdf"
    ims[0].save(out, save_all=True, append_images=ims[1:], resolution=150.0)
    print("OK   %s — %d paginas" % (out, len(ims)))
    return True

deck_pdf()

# 2) Relatório: markdown -> HTML (tema claro, imprimível)
md = (ROOT/"docs"/"relatorio-tecnico.md").read_text(encoding="utf-8")
body = markdown.markdown(md, extensions=["tables","fenced_code","toc"])
html = """<!doctype html><html lang=pt-BR><head><meta charset=utf-8>
<link rel=preconnect href=https://fonts.googleapis.com><link rel=preconnect href=https://fonts.gstatic.com crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono&display=swap" rel=stylesheet>
<style>
@page{size:A4;margin:16mm 14mm}
*{box-sizing:border-box}
body{font-family:Inter,sans-serif;color:#10181F;font-size:11px;line-height:1.5;max-width:800px;margin:0 auto}
h1,h2,h3{font-family:'Space Grotesk',sans-serif;line-height:1.15;margin:1.1em 0 .4em}
h1{font-size:26px;color:#2E7D00;border-bottom:3px solid #A6FF4D;padding-bottom:.2em}
h2{font-size:18px;color:#0A6E7E;margin-top:1.4em}
h3{font-size:14px;color:#10181F}
a{color:#0A6E7E}
code{font-family:'JetBrains Mono',monospace;font-size:9.5px;background:#EDEFF0;padding:1px 4px;border-radius:3px;color:#0A6E7E}
pre{background:#0B1116;color:#D6E3C9;padding:12px 14px;border-radius:8px;overflow-x:auto}
pre code{background:none;color:#D6E3C9;font-size:9.5px}
table{border-collapse:collapse;width:100%;margin:.8em 0;font-size:9.5px}
th{background:#12351A;color:#fff;font-weight:600;text-align:left;padding:6px 8px}
td{border:1px solid #D7DCE0;padding:5px 8px;vertical-align:top}
tr:nth-child(even) td{background:#F6F8F9}
blockquote{border-left:3px solid #A6FF4D;background:#F3F8EC;margin:.8em 0;padding:8px 14px;color:#3A4651;font-size:10px}
hr{border:none;border-top:1px solid #E0E4E8;margin:1.4em 0}
sub{color:#6B7A86}
</style></head><body>__BODY__</body></html>""".replace("__BODY__", body)
rp = ROOT/"docs"/"_relatorio.tmp.html"; rp.write_text(html, encoding="utf-8")
edge_pdf(url(rp), ROOT/"docs"/"relatorio-tecnico.pdf")
rp.unlink(missing_ok=True)
