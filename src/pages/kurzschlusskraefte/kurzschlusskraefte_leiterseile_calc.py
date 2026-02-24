import sys
from pathlib import Path
from datetime import datetime
import threading
import tempfile
import traceback
from typing import Any

from pandas import DataFrame
from sympy.core.numbers import NaN
from taipy.gui import notify, download
import taipy.gui.builder as tgb
import pandas as pd

from .root import build_navbar
from .kurzschlusskraefte_leiterseile_docu import doc_content
from src.utils import dataloader, traceback_detail, formatter, mappings
from src.utils.plotutils import build_vline_shapes, build_sweep_chart_layout
from src.engines.kurzschlusskraefte_leiterseile_engine import calculate_kurschlusskräfte_leiterseile_sweep_df
from src.engines.kurzschlusskraefte_leiterseile_engine import (KurschlusskräfteLeiterseileInput, KurschlusskräfteLeiterseileResult,
                                                               calculate_kurschlusskräfte_leiterseile, CalculationCancelled)


# Configuration for pandas
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.precision', 3)
pd.options.display.float_format = '{:12.3e}'.format

leiterseilbefestigung_lov: list[str] = ["Abgespannt", "Aufgelegt", "Unterschlaufung", "Schlaufe am Spannfeldende"]
leiterseilbefestigung_selected: None|str = None

schlaufe_in_spannfeldmitte_lov: list[str] = ["Nein", "Ja"]
schlaufe_in_spannfeldmitte_selected: None|str = None

standardkurzschlussstroeme_lov: list[str] = ["10", "12.5", "16",  "20", "25", "31.5", "40", "50", "63", "80"]
# Basisliste kopieren, damit die temporären Werte wieder sauber zurückgesetzt werden können, wenn ein Wert nicht im lov steht
standardkurzschlussstroeme_lov_base: list[str] = standardkurzschlussstroeme_lov.copy()
standardkurzschlussstroeme_selected: None|str = None

frequenz_des_netzes_lov: list[str] = ["50", "16.66"]
frequenz_des_netzes_selected: None|str = None

hoehenunterschied_befestigungspunkte_lov: list[str] = ["Nein", "Ja"]
hoehenunterschied_befestigungspunkte_selected: None|str = None

schlaufenebene_parallel_senkrecht_lov: list[str] = ["Ebene senkrecht", "Ebene parallel"]
schlaufenebene_parallel_senkrecht_selected: None|str = None

temperatur_niedrig_lov: list[str] = ["-20", "-30", "-40", "-50"]
temperatur_niedrig_selected: None|str = None

temperatur_hoch_lov: list[str] = ["60", "70", "80", "90", "100"]
temperatur_hoch_selected: None|str = None

teilleiter_lov: list[str] = ["1", "2", "3", "4", "5", "6"]
teilleiter_selected: None|str = None

"""
Auswahl der Leiterseiltypen: 
1. Gesamte Leiterseildaten als Dataframe, 
2. Selektierung der ersten Spalte mit "Bezeichnung" als List of values für das Dropdown, 
3. Parameter für das initiale Laden und die spätere Auswahl
"""
leiterseiltyp: pd.DataFrame = dataloader.load_csv_to_df_with_cache("Leiterseildaten.csv")
leiterseiltyp_lov: list[str] = list(leiterseiltyp["Bezeichnung"])
leiterseiltyp_selected: None|str = None

name_der_verbindung: None|str = ""
kappa: None|float = None
t_k: None|float = None
f: None|float = None
m_c: None|float = None
l: None|float = None
l_i: None|float = None
l_h_f: None|float = None
a: None|float = None
a_s: None|float = None
F_st_20: None|float = None
F_st_80: None|float = None
S: None|float = None
l_s_1: None|float = None
l_s_2: None|float = None
l_s_3: None|float = None
l_s_4: None|float = None
l_s_5: None|float = None
l_s_6: None|float = None
l_s_7: None|float = None
l_s_8: None|float = None
l_s_9: None|float = None
l_s_10: None|float = None

h: None|float = None
w: None|float = None
l_v: None|float = None


content_vorlage: None|dict = None
vorlage_backup: None|dict = None

F_td_temp_niedrig: None|float|str = ""
F_fd_temp_niedrig: None|float|str = ""
F_pi_d_temp_niedrig: None|float|str = ""

F_td_temp_hoch: None|float|str = ""
F_fd_temp_hoch: None|float|str = ""
F_pi_d_temp_hoch: None|float|str = ""

F_td_massg: None|float|str = ""
F_fd_massg: None|float|str = ""
F_pi_d_massg: None|float|str = ""
temp_F_td_massg: None|float|str = ""
temp_F_fd_massg: None|float|str = ""
temp_F_pi_d_massg: None|float|str = ""

F_td_fd_pi_d_massg_1: None|float|str = ""
F_td_fd_pi_d_massg_2: None|float|str = ""

b_h_temp_niedrig: None|float|str = ""
b_h_temp_hoch: None|float|str = ""
b_h_max: None|float|str = ""
temp_b_h: None|float|str = ""

a_min_temp_niedrig: None|float|str = ""
a_min_temp_hoch: None|float|str = ""
a_min_min: None|float|str = ""

calc_result: None | KurschlusskräfteLeiterseileResult = None
calc_result_formatted: None|DataFrame = None
sweep_calc_df: None|DataFrame = None
sweep_vline_shapes: list = []

# Erstellt die Konfiguration des Plots.
def create_plot_config() -> tuple[str, str, str, dict[str, Any]]:
    """
    Erstellt die Werte für die Konfiguration des Plots.
    """
    x_title = "statische Seilzugkraft (kN)"
    y_title = "Dynamische Kurzschluss-Seilzugkräfte (kN)"
    plot_title = "Kurzschluss-Seilzugkräfte in Abhängigkeit von der statischen Seilzugkraft F<sub>st</sub>"
    sweep_chart_layout: dict = build_sweep_chart_layout([], x_title, y_title, plot_title)
    return x_title, y_title, plot_title, sweep_chart_layout

x_title, y_title, plot_title, sweep_chart_layout = create_plot_config()

# Für den Side Pane mit der Dokumentation
show_pane = False

# Variablen zur Verhinderung der Überschreibung von Berechnungen
_calc_run_lock = threading.Lock()
_calc_run_id = 0

"""
Die folgenden zwei internen Funktionen sind dafür die Schleife zu der For-Loop zur Erstellung des Diagramms
zu unterbrechen falls wieder auf Berechnung gedrückt wurde. Damit soll sichergestellt werden, das nicht mehrere 
Schleifen parallel laufen und sich folgend gegenseitig überschreiben. 
Bei jedem klick zählt die Funktion _next_calc_run_id() eine neue ID aus und gibt diese zurück. 
Die Funktion _is_run_cancelled() überprüft ob die aktuelle ID noch gültig ist bzw. übereinstimmen. 
Wenn nicht wird die Berechnung der For-Loop zur Erstellung des Diagramms abgebrochen und die neue kann ihren job machen.
"""
def _next_calc_run_id():
    global _calc_run_id
    with _calc_run_lock:
        _calc_run_id += 1
        return _calc_run_id

def _is_run_cancelled(run_id):
    return run_id != _calc_run_id

def apply_nonstandard_standardkurzschlussstrom_from_excel(state, value: str | int | float | None) -> None:
    """
    Übernimmt einen geladenen Kurzschlussstrom in den Selector.
    Wenn der Wert nicht in der Liste ist, wird er temporär in der lov ergänzt,
    damit er angezeigt werden kann.
    """
    if value is None or value == "":
        # Auswahl zurücksetzen und ursprüngliche Liste wiederherstellen
        state.standardkurzschlussstroeme_selected = None
        state.standardkurzschlussstroeme_lov = standardkurzschlussstroeme_lov_base.copy()
        return

    value_str = str(value).strip()

    if value_str not in standardkurzschlussstroeme_lov_base:
        # Wert temporär ergänzen, damit er im Selector sichtbar ist
        state.standardkurzschlussstroeme_lov = standardkurzschlussstroeme_lov_base + [value_str]
    else:
        # Nur die Basisliste verwenden
        state.standardkurzschlussstroeme_lov = standardkurzschlussstroeme_lov_base.copy()

    # Auswahl setzen
    state.standardkurzschlussstroeme_selected = value_str

def display_results(state) -> None:
    # Darstellung der erweiterten Ergebnisse im Callback:
    # state.calc_result_formatted = formatter.format_numbers_nice_to_str_for_cli(state.calc_result)
    state.calc_result_formatted = dataloader.create_df_from_calc_results_kurzschlusskreafte_leiterseile(state.calc_result, state.temperatur_niedrig_selected, state.temperatur_hoch_selected)

    # Auf die Ergebnisse zugreifen, um sie in dem Text Widgets darzustellen:
    state.F_td_temp_niedrig = round(state.calc_result['F_st_20'].F_td, 2) if state.calc_result['F_st_20'].F_td not in (None, 0.0) else None
    state.F_td_temp_hoch = round(state.calc_result['F_st_80'].F_td, 2) if state.calc_result['F_st_80'].F_td not in (None, 0.0) else None
    state.F_fd_temp_niedrig = round(state.calc_result['F_st_20'].F_fd, 2) if state.calc_result['F_st_20'].F_fd not in (None, 0.0) else None
    state.F_fd_temp_hoch = round(state.calc_result['F_st_80'].F_fd, 2) if state.calc_result['F_st_80'].F_fd not in (None, 0.0) else None
    state.F_pi_d_temp_niedrig = round(state.calc_result['F_st_20'].F_pi_d, 2) if state.calc_result['F_st_20'].F_pi_d not in (None, 0.0) else None
    state.F_pi_d_temp_hoch = round(state.calc_result['F_st_80'].F_pi_d, 2) if state.calc_result['F_st_80'].F_pi_d not in (None,0.0) else None
    state.b_h_temp_niedrig = round(state.calc_result['F_st_20'].b_h, 2) if state.calc_result['F_st_20'].b_h not in (None, 0.0) else None
    state.b_h_temp_hoch = round(state.calc_result['F_st_80'].b_h, 2) if state.calc_result['F_st_80'].b_h not in (None,0.0) else None
    state.a_min_temp_niedrig = round(state.calc_result['F_st_20'].a_min, 2) if state.calc_result['F_st_20'].a_min not in (None,0.0) else None
    state.a_min_temp_hoch = round(state.calc_result['F_st_80'].a_min, 2) if state.calc_result['F_st_80'].a_min not in (None, 0.0) else None

    # Bestimmt maximale (massgebende) Werte
    def get_max_value(val1, val2, val3=None):
        values = [v for v in [val1, val2, val3] if v not in (None, "", NaN)]
        return max(values) if values else ""

    # Bestimmt minimale (massgebende) Werte
    def get_min_value(val1, val2):
        values = [v for v in [val1, val2] if v not in (None, "")]
        return min(values) if values else ""

    state.F_td_massg = get_max_value(state.F_td_temp_niedrig, state.F_td_temp_hoch)
    state.temp_F_td_massg = state.temperatur_hoch_selected if state.F_td_temp_hoch > state.F_td_temp_niedrig else state.temperatur_niedrig_selected
    state.F_fd_massg = get_max_value(state.F_fd_temp_niedrig, state.F_fd_temp_hoch)
    state.temp_F_fd_massg = state.temperatur_hoch_selected if state.F_fd_temp_hoch > state.F_fd_temp_niedrig else state.temperatur_niedrig_selected
    state.F_pi_d_massg = get_max_value(state.F_pi_d_temp_niedrig, state.F_pi_d_temp_hoch)
    if state.F_pi_d_temp_hoch not in (None, 0.0) and state.F_pi_d_temp_niedrig not in (None, 0.0):
        state.temp_F_pi_d_massg = state.temperatur_hoch_selected if state.F_pi_d_temp_hoch > state.F_pi_d_temp_niedrig else state.temperatur_niedrig_selected
    state.F_td_fd_pi_d_massg_1 = round(get_max_value(state.F_td_massg * 1.5, state.F_fd_massg, state.F_pi_d_massg), 2)
    state.F_td_fd_pi_d_massg_2 = get_max_value(state.F_td_massg, state.F_fd_massg, state.F_pi_d_massg)
    state.b_h_max = get_max_value(state.b_h_temp_niedrig, state.b_h_temp_hoch)
    state.temp_b_h = state.temperatur_hoch_selected if state.b_h_temp_niedrig < state.b_h_temp_hoch else state.temperatur_niedrig_selected
    state.a_min_min = get_min_value(state.a_min_temp_niedrig, state.a_min_temp_hoch)

def on_change_selectable_leiterseiltyp(state) -> None:
    # state.leiterseiltyp_lov = list(state.leiterseiltyp.keys())
    state.leiterseiltyp = leiterseiltyp[leiterseiltyp["Bezeichnung"] == state.leiterseiltyp_selected]
    notify(state, notification_type="info", message=f'Leiterseiltyp auf {state.leiterseiltyp["Bezeichnung"].values[0]} geändert')
    # print(state.leiterseiltyp["Dauerstrombelastbarkeit"].values[0])

def on_click_leiterseiltyp_zurücksetzen(state) -> None:
    state.leiterseiltyp = dataloader.load_csv_to_df_with_cache("Leiterseildaten.csv")
    state.leiterseiltyp_selected = None
    # state.leiterseiltyp_lov = list(state.leiterseiltyp.keys())
    # notify(state, notification_type="info", message="Auswahl aufgehoben")

def on_click_zurücksetzen(state) -> None:
    state.name_der_verbindung = ""
    state.leiterseilbefestigung_selected = None
    state.schlaufe_in_spannfeldmitte_selected = None
    state.hoehenunterschied_befestigungspunkte_selected = None
    state.standardkurzschlussstroeme_selected = "0.0" # muss float sein
    state.standardkurzschlussstroeme_lov = standardkurzschlussstroeme_lov_base.copy()
    state.kappa = None
    state.t_k = None
    state.frequenz_des_netzes_selected = None
    state.leiterseiltyp_selected = None
    state.l = None
    state.l_i = None
    state.l_h_f = None
    state.a = None
    state.teilleiter_selected = "0" # muss int sein
    state.a_s = None
    state.F_st_20 = None
    state.F_st_80 = None
    state.S = None
    state.schlaufenebene_parallel_senkrecht_selected = None
    state.temperatur_niedrig_selected = None
    state.temperatur_hoch_selected = None
    state.m_c = None
    state.l_s_1 = None
    state.l_s_2 = None
    state.l_s_3 = None
    state.l_s_4 = None
    state.l_s_5 = None
    state.l_s_6 = None
    state.l_s_7 = None
    state.l_s_8 = None
    state.l_s_9 = None
    state.l_s_10 = None
    state.h = None
    state.w = None
    state.l_v = None
    on_click_leiterseiltyp_zurücksetzen(state)

    state.F_td_temp_niedrig = None
    state.F_fd_temp_niedrig = None
    state.F_pi_d_temp_niedrig = None

    state.F_td_temp_hoch = None
    state.F_fd_temp_hoch = None
    state.F_pi_d_temp_hoch = None

    state.F_td_massg = None
    state.F_fd_massg = None
    state.F_pi_d_massg = None
    state.temp_F_td_massg = None
    state.temp_F_fd_massg = None
    state.temp_F_pi_d_massg = None


    state.F_td_fd_pi_d_massg_1 = None
    state.F_td_fd_pi_d_massg_2 = None

    state.b_h_temp_niedrig = None
    state.b_h_temp_hoch = None
    state.b_h_max = None
    state.temp_b_h = None

    state.a_min_temp_niedrig = None
    state.a_min_temp_hoch = None
    state.a_min_min = None

    state.calc_result = None
    state.calc_result_formatted = None
    state.sweep_calc_df = pd.DataFrame(columns=["F_st", "F_td", "F_fd", "F_pi_d"])
    state.sweep_vline_shapes = []
    state.sweep_chart_layout = build_sweep_chart_layout([], x_title, y_title, plot_title)

def on_click_berechnen(state):
    run_id = _next_calc_run_id()

    required_fields = [
        # Allgemeine Angaben
        ('leiterseilbefestigung_selected', 'Art der Leiterseilbefestigung'),
        ('schlaufe_in_spannfeldmitte_selected', 'Schlaufe in Spannfeldmitte'),
        ('hoehenunterschied_befestigungspunkte_selected', 'Höhenunterschied der Befestigungspunkte'),
        #('schlaufenebene_parallel_senkrecht_selected', 'Schlaufebene'),
        ('temperatur_niedrig_selected', 'Niedrigste Temperatur'),
        ('temperatur_hoch_selected', 'Höchste Temperatur'),
        # Elektrische Werte
        ('standardkurzschlussstroeme_selected', 'Kurzschlussstrom'),
        ('kappa', 'Stossfaktor'),
        ('t_k', 'Kurzschlussdauer'),
        ('frequenz_des_netzes_selected', 'Frequenz des Netzes'),
        # Leiterseilkonfiguration
        ('leiterseiltyp_selected', 'Leiterseiltyp'),
        ('teilleiter_selected', 'Anzahl Teilleiter'),
        # Abstände
        ('l', 'Mittenabstand der Stützpunkte'),
        ('a', 'Leitermittenabstand'),
        # Mechanische Kraftwerte
        ('F_st_20', 'Statische Seilzugkraft bei -20°C'),
        ('F_st_80', 'Statische Seilzugkraft bei 80°C'),
        ('S', 'resultierender Federkoeffizient'),
    ]

    # Prüfe alle minimum Pflichtfelder
    missing = []
    for field, label in required_fields:
        value = getattr(state, field, None)
        if (value is None or value == '' or
                (isinstance(value, (int, float, str)) and str(value) == '0.0') or
                (isinstance(value, (int, float, str)) and str(value) == '0') or
                (isinstance(value, (int, float, str)) and str(value) == '')):
            missing.append(label)

    if missing:
        notify(state, notification_type="error",
               message=f"Bitte folgende Pflichtfelder ausfüllen: {', '.join(missing)}", duration=15000)
        return
    if not state.leiterseiltyp_selected:
        notify(state, notification_type="error",
               message="Bitte Leiterseiltyp auswählen!", duration=15000)
        return

    # Auswahlbedingte Überprüfungen
    if state.teilleiter_selected in (None, 0.0, 0, '', '0.0', '0'):
        notify(state, notification_type="error",
               message=f"Bitte folgendes Pflichtfeld ausfüllen: 'n', 'Anzahl der Teilleiter eines Hauptleiters'", duration=15000)
    if int(state.teilleiter_selected) > 1 and state.a_s in (None, 0.0, 0, '', '0.0', '0'):
        notify(state, notification_type="error",
               message=f"Bitte folgendes Pflichtfeld ausfüllen: 'a_s', 'Wirksamer Abstand zwischen Teilleitern'", duration=15000)
        return
    if float(state.l) > 9 and state.l_s_1 in (None, 0.0, 0, '', '0.0', '0'):
        notify(state, notification_type="warning",
               message=f"Bitte folgende Eingabefelder überprüfen: 'l_s', 'Abstände Abstandshalter'", duration=15000)
    if state.leiterseilbefestigung_selected == "Abgespannt" and state.l_i in (None, 0.0, 0, '', '0.0', '0'):
        notify(state, notification_type="warning",
               message=f"Bitte folgendes Eingabefeld überprüfen: 'l_i', 'Länge einer Abspann-Isolatorkette'", duration=15000)
    if state.leiterseilbefestigung_selected == "Abgespannt" and state.m_c in (None, 0.0, 0, '', '0.0', '0'):
        notify(state, notification_type="warning",
               message=f"Bitte folgendes Eingabefeld überprüfen: 'm_c', 'Summe konzentrischer Massen im Spannfeld'", duration=15000)
    if state.leiterseilbefestigung_selected == "Aufgelegt" and state.l_h_f in (None, 0.0, 0, '', '0.0', '0'):
        notify(state, notification_type="warning",
               message=f"Bitte folgendes Eingabefeld überprüfen: 'l_h_f', 'Länge einer Klemme u. Formfaktor'", duration=15000)
    if state.schlaufe_in_spannfeldmitte_selected == "Ja" and state.h in (None, 0.0, 0, '', '0.0', '0'):
        notify(state, notification_type="warning",
               message=f"Bitte folgendes Eingabefeld überprüfen: 'h', 'Schlaufenhöhe'", duration=15000)
    if state.schlaufe_in_spannfeldmitte_selected == "Ja" and state.w in (None, 0.0, 0, '', '0.0', '0'):
        notify(state, notification_type="warning",
               message=f"Bitte folgendes Eingabefeld überprüfen: 'w', 'Schlaufenbreite'", duration=15000)
    if state.schlaufe_in_spannfeldmitte_selected == "Ja" and state.l_v in (None, 0.0, 0, '', '0.0', '0'):
        notify(state, notification_type="warning",
               message=f"Bitte folgendes Eingabefeld überprüfen: 'l_v', 'Seilbogenlänge der Schlaufe'", duration=15000)

    # Bereinigen der alten States, damit keine Variablenleichen entstehen, wenn zum Beispiel bei einer Rechnung
    # oder Fall nicht alle Parameter berechnet werden. In so einem Fall dürfen sich die "alten" Variablen nicht mit den
    # "neuen vermischen".
    state.F_td_temp_niedrig = None
    state.F_fd_temp_niedrig = None
    state.F_pi_d_temp_niedrig = None

    state.F_td_temp_hoch = None
    state.F_fd_temp_hoch = None
    state.F_pi_d_temp_hoch = None

    state.F_td_massg = None
    state.F_fd_massg = None
    state.F_pi_d_massg = None
    state.temp_F_td_massg = None
    state.temp_F_fd_massg = None
    state.temp_F_pi_d_massg = None

    state.F_td_fd_pi_d_massg_1 = None
    state.F_td_fd_pi_d_massg_2 = None

    state.b_h_temp_niedrig = None
    state.b_h_temp_hoch = None
    state.b_h_max = None
    state.temp_b_h = None

    state.a_min_temp_niedrig = None
    state.a_min_temp_hoch = None
    state.a_min_min = None

    state.calc_result = None
    state.calc_result_formatted = None

    try:
        # Erstellung des Input-Objekts für den Mediator
        inputs = KurschlusskräfteLeiterseileInput(
            leiterseilbefestigung=str(state.leiterseilbefestigung_selected),
            schlaufe_in_spannfeldmitte=str(state.schlaufe_in_spannfeldmitte_selected),
            hoehenunterschied_befestigungspunkte=str(state.hoehenunterschied_befestigungspunkte_selected),
            schlaufenebene_parallel_senkrecht=str(state.schlaufenebene_parallel_senkrecht_selected),
            temperatur_niedrig=int(state.temperatur_niedrig_selected),
            temperatur_hoch=int(state.temperatur_hoch_selected),
            standardkurzschlussstroeme=float(state.standardkurzschlussstroeme_selected),
            κ=float(state.kappa),
            t_k=float(state.t_k),
            f=float(state.frequenz_des_netzes_selected),
            leiterseiltyp=str(state.leiterseiltyp_selected) if state.leiterseiltyp_selected else None,
            d=float(state.leiterseiltyp["Aussendurchmesser"].values[0]),
            A_s=float(state.leiterseiltyp["Querschnitt eines Teilleiters"].values[0]),
            m_s=float(state.leiterseiltyp["Massenbelag eines Teilleiters"].values[0]),
            E=float(state.leiterseiltyp["Elastizitätsmodul"].values[0]),
            c_th=float(state.leiterseiltyp["Kurzzeitstromdichte"].values[0]),
            n=int(state.teilleiter_selected),
            m_c=float(state.m_c) if state.m_c not in (None, 0.0, 0, '', '0.0', '0') else None,
            l=float(state.l),
            l_i=float(state.l_i) if state.l_i not in (None, 0.0, 0, '', '0.0', '0')  else None,
            l_h_f= float(state.l_h_f) if state.l_h_f not in (None, 0.0, 0, '', '0.0', '0')  else None,
            a=float(state.a),
            a_s=float(state.a_s) if state.a_s not in (None, 0.0, 0, '', '0.0', '0') else None,
            F_st_20=float(state.F_st_20),
            F_st_80=float(state.F_st_80),
            S=int(state.S),
            l_s_1=float(state.l_s_1) if state.l_s_1 not in (None, 0.0, 0, '', '0.0', '0') else None,
            l_s_2=float(state.l_s_2) if state.l_s_2 not in (None, 0.0, 0, '', '0.0', '0') else None,
            l_s_3=float(state.l_s_3) if state.l_s_3 not in (None, 0.0, 0, '', '0.0', '0') else None,
            l_s_4=float(state.l_s_4) if state.l_s_4 not in (None, 0.0, 0, '', '0.0', '0') else None,
            l_s_5=float(state.l_s_5) if state.l_s_5 not in (None, 0.0, 0, '', '0.0', '0') else None,
            l_s_6=float(state.l_s_6) if state.l_s_6 not in (None, 0.0, 0, '', '0.0', '0') else None,
            l_s_7=float(state.l_s_7) if state.l_s_7 not in (None, 0.0, 0, '', '0.0', '0') else None,
            l_s_8=float(state.l_s_8) if state.l_s_8 not in (None, 0.0, 0, '', '0.0', '0') else None,
            l_s_9=float(state.l_s_9) if state.l_s_9 not in (None, 0.0, 0, '', '0.0', '0') else None,
            l_s_10=float(state.l_s_10) if state.l_s_10 not in (None, 0.0, 0, '', '0.0', '0') else None,
            h=float(state.h) if state.h not in (None, 0.0, 0, '', '0.0', '0') else None,
            w=float(state.w) if state.w not in (None, 0.0, 0, '', '0.0', '0') else None,
            l_v=float(state.l_v) if state.l_v not in (None, 0.0, 0, '', '0.0', '0') else None
        )

        # Berechnung über den Mediator
        #print(inputs)
        calc_result = calculate_kurschlusskräfte_leiterseile(inputs)

        # Überprüft, ob das Abbruchkriterium bei mehrfachem Klicken von Berechnen für die For-Loop des Diagramms zutrifft
        if _is_run_cancelled(run_id):
            return

        # Übertragung der berechneten Werte an den state
        state.calc_result = calc_result

        # Darstellung und Auswertung der Ergebnisse
        display_results(state)

        notify(state, notification_type="success", message="Berechnung erfolgreich abgeschlossen", duration=5000)

        # Überprüft, ob das Abbruchkriterium bei mehrfachem Klicken von Berechnen für die For-Loop des Diagramms zutrifft
        if _is_run_cancelled(run_id):
            return

        try:
            state.sweep_calc_df = calculate_kurschlusskräfte_leiterseile_sweep_df(inputs, cancel_check=lambda: _is_run_cancelled(run_id))
            state.sweep_vline_shapes = build_vline_shapes(state.sweep_calc_df, [state.F_st_20, state.F_st_80])
            state.sweep_chart_layout = build_sweep_chart_layout(
                state.sweep_vline_shapes,
                x_title,
                y_title,
                plot_title,
            )
            # print("Sweep calc df Vorschau:")
            # print(state.sweep_calc_df.head(10).to_string(index=False))
            notify(state, notification_type="success", message=f"Diagramm mit {len(state.sweep_calc_df)} Werten erstellt", duration=5000)
        except CalculationCancelled:
            notify(state, notification_type="warning", message=f"Berechnung des Diagramms wurde durch wiederholtes dücken von Berechnen abgebrochen", duration=10000)
            return
        except Exception as sw:
            state.sweep_calc_df = None
            state.sweep_vline_shapes = []
            state.sweep_chart_layout = build_sweep_chart_layout([], x_title, y_title, plot_title)
            error_msg = traceback_detail.get_exception_message(sw)
            sys.stderr.write(f"{error_msg}\n")
            notify(state, notification_type="warning", message=f"Diagramm konnte nicht erstellt werden: {str(sw)}", duration=10000)
            traceback.print_exc(limit=10, file=sys.stderr, chain=True)

    except ValueError as ve:
        error_msg = traceback_detail.get_exception_message(ve, show_chain=True)
        sys.stderr.write(f"{error_msg}\n")
        notify(state, notification_type="error", message=f"Fehler bei der Berechnung {error_msg}", duration=15000)
        traceback.print_exc(limit=10, file=sys.stderr, chain=True)

    except IndexError as ie:
        error_msg = traceback_detail.get_exception_message(ie, show_chain=True)
        sys.stderr.write(f"{error_msg}\n")
        notify(state, notification_type="error", message=f"Fehler bei der Berechnung {error_msg}", duration=15000)
        traceback.print_exc(limit=10, file=sys.stderr, chain=True)

    except NotImplementedError as nie:
        # Behandlung für noch nicht implementierte Fälle
        notify(state, notification_type="warning", message=f"⚠️ Diese Berechnungsmethode ist noch nicht implementiert:\n{str(nie)}", duration=15000)

    except Exception as e:
        error_msg = traceback_detail.get_exception_message(e, show_chain=True)
        sys.stderr.write(f"{error_msg}\n")
        notify(state, notification_type="error", message=f"Fehler bei der Berechnung {error_msg}", duration=15000)
        traceback.print_exc(limit=10, file=sys.stderr, chain=True)

def on_click_load_vorlage(state) -> None:
    """
    Lädt Vorlage aus Excel und setzt GUI-Widgets.
    """

    # Setzt alle Felder und Ergebnisse zurück, um zu bereinigen
    on_click_zurücksetzen(state)

    # Überprüfe, ob der file_selector einen Inhalt besitzt
    file_path = state.content_vorlage

    # Überprüfe, ob der Dateipfad vorhanden und gültig ist
    if not file_path or file_path == '' or file_path is None:
        notify(state, notification_type="warning", message="Bitte erst eine Datei auswählen")
        return

    # Überprüfe, ob der Dateipfad ein String ist
    if not isinstance(file_path, str):
        notify(state, notification_type="warning", message="Ungültiger Dateipfad. Bitte Datei erneut auswählen.")
        return

    try:
        # Lade die Excel-Datei über dataloader
        df = dataloader.load_excel_to_df(file_path)

        if df.empty:
            notify(state, notification_type="error", message="Datei konnte nicht geladen werden oder ist leer")
            return

        # Konvertiere DataFrame zu Dictionary mit den State-Variablen
        input_dict, loaded_fields, skipped_fields = dataloader.convert_excel_to_dict_with_mapping(df=df, mapping="Import Kurzschlusskraft Leiterseile")

        if not input_dict:
            notify(state, notification_type="error", message="Keine gültigen Eingabedaten in der Datei gefunden")
            return

        # Speichere aktuellen Zustand für Undo
        state.vorlage_backup = {}
        for key in input_dict.keys():
            state.vorlage_backup[key] = getattr(state, key, None)

        # Spezialfall: Wenn der Wert im Excel nicht dem Standardkurzschlussstrom entspricht und ihn trotzdem im selector sichtbar zu machen
        if "standardkurzschlussstroeme_selected" in input_dict:
            apply_nonstandard_standardkurzschlussstrom_from_excel(
                state,
                input_dict.get("standardkurzschlussstroeme_selected")
            )
            # Damit der Wert nicht doppelt gesetzt wird
            input_dict.pop("standardkurzschlussstroeme_selected", None)

        # Setze alle State-Variablen aus dem Dictionary
        for key, value_from_dict in input_dict.items():
            setattr(state, key, value_from_dict)

        # Laden des Leiterseiltyps
        on_change_selectable_leiterseiltyp(state)

        # Erstelle Feedback-Nachricht
        message = f"✓ {len(loaded_fields)} Felder geladen"
        if skipped_fields:
            # Nur optionale Felder anzeigen, wenn sie übersprungen wurden
            optional_keywords = ['Leiterseilverbindung', 'Schlaufenebene', 'Phasenabstandshalter',
                                 'Summe konzentrischer Massen', 'Länge einer Abspann-Isolatorkette',
                                 'wirksamer Abstand', 'Länge einer Klemme','Schlaufenhöhe', 'Schlaufenbreite',
                                 'Seilbogenlänge der Schlaufe']
            optional_skipped = [f for f in skipped_fields if any(kw in f for kw in optional_keywords)]
            required_skipped = [f for f in skipped_fields if f not in optional_skipped]

            if required_skipped:
                message += f"\n⚠ {len(required_skipped)} Pflichtfelde(r) fehlen: {', '.join(required_skipped)}"

        notify(state, notification_type="success", message=message, duration=5000)

        # WICHTIG: Setze content_vorlage zurück, um Memory Leak zu vermeiden
        state.content_vorlage = None

    except Exception as e:
        error_msg = traceback_detail.get_exception_message(e)
        sys.stderr.write(f"{error_msg}\n")
        notify(state, notification_type="error", message=f"Fehler beim Laden der Datei {error_msg}", duration=15000)
        traceback.print_exc(limit=10, file=sys.stderr, chain=True)
        # Setze auch bei Fehler zurück
        state.content_vorlage = None

def on_click_undo_vorlage(state) -> None:
    """
    Stellt den vorherigen Zustand vor dem Laden der Vorlage wieder her.
    """
    if state.vorlage_backup is None:
        notify(state, notification_type="warning", message="Keine vorherige Version zum Wiederherstellen vorhanden")
        return

    try:
        # Stelle alle gespeicherten Werte wieder her
        for key, value in state.vorlage_backup.items():
            setattr(state, key, value)

        on_click_leiterseiltyp_zurücksetzen(state)

        # Lösche das Backup nach dem Wiederherstellen
        state.vorlage_backup = None

        notify(state, notification_type="info", message="Vorherige Werte wiederhergestellt")

    except Exception as e:
        error_msg = traceback_detail.get_exception_message(e)
        sys.stderr.write(f"{error_msg}\n")
        notify(state, notification_type="error", message=f"Fehler beim Wiederherstellen {error_msg}", duration=15000)
        traceback.print_exc(limit=10, file=sys.stderr, chain=True)

def on_click_export_vorlage(state) -> None:
    """
    Exportiert die aktuellen GUI-Werte in eine Excel-Datei.
    Verwendet die hochgeladene Vorlage als Basis oder die Standard-Vorlage.
    """
    try:
        # Bestimme die Vorlage: Entweder die hochgeladene Datei oder die Standard-Vorlage
        template_path = None
        if state.content_vorlage and state.content_vorlage != '':
            template_path = Path(state.content_vorlage)
        else:
            # Verwende Standard-Vorlage
            template_path = Path(dataloader.get_project_root()) / "src" / "templates" / "Export Vorlage Kurzschlusskraft Leiterseile.xlsx"

        if not template_path.exists():
            notify(state, notification_type="error", message="Keine Vorlage gefunden. Bitte erst eine Datei auswählen.", duration=15000)
            return

        # Sammle alle aktuellen State-Werte für das spätere mappingreversed in src/utils/mappingreversed.json
        export_dict = {
            'leiterseilbefestigung_selected': state.leiterseilbefestigung_selected,
            'schlaufe_in_spannfeldmitte_selected': state.schlaufe_in_spannfeldmitte_selected,
            'hoehenunterschied_befestigungspunkte_selected': state.hoehenunterschied_befestigungspunkte_selected,
            'schlaufenebene_parallel_senkrecht_selected': state.schlaufenebene_parallel_senkrecht_selected,
            'temperatur_niedrig_selected': state.temperatur_niedrig_selected,
            'temperatur_hoch_selected': state.temperatur_hoch_selected,
            'standardkurzschlussstroeme_selected': state.standardkurzschlussstroeme_selected,
            'kappa': state.kappa,
            't_k': state.t_k,
            'frequenz_des_netzes_selected': state.frequenz_des_netzes_selected,
            'leiterseiltyp_selected': state.leiterseiltyp_selected,
            'teilleiter_selected': state.teilleiter_selected,
            'm_c': state.m_c,
            'l': state.l,
            'l_i': state.l_i,
            'a': state.a,
            'a_s': state.a_s,
            'F_st_20': state.F_st_20,
            'F_st_80': state.F_st_80,
            'S': state.S,
            'l_s_1': state.l_s_1,
            'l_s_2': state.l_s_2,
            'l_s_3': state.l_s_3,
            'l_s_4': state.l_s_4,
            'l_s_5': state.l_s_5,
            'l_s_6': state.l_s_6,
            'l_s_7': state.l_s_7,
            'l_s_8': state.l_s_8,
            'l_s_9': state.l_s_9,
            'l_s_10': state.l_s_10,
            'h': state.h,
            'w': state.w,
            'l_v': state.l_v,
        }

        # Erstelle Dateinamen mit name_der_verbindung und Timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        connection_name = state.name_der_verbindung if state.name_der_verbindung else "Unbenannt"
        # Entferne ungültige Zeichen für Dateinamen
        connection_name = "".join(c for c in connection_name if c.isalnum() or c in (' ', '_', '-')).strip()
        if not connection_name:
            connection_name = "Unbenannt"
        filename = f"{connection_name}_{timestamp}.xlsx"

        # Erstelle temporäre Datei mit richtigem Namen im Temp-Verzeichnis
        # Wichtig: Datei muss mit dem gewünschten Namen existieren, damit Browser ihn übernimmt
        temp_dir = tempfile.gettempdir()
        output_path = Path(temp_dir) / filename

        # Exportiere zu Excel mit Vorlage
        success = dataloader.export_dict_to_excel_with_reversemapping(export_dict, template_path, output_path)

        if success:
            # Lese die erstellte Datei und trigger Download mit Datum-Zeit-Dateinamen
            with open(output_path, 'rb') as f:
                file_content = f.read()

            # Nutze download() Funktion für Datum-Zeit-Dateinamen
            download(state, content=file_content, name=filename)
            notify(state, notification_type="success", message=f"Download gestartet: {filename}", duration=5000)
        else:
            notify(state, notification_type="error", message="Fehler beim Erstellen der Excel-Datei.", duration=15000)

    except Exception as e:
        error_msg = traceback_detail.get_exception_message(e)
        sys.stderr.write(f"{error_msg}\n")
        notify(state, notification_type="error", message=f"Fehler beim Export{error_msg}", duration=15000)
        traceback.print_exc(limit=10, file=sys.stderr, chain=True)

with tgb.Page() as kurzschlusskraefte_leiterseile_calc_page:
    build_navbar()
    with tgb.part(class_name="pane-layout"):
        with tgb.pane(open=show_pane, persistent=True, show_button=True, anchor="right", width="40%", class_name="pane-side"):
            with tgb.part(class_name="card doc-card card-inner pane-card-fit"):
                        tgb.part(class_name="card taipy-text third-party-iframe-taipy-style-pane vh-fit-with-navbar-pane card-inner",
                                 content="{doc_content}", height="100%")
        with tgb.part(class_name="pane-main"):
            tgb.html("br")
            tgb.text(value="Kurzschlussfestigkeit bei Leiterseilen", class_name="h2 pl1")
            tgb.text(value="Nach SN EN 60865-1:2012", class_name="h6 pl1")
            with tgb.layout(columns="1 1", class_name="p1"):
                with tgb.part(class_name="card pt1 card-inner"):
                    with tgb.layout(columns="1", class_name=""):
                        tgb.text(value="Eingaben", class_name="h3 p-half")
                        with tgb.part(class_name="card p1 md-tight "):
                            tgb.text(value="Allgemeine Angaben", class_name="h6")
                            tgb.html("hr")
                            with tgb.layout(columns="1", columns__mobile="1"):
                                tgb.input(label="Name der Leiterseilverbindung", value="{name_der_verbindung}",
                                      hover_text="Angabe des Projekts, der Station, des Feldes und der Verbindung.",
                                      class_name="input-with-unit --unit; mb1")
                            with tgb.layout(columns="1 1 1", columns__mobile="1"):
                                tgb.selector(label="Art der Leiterseilbefestigung", value="{leiterseilbefestigung_selected}", lov="{leiterseilbefestigung_lov}", dropdown=True,
                                             hover_text="Abgespannt bei Abspannportalen, Hochgerüsten oder Überspannungen und "
                                                        "aufgelegt bei Geräteanschlüssen oder Stützisolatoren.",
                                             class_name="select-center-align")
                                tgb.selector(label="Schlaufe in Spannfeldmitte", value="{schlaufe_in_spannfeldmitte_selected}", lov="{schlaufe_in_spannfeldmitte_lov}", dropdown=True,
                                             hover_text="Ja, wenn der obere Befestigungspunkt der Schlaufe bis zu 10% der "
                                                        "Länge des Hauptleiters von der Mitte entfernt ist.",
                                             class_name="select-center-align")
                                tgb.selector(label="Höhenunterschied der Befestigungspunkte mehr als 25%", value="{hoehenunterschied_befestigungspunkte_selected}", lov="{hoehenunterschied_befestigungspunkte_lov}", dropdown=True,
                                             hover_text="Ja, wenn der Höhenunterschied der Befestigungspunkte mehr als 25% "
                                                        "bezogen auf die Spannfeldlänge beträgt.",
                                             class_name="select-center-align")
                                tgb.selector(label="Schlaufenebene bei Schlaufen in Spannfeldmitte", value="{schlaufenebene_parallel_senkrecht_selected}", lov="{schlaufenebene_parallel_senkrecht_lov}", dropdown=True,
                                             hover_text="Angabe nur notwendig, wenn Schlaufen in der Spannfeldmitte verwendet werden.",
                                             class_name="select-center-align")
                                tgb.selector(label="ϑ_l Niedrigste Temperatur", value="{temperatur_niedrig_selected}", lov="{temperatur_niedrig_lov}", dropdown=True,
                                             hover_text="örtliche Tiefsttemperatur",
                                             class_name="input-with-unit Grad-Celsius-unit")
                                tgb.selector(label="ϑ_h Höchste Temperatur", value="{temperatur_hoch_selected}", lov="{temperatur_hoch_lov}", dropdown=True,
                                             hover_text="Höchste Betriebstemperatur der Leiter",
                                             class_name="input-with-unit Grad-Celsius-unit")
                        with tgb.part(class_name="card p1 md-tight "):
                            tgb.text(value="Elektrische Werte", class_name="h6")
                            tgb.html("hr")
                            with tgb.layout(columns="1 1 1 1", columns__mobile="1", class_name=""):
                                tgb.selector(label="I''k Anfangs-Kurzschlusswechselstrom",
                                             value="{standardkurzschlussstroeme_selected}", lov="{standardkurzschlussstroeme_lov}",
                                             hover_text="Anfangs-Kurzschlusswechselstrom beim dreipoligen Kurzschluss (Effektivwert).",
                                             dropdown=True, class_name="input-with-unit A-unit")
                                tgb.number(label="κ Sossfaktor", value="{kappa}", min=0.01, max=2.0, step=0.01,
                                           hover_text="Wird kein Stossfaktor angegeben wird der Wert 1.8 angenommen.",
                                           class_name="input-with-unit --unit")
                                tgb.number(label="t_k Kurzschlussdauer", value="{t_k}", min=0.01, max=5.0, step=0.01,
                                           hover_text="Wird keine Kurzschlussdauer angegeben wird die Dauer von 1 s angenommen.",
                                           class_name="input-with-unit tk-unit Mui-focused")
                                tgb.selector(label="f Frequenz des Netzes",
                                             value="{frequenz_des_netzes_selected}", lov="{frequenz_des_netzes_lov}",
                                             dropdown=True, class_name="input-with-unit Hz-unit")
                        with tgb.part(class_name="card p1 md-tight "):
                            tgb.text(value="Leiterseilkonfiguration", class_name="h6")
                            tgb.html("hr")
                            with tgb.layout(columns="1 1 1", columns__mobile="1"):
                                tgb.selector(label="Leiterseiltyp", value="{leiterseiltyp_selected}", lov="{leiterseiltyp_lov}",
                                             dropdown=True, on_change=on_change_selectable_leiterseiltyp,
                                             class_name="select-center-align")
                                tgb.selector(label="n Anzahl der Teilleiter eines Hauptleiters",
                                             value="{teilleiter_selected}", lov="{teilleiter_lov}", dropdown=True,
                                             class_name="select-right-align")
                                tgb.number(label="m_c Summe konzentrierter Massen im Spannfeld", value = "{m_c}", min = 0.0, max = 500.0, step = 0.1,
                                           hover_text="Summe aller konzentrierter Massen im Spannfeld z.B. durch Klemmen, "
                                                      "Schlaufen, Abstandshalter oder Gegenkontakte. \n "
                                                      "m_c beinhaltet die Masse aller Massen die sich gesamthaft auf allen Teilleitern befinden.",
                                           class_name = "input-with-unit kg-unit Mui-focused")
                        with tgb.part(class_name="card p1 md-tight "):
                            tgb.text(value="Abstände", class_name="h6")
                            tgb.html("hr")
                            with tgb.layout(columns="1 1 1", columns__mobile="1"):
                                tgb.number(label="l Mittenabstand der Stützpunkte", value="{l}", min=0.0, max=150.0, step=0.1,
                                           class_name="input-with-unit m-unit Mui-focused")
                                tgb.number(label="l_i Länge einer Abspann-Isolatorkette", value="{l_i}", min=0.0, max=20.0, step=0.1,
                                           hover_text="Es ist der Abstand nur einer Abspann-Isolatorkette einzugeben.",
                                           class_name="input-with-unit m-unit Mui-focused")
                                tgb.number(label="l_h_f Länge einer Klemme u. Formfaktor", value="{l_h_f}", min=0.0, max=20.0, step=0.1,
                                           hover_text="Nur bei aufgelegten Leiterseilen anzugeben.\nEs ist die Länge nur einer "
                                                      "Klemme und nur ein Formfaktor anzugeben.",
                                           class_name="input-with-unit m-unit Mui-focused")
                                tgb.number(label="a Leitermittenabstand", value="{a}", min=0.0, max=20.0, step=0.1,
                                           hover_text="Bei sich verändernden Leitermittenabständen im Spannfeld (z.B. durch "
                                                      "zueinander zulaufende Leiterseilverbindungen, bei den der Abstand an "
                                                      "den Befestigungspunkten unterschiedlich sind, ist der Mittelwert, also "
                                                      "der über die Länge gemittelte Abstand, zu verwenden.",
                                           class_name="input-with-unit m-unit Mui-focused")
                                tgb.number(label="a_s wirksamer Abstand zwischen Teilleitern", value="{a_s}", min=0.0, max=5.0, step=0.1,
                                           hover_text="Nur bei mehreren Teilleitern anzugeben.", class_name="input-with-unit m-unit Mui-focused")
                        with tgb.part(class_name="card p1 md-tight "):
                            tgb.text(value="Mechanische Kraftwerte", class_name="h6")
                            tgb.html("hr")
                            with tgb.layout(columns="1 1 1", columns__mobile="1"):
                                tgb.number(label="F_st_-20 statische Seilzugkraft in einem Hauptleiter", value="{F_st_20}", min=0.0,
                                           step=0.1,
                                           hover_text="Bei der Ermittlung der statischen Seilzugkraft Fst sollte der Beitrag "
                                                      "konzentrierter Massen im Spannfeld, z. B. durch Klemmen, Schlaufen oder "
                                                      "Gegenkontakte, berücksichtigt werden. Bei Schlaufen sollte dabei die "
                                                      "Hälfte der Schlaufenmasse angesetzt werden.\n"
                                                      "F_st_-20 symbolisiert die örtliche Tiefsttemperatur, welche jedoch nicht "
                                                      "bei -20°C liegen muss.\n"
                                                      "Die statische Seilzugkraft bezieht sich auf den Hauptleiter und muss die statischen"
                                                      "Seilzugkräfte aller Teilleiter beinhalten.",
                                           class_name="input-with-unit N-unit Mui-focused")
                                tgb.number(label="F_st_80 statische Seilzugkraft in einem Hauptleiter", value="{F_st_80}", min=0.0, step=0.1,
                                           hover_text="Bei der Ermittlung der statischen Seilzugkraft Fst sollte der Beitrag " 
                                                      "konzentrierter Massen im Spannfeld, z. B. durch Klemmen, Schlaufen oder "
                                                      "Gegenkontakte, berücksichtigt werden. Bei Schlaufen sollte dabei die "
                                                      "Hälfte der Schlaufenmasse angesetzt werden.\n"
                                                      "F_st_80 symbolisiert die höchste Betriebstemperatur, welche jedoch nicht "
                                                      "bei 80°C liegen muss.\n"
                                                      "Die statische Seilzugkraft bezieht sich auf den Hauptleiter und muss die statischen"
                                                      "Seilzugkräfte aller Teilleiter beinhalten.",
                                           class_name="input-with-unit N-unit Mui-focused")
                                tgb.number(label="S resultierender Federkoeffizient beider Stützpunkte", value="{S}",
                                           hover_text=(
                                               "Der resultierende Federkoeffizient beschreibt die Steifigkeit beider Gerüste "
                                               "an denen das Leiterseil befestigt ist.\n"
                                               "100'000 bei aufgelegten Leiterseilen\n"
                                               "150'000 - 1'300'000 bei Bemessungsspannung 123 kV\n"
                                               "400'000 - 2'000'000 bei Bemessungsspannung 245 kV\n"
                                               "600'000 - 3'000'000 bei Bemessungsspannung 420 kV"),
                                            class_name="input-with-unit Nm-unit Mui-focused long-unit")
                        with tgb.part(class_name="card p1 md-tight "):
                            tgb.text(value="Erweiterte Eingaben", class_name="h6")
                            tgb.html("hr")
                            with tgb.layout(columns="1", columns__mobile="1"):
                                with tgb.expandable(title="Abstände Abstandshalter", expanded=False, class_name="h6 expandable-fit",
                                                    hover_text="Abstände beginnend von links vom Ende der Isolatorkette oder dem "
                                                               "Anschlusspunkt bei aufgelegten Leiterseilen. \n"
                                                               "Abstände zwischen Abstandshaltern, Gegenkontakte von Trennern "
                                                               "zählen ebenfalls als Abstandshalter. \n"
                                                               "Die gesamte Seillänge eines Hauptleiters und die Summe der "
                                                               "angegebenen Abstände müssen übereinstimmen bzw. gleich sein."):
                                    with tgb.layout(columns="1 1 1 1 1", columns__mobile="1"):
                                        tgb.number(label="Abstandshalter 1", value="{l_s_1}", min=0.0, step=0.1,
                                                   class_name="input-with-unit m-unit Mui-focused")
                                        tgb.number(label="Abstandshalter 2", value="{l_s_2}", min=0.0, step=0.1,
                                                   class_name="input-with-unit m-unit Mui-focused")
                                        tgb.number(label="Abstandshalter 3", value="{l_s_3}", min=0.0, step=0.1,
                                                   class_name="input-with-unit m-unit Mui-focused")
                                        tgb.number(label="Abstandshalter 4", value="{l_s_4}", min=0.0, step=0.1,
                                                   class_name="input-with-unit m-unit Mui-focused")
                                        tgb.number(label="Abstandshalter 5", value="{l_s_5}", min=0.0, step=0.1,
                                                   class_name="input-with-unit m-unit Mui-focused")
                                        tgb.number(label="Abstandshalter 6", value="{l_s_6}", min=0.0, step=0.1,
                                                   class_name="input-with-unit m-unit Mui-focused")
                                        tgb.number(label="Abstandshalter 7", value="{l_s_7}", min=0.0, step=0.1,
                                                   class_name="input-with-unit m-unit Mui-focused")
                                        tgb.number(label="Abstandshalter 8", value="{l_s_8}", min=0.0, step=0.1,
                                                   class_name="input-with-unit m-unit Mui-focused")
                                        tgb.number(label="Abstandshalter 9", value="{l_s_9}", min=0.0, step=0.1,
                                                   class_name="input-with-unit m-unit Mui-focused")
                                        tgb.number(label="Abstandshalter 10", value="{l_s_10}", min=0.0, step=0.1,
                                                   class_name="input-with-unit m-unit Mui-focused")
                                with tgb.expandable(title="Schlaufengeometrie bei Schlaufen in Spannfeldmitte", expanded=False, class_name="h6 expandable-fit",
                                                    hover_text="Die Eingabefelder gelten für parallel als auch für senkrecht "
                                                               "zum Hauptleiter verlaufende Schlaufenanordnungen.\n"
                                                               "Wird die Seilbogenlänge nicht eingegeben, wird diese "
                                                               "automatisch berechnet."):
                                    with tgb.layout(columns="1 1 1", columns__mobile="1"):
                                        tgb.number(label="h Schlaufenhöhe", value="{h}", min=0.0, step=0.1,
                                                   class_name="input-with-unit m-unit Mui-focused")
                                        tgb.number(label="w Schlaufenbreite", value="{w}", min=0.0, step=0.1,
                                                   class_name="input-with-unit m-unit Mui-focused")
                                        tgb.number(label="l_v Seilbogenlänge der Schlaufe", value="{l_v}", min=0.0, step=0.1,
                                                   class_name="input-with-unit m-unit Mui-focused")
                        with tgb.layout(columns="1 1 1 1 1", columns__mobile="1", class_name="p0 button-wrap"):
                            tgb.button(label="Berechnen", on_action=on_click_berechnen, class_name="fullwidth")
                            tgb.button(label="Eingaben zurücksetzen", on_action=on_click_zurücksetzen, class_name="fullwidth")
                            tgb.file_selector(content="{content_vorlage}", label="Vorlage laden", extensions=".xlsx",
                                              drop_message="Drop Message", on_action=on_click_load_vorlage, class_name="fullwidth")
                            tgb.button(label="Laden Rückgängig", on_action=on_click_undo_vorlage, class_name="fullwidth")
                            tgb.button(label="Export herunterladen", on_action=on_click_export_vorlage, class_name="fullwidth")
                            # Button "Leiterseiltyp aufheben" nur optional auf Anfrage wenn diese Funktion mal gewünscht wird.
                            # tgb.button(label="Leiterseiltyp aufheben", on_action=on_click_leiterseiltyp_zurücksetzen, class_name="fullwidth")
                with tgb.part(class_name="card pt1 card-inner"):
                    with tgb.layout(columns="1", class_name=""):
                        tgb.text(value="Ergebnisse", class_name="h3 p-half")
                        with tgb.layout(columns="1 1", columns__mobile="1", class_name="p0"):
                            with tgb.part(class_name="card p1 md-tight "):
                                tgb.text(value="Massgebende Seilzugkräfte bei {temperatur_niedrig_selected}/{temperatur_hoch_selected} °C", class_name="h6")
                                tgb.html("hr")
                                tgb.text(value="Ft,d bei {temp_F_td_massg} °C: **{F_td_massg}** kN", mode="md")
                                tgb.text(value="Ff,d bei {temp_F_fd_massg} °C: **{F_fd_massg}** kN", mode="md")
                                tgb.text(value="Fpi,d bei {temp_F_pi_d_massg} °C: **{F_pi_d_massg}** kN", mode="md")
                                with tgb.expandable(title="Zusätzliche Seilzugkräfte", expanded=False):
                                    tgb.text(value="Max. Seilzugkräfte bei {temperatur_niedrig_selected} °C", class_name="h6")
                                    tgb.html("hr")
                                    tgb.text(value="Ft,d bei {temperatur_niedrig_selected} °C: {F_td_temp_niedrig} kN", mode="md")
                                    tgb.text(value="Ff,d bei {temperatur_niedrig_selected} °C: {F_fd_temp_niedrig} kN", mode="md")
                                    tgb.text(value="Fpi,d bei {temperatur_niedrig_selected} °C: {F_pi_d_temp_niedrig} kN", mode="md")
                                    tgb.html("br")
                                    tgb.text(value="Max. Seilzugkräfte bei {temperatur_hoch_selected} °C", class_name="h6")
                                    tgb.html("hr")
                                    tgb.text(value="Ft,d bei {temperatur_hoch_selected} °C: {F_td_temp_hoch} kN", mode="md")
                                    tgb.text(value="Ff,d bei {temperatur_hoch_selected} °C: {F_fd_temp_hoch} kN", mode="md")
                                    tgb.text(value="Fpi,d bei {temperatur_hoch_selected} °C: {F_pi_d_temp_hoch} kN", mode="md")
                            with tgb.part(class_name="card p1 md-tight "):
                                tgb.text(value="Auslegungen der Stütz- und Abspannpunkte", class_name="h6")
                                tgb.html("hr")
                                tgb.text(value="Befestigungsmittel: **{F_td_fd_pi_d_massg_1}** kN", mode="md")
                                tgb.text(value="Stützisolatoren und Hochspannungsapparate sowie deren Unterkonstruktionen und Fundamente "
                                               "**{F_td_fd_pi_d_massg_2}** kN", mode="md")
                                tgb.text(value="Abspanngerüste, deren Unterkonstruktionen und Fundamente sowie Isolatorketten und "
                                               "Verbindungsmittel **{F_td_fd_pi_d_massg_2}** kN", mode="md")
                                with tgb.expandable(title="Zusätzliche Lastangaben", expanded=False):
                                    tgb.text(value="Die Befestigungsmittel (z.B. Klemmen oder Anschlussbolzen) von Leiterseilen "
                                                   "an Hochspannungsapparaten oder Stützisolatoren sind für den höchsten der "
                                                   "Werte 1,5 Ft,d, 1,0 Ff,d oder 1,0 Fpi,d, hier **{F_td_fd_pi_d_massg_1}** kN,  "
                                                   "zu bemessen.", mode="md", class_name="pt0")
                                    tgb.text(value="Der Bemessungswert der Festigkeit für die Unterkonstruktionen (Gerätegerüste), "
                                                   "Fundamente der Unterkonstruktionen und der Stützisolatoren sowie der Hochspannungsapparaten "
                                                   "muss mindestens **{F_td_fd_pi_d_massg_2}** kN betragen. "
                                                   "Der Bemessungswert der Biegekraft ist als eine am "
                                                   "Isolatorkopf oder an den Anschlusspunkten der Hochspannungsapparate "
                                                   "angreifende Kraft anzusetzen.", mode="md")
                                    tgb.text(value="Für die Bemessung der Abspanngerüste, deren Unterkonstruktionen, "
                                                   "Isolatorketten, Verbindungsmittel und Fundamente ist der höchste "
                                                   "der Werte Ft,d, Ff,d, Fpi,d, hier **{F_td_fd_pi_d_massg_2}** kN, als "
                                                   "statische Last anzusetzen.", mode="md")
                        with tgb.layout(columns="1 1", columns__mobile="1", class_name="p0"):
                            with tgb.part(class_name="card p1 md-tight "):
                                tgb.text(value="Seilauslenkung und Abstand", class_name="h6")
                                tgb.html("hr")
                                tgb.text(value="Max. horizontale Seilauslenkung bei {temp_b_h} °C: **{b_h_max}** m", mode="md")
                                tgb.text(value="Min. Leiterabstand bei {temp_b_h} °C: **{a_min_min}** m", mode="md")
                            with tgb.part(class_name="card p1 md-tight "):
                                tgb.text(value="Erweiterte Ergebnisse", class_name="h6")
                                tgb.html("hr")
                                with tgb.expandable(title="Zusätzliche Berechnungsergebnisse", expanded=False):
                                    tgb.table(data="{calc_result_formatted}", rebuild=True, number_format="%.3e",
                                              size="small", width="100%", page_size=7,
                                              page_size_options=[5, 10, 15, 20, 25, 30, 35, 40, 45, 50])
                        with tgb.layout(columns="1", columns__mobile="1", class_name="p0"):
                            with tgb.part(class_name="card p1 md-tight "):
                                tgb.text(value="Abbildungen", class_name="h6")
                                tgb.html("hr")
                                with tgb.layout(columns="1", class_name="layout-fit", columns__mobile="1"):
                                    with tgb.expandable(title="Diagramm", expanded=False, class_name="h6 expandable-fit"):
                                        with tgb.part(class_name="expandable-scroll"):
                                            tgb.chart(data="{sweep_calc_df}", x="F_st",
                                                      y=["F_td", "F_fd", "F_pi_d"], name=["F<sub>t,d</sub>", "F<sub>f,d</sub>", "F<sub>pi,d</sub>"],
                                                      color=["red", "blue", "green"], mode="lines", rebuild=True, height="800px", width="100%",
                                                      layout="{sweep_chart_layout}", plot_config={"toImageButtonOptions": {"format": 'svg'}})
                                            #tgb.table(examples="{calc_result_formatted}", rebuild=True, show_all=True, number_format="%.3e", size="small", width="35%")
                                        #with tgb.expandable(title="Zusätzliche Berechnungsergebnisse", expanded=False, class_name="h6"):
                                            #tgb.text(value="{calc_result_formatted}", mode="pre")
            with tgb.layout(columns="1", class_name="p1 pt0 layout-fit", columns__mobile="1"):
                with tgb.expandable(title="Tabelle Leiterseiltypen", expanded=False, class_name="expandable-fit"):
                    with tgb.part(class_name="expandable-scroll"):
                        tgb.table("{leiterseiltyp}", width="100%")
        
        


