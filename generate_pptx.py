#!/usr/bin/env python3
"""EIB pathway — editable PowerPoint with connected arrows.

Every connector is wired to its source/destination shape via OOXML
stCxn/endCxn references, so moving a box in PowerPoint drags the
connected arrows with it.
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

# ─── Palette ──────────────────────────────────────────────────────────────
C_TITLE       = RGBColor(0x1F, 0x4E, 0x5F)
C_HEADER_FILL = RGBColor(0x2C, 0x5F, 0x7C)
C_HEADER_TX   = RGBColor(0xFF, 0xFF, 0xFF)
C_ACTION_F    = RGBColor(0xE1, 0xEC, 0xF4)
C_ACTION_E    = RGBColor(0x3A, 0x7C, 0xA5)
C_DECISION_F  = RGBColor(0xFF, 0xF4, 0xD6)
C_DECISION_E  = RGBColor(0xC6, 0x8A, 0x00)
C_TREAT_F     = RGBColor(0xDC, 0xEE, 0xDC)
C_TREAT_E     = RGBColor(0x3D, 0x8B, 0x3D)
C_ALT_F       = RGBColor(0xF8, 0xE0, 0xDC)
C_ALT_E       = RGBColor(0xB0, 0x52, 0x4C)
C_TEXT        = RGBColor(0x1A, 0x1A, 0x1A)
C_ARROW       = RGBColor(0x3A, 0x3A, 0x3A)
C_LEGEND_BG   = RGBColor(0xF2, 0xF2, 0xF2)
C_LEGEND_EDGE = RGBColor(0xB0, 0xB0, 0xB0)
C_YES         = RGBColor(0x3D, 0x8B, 0x3D)
C_NO          = RGBColor(0xB0, 0x52, 0x4C)
C_GRAY_TX     = RGBColor(0x55, 0x55, 0x55)
C_SUB_TX      = RGBColor(0x44, 0x44, 0x44)

I = Inches

prs = Presentation()
prs.slide_width  = I(10)
prs.slide_height = I(14)
slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank


# ─── Shape helpers ────────────────────────────────────────────────────────

def add_shape(shp_type, cx, cy, w, h, fill=None, line_color=None, line_w=1.5):
    s = slide.shapes.add_shape(
        shp_type, I(cx - w/2), I(cy - h/2), I(w), I(h)
    )
    s.fill.solid() if fill else s.fill.background()
    if fill:
        s.fill.fore_color.rgb = fill
    if line_color:
        s.line.color.rgb = line_color
        s.line.width = Pt(line_w)
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    return s


def set_text(shp, paragraphs):
    tf = shp.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = I(0.07)
    tf.margin_top = tf.margin_bottom = I(0.04)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for i, p in enumerate(paragraphs):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = PP_ALIGN.CENTER
        run = para.add_run()
        run.text = p['text']
        run.font.size = Pt(p.get('size', 10))
        run.font.bold = p.get('bold', False)
        run.font.italic = p.get('italic', False)
        run.font.name = 'Calibri'
        if 'color' in p:
            run.font.color.rgb = p['color']


def add_textbox(cx, cy, w, h, paragraphs, align='center'):
    tb = slide.shapes.add_textbox(I(cx - w/2), I(cy - h/2), I(w), I(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = I(0.03)
    tf.margin_top = tf.margin_bottom = I(0.02)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    pp_align = PP_ALIGN.CENTER if align == 'center' else PP_ALIGN.LEFT
    for i, p in enumerate(paragraphs):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = pp_align
        run = para.add_run()
        run.text = p['text']
        run.font.size = Pt(p.get('size', 10))
        run.font.bold = p.get('bold', False)
        run.font.italic = p.get('italic', False)
        run.font.name = 'Calibri'
        if 'color' in p:
            run.font.color.rgb = p['color']
    return tb


# Connection point indices for preset shapes (roundRect, diamond):
#   0 = top center, 1 = right center, 2 = bottom center, 3 = left center
_CXN = {
    0: (0.5, 0.0),
    1: (1.0, 0.5),
    2: (0.5, 1.0),
    3: (0.0, 0.5),
}

def _pt(shp, idx):
    fx, fy = _CXN[idx]
    return shp.left + int(shp.width * fx), shp.top + int(shp.height * fy)


def arrow(src, src_idx, dst, dst_idx, ctype=MSO_CONNECTOR.ELBOW):
    """Add an arrowhead connector wired to src and dst shapes."""
    sx, sy = _pt(src, src_idx)
    dx, dy = _pt(dst, dst_idx)
    conn = slide.shapes.add_connector(ctype, sx, sy, dx, dy)
    conn.line.color.rgb = C_ARROW
    conn.line.width = Pt(1.6)

    # Arrowhead at the destination end
    ln = conn.line._get_or_add_ln()
    tail = etree.SubElement(ln, qn('a:tailEnd'))
    tail.set('type', 'triangle')
    tail.set('w', 'med')
    tail.set('len', 'med')

    # Wire stCxn / endCxn so PowerPoint knows which shapes are connected
    cNvCxnSpPr = (conn._element
                  .find(qn('p:nvCxnSpPr'))
                  .find(qn('p:cNvCxnSpPr')))
    etree.SubElement(cNvCxnSpPr, qn('a:stCxn'),
                     {'id': str(src.shape_id), 'idx': str(src_idx)})
    etree.SubElement(cNvCxnSpPr, qn('a:endCxn'),
                     {'id': str(dst.shape_id), 'idx': str(dst_idx)})
    return conn


S = MSO_CONNECTOR.STRAIGHT
E = MSO_CONNECTOR.ELBOW


# ═══════════════════════════════════════════════════════════════════════════
# SHAPES  (create first so IDs are known before connectors reference them)
# ═══════════════════════════════════════════════════════════════════════════

# Title
add_textbox(5, 0.40, 9, 0.45, [
    {'text': 'Evaluation of Suspected Exercise-Induced Bronchoconstriction',
     'size': 16, 'bold': True, 'color': C_TITLE}])
add_textbox(5, 0.78, 9, 0.30, [
    {'text': 'A clinical decision pathway',
     'size': 10.5, 'italic': True, 'color': C_GRAY_TX}])

# Header chip
sym = add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 5, 1.20, 4.0, 0.50,
                fill=C_HEADER_FILL, line_color=C_HEADER_FILL)
set_text(sym, [{'text': 'Symptoms suggestive of EIB',
                'size': 13, 'bold': True, 'color': C_HEADER_TX}])

# Spirometry
spi = add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 5, 1.95, 3.6, 0.50,
                fill=C_ACTION_F, line_color=C_ACTION_E)
set_text(spi, [{'text': 'Baseline spirometry',
                'size': 13, 'bold': True, 'color': C_TEXT}])

# Branch labels (floating, no connections needed)
add_textbox(2.3, 2.36, 2.8, 0.22,
            [{'text': 'Airflow obstruction', 'size': 10, 'bold': True, 'color': C_TITLE}])
add_textbox(7.7, 2.36, 2.8, 0.22,
            [{'text': 'Normal spirometry', 'size': 10, 'bold': True, 'color': C_TITLE}])

# ── Left branch ────────────────────────────────────────────────────────────
bdr = add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 2.3, 3.05, 2.9, 0.55,
                fill=C_ACTION_F, line_color=C_ACTION_E)
set_text(bdr, [{'text': 'Bronchodilator reversibility testing',
                'size': 11, 'bold': True, 'color': C_TEXT}])

rev = add_shape(MSO_SHAPE.DIAMOND, 2.3, 4.00, 2.4, 0.80,
                fill=C_DECISION_F, line_color=C_DECISION_E)
set_text(rev, [{'text': 'Reversible?¹', 'size': 12, 'bold': True, 'color': C_TEXT}])

ast = add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 1.10, 4.78, 1.85, 0.55,
                fill=C_TREAT_F, line_color=C_TREAT_E)
set_text(ast, [{'text': 'Treat as asthma + EIB',
                'size': 11, 'bold': True, 'color': C_TEXT}])

# ── Right branch ───────────────────────────────────────────────────────────
sab = add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 7.7, 3.05, 3.4, 0.55,
                fill=C_ACTION_F, line_color=C_ACTION_E)
set_text(sab, [{'text': 'Empiric pre-exercise SABA (15–30 min before exercise)',
                'size': 11, 'bold': True, 'color': C_TEXT}])

res = add_shape(MSO_SHAPE.DIAMOND, 7.7, 4.00, 2.4, 0.80,
                fill=C_DECISION_F, line_color=C_DECISION_E)
set_text(res, [{'text': 'Symptoms\nresolved?²', 'size': 12, 'bold': True, 'color': C_TEXT}])

con = add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 8.90, 4.78, 1.95, 0.55,
                fill=C_TREAT_F, line_color=C_TREAT_E)
set_text(con, [{'text': 'Continue pre-exercise SABA',
                'size': 11, 'bold': True, 'color': C_TEXT}])

# ── Bronchoprovocation ─────────────────────────────────────────────────────
bp = add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 5, 6.75, 6.2, 1.20,
               fill=C_ACTION_F, line_color=C_ACTION_E)
set_text(bp, [
    {'text': 'Bronchoprovocation testing³',
     'size': 13.5, 'bold': True, 'color': C_TEXT},
    {'text': '(indirect tests preferred)',
     'size': 10.5, 'italic': True, 'color': C_SUB_TX},
    {'text': ' ', 'size': 4},
    {'text': 'Also consider when formal/objective documentation is required',
     'size': 10, 'color': C_TEXT},
    {'text': '(e.g., elite athletes, military service, insurance, occupational clearance)',
     'size': 10, 'color': C_TEXT},
])

# ── Result ─────────────────────────────────────────────────────────────────
pos = add_shape(MSO_SHAPE.DIAMOND, 5, 8.05, 2.4, 0.80,
                fill=C_DECISION_F, line_color=C_DECISION_E)
set_text(pos, [{'text': 'Positive\nresult?⁴', 'size': 12, 'bold': True, 'color': C_TEXT}])

dxs = add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 3.80, 8.83, 2.0, 0.55,
                fill=C_TREAT_F, line_color=C_TREAT_E)
set_text(dxs, [{'text': 'Diagnose & treat EIB',
                'size': 12, 'bold': True, 'color': C_TEXT}])

alt = add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 6.20, 8.83, 2.5, 0.55,
                fill=C_ALT_F, line_color=C_ALT_E)
set_text(alt, [{'text': 'Evaluate for alternative diagnoses',
                'size': 11, 'bold': True, 'color': C_TEXT}])


# ═══════════════════════════════════════════════════════════════════════════
# CONNECTED ARROWS  (created after shapes so shape IDs are stable)
# ═══════════════════════════════════════════════════════════════════════════
#   Connection point index: 0=top  1=right  2=bottom  3=left

arrow(sym, 2, spi, 0, S)   # symptoms → spirometry
arrow(spi, 2, bdr, 0, E)   # spirometry → bronchodilator (elbow left)
arrow(spi, 2, sab, 0, E)   # spirometry → SABA (elbow right)
arrow(bdr, 2, rev, 0, S)   # bronchodilator → reversible?
arrow(rev, 3, ast, 0, E)   # reversible Yes → treat asthma
arrow(rev, 2, bp,  0, E)   # reversible No  → bronchoprovocation
arrow(sab, 2, res, 0, S)   # SABA → symptoms resolved?
arrow(res, 1, con, 0, E)   # resolved Yes → continue SABA
arrow(res, 2, bp,  0, E)   # resolved No  → bronchoprovocation
arrow(bp,  2, pos, 0, S)   # bronchoprovocation → positive result?
arrow(pos, 3, dxs, 0, E)   # positive → diagnose EIB
arrow(pos, 1, alt, 0, E)   # negative → alternative diagnoses

# Yes/No labels (floating textboxes)
add_textbox(0.90, 4.06, 0.7, 0.22,
            [{'text': 'Yes', 'size': 10.5, 'bold': True,
              'italic': True, 'color': C_YES}], align='center')
add_textbox(2.52, 4.46, 0.5, 0.22,
            [{'text': 'No', 'size': 10.5, 'bold': True,
              'italic': True, 'color': C_NO}], align='center')
add_textbox(9.08, 4.06, 0.7, 0.22,
            [{'text': 'Yes', 'size': 10.5, 'bold': True,
              'italic': True, 'color': C_YES}], align='center')
add_textbox(7.92, 4.46, 0.5, 0.22,
            [{'text': 'No', 'size': 10.5, 'bold': True,
              'italic': True, 'color': C_NO}], align='center')
add_textbox(3.55, 8.11, 0.9, 0.22,
            [{'text': 'Positive', 'size': 10.5, 'bold': True,
              'italic': True, 'color': C_YES}], align='center')
add_textbox(6.45, 8.11, 0.9, 0.22,
            [{'text': 'Negative', 'size': 10.5, 'bold': True,
              'italic': True, 'color': C_NO}], align='center')


# ═══════════════════════════════════════════════════════════════════════════
# LEGEND
# ═══════════════════════════════════════════════════════════════════════════

add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 5.0, 11.55, 9.4, 3.2,
          fill=C_LEGEND_BG, line_color=C_LEGEND_EDGE, line_w=1.0)

add_textbox(5.0, 10.20, 9.0, 0.32, [
    {'text': 'Key Definitions & Diagnostic Criteria',
     'size': 12, 'bold': True, 'color': C_TITLE}])

# Divider
div = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,
                                  I(0.9), I(10.42), I(9.1), I(10.42))
div.line.color.rgb = C_LEGEND_EDGE
div.line.width = Pt(0.8)

notes = [
    ('¹  Reversible — ',
     'FEV₁ increase ≥12% AND ≥200 mL after bronchodilator (supports asthma).'),
    ('²  Important — ',
     'Symptom improvement alone does NOT confirm EIB. '
     'Normal resting spirometry does NOT exclude EIB.'),
    ('³  Indirect tests (preferred) — ',
     'standardized exercise challenge, eucapnic voluntary hyperpnea (EVH), '
     'mannitol challenge, or hypertonic saline challenge. '
     'Direct (methacholine) is less specific for EIB.'),
    ('⁴  Positive bronchoprovocation — ',
     'FEV₁ ↓ ≥10% from baseline (exercise / EVH);   '
     'FEV₁ ↓ ≥15% (mannitol / hypertonic saline).'),
]
y = 10.65
for key, body in notes:
    tb = slide.shapes.add_textbox(I(0.7), I(y), I(8.6), I(0.62))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = I(0.02)
    tf.margin_top = tf.margin_bottom = I(0.02)
    para = tf.paragraphs[0]
    para.alignment = PP_ALIGN.LEFT
    for txt, bold, color in [(key, True, C_TITLE), (body, False, C_TEXT)]:
        r = para.add_run()
        r.text = txt
        r.font.size = Pt(10.5)
        r.font.bold = bold
        r.font.color.rgb = color
        r.font.name = 'Calibri'
    y += 0.62

add_textbox(5.0, 13.45, 9.2, 0.30, [
    {'text': ('EIB = exercise-induced bronchoconstriction   |   '
              'SABA = short-acting β₂-agonist   |   '
              'EVH = eucapnic voluntary hyperpnea   |   '
              'FEV₁ = forced expiratory volume in 1 second'),
     'size': 8.5, 'italic': True, 'color': C_GRAY_TX}])


# ─── Save ──────────────────────────────────────────────────────────────────
out = '/home/user/bronchoclaude/spirometry_pathway.pptx'
prs.save(out)
print(f'Saved {out}')
