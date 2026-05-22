from __future__ import annotations

from html import escape
from pathlib import Path


def write_bar_chart(rows: list[dict[str, object]], output_path: str | Path, *, metric: str, title: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    width = 980
    row_height = 42
    margin_left = 250
    margin_right = 60
    margin_top = 70
    height = margin_top + (row_height * max(len(rows), 1)) + 40
    max_value = max([float(row.get(metric, 0.0)) for row in rows] + [1.0])
    chart_width = width - margin_left - margin_right

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="24" y="34" font-family="Arial" font-size="22" font-weight="700">{escape(title)}</text>',
    ]
    for index, row in enumerate(rows):
        y = margin_top + index * row_height
        agent = escape(str(row["agent"]))
        value = float(row.get(metric, 0.0))
        bar_width = 0 if max_value == 0 else (value / max_value) * chart_width
        parts.extend(
            [
                f'<text x="24" y="{y + 23}" font-family="Arial" font-size="14">{agent}</text>',
                f'<rect x="{margin_left}" y="{y}" width="{bar_width:.2f}" height="24" rx="3" fill="#2563eb"/>',
                f'<text x="{margin_left + bar_width + 8:.2f}" y="{y + 18}" font-family="Arial" font-size="13">{value:.3f}</text>',
            ]
        )
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")
