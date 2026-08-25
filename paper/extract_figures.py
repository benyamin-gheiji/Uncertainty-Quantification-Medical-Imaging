"""Extract the real (matplotlib) output figures from the implementation notebooks.

Figures are identified by session number and the ordinal of the figure-producing
code cell within that notebook, as inventoried from the notebook outputs.
"""
import base64
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# (session, figure-cell ordinal, image index within cell, output filename)
WANTED = [
    (10, 1, 0, "uncertainty_decomposition_ensembles.png"),
    (16, 1, 0, "calibration_temperature_scaling.png"),
    (17, 4, 0, "risk_coverage_all_methods.png"),
    (18, 6, 0, "ood_roc_all_methods.png"),
    (18, 7, 0, "ood_qualitative.png"),
]


def notebook_for(sid: int) -> Path:
    hits = sorted((REPO / f"session {sid:02d}").glob("*.ipynb"))
    if not hits:
        raise SystemExit(f"no notebook for session {sid}")
    return hits[0]


def figure_cells(nb):
    """Code cells that emitted at least one PNG, in document order."""
    out = []
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        imgs = [o["data"]["image/png"] for o in c.get("outputs", [])
                if "image/png" in o.get("data", {})]
        if imgs:
            out.append(imgs)
    return out


for sid, cell_ord, img_idx, name in WANTED:
    nb = json.loads(notebook_for(sid).read_text(encoding="utf-8"))
    cells = figure_cells(nb)
    if cell_ord >= len(cells):
        print(f"!! session {sid}: only {len(cells)} figure cells, wanted #{cell_ord}")
        continue
    imgs = cells[cell_ord]
    if img_idx >= len(imgs):
        print(f"!! session {sid} cell {cell_ord}: only {len(imgs)} images")
        continue
    b64 = imgs[img_idx]
    if isinstance(b64, list):
        b64 = "".join(b64)
    data = base64.b64decode(b64)
    (OUT / name).write_bytes(data)
    print(f"  {name:44s} {len(data)/1024:7.1f} KB   (session {sid})")

print(f"\nwrote {len(list(OUT.glob('*.png')))} figures to {OUT}")
