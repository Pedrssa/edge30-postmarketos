#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Converte docs/relatorio-tecnico.md em docs/relatorio-tecnico.docx.
Documento legível para impressão (fundo claro), com acento verde da identidade.
Uso: python scripts/gen_docx.py
"""
import os, re
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(__file__)
SRC  = os.path.join(HERE, "..", "docs", "relatorio-tecnico.md")
OUT  = os.path.join(HERE, "..", "docs", "relatorio-tecnico.docx")

INK   = RGBColor(0x10,0x18,0x1F)
GREEN = RGBColor(0x2E,0x7D,0x00)   # verde legível em papel
CYAN  = RGBColor(0x0A,0x6E,0x7E)
GREY  = RGBColor(0x55,0x61,0x6B)
MONOBG= "EDEFF0"

doc = Document()
st = doc.styles["Normal"]; st.font.name = "Inter"; st.font.size = Pt(10.5); st.font.color.rgb = INK
for s in ["Heading 1","Heading 2","Heading 3"]:
    doc.styles[s].font.name = "Space Grotesk"
sec = doc.sections[0]
sec.left_margin = sec.right_margin = Inches(0.9); sec.top_margin = sec.bottom_margin = Inches(0.8)

def shade(cell, hexc):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"),"clear"); sh.set(qn("w:fill"),hexc); tcPr.append(sh)

def add_runs(p, text, base_color=INK):
    # inline **bold** e `code`
    for part in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text):
        if not part: continue
        if part.startswith("**") and part.endswith("**"):
            r=p.add_run(part[2:-2]); r.bold=True; r.font.color.rgb=base_color
        elif part.startswith("`") and part.endswith("`"):
            r=p.add_run(part[1:-1]); r.font.name="JetBrains Mono"; r.font.size=Pt(9.5); r.font.color.rgb=CYAN
        else:
            r=p.add_run(part); r.font.color.rgb=base_color

lines = open(SRC, encoding="utf-8").read().splitlines()
i=0; in_code=False; code_buf=[]
while i < len(lines):
    ln = lines[i]
    if ln.strip().startswith("```"):
        if in_code:
            p=doc.add_paragraph(); p.paragraph_format.left_indent=Inches(0.1)
            r=p.add_run("\n".join(code_buf)); r.font.name="JetBrains Mono"; r.font.size=Pt(9); r.font.color.rgb=INK
            pPr=p._p.get_or_add_pPr(); sh=OxmlElement("w:shd"); sh.set(qn("w:val"),"clear"); sh.set(qn("w:fill"),MONOBG); pPr.append(sh)
            code_buf=[]; in_code=False
        else: in_code=True
        i+=1; continue
    if in_code: code_buf.append(ln); i+=1; continue
    # tabela
    if ln.strip().startswith("|") and i+1<len(lines) and set(lines[i+1].replace("|","").strip())<=set("-: "):
        rows=[];
        while i<len(lines) and lines[i].strip().startswith("|"):
            rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i+=1
        header=rows[0]; body=[r for r in rows[2:]]
        t=doc.add_table(rows=1, cols=len(header)); t.style="Table Grid"; t.alignment=WD_TABLE_ALIGNMENT.CENTER
        for j,h in enumerate(header):
            c=t.rows[0].cells[j]; c.text=""; shade(c,"12351A")
            pr=c.paragraphs[0]; run=pr.add_run(re.sub(r"\*\*|`","",h)); run.bold=True; run.font.color.rgb=RGBColor(0xFF,0xFF,0xFF); run.font.size=Pt(9.5)
        for row in body:
            cells=t.add_row().cells
            for j,val in enumerate(row[:len(header)]):
                cells[j].text=""; add_runs(cells[j].paragraphs[0], val)
                for rn in cells[j].paragraphs[0].runs: rn.font.size=Pt(9)
        doc.add_paragraph(); continue
    # headings
    m=re.match(r"^(#{1,4})\s+(.*)", ln)
    if m:
        lvl=len(m.group(1)); txt=re.sub(r"\*\*|`","",m.group(2))
        h=doc.add_heading(level=min(lvl,3)); r=h.add_run(txt)
        r.font.color.rgb = GREEN if lvl<=1 else (CYAN if lvl==2 else INK)
        i+=1; continue
    if ln.strip().startswith(">"):
        p=doc.add_paragraph(); p.paragraph_format.left_indent=Inches(0.25)
        add_runs(p, ln.strip()[1:].strip(), GREY)
        pb=OxmlElement("w:pBdr"); lf=OxmlElement("w:left"); lf.set(qn("w:val"),"single"); lf.set(qn("w:sz"),"18"); lf.set(qn("w:space"),"8"); lf.set(qn("w:color"),"2E7D00"); pb.append(lf); p._p.get_or_add_pPr().append(pb)
        i+=1; continue
    if re.match(r"^[-*]\s+", ln):
        p=doc.add_paragraph(style="List Bullet"); add_runs(p, re.sub(r"^[-*]\s+","",ln)); i+=1; continue
    if re.match(r"^\d+\.\s+", ln):
        p=doc.add_paragraph(style="List Number"); add_runs(p, re.sub(r"^\d+\.\s+","",ln)); i+=1; continue
    if ln.strip()=="---": i+=1; continue
    if ln.strip()=="": doc.add_paragraph(); i+=1; continue
    p=doc.add_paragraph(); add_runs(p, ln); i+=1

doc.save(OUT)
print("OK:", os.path.abspath(OUT))
