#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera presentation/edge30-postmarketos.pptx (16:9) a partir da arte renderizada
do deck HTML (assets/slides/slide_NN.png), com TRANSIÇÃO DE FADE real entre slides.

Assim o PPTX fica visualmente idêntico ao HTML (com as ilustrações) e tem animação
que o PowerPoint toca de forma confiável. A versão plenamente animada (scanline,
digitação, contadores) é o próprio HTML — fonte canônica.

Pré-requisito: rodar antes os renders (gen_pdf.py gera o deck; as PNGs ficam em
assets/slides/). Uso: python scripts/gen_pptx.py
"""
import os, glob
from pptx import Presentation
from pptx.util import Inches
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml

HERE = os.path.dirname(__file__)
SLIDES = sorted(glob.glob(os.path.join(HERE, "..", "assets", "slides", "slide_*.png")))
OUT = os.path.join(HERE, "..", "presentation", "edge30-postmarketos.pptx")

prs = Presentation()
prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

FADE = ('<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        'xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" '
        'spd="med" p14:dur="700" advClick="1"><p:fade/></p:transition>')

for png in SLIDES:
    s = prs.slides.add_slide(blank)
    s.shapes.add_picture(png, 0, 0, width=prs.slide_width, height=prs.slide_height)
    # transição de fade neste slide
    s._element.insert(s._element.index(s._element.find(qn('p:clrMapOvr'))) + 1, parse_xml(FADE)) \
        if s._element.find(qn('p:clrMapOvr')) is not None else s._element.append(parse_xml(FADE))

prs.save(OUT)
print("OK:", os.path.abspath(OUT), "·", len(SLIDES), "slides (imagem + transição fade)")
