from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def export_csv(trades: Iterable[Dict], path: str | Path) -> None:
    trades_list = list(trades)
    if not trades_list:
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=trades_list[0].keys())
        writer.writeheader()
        writer.writerows(trades_list)


def export_pdf(summary: Dict[str, float], trades: Iterable[Dict], path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=letter)
    text = c.beginText(40, 750)
    text.textLine("LeekBot Daily Journal")
    for key, value in summary.items():
        text.textLine(f"{key}: {value}")
    c.drawText(text)
    c.showPage()
    c.save()
