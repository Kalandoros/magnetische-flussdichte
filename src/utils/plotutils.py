from typing import Any, Iterable
import textwrap

import pandas as pd
from pandas import DataFrame
from sympy.core.numbers import NaN


def build_vline_shapes(sweep_df: DataFrame | None, f_st_values: Iterable[Any]) -> list[dict[str, Any]]:
    # Erzeugt Hilfslinien für die angegebenen F_st-Werte.
    if sweep_df is None or sweep_df.empty:
        return []
    if "F_st" not in sweep_df.columns:
        return []

    sweep_sorted = sweep_df.sort_values("F_st").reset_index(drop=True)
    f_st_series = sweep_sorted["F_st"]
    f_st_min = f_st_series.min()
    f_st_max = f_st_series.max()
    shapes: list[dict[str, Any]] = []

    for x_value in f_st_values:
        if x_value in (None, "", NaN):
            continue
        try:
            x_float = float(x_value)
        except (TypeError, ValueError):
            continue
        if x_float < f_st_min or x_float > f_st_max:
            continue

        # Randfälle direkt nehmen, sonst linear interpolieren.
        if x_float == f_st_series.iloc[0]:
            row_low = row_high = sweep_sorted.iloc[0]
            x_low = x_high = f_st_series.iloc[0]
        elif x_float == f_st_series.iloc[-1]:
            row_low = row_high = sweep_sorted.iloc[-1]
            x_low = x_high = f_st_series.iloc[-1]
        else:
            idx_upper = f_st_series.searchsorted(x_float, side="left")
            if idx_upper <= 0 or idx_upper >= len(f_st_series):
                continue
            x_low = f_st_series.iloc[idx_upper - 1]
            x_high = f_st_series.iloc[idx_upper]
            row_low = sweep_sorted.iloc[idx_upper - 1]
            row_high = sweep_sorted.iloc[idx_upper]

        y_values: list[float] = []
        for col in ["F_td", "F_fd", "F_pi_d"]:
            if x_low == x_high:
                y_val = row_low.get(col)
            else:
                y_low = row_low.get(col)
                y_high = row_high.get(col)
                if y_low in (None, "", NaN) or y_high in (None, "", NaN):
                    continue
                if pd.isna(y_low) or pd.isna(y_high):
                    continue
                y_val = y_low + (y_high - y_low) * ((x_float - x_low) / (x_high - x_low))
            if y_val in (None, "", NaN) or pd.isna(y_val):
                continue
            y_values.append(y_val)

        if not y_values:
            continue

        y_top = max(y_values)
        shapes.append({
            "type": "line",
            "xref": "x",
            "yref": "y",
            "x0": x_float,
            "x1": x_float,
            "y0": 0,
            "y1": y_top,
            "line": {"color": "#444444", "width": 1, "dash": "dot"},
        })
        shapes.append({
            "type": "line",
            "xref": "x",
            "yref": "y",
            "x0": 0,
            "x1": x_float,
            "y0": y_top,
            "y1": y_top,
            "line": {"color": "#444444", "width": 1, "dash": "dot"},
        })

    return shapes

def build_sweep_chart_layout(shapes: Iterable[dict[str, Any]], x_title: str, y_title: str, plot_title: str) -> dict[str, Any]:
    # Baut das Layout für das Sweep-Diagramm inkl. Titel-Umbruch.
    wrapped_title = "<br>".join(textwrap.wrap(text=plot_title, width=45, max_lines=2, break_long_words=False))

    return {
        "paper_bgcolor": "white",
        "plot_bgcolor": "white",
        "font": {"family": "Arial", "size": 14, "color": "black"},
        "title": {
            "text": wrapped_title,
            "x": 0.5,               # Dies sorgt für das dynamische x="121.5" im Browser
            "xanchor": "center",    # Zentriert den Text um diesen Punkt
            "yanchor": "top",
            "y": 0.97               # Schiebt den Titel ganz nach oben
        },
        "xaxis": {
            "title": x_title,
            "showline": True,
            "linecolor": "black",
            "ticks": "outside",
            "tickcolor": "black",
            "gridcolor": "#bbbbbb",
        },
        "yaxis": {
            "title": y_title,
            "rangemode": "tozero",
            "showline": True,
            "linecolor": "black",
            "ticks": "outside",
            "tickcolor": "black",
            "gridcolor": "#bbbbbb",
            "zeroline": True,
            "zerolinecolor": "black",
        },
        "shapes": list(shapes),
        "legend": {"title": {"text": "Legende:"}, "orientation": "h", "y": -0.11, "x": 0, "bgcolor": "transparent"},
        "margin": {"l": 60, "r": 20, "t": 80, "b": 50},
    }
