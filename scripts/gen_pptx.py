#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera presentation/edge30-postmarketos.pptx com tema "hacking" (16:9).

python-pptx NÃO cria animações de entrada nativamente. Para não entregar um
arquivo estático disfarçado de animado, injetamos uma animação real de entrada
(fade) por slide via XML do PowerPoint. A versão plenamente animada é o HTML.
Uso: python scripts/gen_pptx.py
"""
import os, copy
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

BG   = RGBColor(0x09,0x0D,0x12)
SURF = RGBColor(0x15,0x1C,0x25)
SUR2 = RGBColor(0x1B,0x25,0x31)
TEXT = RGBColor(0xE8,0xEE,0xF5)
SOFT = RGBColor(0xB4,0xC3,0xD0)
GREEN= RGBColor(0xA6,0xFF,0x4D)
CYAN = RGBColor(0x22,0xD3,0xEE)
AMBER= RGBColor(0xF6,0xC1,0x77)
LINE = RGBColor(0x2A,0x36,0x42)

TITLE_F="Space Grotesk"; BODY_F="Inter"; MONO_F="JetBrains Mono"
EMU_W, EMU_H = Inches(13.333), Inches(7.5)

prs = Presentation()
prs.slide_width = EMU_W; prs.slide_height = EMU_H
BLANK = prs.slide_layouts[6]

def slide():
    s = prs.slides.add_slide(BLANK)
    r = s.shapes.add_shape(1, 0, 0, EMU_W, EMU_H)  # rect bg
    r.fill.solid(); r.fill.fore_color.rgb = BG; r.line.fill.background()
    r.shadow.inherit = False
    return s

def box(s, x, y, w, h, fill=None, line=None, line_w=1.0, radius=True):
    shp = s.shapes.add_shape(5 if radius else 1, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None: shp.fill.background()
    else: shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if line is None: shp.line.fill.background()
    else: shp.line.color.rgb = line; shp.line.width = Pt(line_w)
    shp.shadow.inherit = False
    return shp

def txt(s, x, y, w, h, runs, size=18, font=BODY_F, color=TEXT, bold=False,
        align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, sp=1.0, spacing_after=4):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    if isinstance(runs, str): runs = [[(runs, color, bold)]]
    for i, para in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.line_spacing = sp; p.space_after = Pt(spacing_after)
        if isinstance(para, str): para = [(para, color, bold)]
        for t, c, b in para:
            run = p.add_run(); run.text = t
            run.font.name = font; run.font.size = Pt(size)
            run.font.color.rgb = c; run.font.bold = b
    return tb

def tag(s, left_text, idx):
    txt(s, 0.55, 0.30, 6, 0.4, [[(("// "+left_text).upper(), GREEN, True)]], size=11, font=MONO_F)
    txt(s, 9.5, 0.30, 3.3, 0.4, [[(f"{idx:02d} / 14", SOFT, False)]], size=11, font=MONO_F, align=PP_ALIGN.RIGHT)

def eyebrow(s, t, y=1.2):
    txt(s, 0.75, y, 11, 0.4, [[(("// "+t).upper(), CYAN, True)]], size=12, font=MONO_F)

def animate_fade(s):
    """Injeta uma animação de entrada (fade) real no slide via timing XML."""
    # encontra o id do primeiro placeholder/shape com texto para animar
    sp = None
    for shp in s.shapes:
        if shp.has_text_frame and shp.text_frame.text.strip():
            sp = shp; break
    if sp is None: return
    sid = sp.shape_id
    xml = f'''<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
<p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">
<p:childTnLst><p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>
<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>
<p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>
<p:par><p:cTn id="5" presetID="10" presetClass="entr" presetSubtype="0" fill="hold" nodeType="clickEffect"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>
<p:set><p:cBhvr><p:cTn id="6" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>
<p:anim calcmode="lin" valueType="num"><p:cBhvr additive="base"><p:cTn id="7" dur="600" fill="hold"/><p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl><p:attrNameLst><p:attrName>ppt_x</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst><p:tav tm="0"><p:val><p:strVal val="#ppt_x-0.03"/></p:val></p:tav><p:tav tm="100000"><p:val><p:strVal val="#ppt_x"/></p:val></p:tav></p:tavLst></p:anim>
<p:anim calcmode="lin" valueType="num"><p:cBhvr additive="base"><p:cTn id="8" dur="600" fill="hold"/><p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl><p:attrNameLst><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst><p:tav tm="0"><p:val><p:strVal val="#ppt_y+0.04"/></p:val></p:tav><p:tav tm="100000"><p:val><p:strVal val="#ppt_y"/></p:val></p:tav></p:tavLst></p:anim>
<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="9" dur="600"/><p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl></p:cBhvr></p:animEffect>
</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>
</p:childTnLst></p:cTn></p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>'''
    from pptx.oxml import parse_xml
    s.slides if False else None
    s._element.append(parse_xml(xml))

def card(s, x, y, w, h, kicker, title, body, accent=False):
    box(s, x, y, w, h, fill=SURF, line=(GREEN if accent else LINE), line_w=1.25)
    txt(s, x+0.22, y+0.18, w-0.4, 0.4, [[(kicker.upper(), CYAN, True)]], size=10, font=MONO_F)
    txt(s, x+0.22, y+0.52, w-0.4, 0.6, [[(title, TEXT, True)]], size=19, font=TITLE_F)
    txt(s, x+0.22, y+1.12, w-0.4, h-1.2, [[(body, SOFT, False)]], size=13, font=BODY_F, sp=1.08)

# ---------------- SLIDES ----------------
# 1 Abertura
s = slide(); tag(s,"projeto dubai",1); eyebrow(s,"engenharia linux embarcada · ARM64")
txt(s,0.75,1.7,12,2.2,[[("De Android travado a ",TEXT,True)],[("Linux de bolso",GREEN,True)]],size=58,font=TITLE_F,sp=0.98)
txt(s,0.75,4.05,11.5,1.2,[[("Trocamos o sistema de um ",SOFT,False),("Motorola Edge 30",TEXT,True),(" na raiz e colocamos ",SOFT,False),("postmarketOS",GREEN,True),(" rodando — com GUI, Wi-Fi e SSH de pé.",SOFT,False)]],size=20,font=BODY_F,sp=1.1)
txt(s,0.75,5.5,12,0.5,[[("XT2203-1 · dubai    postmarketOS / Nura    Phosh · Wayland    aarch64",CYAN,True)]],size=13,font=MONO_F)
animate_fade(s)

# 2 Desafio
s=slide(); tag(s,"motivação",2); eyebrow(s,"o desafio")
txt(s,0.75,1.7,12,1.3,[[("Um celular é um ",TEXT,True),("computador ARM64",CYAN,True),(" que a gente aluga do fabricante.",TEXT,True)]],size=34,font=TITLE_F,sp=1.0)
card(s,0.75,3.4,3.9,3.2,"Objetivo","Virar dono do sistema","Usar o hardware como estação portátil de engenharia e redes — não como aparelho fechado.")
card(s,4.85,3.4,3.9,3.2,"O preço","Operação destrutiva","Destravar o bootloader e trocar o sistema apaga o aparelho e tira a garantia.")
card(s,8.95,3.4,3.9,3.2,"A disciplina","Rede de segurança","Integridade por hash e um caminho de volta ao Android guardado.",accent=True)
animate_fade(s)

# 3 postmarketOS
s=slide(); tag(s,"contexto",3); eyebrow(s,"o que é postmarketOS")
txt(s,0.75,1.7,12,1.2,[[("Um ",TEXT,True),("Linux de verdade",GREEN,True),(" para celulares, sobre Alpine.",TEXT,True)]],size=34,font=TITLE_F)
card(s,0.75,3.3,5.9,3.0,"Filosofia","Kernel perto do mainline","Dá vida longa ao aparelho rodando um kernel próximo do oficial, em vez do kernel travado de fábrica.")
card(s,6.85,3.3,6.0,3.0,"Nota de contexto","Agora chamado Nura","Rebatizado em set/2026 (mesmo projeto, domínio nura.eco). No aparelho aparece como 'Nura Linux edge'.")
txt(s,0.75,6.5,12,0.4,[[("Fonte: Linuxiac / Notebookcheck (set/2026) · acesso 2026-11-24.",SOFT,False)]],size=11,font=MONO_F)
animate_fade(s)

# 4 Dispositivo
s=slide(); tag(s,"alvo",4); eyebrow(s,"nosso dispositivo")
txt(s,0.75,1.6,12,0.9,[[("Edge 30 · codinome ",TEXT,True),("dubai",GREEN,True)]],size=34,font=TITLE_F)
specs=[("Modelo","Edge 30","XT2203-1"),("SoC","SD 778G+","SM7325 · sc7280"),("Arquitetura","ARM64","aarch64"),("UI","Phosh","Wayland · 0.58")]
for i,(k,t,m) in enumerate(specs):
    x=0.75+i*3.05
    box(s,x,2.7,2.85,1.7,fill=SURF,line=LINE,line_w=1.1)
    txt(s,x+0.18,2.85,2.5,0.3,[[(k.upper(),CYAN,True)]],size=10,font=MONO_F)
    txt(s,x+0.18,3.15,2.5,0.5,[[(t,TEXT,True)]],size=19,font=TITLE_F)
    txt(s,x+0.18,3.75,2.6,0.4,[[(m,SOFT,False)]],size=12,font=MONO_F)
box(s,0.75,4.7,5.9,1.7,fill=SUR2,line=AMBER,line_w=1.1)
txt(s,0.95,4.85,5.5,1.5,[[("▲ Sem imagem pronta. ",AMBER,True),("No pmOS o dubai é 'testing' — precisávamos construir o sistema.",SOFT,False)]],size=13,font=BODY_F,sp=1.05)
box(s,6.95,4.7,5.9,1.7,fill=SUR2,line=AMBER,line_w=1.1)
txt(s,7.15,4.85,5.5,1.5,[[("▲ Risco de kernel. ",AMBER,True),("A wiki alerta p/ baixa responsividade no sc7280-mainline. Impacto NÃO medido por nós.",SOFT,False)]],size=13,font=BODY_F,sp=1.05)
animate_fade(s)

# 5 Objetivo
s=slide(); tag(s,"critério",5); eyebrow(s,"objetivo e sucesso")
txt(s,0.75,1.7,12,1.0,[[("Quatro provas de que o port funciona.",TEXT,True)]],size=34,font=TITLE_F)
crit=[("01","Boot","O aparelho inicializa em Linux."),("02","GUI","A interface Phosh sobe."),("03","Wi-Fi","Conecta na rede sem fio."),("04","SSH","Aceita acesso remoto.")]
for i,(n,t,d) in enumerate(crit):
    x=0.75+i*3.05
    box(s,x,3.1,2.85,2.1,fill=SURF,line=GREEN,line_w=1.25)
    txt(s,x+0.2,3.25,2.5,0.4,[[(n,CYAN,True)]],size=11,font=MONO_F)
    txt(s,x+0.2,3.65,2.5,0.6,[[(t,GREEN,True)]],size=24,font=TITLE_F)
    txt(s,x+0.2,4.35,2.6,0.8,[[(d,SOFT,False)]],size=13,font=BODY_F,sp=1.05)
txt(s,0.75,5.6,12,0.9,[[("Tudo além disso — áudio, câmera, chamadas — ficou como ",SOFT,False),("bônus a validar depois",CYAN,True),(".",SOFT,False)]],size=19,font=BODY_F)
animate_fade(s)

# 6 Ambiente
s=slide(); tag(s,"ferramentas",6); eyebrow(s,"ambiente de trabalho")
txt(s,0.75,1.6,12,1.1,[[("Dois mundos: a VM que ",TEXT,True),("fabrica",GREEN,True),(", o PC que ",TEXT,True),("grava",CYAN,True),(".",TEXT,True)]],size=32,font=TITLE_F)
card(s,0.75,3.0,5.9,2.0,"Build (Linux)","VM Ubuntu + pmbootstrap","VirtualBox, 4 GB RAM. pmbootstrap é a toolchain oficial: compila rootfs e kernel p/ o aparelho-alvo.")
card(s,6.85,3.0,6.0,2.0,"Gravação (Windows)","Android platform-tools","fastboot grava as partições em modo bootloader. adb para reiniciar e inspecionar.")
box(s,0.75,5.25,12.1,1.5,fill=RGBColor(0x05,0x08,0x0B),line=LINE,line_w=1.0)
txt(s,1.0,5.45,11.6,1.2,[[("$ ",GREEN,True),("pmbootstrap init",TEXT,False),("        # device: motorola-dubai · UI: phosh",SOFT,False)],[("$ ",GREEN,True),("pmbootstrap install",TEXT,False),("     # gera rootfs + kernel",SOFT,False)]],size=14,font=MONO_F,sp=1.3)
animate_fade(s)

# 7 Arquitetura (texto + imagem do diagrama se existir)
s=slide(); tag(s,"arquitetura",7); eyebrow(s,"fluxo técnico")
txt(s,0.75,1.5,12,1.0,[[("Da VM às partições, do kernel ao ",TEXT,True),("SSH",GREEN,True),(".",TEXT,True)]],size=32,font=TITLE_F)
png=os.path.join(os.path.dirname(__file__),"..","assets","diagram.png")
if os.path.exists(png):
    s.shapes.add_picture(png, Inches(0.9), Inches(2.6), width=Inches(11.5))
else:
    # fallback: blocos
    seq=[("VM Linux\npmbootstrap",GREEN),("boot / dtbo\nrootfs 2GB",CYAN),("fastboot\n→ partições",CYAN),("Phosh\nWi-Fi · SSH",GREEN)]
    for i,(t,c) in enumerate(seq):
        x=0.75+i*3.1
        box(s,x,3.4,2.6,1.7,fill=SURF,line=c,line_w=1.25)
        txt(s,x+0.1,3.7,2.4,1.2,[[(t.split(chr(10))[0],TEXT,True)],[(t.split(chr(10))[1],SOFT,False)]],size=15,font=TITLE_F,align=PP_ALIGN.CENTER,sp=1.1)
        if i<3: txt(s,x+2.65,3.9,0.5,0.6,[[("→",CYAN,True)]],size=24,font=TITLE_F)
txt(s,0.75,6.6,12,0.4,[[("Diagrama exato. O passo fastboot é reconstruído do fluxo oficial — sem log de flash capturado.",SOFT,False)]],size=11,font=MONO_F)
animate_fade(s)

# 8 Etapas
s=slide(); tag(s,"execução",8); eyebrow(s,"etapas realizadas")
txt(s,0.75,1.5,12,0.9,[[("Seis passos — e uma ressalva honesta.",TEXT,True)]],size=32,font=TITLE_F)
steps=[("01","Viabilidade","Device suportado e bootloader destravável.","confirmado",GREEN),
("02","Build na VM","pmbootstrap gera rootfs + kernel.","resultado ✓",GREEN),
("03","Destravar bootloader","OEM unlock + código Motorola (destrutivo).","reconstruído",AMBER),
("04","Gravar partições","fastboot: boot · dtbo · userdata.","reconstruído",AMBER),
("05","Primeiro boot","Phosh sobe na tela do aparelho.","confirmado",GREEN),
("06","Wi-Fi + SSH","Acesso remoto ao aparelho.","confirmado",GREEN)]
for i,(n,t,d,b,c) in enumerate(steps):
    y=2.55+i*0.62
    box(s,0.75,y,12.1,0.54,fill=SURF,line=LINE,line_w=0.8)
    txt(s,0.95,y+0.07,0.6,0.4,[[(n,GREEN,True)]],size=14,font=MONO_F)
    txt(s,1.6,y+0.07,6.5,0.4,[[(t+"  ",TEXT,True),(d,SOFT,False)]],size=13,font=BODY_F)
    txt(s,10.6,y+0.08,2.1,0.4,[[(b,c,True)]],size=11,font=MONO_F,align=PP_ALIGN.RIGHT)
txt(s,0.75,6.5,12,0.5,[[("Temos a prova de que funcionou (SSH + captura). O registro do flash não ficou salvo → 03–04 = reconstruído.",AMBER,False)]],size=12,font=BODY_F)
animate_fade(s)

# 9 Dificuldades
s=slide(); tag(s,"diagnóstico",9); eyebrow(s,"dificuldades reais")
txt(s,0.75,1.6,12,1.0,[[("Problemas de quem opera — e como contornamos.",TEXT,True)]],size=30,font=TITLE_F)
difs=[("Sem imagem pronta","Device 'testing' no pmOS. → Build próprio na VM."),
("Bloco não enviado","Shell do Windows não processou comando grande. → Árvore via SFTP."),
("Erro de codificação","UnicodeEncodeError (cp1252). → Forçar UTF-8."),
("Reconexão falhou","IP do aparelho mudou de rede. → Pegar IP novo no celular.")]
for i,(t,d) in enumerate(difs):
    x=0.75+(i%2)*6.1; y=3.0+(i//2)*1.75
    box(s,x,y,5.85,1.55,fill=SURF,line=LINE,line_w=1.0)
    txt(s,x+0.2,y+0.15,5.5,0.4,[[("OBSTÁCULO → SOLUÇÃO",CYAN,True)]],size=9,font=MONO_F)
    txt(s,x+0.2,y+0.45,5.5,0.4,[[(t,TEXT,True)]],size=17,font=TITLE_F)
    txt(s,x+0.2,y+0.9,5.5,0.6,[[(d,SOFT,False)]],size=12,font=BODY_F,sp=1.05)
animate_fade(s)

# 10 Evidências
s=slide(); tag(s,"rigor",10); eyebrow(s,"como classifico tudo")
txt(s,0.75,1.6,12,1.0,[[("Não peço fé. Mostro a ",TEXT,True),("régua",GREEN,True),(".",TEXT,True)]],size=32,font=TITLE_F)
legend=[("CONFIRMADO",GREEN),("RELATADO",CYAN),("RECONSTRUÍDO",AMBER),("AUSENTE",SOFT)]
for i,(t,c) in enumerate(legend):
    x=0.75+i*3.0; box(s,x,2.9,2.8,0.5,fill=SURF,line=c,line_w=1.1)
    txt(s,x+0.15,2.98,2.6,0.35,[[(t,c,True)]],size=11,font=MONO_F)
card(s,0.75,3.7,5.9,2.6,"exemplos confirmados","Imagens + hashes · Boot/GUI/Wi-Fi/SSH","Tudo o que verifiquei em arquivo ou transcrição recebe CONFIRMADO.")
card(s,6.85,3.7,6.0,2.6,"exemplos com ressalva","Kernel=RELATADO · Flash=RECONSTRUÍDO","Áudio, câmera e modem = AUSENTE. Nada pintado além do medido.")
txt(s,0.75,6.5,12,0.4,[[("Tabela completa (24 itens): docs/evidencias.md",SOFT,False)]],size=11,font=MONO_F)
animate_fade(s)

# 11 Resultados
s=slide(); tag(s,"resultado",11); eyebrow(s,"o que ficou de pé")
txt(s,0.75,1.6,12,1.0,[[("Não é só que ",TEXT,True),("ligou",GREEN,True),(". É base para trabalhar.",TEXT,True)]],size=32,font=TITLE_F)
stats=[("4/4","critérios de sucesso",GREEN),("3","imagens íntegras (sha256)",CYAN),("7","pacotes + rollback",TEXT),("0","diferença após reverter",TEXT)]
for i,(n,l,c) in enumerate(stats):
    x=0.75+i*3.05; box(s,x,3.0,2.85,1.9,fill=SURF,line=(GREEN if i==0 else LINE),line_w=1.25)
    txt(s,x+0.2,3.15,2.5,0.9,[[(n,c,True)]],size=46,font=TITLE_F)
    txt(s,x+0.2,4.25,2.6,0.6,[[(l.upper(),SOFT,True)]],size=10,font=MONO_F,sp=1.0)
txt(s,0.75,5.4,12,0.9,[[("Boot + Phosh + Wi-Fi + SSH confirmados; apk operante; ferramentas instaladas e ",SOFT,False),("revertidas sem resíduo",GREEN,True),(".",SOFT,False)]],size=18,font=BODY_F,sp=1.1)
animate_fade(s)

# 12 Timeline
s=slide(); tag(s,"cronologia",12); eyebrow(s,"linha do tempo")
txt(s,0.75,1.5,12,0.8,[[("Da pesquisa à documentação.",TEXT,True)]],size=32,font=TITLE_F)
tl=[("2026-10-26","Pesquisa de viabilidade: Linux em celular; recomendação de aparelho suportado."),
("2026-11-04 · dia","Build do pmOS na VM; geração de boot/dtbo/rootfs + SHA256SUMS."),
("2026-11-04 · noite","Aparelho já em Linux via SSH; scaffolding, 18 testes, rollback verificado."),
("2026-11-18","Operação e reconexão (IP mudou); ferramentas de rede no aparelho."),
("2026-11-24","Esta entrega: relatório (DOCX/PDF), apresentação (HTML/PPTX/PDF), repositório.")]
for i,(d,t) in enumerate(tl):
    y=2.6+i*0.82
    c=s.shapes.add_shape(9,Inches(0.8),Inches(y),Inches(0.22),Inches(0.22))
    c.fill.solid(); c.fill.fore_color.rgb=GREEN; c.line.fill.background(); c.shadow.inherit=False
    txt(s,1.25,y-0.08,2.4,0.4,[[(d,CYAN,True)]],size=12,font=MONO_F)
    txt(s,3.8,y-0.08,9.0,0.7,[[(t,SOFT,False)]],size=13,font=BODY_F,sp=1.0)
animate_fade(s)

# 13 Matriz
s=slide(); tag(s,"honestidade",13); eyebrow(s,"matriz de funcionalidades")
txt(s,0.75,1.5,12,0.9,[[("O que ",TEXT,True),("medimos",GREEN,True),(" — e o que ainda não.",TEXT,True)]],size=32,font=TITLE_F)
rows=[("Boot em Linux",True),("Áudio",False),("Interface Phosh (GUI)",True),("Modem · chamadas · SMS",False),
("Wi-Fi (wlan0)",True),("Dados móveis",False),("SSH remoto",True),("GPU · câmera",False),
("apk · pacotes + rollback",True),("Bluetooth · NFC · sensores · bateria",False)]
for i,(t,ok) in enumerate(rows):
    x=0.75+(i%2)*6.1; y=2.55+(i//2)*0.7
    box(s,x,y,5.85,0.58,fill=(SUR2 if ok else SURF),line=(GREEN if ok else LINE),line_w=1.0)
    mark="●" if ok else "○"
    txt(s,x+0.2,y+0.1,0.4,0.4,[[(mark,(GREEN if ok else SOFT),True)]],size=14,font=BODY_F)
    txt(s,x+0.65,y+0.12,4.2,0.4,[[(t,(TEXT if ok else SOFT),ok)]],size=13,font=BODY_F)
    txt(s,x+4.6,y+0.14,1.1,0.4,[[(("VERIF." if ok else "NÃO"),(GREEN if ok else SOFT),True)]],size=9,font=MONO_F,align=PP_ALIGN.RIGHT)
txt(s,0.75,6.5,12,0.4,[[("Não pinto de verde o que não medi. O cinza é o próximo passo.",SOFT,False)]],size=12,font=BODY_F)
animate_fade(s)

# 14 Encerramento
s=slide(); tag(s,"fim",14); eyebrow(s,"aprendizados e próximos passos")
txt(s,0.75,1.6,12,1.6,[[("Linux no bolso dá —",TEXT,True)],[("o preço é ",TEXT,True),("rigor",GREEN,True),(".",TEXT,True)]],size=46,font=TITLE_F,sp=1.0)
nxt=[("Matriz no device","Medir áudio, modem, BT, sensores no aparelho."),("Confirmar kernel","uname -a p/ fechar a versão relatada."),("Log de flash","Capturar regravação limpa → vira 'confirmado'.")]
for i,(t,d) in enumerate(nxt):
    x=0.75+i*4.05; card(s,x,3.7,3.8,1.9,"próximo",t,d)
txt(s,0.75,5.9,12,0.9,[[("O repositório traz o relatório, a tabela de evidências e esta apresentação. ",SOFT,False),("Obrigado.",GREEN,True)]],size=17,font=BODY_F)
animate_fade(s)

out=os.path.join(os.path.dirname(__file__),"..","presentation","edge30-postmarketos.pptx")
prs.save(out)
print("OK:", os.path.abspath(out), "·", len(prs.slides.__iter__.__self__._sldIdLst), "slides")
