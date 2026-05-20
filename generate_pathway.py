#!/usr/bin/env python3
"""EIB Spirometry Pathway – AFP rapid evidence review style"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

fig, ax = plt.subplots(figsize=(16, 24))
ax.set_xlim(0, 16)
ax.set_ylim(0, 24)
ax.axis('off')
fig.patch.set_facecolor('white')

LW = 0.8
FS = 8.5
FSS = 7.5
FST = 7.0


def rect(cx, cy, w, h, text, fs=FS, bold=False, lw=LW):
    p = FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                       boxstyle="square,pad=0.04",
                       fc='white', ec='black', lw=lw, zorder=3)
    ax.add_patch(p)
    ax.text(cx, cy, text, ha='center', va='center', fontsize=fs,
            multialignment='center', linespacing=1.4,
            fontweight='bold' if bold else 'normal', zorder=4)


def diam(cx, cy, w, h, text, fs=FSS):
    pts = [[cx, cy + h / 2], [cx + w / 2, cy],
           [cx, cy - h / 2], [cx - w / 2, cy]]
    p = Polygon(pts, fc='white', ec='black', lw=LW, zorder=3)
    ax.add_patch(p)
    ax.text(cx, cy, text, ha='center', va='center', fontsize=fs,
            multialignment='center', linespacing=1.4, zorder=4)


def arr(x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='black', lw=LW,
                                mutation_scale=10), zorder=5)


def ln(*pts):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, 'k-', lw=LW, zorder=2)


def lbl(x, y, text, fs=FSS, ha='center', va='center', italic=True):
    ax.text(x, y, text, ha=ha, va=va, fontsize=fs,
            style='italic' if italic else 'normal', zorder=6)


# ── Title ─────────────────────────────────────────────────────────────────────
ax.text(8, 23.55,
        'Algorithm for the Evaluation of Suspected Exercise-Induced Bronchoconstriction (EIB)',
        ha='center', va='center', fontsize=10, fontweight='bold', zorder=4)

# ── Symptoms box ──────────────────────────────────────────────────────────────
rect(8, 23.0, 5.5, 0.65, 'Symptoms suggestive of EIB', bold=True, fs=FS)
arr(8, 22.675, 8, 22.2)

# ── Spirometry box ────────────────────────────────────────────────────────────
rect(8, 21.85, 9.5, 0.8,
     'Perform baseline spirometry\n'
     'Normal result does not exclude EIB;\n'
     'assess for asthma or obstructive lung disease',
     fs=FSS)

# Branch lines from spirometry
ln((8, 21.45), (8, 21.05), (3.0, 21.05))
ln((8, 21.05), (13.0, 21.05))
arr(3.0, 21.05, 3.0, 20.6)
arr(13.0, 21.05, 13.0, 20.6)
lbl(3.0, 21.18, 'Airflow obstruction')
lbl(13.0, 21.18, 'Normal spirometry')

# ═════════════════════════════════════════════════════════════════════════════
# LEFT BRANCH – Abnormal spirometry
# ═════════════════════════════════════════════════════════════════════════════

rect(3.0, 20.2, 4.2, 0.65,
     'Bronchodilator reversibility\ntesting', fs=FS)
arr(3.0, 19.875, 3.0, 19.25)

diam(3.0, 18.75, 3.8, 1.0,
     'FEV₁ increase ≥12%\nand 200 mL after\nbronchodilator?')

# Yes – left corner: 3.0 - 3.8/2 = 1.1
arr(1.1, 18.75, 1.1, 17.9)
lbl(1.0, 18.78, 'Yes', ha='right')
rect(1.1, 17.55, 2.0, 0.65,
     'Supports asthma;\ntreat for asthma\nand EIB', fs=FS)

# No – bottom corner: y = 18.75 - 0.5 = 18.25
lbl(3.15, 18.25, 'No', ha='left')
ln((3.0, 18.25), (3.0, 15.65))

# ═════════════════════════════════════════════════════════════════════════════
# RIGHT BRANCH – Normal spirometry
# ═════════════════════════════════════════════════════════════════════════════

rect(13.0, 20.2, 5.0, 0.95,
     'Empiric pre-exercise SABA trial\n(15–30 min before exercise)\n'
     'Symptom improvement alone\ndoes not confirm EIB',
     fs=FSS)

arr(13.0, 19.725, 13.0, 19.15)

diam(13.0, 18.7, 3.8, 0.9, 'Adequate\nresponse?')

# Yes – right corner: 13.0 + 3.8/2 = 14.9
arr(14.9, 18.7, 14.9, 17.85)
lbl(15.05, 18.73, 'Yes', ha='left')
rect(14.9, 17.5, 2.1, 0.65,
     'Continue\npre-exercise SABA', fs=FS)

# No – bottom corner: y = 18.7 - 0.45 = 18.25
lbl(13.15, 18.25, 'No', ha='left')
ln((13.0, 18.25), (13.0, 16.45))

# Small box on right "No" path for context
rect(13.0, 16.1, 5.0, 0.6,
     'Persistent symptoms, diagnostic uncertainty,\nor need for objective documentation',
     fs=6.5)
ln((13.0, 15.8), (13.0, 15.65))

# ═════════════════════════════════════════════════════════════════════════════
# MERGE → Bronchoprovocation
# ═════════════════════════════════════════════════════════════════════════════

ln((3.0, 15.65), (13.0, 15.65))
arr(8.0, 15.65, 8.0, 15.2)

# ── Bronchoprovocation box ────────────────────────────────────────────────────
rect(8.0, 14.65, 10.5, 0.9,
     'Bronchoprovocation testing\n'
     'Indirect tests preferred: standardized exercise challenge, eucapnic voluntary\n'
     'hyperpnea (EVH), mannitol challenge, or hypertonic saline challenge',
     fs=FSS)

lbl(8.0, 14.0,
    'Direct bronchoprovocation (methacholine challenge): may identify airway hyperresponsiveness; '
    'less specific for EIB',
    fs=6.5)

arr(8.0, 13.78, 8.0, 13.25)

# ── Result diamond ────────────────────────────────────────────────────────────
diam(8.0, 12.7, 9.5, 1.1,
     'Positive result?\n'
     'FEV₁ ↓ ≥10% from baseline (exercise challenge or EVH)\n'
     'FEV₁ ↓ ≥15% from baseline (mannitol or hypertonic saline)')

# Positive – left corner: 8.0 - 9.5/2 = 3.25
arr(3.25, 12.7, 3.25, 11.9)
lbl(3.1, 12.73, 'Positive', ha='right')
rect(3.25, 11.55, 2.8, 0.65, 'Confirm EIB;\ntreat', fs=FS)

# Negative – right corner: 8.0 + 9.5/2 = 12.75
arr(12.75, 12.7, 12.75, 11.9)
lbl(12.9, 12.73, 'Negative', ha='left')
rect(12.75, 11.55, 3.5, 0.65,
     'Evaluate for\nalternative diagnoses', fs=FS)

# ── Abbreviations / footnote ──────────────────────────────────────────────────
lbl(8.0, 0.55,
    'EIB = exercise-induced bronchoconstriction  |  EVH = eucapnic voluntary hyperpnea  |  '
    'SABA = short-acting β₂-agonist  |  FEV₁ = forced expiratory volume in 1 second',
    fs=6.5, italic=False)
lbl(8.0, 0.22, 'Adapted from references 1, 3, 4, 5.', fs=6.5)

plt.savefig('/home/user/bronchoclaude/spirometry_pathway.png',
            dpi=200, bbox_inches='tight', facecolor='white', format='png')
print('Saved spirometry_pathway.png')
