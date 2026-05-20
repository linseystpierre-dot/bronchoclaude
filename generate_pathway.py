#!/usr/bin/env python3
"""EIB Spirometry Pathway - clinical pocket-card style."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

# ── Palette ───────────────────────────────────────────────────────────────
C_BG          = '#FAFAFA'
C_TITLE       = '#1F4E5F'
C_HEADER_FILL = '#2C5F7C'
C_HEADER_TX   = '#FFFFFF'
C_ACTION_F    = '#E1ECF4'
C_ACTION_E    = '#3A7CA5'
C_DECISION_F  = '#FFF4D6'
C_DECISION_E  = '#C68A00'
C_TREAT_F     = '#DCEEDC'
C_TREAT_E     = '#3D8B3D'
C_ALT_F       = '#F8E0DC'
C_ALT_E       = '#B0524C'
C_TEXT        = '#1A1A1A'
C_ARROW       = '#3A3A3A'
C_LEGEND_BG   = '#F2F2F2'
C_LEGEND_EDGE = '#B0B0B0'
C_YES         = '#3D8B3D'
C_NO          = '#B0524C'

plt.rcParams['font.family'] = 'DejaVu Sans'

fig, ax = plt.subplots(figsize=(13, 18))
ax.set_xlim(0, 13)
ax.set_ylim(0, 18)
ax.axis('off')
fig.patch.set_facecolor(C_BG)
ax.set_facecolor(C_BG)


def rrect(cx, cy, w, h, text, fill, edge, fs=10, bold=False, text_color=None):
    if text_color is None:
        text_color = C_TEXT
    p = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                       boxstyle='round,pad=0.02,rounding_size=0.18',
                       fc=fill, ec=edge, lw=1.6, zorder=3)
    ax.add_patch(p)
    ax.text(cx, cy, text, ha='center', va='center', fontsize=fs,
            color=text_color, multialignment='center', linespacing=1.4,
            fontweight='bold' if bold else 'normal', zorder=4)


def diamond(cx, cy, w, h, text, fs=10):
    pts = [[cx, cy + h/2], [cx + w/2, cy],
           [cx, cy - h/2], [cx - w/2, cy]]
    p = Polygon(pts, fc=C_DECISION_F, ec=C_DECISION_E, lw=1.6, zorder=3)
    ax.add_patch(p)
    ax.text(cx, cy, text, ha='center', va='center', fontsize=fs,
            color=C_TEXT, multialignment='center', linespacing=1.35,
            fontweight='bold', zorder=4)


def arr(x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', color=C_ARROW, lw=1.6,
                                mutation_scale=14), zorder=5)


def ln(*pts):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=C_ARROW, lw=1.6, zorder=2)


def lbl(x, y, text, fs=9, ha='center', va='center', color='#444444', bold=True):
    ax.text(x, y, text, ha=ha, va=va, fontsize=fs, color=color,
            fontweight='bold' if bold else 'normal', zorder=6)


# ── Title ─────────────────────────────────────────────────────────────────
ax.text(6.5, 17.4,
        'Evaluation of Suspected Exercise-Induced Bronchoconstriction',
        ha='center', va='center', fontsize=15, fontweight='bold',
        color=C_TITLE)
ax.text(6.5, 16.95, 'A clinical decision pathway',
        ha='center', va='center', fontsize=10, style='italic',
        color='#666666')

# ── 1. Symptoms (header chip) ─────────────────────────────────────────────
rrect(6.5, 16.25, 5.6, 0.7,
      'Symptoms suggestive of EIB',
      C_HEADER_FILL, C_HEADER_FILL,
      fs=12, bold=True, text_color=C_HEADER_TX)
arr(6.5, 15.9, 6.5, 15.55)

# ── 2. Spirometry ─────────────────────────────────────────────────────────
rrect(6.5, 15.15, 4.8, 0.65,
      'Baseline spirometry',
      C_ACTION_F, C_ACTION_E, fs=12, bold=True)

# Branch lines
ln((6.5, 14.825), (6.5, 14.4))
ln((6.5, 14.4), (3.0, 14.4))
ln((6.5, 14.4), (10.0, 14.4))
arr(3.0, 14.4, 3.0, 13.95)
arr(10.0, 14.4, 10.0, 13.95)
lbl(3.0, 14.55, 'Airflow obstruction', fs=9, color=C_TITLE)
lbl(10.0, 14.55, 'Normal spirometry', fs=9, color=C_TITLE)

# ══════════════════════ LEFT BRANCH ═══════════════════════════════════════
rrect(3.0, 13.55, 4.0, 0.75,
      'Bronchodilator\nreversibility testing',
      C_ACTION_F, C_ACTION_E, fs=10.5, bold=True)
arr(3.0, 13.175, 3.0, 12.7)

diamond(3.0, 12.15, 3.4, 0.9, 'Reversible?¹', fs=11)

# Yes (left corner: 3.0 - 1.7 = 1.3)
arr(1.3, 12.15, 1.3, 11.5)
lbl(1.2, 12.2, 'Yes', fs=10, ha='right', color=C_YES)
rrect(1.3, 11.05, 2.2, 0.75,
      'Treat as asthma\n+ EIB',
      C_TREAT_F, C_TREAT_E, fs=10.5, bold=True)

# No (bottom corner)
lbl(3.18, 11.65, 'No', fs=10, ha='left', color=C_NO)
ln((3.0, 11.7), (3.0, 8.95))

# ══════════════════════ RIGHT BRANCH ══════════════════════════════════════
rrect(10.0, 13.55, 4.4, 0.75,
      'Empiric pre-exercise SABA\n(15–30 min before exercise)',
      C_ACTION_F, C_ACTION_E, fs=10.5, bold=True)
arr(10.0, 13.175, 10.0, 12.7)

diamond(10.0, 12.15, 3.4, 0.9, 'Symptoms\nresolved?²', fs=11)

# Yes (right corner: 10.0 + 1.7 = 11.7)
arr(11.7, 12.15, 11.7, 11.5)
lbl(11.8, 12.2, 'Yes', fs=10, ha='left', color=C_YES)
rrect(11.7, 11.05, 2.4, 0.75,
      'Continue\npre-exercise SABA',
      C_TREAT_F, C_TREAT_E, fs=10.5, bold=True)

# No (bottom corner)
lbl(10.18, 11.65, 'No', fs=10, ha='left', color=C_NO)
ln((10.0, 11.7), (10.0, 8.95))

# ══════════════════════ MERGE → BRONCHOPROVOCATION ═══════════════════════
ln((3.0, 8.95), (10.0, 8.95))
arr(6.5, 8.95, 6.5, 8.45)

rrect(6.5, 7.95, 5.6, 0.8,
      'Bronchoprovocation testing\n(indirect tests preferred)³',
      C_ACTION_F, C_ACTION_E, fs=11, bold=True)
arr(6.5, 7.55, 6.5, 6.95)

diamond(6.5, 6.4, 3.6, 0.9, 'Positive\nresult?⁴', fs=11)

# Positive (left corner: 6.5 - 1.8 = 4.7)
arr(4.7, 6.4, 4.7, 5.55)
lbl(4.55, 6.45, 'Positive', fs=10, ha='right', color=C_YES)
rrect(4.7, 5.1, 2.6, 0.75, 'Diagnose &\ntreat EIB',
      C_TREAT_F, C_TREAT_E, fs=11.5, bold=True)

# Negative (right corner)
arr(8.3, 6.4, 8.3, 5.55)
lbl(8.45, 6.45, 'Negative', fs=10, ha='left', color=C_NO)
rrect(8.3, 5.1, 3.3, 0.75,
      'Evaluate for\nalternative diagnoses',
      C_ALT_F, C_ALT_E, fs=10.5, bold=True)

# ══════════════════════ LEGEND / REFERENCE BOX ════════════════════════════
legend = FancyBboxPatch((0.3, 0.3), 12.4, 3.85,
                        boxstyle='round,pad=0.02,rounding_size=0.18',
                        fc=C_LEGEND_BG, ec=C_LEGEND_EDGE, lw=1.2, zorder=2)
ax.add_patch(legend)

# Legend header
ax.text(6.5, 3.85, 'Key Definitions & Diagnostic Criteria',
        ha='center', va='center', fontsize=11.5, fontweight='bold',
        color=C_TITLE, zorder=4)
ax.plot([1.0, 12.0], [3.6, 3.6], color=C_LEGEND_EDGE, lw=0.8, zorder=3)

# Numbered notes
notes = [
    ('¹  Reversible — ',
     'FEV₁ increase ≥12% AND ≥200 mL after bronchodilator (supports asthma).'),
    ('²  Important — ',
     'Symptom improvement alone does NOT confirm EIB. Normal resting spirometry does NOT exclude EIB.'),
    ('³  Indirect tests (preferred) — ',
     'standardized exercise challenge, eucapnic voluntary hyperpnea (EVH),\n      mannitol challenge, or hypertonic saline challenge.   Direct (methacholine) is less specific for EIB.'),
    ('⁴  Positive bronchoprovocation — ',
     'FEV₁ ↓ ≥10% from baseline (exercise / EVH);   FEV₁ ↓ ≥15% (mannitol / hypertonic saline).'),
    ('Persistent symptoms despite SABA, diagnostic uncertainty, or need for objective documentation → bronchoprovocation.',
     ''),
]

y = 3.2
for key, body in notes:
    ax.text(0.8, y, key, ha='left', va='top', fontsize=9.2,
            fontweight='bold', color=C_TITLE, zorder=4)
    if body:
        # Compute offset by character width approximation; use separate line if too long
        ax.text(0.8, y - 0.32, body, ha='left', va='top', fontsize=9.2,
                color=C_TEXT, zorder=4, linespacing=1.4)
        y -= 0.78
    else:
        y -= 0.45

# Abbreviations footer
ax.text(6.5, 0.5,
        'EIB = exercise-induced bronchoconstriction   |   '
        'SABA = short-acting β₂-agonist   |   '
        'EVH = eucapnic voluntary hyperpnea   |   '
        'FEV₁ = forced expiratory volume in 1 second',
        ha='center', va='center', fontsize=7.8, color='#555555',
        style='italic', zorder=4)

plt.savefig('/home/user/bronchoclaude/spirometry_pathway.png',
            dpi=200, bbox_inches='tight', facecolor=C_BG, format='png')
print('Saved spirometry_pathway.png')
