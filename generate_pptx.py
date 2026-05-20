#!/usr/bin/env python3
"""Generate an editable PowerPoint version of the EIB spirometry pathway.

Every box, diamond, arrow, and label is a native PowerPoint shape, so the
clinician can drag, recolor, resize, or edit text directly in PowerPoint.
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

# ── Palette (RGB) ─────────────────────────────────────────────────────────
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

# ── Slide setup ───────────────────────────────────────────────────────────
prs = Presentation()
prs.slide_width  = Inches(10)
prs.slide_height = Inches(14)

slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank


# ── Helpers ───────────────────────────────────────────────────────────────
def shape(shp_type, cx, cy, w, h, fill=None, line=None, line_w=1.5):
    """Add a shape centered at (cx, cy) in inches; return the shape."""
    s = slide.shapes.add_shape(
        shp_type,
        Inches(cx - w / 2), Inches(cy - h / 2),
        Inches(w), Inches(h),
    )
    if fill is not None:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is not None:
        s.line.color.rgb = line
        s.line.width = Pt(line_w)
    s.shadow.inherit = False
    return s


def set_text(shp, runs, vertical='middle'):
    """Set text in a shape. `runs` is a list of paragraph dicts:
       [{'text': str, 'size': float, 'bold': bool, 'italic': bool,
         'color': RGBColor}]  – each entry becomes its own paragraph."""
    tf = shp.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.06)
    tf.margin_right = Inches(0.06)
    tf.margin_top = Inches(0.03)
    tf.margin_bottom = Inches(0.03)
    if vertical == 'middle':
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    elif vertical == 'top':
        tf.vertical_anchor = MSO_ANCHOR.TOP

    for i, r in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        # clear any default run text
        for child in list(p._pPr.getparent()) if p._pPr is not None else []:
            pass
        run = p.add_run()
        run.text = r['text']
        run.font.size = Pt(r.get('size', 10))
        run.font.bold = r.get('bold', False)
        run.font.italic = r.get('italic', False)
        run.font.name = 'Calibri'
        if 'color' in r:
            run.font.color.rgb = r['color']


def textbox(cx, cy, w, h, runs, align='center', vertical='top'):
    """Add a plain textbox (no fill/border)."""
    tb = slide.shapes.add_textbox(
        Inches(cx - w / 2), Inches(cy - h / 2), Inches(w), Inches(h)
    )
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    if vertical == 'middle':
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    elif vertical == 'top':
        tf.vertical_anchor = MSO_ANCHOR.TOP

    for i, r in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        if align == 'center':
            p.alignment = PP_ALIGN.CENTER
        elif align == 'left':
            p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = r['text']
        run.font.size = Pt(r.get('size', 10))
        run.font.bold = r.get('bold', False)
        run.font.italic = r.get('italic', False)
        run.font.name = 'Calibri'
        if 'color' in r:
            run.font.color.rgb = r['color']
    return tb


def line_or_arrow(x1, y1, x2, y2, arrow=False, color=None, width=1.5):
    conn = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT,
        Inches(x1), Inches(y1), Inches(x2), Inches(y2),
    )
    conn.line.color.rgb = color if color is not None else C_ARROW
    conn.line.width = Pt(width)
    if arrow:
        ln = conn.line._get_or_add_ln()
        tail = etree.SubElement(ln, qn('a:tailEnd'))
        tail.set('type', 'triangle')
        tail.set('w', 'med')
        tail.set('len', 'med')
    return conn


def line(x1, y1, x2, y2, color=None, width=1.5):
    return line_or_arrow(x1, y1, x2, y2, arrow=False, color=color, width=width)


def arrow(x1, y1, x2, y2, color=None, width=1.5):
    return line_or_arrow(x1, y1, x2, y2, arrow=True, color=color, width=width)


# ══════════════════════════════════════════════════════════════════════════
# CHART
# ══════════════════════════════════════════════════════════════════════════

# ── Title ─────────────────────────────────────────────────────────────────
textbox(5, 0.4, 9, 0.45, [
    {'text': 'Evaluation of Suspected Exercise-Induced Bronchoconstriction',
     'size': 16, 'bold': True, 'color': C_TITLE},
], vertical='middle')
textbox(5, 0.78, 9, 0.3, [
    {'text': 'A clinical decision pathway',
     'size': 10.5, 'italic': True, 'color': C_GRAY_TX},
], vertical='middle')

# ── 1. Symptoms header chip ───────────────────────────────────────────────
s = shape(MSO_SHAPE.ROUNDED_RECTANGLE, 5, 1.20, 4.0, 0.50,
          fill=C_HEADER_FILL, line=C_HEADER_FILL)
set_text(s, [{'text': 'Symptoms suggestive of EIB',
              'size': 13, 'bold': True, 'color': C_HEADER_TX}])
arrow(5, 1.45, 5, 1.70)

# ── 2. Spirometry ─────────────────────────────────────────────────────────
s = shape(MSO_SHAPE.ROUNDED_RECTANGLE, 5, 1.95, 3.6, 0.50,
          fill=C_ACTION_F, line=C_ACTION_E)
set_text(s, [{'text': 'Baseline spirometry',
              'size': 13, 'bold': True, 'color': C_TEXT}])

# Branch lines from spirometry
line(5, 2.20, 5, 2.45)
line(2.3, 2.45, 7.7, 2.45)
arrow(2.3, 2.45, 2.3, 2.75)
arrow(7.7, 2.45, 7.7, 2.75)
textbox(2.3, 2.36, 2.6, 0.22, [
    {'text': 'Airflow obstruction',
     'size': 10, 'bold': True, 'color': C_TITLE}], vertical='middle')
textbox(7.7, 2.36, 2.6, 0.22, [
    {'text': 'Normal spirometry',
     'size': 10, 'bold': True, 'color': C_TITLE}], vertical='middle')

# ══════════════════════ LEFT BRANCH ═══════════════════════════════════════
s = shape(MSO_SHAPE.ROUNDED_RECTANGLE, 2.3, 3.05, 2.9, 0.55,
          fill=C_ACTION_F, line=C_ACTION_E)
set_text(s, [{'text': 'Bronchodilator\nreversibility testing',
              'size': 11, 'bold': True, 'color': C_TEXT}])
arrow(2.3, 3.325, 2.3, 3.60)

# Decision diamond
s = shape(MSO_SHAPE.DIAMOND, 2.3, 4.00, 2.4, 0.80,
          fill=C_DECISION_F, line=C_DECISION_E)
set_text(s, [{'text': 'Reversible?¹',
              'size': 12, 'bold': True, 'color': C_TEXT}])

# Yes → left
arrow(1.10, 4.00, 1.10, 4.50)
textbox(1.0, 4.05, 0.6, 0.22, [
    {'text': 'Yes', 'size': 11, 'bold': True, 'italic': True, 'color': C_YES}],
    align='center', vertical='middle')
s = shape(MSO_SHAPE.ROUNDED_RECTANGLE, 1.10, 4.78, 1.85, 0.55,
          fill=C_TREAT_F, line=C_TREAT_E)
set_text(s, [{'text': 'Treat as\nasthma + EIB',
              'size': 11, 'bold': True, 'color': C_TEXT}])

# No → down (to merge)
textbox(2.50, 4.45, 0.4, 0.22, [
    {'text': 'No', 'size': 11, 'bold': True, 'italic': True, 'color': C_NO}],
    align='left', vertical='middle')
line(2.3, 4.40, 2.3, 5.85)

# ══════════════════════ RIGHT BRANCH ══════════════════════════════════════
s = shape(MSO_SHAPE.ROUNDED_RECTANGLE, 7.7, 3.05, 3.4, 0.55,
          fill=C_ACTION_F, line=C_ACTION_E)
set_text(s, [{'text': 'Empiric pre-exercise SABA\n(15–30 min before exercise)',
              'size': 11, 'bold': True, 'color': C_TEXT}])
arrow(7.7, 3.325, 7.7, 3.60)

s = shape(MSO_SHAPE.DIAMOND, 7.7, 4.00, 2.4, 0.80,
          fill=C_DECISION_F, line=C_DECISION_E)
set_text(s, [{'text': 'Symptoms\nresolved?²',
              'size': 12, 'bold': True, 'color': C_TEXT}])

# Yes → right
arrow(8.90, 4.00, 8.90, 4.50)
textbox(9.00, 4.05, 0.6, 0.22, [
    {'text': 'Yes', 'size': 11, 'bold': True, 'italic': True, 'color': C_YES}],
    align='center', vertical='middle')
s = shape(MSO_SHAPE.ROUNDED_RECTANGLE, 8.90, 4.78, 1.95, 0.55,
          fill=C_TREAT_F, line=C_TREAT_E)
set_text(s, [{'text': 'Continue\npre-exercise SABA',
              'size': 11, 'bold': True, 'color': C_TEXT}])

# No → down (to merge)
textbox(7.90, 4.45, 0.4, 0.22, [
    {'text': 'No', 'size': 11, 'bold': True, 'italic': True, 'color': C_NO}],
    align='left', vertical='middle')
line(7.7, 4.40, 7.7, 5.85)

# ══════════════════════ MERGE → BRONCHOPROVOCATION ════════════════════════
line(2.3, 5.85, 7.7, 5.85)
arrow(5, 5.85, 5, 6.15)

# Bronchoprovocation box — title + indications blurb
s = shape(MSO_SHAPE.ROUNDED_RECTANGLE, 5, 6.75, 6.2, 1.20,
          fill=C_ACTION_F, line=C_ACTION_E)
set_text(s, [
    {'text': 'Bronchoprovocation testing³',
     'size': 13.5, 'bold': True, 'color': C_TEXT},
    {'text': '(indirect tests preferred)',
     'size': 10.5, 'italic': True, 'color': C_SUB_TX},
    {'text': ' ', 'size': 4, 'color': C_TEXT},
    {'text': 'Also consider when formal/objective documentation is required',
     'size': 10, 'color': C_TEXT},
    {'text': '(e.g., elite athletes, military service, insurance, occupational clearance)',
     'size': 10, 'color': C_TEXT},
])

arrow(5, 7.35, 5, 7.65)

# Result diamond
s = shape(MSO_SHAPE.DIAMOND, 5, 8.05, 2.4, 0.80,
          fill=C_DECISION_F, line=C_DECISION_E)
set_text(s, [{'text': 'Positive\nresult?⁴',
              'size': 12, 'bold': True, 'color': C_TEXT}])

# Positive (left corner: 5 - 1.2 = 3.8)
arrow(3.80, 8.05, 3.80, 8.55)
textbox(3.45, 8.10, 0.7, 0.22, [
    {'text': 'Positive', 'size': 10.5, 'bold': True, 'italic': True,
     'color': C_YES}], align='right', vertical='middle')
s = shape(MSO_SHAPE.ROUNDED_RECTANGLE, 3.80, 8.83, 2.0, 0.55,
          fill=C_TREAT_F, line=C_TREAT_E)
set_text(s, [{'text': 'Diagnose &\ntreat EIB',
              'size': 12, 'bold': True, 'color': C_TEXT}])

# Negative (right corner: 5 + 1.2 = 6.2)
arrow(6.20, 8.05, 6.20, 8.55)
textbox(6.55, 8.10, 0.8, 0.22, [
    {'text': 'Negative', 'size': 10.5, 'bold': True, 'italic': True,
     'color': C_NO}], align='left', vertical='middle')
s = shape(MSO_SHAPE.ROUNDED_RECTANGLE, 6.20, 8.83, 2.5, 0.55,
          fill=C_ALT_F, line=C_ALT_E)
set_text(s, [{'text': 'Evaluate for\nalternative diagnoses',
              'size': 11, 'bold': True, 'color': C_TEXT}])

# ══════════════════════ LEGEND ════════════════════════════════════════════
legend = shape(MSO_SHAPE.ROUNDED_RECTANGLE, 5.0, 11.55, 9.4, 3.2,
               fill=C_LEGEND_BG, line=C_LEGEND_EDGE, line_w=1.0)

# Legend header (as separate textbox so it sits visually inside)
textbox(5.0, 10.20, 9.0, 0.32, [
    {'text': 'Key Definitions & Diagnostic Criteria',
     'size': 12, 'bold': True, 'color': C_TITLE}], vertical='middle')

# Underline divider
line(0.9, 10.42, 9.1, 10.42, color=C_LEGEND_EDGE, width=0.8)

# Numbered notes — one textbox per note for easy editing
notes = [
    ('¹  Reversible — ',
     'FEV₁ increase ≥12% AND ≥200 mL after bronchodilator (supports asthma).'),
    ('²  Important — ',
     'Symptom improvement alone does NOT confirm EIB. Normal resting spirometry does NOT exclude EIB.'),
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
    tb = slide.shapes.add_textbox(
        Inches(0.7), Inches(y), Inches(8.6), Inches(0.62)
    )
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)

    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r1 = p.add_run()
    r1.text = key
    r1.font.size = Pt(10.5)
    r1.font.bold = True
    r1.font.color.rgb = C_TITLE
    r1.font.name = 'Calibri'

    r2 = p.add_run()
    r2.text = body
    r2.font.size = Pt(10.5)
    r2.font.color.rgb = C_TEXT
    r2.font.name = 'Calibri'

    y += 0.62

# Abbreviations footer
textbox(5.0, 13.45, 9.2, 0.30, [
    {'text': ('EIB = exercise-induced bronchoconstriction   |   '
              'SABA = short-acting β₂-agonist   |   '
              'EVH = eucapnic voluntary hyperpnea   |   '
              'FEV₁ = forced expiratory volume in 1 second'),
     'size': 8.5, 'italic': True, 'color': C_GRAY_TX}],
    vertical='middle')

# ── Save ──────────────────────────────────────────────────────────────────
out = '/home/user/bronchoclaude/spirometry_pathway.pptx'
prs.save(out)
print(f'Saved {out}')
