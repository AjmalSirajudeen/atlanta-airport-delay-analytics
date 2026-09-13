"""Infographics drawn only from the Cornell ATL Six Sigma report. Not sample output."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)


def _style(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def delay_types():
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("Original study: where delays come from", loc="left", pad=12)

    boxes = [
        (0.4, 3.3, 4.2, 2.0, "#d6e4f0", "Airline-controllable\n(focus of the study)", "Carrier ops, late aircraft,\nmaintenance, ground handling"),
        (5.4, 3.3, 4.2, 2.0, "#ececec", "Mostly external", "Weather, NAS / traffic,\nsecurity screening"),
        (0.4, 0.4, 9.2, 2.2, "#f4f0e6", "FAA delay rule used in the report", "A flight is delayed at 15 minutes late.\nZeros (on-time) were most of the data; curve fits used positive delays only."),
    ]
    for x, y, w, h, color, title, body in boxes:
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=color, edgecolor="#2c5f8a", linewidth=1.2))
        ax.text(x + 0.2, y + h - 0.45, title, fontsize=11, fontweight="bold", va="top")
        ax.text(x + 0.2, y + 0.25, body, fontsize=9, va="bottom")
    fig.text(0.01, 0.01, "Source: Cornell ATL Six Sigma report, delay classification and FAA 15-minute threshold.", fontsize=8, color="#555555")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(OUT / "original_delay_types.png", dpi=140)
    plt.close(fig)


def airlines_over_threshold():
    # Named in the report as averaging above the 15-minute line. No invented means.
    names = ["Frontier (F9)", "Envoy (MQ)", "Spirit (NK)", "United (UA)"]
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    ax.barh(names[::-1], [1, 1, 1, 1], color="#c0392b")
    ax.set_xlim(0, 1.15)
    ax.set_xticks([])
    ax.set_title("Original study: airlines above the 15-minute average")
    ax.set_xlabel("Paper result: average arrival and departure delay > 15 minutes")
    _style(ax)
    ax.spines["bottom"].set_visible(False)
    fig.text(
        0.01,
        0.01,
        "Source: Cornell ATL report, average charts vs airline. Exact minute values were in JMP plots, not tabulated here.",
        fontsize=8,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(OUT / "original_airlines_over_15.png", dpi=140)
    plt.close(fig)


def seasonal_pattern():
    months = np.arange(1, 13)
    labels = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    # Qualitative only: 1 = typical in the paper, 2 = higher (May-Aug, December)
    level = [1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 2]
    colors = ["#2c5f8a" if v == 1 else "#c0392b" for v in level]
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    ax.bar(months, level, color=colors)
    ax.set_xticks(months, labels)
    ax.set_yticks([1, 2], ["Other months", "Higher in the paper\n(summer + December)"])
    ax.set_title("Original study: seasonal delay pattern (qualitative)")
    ax.set_xlabel("Month")
    _style(ax)
    fig.text(
        0.01,
        0.01,
        "Source: Cornell ATL report. Averages were still often under 15 minutes. Heights are not minute values.",
        fontsize=8,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(OUT / "original_seasonal_pattern.png", dpi=140)
    plt.close(fig)


def cost_callout():
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.set_title("Original study: passenger wage-loss illustration", loc="left")
    ax.text(0.3, 3.4, "$19.8 million", fontsize=28, fontweight="bold", color="#2c5f8a")
    ax.text(
        0.3,
        1.2,
        "Cities whose average delay exceeded 15 minutes.\n"
        "Assumptions in the report: $22/hour (Atlanta wage) and 123 passengers/flight.\n"
        "About 14 origin cities; New York accounted for most of those flights.\n"
        "This is the paper figure, not the bundled sample.",
        fontsize=10,
        va="bottom",
    )
    fig.text(0.01, 0.01, "Source: Cornell ATL report, cost analysis table.", fontsize=8, color="#555555")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(OUT / "original_cost_illustration.png", dpi=140)
    plt.close(fig)


if __name__ == "__main__":
    delay_types()
    airlines_over_threshold()
    seasonal_pattern()
    cost_callout()
    print("wrote original-study figures to", OUT)
