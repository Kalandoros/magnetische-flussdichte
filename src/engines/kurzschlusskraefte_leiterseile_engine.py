from dataclasses import dataclass
from typing import Optional, Callable
import pandas as pd
import scipy.constants

from src.calculations import kurzschlusskraefte_leiterseile_berechnungen as bkskls


class CalculationCancelled(Exception):
    pass


@dataclass(slots=True)
class KurschlusskräfteLeiterseileInput:
    # Allgemeine Angaben
    leiterseilbefestigung: str
    schlaufe_in_spannfeldmitte: str
    hoehenunterschied_befestigungspunkte: str
    schlaufenebene_parallel_senkrecht: str
    temperatur_niedrig: int
    temperatur_hoch: int

    # Elektrische Werte
    standardkurzschlussstroeme: float
    κ: float
    t_k: float
    f: float

    # Leiterseilkonfiguration
    leiterseiltyp: str
    d: float
    A_s: float
    m_s: float
    E: float
    c_th: float
    n: int
    m_c: Optional[float]

    # Abstände
    l: float
    l_i: Optional[float]
    l_h_f: Optional[float]
    a: float
    a_s: Optional[float]

    # Mechanische Kraftwerte
    F_st_20: float
    F_st_80: float
    S: int

    # Erweiterte Eingaben - Abstände Phasenabstandshalter
    l_s_1: Optional[float]
    l_s_2: Optional[float]
    l_s_3: Optional[float]
    l_s_4: Optional[float]
    l_s_5: Optional[float]
    l_s_6: Optional[float]
    l_s_7: Optional[float]
    l_s_8: Optional[float]
    l_s_9: Optional[float]
    l_s_10: Optional[float]

    # Erweiterte Eingaben - Schlaufengeometrie
    h: Optional[float]
    w: Optional[float]
    l_v: Optional[float]

    def __post_init__(self):
        self.standardkurzschlussstroeme = self.standardkurzschlussstroeme * 10 ** 3
        self.d = self.d * 10 ** -3
        self.A_s = self.A_s * 10 ** -6
        self.E = self.E * 10 ** 6
        self.F_st_20 = self.F_st_20 * 10 ** 3
        self.F_st_80 = self.F_st_80 * 10 ** 3


@dataclass(slots=True)
class KurschlusskräfteLeiterseileResult:
    l_c: Optional[float] = None
    l_eff: Optional[float] = None
    m_c: Optional[float] = None
    F_a: Optional[float] = None
    r: Optional[float] = None
    δ_1: Optional[float] = None
    f_es: Optional[float] = None
    T: Optional[float] = None
    T_res: Optional[float] = None
    E_eff: Optional[float] = None
    N: Optional[float] = None
    ζ: Optional[float] = None
    δ_end: Optional[float] = None
    δ_max: Optional[float] = None
    φ: Optional[float] = None
    ψ: Optional[float] = None
    F_td: Optional[float] = None
    ε_ela: Optional[float] = None
    ε_th: Optional[float] = None
    C_D: Optional[float] = None
    C_F: Optional[float] = None
    f_ed: Optional[float] = None
    F_fd: Optional[float] = None
    b_h: Optional[float] = None
    a_min: Optional[float] = None
    l_s: Optional[float] = None
    F_pi_d: Optional[float] = None
    ν_1: Optional[float] = None
    τ: Optional[float] = None
    γ: Optional[float] = None
    t_pi: Optional[float] = None
    ν_2: Optional[float] = None
    ν_3: Optional[float] = None
    F_v: Optional[float] = None
    ε_st: Optional[float] = None
    ε_pi: Optional[float] = None
    j: Optional[float] = None
    ν_4: Optional[float] = None
    ξ: Optional[float] = None
    η: Optional[float] = None
    ν_e: Optional[float] = None

    def convert_units(self):
        """Konvertiert berechnete Werte in die gewünschten Einheiten """
        if self.F_td is not None:
            self.F_td = self.F_td / 1000
        if self.F_fd is not None:
            self.F_fd = self.F_fd / 1000
        if self.F_pi_d is not None:
            self.F_pi_d = self.F_pi_d / 1000


class KurschlusskräfteLeiterseileMediator:
    def __init__(self, inputs: KurschlusskräfteLeiterseileInput):
        self.inputs = inputs
        self.results = KurschlusskräfteLeiterseileResult()
        self.mode = "normal"
        self.mu0 = scipy.constants.mu_0
        self.g = scipy.constants.g
        self.σ_fin = 50 * 10**6
        
        # Lookup-Dictionary für Berechnungsmethoden
        self._calculation_matrix: dict[tuple, Callable] = {
            # (Leiterseilbefestigung, Schlaufe in Spannfeldmitte, Höhenunterschied, Schlaufenebene)
            ("Abgespannt", "Nein", "Nein", None): self.run_calculation_1_1,
            ("Abgespannt", "Nein", "Nein", ""): self.run_calculation_1_1,  # Fallback für leeren String
            ("Abgespannt", "Nein", "Ja", None): self.run_calculation_1_2,
            ("Abgespannt", "Nein", "Ja", ""): self.run_calculation_1_2,
            ("Abgespannt", "Ja", "Nein", "Ebene parallel"): self.run_calculation_2_1,
            ("Abgespannt", "Ja", "Nein", "Ebene senkrecht"): self.run_calculation_2_2,
            ("Abgespannt", "Ja", "Ja", "Ebene parallel"): self.run_calculation_2_3,
            ("Abgespannt", "Ja", "Ja", "Ebene senkrecht"): self.run_calculation_2_4,
            ("Aufgelegt", "Nein", "Nein", None): self.run_calculation_3_1,
            ("Aufgelegt", "Nein", "Nein", ""): self.run_calculation_3_1,
            ("Unterschlaufung", "Nein", "Nein", None):self.run_calculation_3_2,
            ("Unterschlaufung", "Nein", "Nein", ""):self.run_calculation_3_2,
            # Weitere Kombinationen hier ergänzen ...
        }
    
    def select_and_run_calculation(self) -> dict[str, KurschlusskräfteLeiterseileResult]:
        """
        Wählt die passende Berechnungsmethode basierend auf den Eingabeparametern und führt die Berechnung aus.
        
        Returns:
            Dictionary mit Ergebnissen für F_st_20 und F_st_80
            
        Raises:
            ValueError: Wenn keine passende Berechnungsmethode gefunden wurde
        """
        # Normalisiere Schlaufenebene-Parameter (None wenn nicht relevant)
        schlaufenebene = self.inputs.schlaufenebene_parallel_senkrecht
        if self.inputs.schlaufe_in_spannfeldmitte == "Nein":
            schlaufenebene = None
        
        # Erstelle Lookup-Key
        key = (self.inputs.leiterseilbefestigung, self.inputs.schlaufe_in_spannfeldmitte, self.inputs.hoehenunterschied_befestigungspunkte, schlaufenebene)
        
        # Suche passende Berechnungsmethode
        calculation_method = self._calculation_matrix.get(key)
        
        if calculation_method is None:
            raise ValueError(
                f"❌ Keine Berechnungsmethode für diese Konfiguration gefunden:\n"
                f"  • Leiterseilbefestigung: {self.inputs.leiterseilbefestigung}\n"
                f"  • Schlaufe in Spannfeldmitte: {self.inputs.schlaufe_in_spannfeldmitte}\n"
                f"  • Höhenunterschied >25%: {self.inputs.hoehenunterschied_befestigungspunkte}\n"
                f"  • Schlaufenebene: {self.inputs.schlaufenebene_parallel_senkrecht or 'nicht relevant'}"
            )

        # Führe die ausgewählte Berechnung durch
        return calculation_method()

    def mode_call(self, func_name, *args, **kwargs):
        # 1. Modus ermitteln
        mode = getattr(self, "mode", "normal")

        try:
            # 2. Pfad wählen
            if mode == "loop-mode":
                # Direkt zur numerischen Funktion
                func = getattr(bkskls, f"{func_name}_numerisch")
                return func(*args, **kwargs)
            else:
                # Standard-Kaskade: Symbolisch probieren, sonst numerisch
                try:
                    func_sym = getattr(bkskls, f"{func_name}_symbolisch")
                    return func_sym(*args, **kwargs)
                except (AttributeError, Exception):
                    # Fallback auf numerisch, falls symbolisch nicht geht
                    func_num = getattr(bkskls, f"{func_name}_numerisch")
                    return func_num(*args, **kwargs)

        except Exception as e:
            # HIER ist der entscheidende Punkt:
            # Abfangen des Fehlers und Angabe der Info, in welchem Modus die Engine gerade war.
            raise RuntimeError(f"Fehler in '{func_name}' während {mode}: {str(e)}") from e

    def calculate_sweep_f_st_dataframe(self, f_st_min: float = 0.01, f_st_max: float = 35.0, f_st_step: float = 0.01,
                                       cancel_check: Optional[Callable[[], bool]] = None):

        # Berechnet die Kurzschlusskräfte für eine Reihe von F_st-Werten und gibt einen DataFrame zurück.
        if f_st_step <= 0:
            raise ValueError("f_st_step muss groesser als 0 sein.")
        if f_st_max < f_st_min:
            raise ValueError("f_st_max muss groesser oder gleich f_st_min sein.")

        rows = []
        original_f_st_20 = self.inputs.F_st_20
        original_f_st_80 = self.inputs.F_st_80

        try:
            self.mode = "loop-mode"
            steps = int(round((f_st_max - f_st_min) / f_st_step))
            for i in range(steps + 1):
                if cancel_check and cancel_check():
                    raise CalculationCancelled("Berechnung abgebrochen.")
                f_st_value = f_st_min + (i * f_st_step)
                f_st_internal = f_st_value * 10 ** 3
                self.inputs.F_st_20 = f_st_internal
                #self.inputs.F_st_80 = f_st_internal
                calc_result = self.select_and_run_calculation()

                # Die auskommentierten Zeilen sind nicht notwendig, da F_st_20 und F_st_80 in der Schleife gleich sind.
                result_20 = calc_result.get("F_st_20")
                #result_80 = calc_result.get("F_st_80")

                rows.append({
                    "F_st": f_st_value,
                    #"F_st_20": f_st_value,
                    #"F_st_80": f_st_value,
                    "F_td": result_20.F_td if result_20 else None,
                    "F_fd": result_20.F_fd if result_20 else None,
                    "F_pi_d": result_20.F_pi_d if result_20 else None,
                    #"F_td_80": result_80.F_td if result_80 else None,
                    #"F_fd_80": result_80.F_fd if result_80 else None,
                    #"F_pi_d_80": result_80.F_pi_d if result_80 else None,
                })
        finally:
            self.inputs.F_st_20 = original_f_st_20
            self.inputs.F_st_80 = original_f_st_80
            self.mode = "normal"

        return pd.DataFrame(rows)

    def run_calculation_1_1(self) -> dict[str, KurschlusskräfteLeiterseileResult]:
        """
        Fall 1.1: Abgespannte Leiterseile ohne Schlaufe, ohne Höhenunterschied

        Anwendungsbereich:
        - Leiterseilbefestigung: Abgespannt
        - Schlaufe in Spannfeldmitte: Nein
        - Höhenunterschied >25%: Nein

        Norm: SN EN 60865-1:2012 Kapitel 6.2.3
        """
        results = {}

        for key, F_st in [('F_st_20', self.inputs.F_st_20), ('F_st_80', self.inputs.F_st_80)]:
            result = KurschlusskräfteLeiterseileResult()

            # Schritt 1: Effektive Seillänge
            result.l_c = bkskls.l_c(self.inputs.l, self.inputs.l_i)

            # Schritt 1a: Massenbelag konzentrischer Lasten
            result.m_c = bkskls.m_c(self.inputs.m_c, self.inputs.n, result.l_c)

            # Schritt 2: Charakteristischer elektromagnetischer Kraftbelag
            result.F_a = bkskls.F_a(self.mu0, self.inputs.standardkurzschlussstroeme,
                                    self.inputs.l, result.l_c, self.inputs.a)

            # Schritt 3: Verhältnis r
            result.r = bkskls.r(result.F_a, self.inputs.n, self.inputs.m_s+result.m_c, self.g)

            # Schritt 4: Richtung δ_1
            result.δ_1 = bkskls.δ_1(result.r)

            # Schritt 5: Statischer Durchhang
            result.f_es = bkskls.f_es(self.inputs.n, self.inputs.m_s+result.m_c, self.g, self.inputs.l, F_st)

            # Schritt 6: Periodendauer
            result.T = bkskls.T(result.f_es, self.g)

            # Schritt 7: Resultierende Periodendauer
            result.T_res = bkskls.T_res(result.T, result.r, result.δ_1)

            # Schritt 8: Effektiver E-Modul
            result.E_eff = bkskls.E_eff(self.inputs.E, F_st, self.inputs.n, self.inputs.A_s, self.σ_fin)

            # Schritt 9: Steifigkeitsnorm
            result.N = bkskls.N(self.inputs.S, self.inputs.l,
                               self.inputs.n, result.E_eff, self.inputs.A_s)

            # Schritt 10: Beanspruchungsfaktor
            result.ζ = bkskls.ζ(self.inputs.n, self.g, self.inputs.m_s+result.m_c, self.inputs.l, F_st, result.N)

            # Schritt 11: Ausschwingwinkel
            result.δ_end = bkskls.δ_end(result.δ_1, self.inputs.t_k, result.T_res)

            # Schritt 12: Maximaler Ausschwingwinkel
            result.δ_max = bkskls.δ_max(result.r, result.δ_end)

            # Schritt 13: Lastparameter φ
            result.φ = bkskls.φ_ohne_schlaufe(self.inputs.t_k, result.T_res, result.r, result.δ_end)

            # Schritt 14: Lastparameter ψ
            result.ψ = self.mode_call(func_name="ψ_ohne_schlaufe", φ=result.φ, ζ=result.ζ)
            # result.ψ = bkskls.ψ_ohne_schlaufe(result.φ, result.ζ)

            # Schritt 15: Kurzschluss-Seilzugkraft F_td
            result.F_td = bkskls.F_td_ohne_schlaufe_spannfeldmitte(F_st, result.φ, result.ψ)

            # Schritt 16: Elastische Seildehnung ε_ela
            result.ε_ela = bkskls.ε_ela(result.N, result.F_td, F_st)

            # Schritt 17: thermische Seildehnung ε_th
            result.ε_th = bkskls.ε_th(self.inputs.c_th, self.inputs.standardkurzschlussstroeme, self.inputs.n,
                                      self.inputs.A_s, self.inputs.t_k, result.T_res)

            # Schritt 18: Faktor Durchhangvergrößerung C_D
            result.C_D = bkskls.C_D(self.inputs.l, result.f_es, result.ε_ela, result.ε_th)

            # Schritt 19: Faktor Durchhangvergrößerung C_F
            result.C_F = bkskls.C_F(result.r)

            # Schritt 20: Dynamischer Seildurchhangs f_ed
            result.f_ed = bkskls.f_ed(result.C_D, result.C_F, result.f_es)

            # Schritt 21: Fall-Seilzugkraft F_fd
            result.F_fd = bkskls.F_fd(F_st, result.ζ, result.δ_max)

            # Schritt 22: Max. Horizontale Seilauslenkung b_h
            result.b_h = bkskls.b_h_ohne_schlaufe_spannfeldmitte_abgespannt(result.f_ed, result.δ_max, result.δ_1)

            # Schritt 23: Min. minimaler Leiterabstand a_min
            result.a_min = bkskls.a_min(self.inputs.a, result.b_h)

            # Schritt 24: Abstände Abstandshalter
            result.l_s = bkskls.l_s(self.inputs.l_s_1, self.inputs.l_s_2, self.inputs.l_s_3, self.inputs.l_s_4, self.inputs.l_s_5,
                                    self.inputs.l_s_6, self.inputs.l_s_7, self.inputs.l_s_8, self.inputs.l_s_9, self.inputs.l_s_10)

            # Schritt 25: Bündel-Seilzugkraft F_pi_d
            if self.inputs.a_s not in (None, 0) and self.inputs.d not in (None, 0) and self.inputs.n not in (None, 0):
                if (self.inputs.a_s / self.inputs.d <= 2.0 and result.l_s >= 50 * self.inputs.a_s and self.inputs.n > 1) or (self.inputs.a_s / self.inputs.d <= 2.5 and result.l_s >= 70 * self.inputs.a_s and self.inputs.n > 1):
                    result.F_pi_d = bkskls.F_pi_d_ohne_j(result.F_td, self.inputs.a_s, self.inputs.d, result.l_s)
                elif self.inputs.n > 1:
                    result.ν_1 = bkskls.ν_1(self.mu0, self.inputs.standardkurzschlussstroeme, self.inputs.a_s, self.inputs.n, self.inputs.m_s, self.inputs.d, self.inputs.f)
                    result.τ = bkskls.τ(self.inputs.f, self.inputs.κ)
                    result.γ = bkskls.γ(self.inputs.f, result.τ)
                    result.t_pi, result.ν_2 = bkskls.T_pi_and_ν_2(result.ν_1, self.inputs.f, result.τ, result.γ)
                    result.ν_3 = bkskls.ν_3(self.inputs.a_s, self.inputs.d, self.inputs.n)
                    result.F_v = bkskls.F_v(self.mu0, self.inputs.standardkurzschlussstroeme, self.inputs.a_s, result.l_c, result.l_s, result.l_eff, self.inputs.n, result.ν_2, result.ν_3)
                    result.ε_st = bkskls.ε_st(F_st, result.l_c, result.l_s, result.l_eff, result.N, self.inputs.a_s, self.inputs.n, self.inputs.d)
                    result.ε_pi = bkskls.ε_pi(result.F_v, result.l_c, result.l_s, result.l_eff, result.N, self.inputs.a_s, self.inputs.n, self.inputs.d)
                    result.j = bkskls.j(result.ε_st, result.ε_pi)
                    # Optional ein If-else einfügen für j=>1 und j<1, aber eigentlich schon Funktion enthalten
                    result.ξ = self.mode_call(func_name="ξ", j=result.j, ε_st=result.ε_st)
                    #result.ξ = bkskls.ξ(result.j, result.ε_st)
                    result.η = bkskls.η(result.ε_st, result.j, result.ν_3, self.inputs.n, self.inputs.a_s, self.inputs.d)
                    result.ν_4 = bkskls.ν_4(result.j, self.inputs.a_s, self.inputs.d, result.η)
                    result.ν_e = bkskls.ν_e(self.mu0, result.j, self.inputs.standardkurzschlussstroeme, self.inputs.a_s, result.N,
                                            self.inputs.n, result.l_c, result.l_s, result.l_eff, self.inputs.d, result.ν_2, result.ν_4, result.ξ, result.η)
                    result.F_pi_d = bkskls.F_pi_d_mit_j(F_st, result.j, result.ν_e, result.ε_st, result.ξ, result.η)

            # Einheitenkonvertierung
            result.convert_units()

            results[key] = result

        return results

    def run_calculation_1_2(self) -> dict[str, KurschlusskräfteLeiterseileResult]:
        """
        Fall 1.2: Abgespannte Leiterseile ohne Schlaufe, mit Höhenunterschied >25%
        
        Anwendungsbereich:
        - Leiterseilbefestigung: Abgespannt
        - Schlaufe in Spannfeldmitte: Nein
        - Höhenunterschied >25%: Ja
        
        Norm: SN EN 60865-1:2012 Kapitel 6.3
        """
        # TODO: Implementierung für Fall 1.2
        raise NotImplementedError("Fall 1.2 noch nicht implementiert")

    def run_calculation_2_1(self) -> dict[str, KurschlusskräfteLeiterseileResult]:
        """
        Fall 2.1: Abgespannte Leiterseile mit Schlaufe (Ebene parallel)
        
        Anwendungsbereich:
        - Leiterseilbefestigung: Abgespannt
        - Schlaufe in Spannfeldmitte: Ja
        - Schlaufenebene: Ebene parallel
        
        Norm: SN EN 60865-1:2012 Kapitel 6.2.5
        """
        # TODO: Implementierung für Fall 2.1
        raise NotImplementedError("Fall 2.1 noch nicht implementiert")

    def run_calculation_2_2(self) -> dict[str, KurschlusskräfteLeiterseileResult]:
        """
        Fall 2.2: Abgespannte Leiterseile mit Schlaufe (Ebene senkrecht)
        
        Anwendungsbereich:
        - Leiterseilbefestigung: Abgespannt
        - Schlaufe in Spannfeldmitte: Ja
        - Schlaufenebene: Ebene senkrecht
        
        Norm: SN EN 60865-1:2012 Kapitel 6.2.5
        """
        # TODO: Implementierung für Fall 2.2
        raise NotImplementedError("Fall 2.2 noch nicht implementiert")

    def run_calculation_2_3(self) -> dict[str, KurschlusskräfteLeiterseileResult]:
        """
        Fall 2.3: Abgespannte Leiterseile mit Schlaufe und Höhenunterschied (Ebene parallel)
        """
        # TODO: Implementierung für Fall 2.3
        raise NotImplementedError("Fall 2.3 noch nicht implementiert")

    def run_calculation_2_4(self) -> dict[str, KurschlusskräfteLeiterseileResult]:
        """
        Fall 2.4: Abgespannte Leiterseile mit Schlaufe und Höhenunterschied (Ebene senkrecht)
        """
        # TODO: Implementierung für Fall 2.4
        raise NotImplementedError("Fall 2.4 noch nicht implementiert")

    def run_calculation_3_1(self) -> dict[str, KurschlusskräfteLeiterseileResult]:
        """
        Fall 3.1: Aufgelegte Leiterseile ohne Schlaufe
        
        Anwendungsbereich:
        - Leiterseilbefestigung: Aufgelegt
        - Schlaufe in Spannfeldmitte: Nein
        
        Norm: SN EN 60865-1:2012 Kapitel 6.2.3
        """

        results = {}

        for key, F_st in [('F_st_20', self.inputs.F_st_20), ('F_st_80', self.inputs.F_st_80)]:
            result = KurschlusskräfteLeiterseileResult()

            # Schritt 1: Effektive Seillänge
            result.l_eff = bkskls.l_eff(self.inputs.l, self.inputs.l_h_f)

            # Schritt 1a: Massenbelag konzentrischer Lasten
            result.m_c = bkskls.m_c(self.inputs.m_c, self.inputs.n, self.inputs.l)

            # Schritt 2: Charakteristischer elektromagnetischer Kraftbelag
            result.F_a = bkskls.F_a(self.mu0, self.inputs.standardkurzschlussstroeme, result.l_eff, result.l_eff, self.inputs.a)

            # Schritt 3: Verhältnis r
            result.r = bkskls.r(result.F_a, self.inputs.n, self.inputs.m_s + result.m_c, self.g)

            # Schritt 4: Richtung δ_1
            result.δ_1 = bkskls.δ_1(result.r)

            # Schritt 5: Statischer Durchhang
            result.f_es = bkskls.f_es(self.inputs.n, self.inputs.m_s + result.m_c, self.g, result.l_eff, F_st)

            # Schritt 6: Periodendauer
            result.T = bkskls.T(result.f_es, self.g)

            # Schritt 7: Resultierende Periodendauer
            result.T_res = bkskls.T_res(result.T, result.r, result.δ_1)

            # Schritt 8: Effektiver E-Modul
            result.E_eff = bkskls.E_eff(self.inputs.E, F_st, self.inputs.n, self.inputs.A_s, self.σ_fin)

            # Schritt 9: Steifigkeitsnorm
            result.N = bkskls.N(self.inputs.S, result.l_eff, self.inputs.n, result.E_eff, self.inputs.A_s)

            # Schritt 10: Beanspruchungsfaktor
            result.ζ = bkskls.ζ(self.inputs.n, self.g, self.inputs.m_s + result.m_c, result.l_eff, F_st, result.N)

            # Schritt 11: Ausschwingwinkel
            result.δ_end = bkskls.δ_end(result.δ_1, self.inputs.t_k, result.T_res)

            # Schritt 12: Maximaler Ausschwingwinkel
            result.δ_max = bkskls.δ_max(result.r, result.δ_end)

            # Schritt 13: Lastparameter φ
            result.φ = bkskls.φ_ohne_schlaufe(self.inputs.t_k, result.T_res, result.r, result.δ_end)

            # Schritt 14: Lastparameter ψ
            result.ψ = self.mode_call(func_name="ψ_ohne_schlaufe", φ=result.φ, ζ=result.ζ)
            #result.ψ = bkskls.ψ_ohne_schlaufe(result.φ, result.ζ)

            # Schritt 15: Kurzschluss-Seilzugkraft F_td
            result.F_td = bkskls.F_td_ohne_schlaufe_spannfeldmitte(F_st, result.φ, result.ψ)

            # Schritt 16: Elastische Seildehnung ε_ela
            result.ε_ela = bkskls.ε_ela(result.N, result.F_td, F_st)

            # Schritt 17: thermische Seildehnung ε_th
            result.ε_th = bkskls.ε_th(self.inputs.c_th, self.inputs.standardkurzschlussstroeme, self.inputs.n, self.inputs.A_s, self.inputs.t_k, result.T_res)

            # Schritt 18: Faktor Durchhangvergrößerung C_D
            result.C_D = bkskls.C_D(result.l_eff, result.f_es, result.ε_ela, result.ε_th)

            # Schritt 19: Faktor Durchhangvergrößerung C_F
            result.C_F = bkskls.C_F(result.r)

            # Schritt 20: Dynamischer Seildurchhangs f_ed
            result.f_ed = bkskls.f_ed(result.C_D, result.C_F, result.f_es)

            # Schritt 21: Fall-Seilzugkraft F_fd
            result.F_fd = bkskls.F_fd(F_st, result.ζ, result.δ_max)

            # Schritt 22: Max. Horizontale Seilauslenkung b_h
            result.b_h = bkskls.b_h_ohne_schlaufe_spannfeldmitte_aufgelegt(result.f_ed, result.δ_max)

            # Schritt 23: Min. minimaler Leiterabstand a_min
            result.a_min = bkskls.a_min(self.inputs.a, result.b_h)

            # Schritt 24: Abstände Abstandshalter
            result.l_s = bkskls.l_s(self.inputs.l_s_1, self.inputs.l_s_2, self.inputs.l_s_3, self.inputs.l_s_4,
                                    self.inputs.l_s_5,
                                    self.inputs.l_s_6, self.inputs.l_s_7, self.inputs.l_s_8, self.inputs.l_s_9,
                                    self.inputs.l_s_10)

            # Schritt 25: Bündel-Seilzugkraft F_pi_d
            if self.inputs.a_s not in (None, 0) and self.inputs.d not in (None, 0) and self.inputs.n not in (None, 0):
                if (self.inputs.a_s / self.inputs.d <= 2.0 and result.l_s >= 50 * self.inputs.a_s and self.inputs.n > 1) or (self.inputs.a_s / self.inputs.d <= 2.5 and result.l_s >= 70 * self.inputs.a_s and self.inputs.n > 1):
                    result.F_pi_d = bkskls.F_pi_d_ohne_j(result.F_td, self.inputs.a_s, self.inputs.d, result.l_s)
                elif self.inputs.n > 1:
                    result.ν_1 = bkskls.ν_1(self.mu0, self.inputs.standardkurzschlussstroeme, self.inputs.a_s, self.inputs.n, self.inputs.m_s, self.inputs.d, self.inputs.f)
                    result.τ = bkskls.τ(self.inputs.f, self.inputs.κ)
                    result.γ = bkskls.γ(self.inputs.f, result.τ)
                    result.t_pi, result.ν_2 = bkskls.T_pi_and_ν_2(result.ν_1, self.inputs.f, result.τ, result.γ)
                    result.ν_3 = bkskls.ν_3(self.inputs.a_s, self.inputs.d, self.inputs.n)
                    result.F_v = bkskls.F_v(self.mu0, self.inputs.standardkurzschlussstroeme, self.inputs.a_s, result.l_c, result.l_s, result.l_eff, self.inputs.n, result.ν_2, result.ν_3)
                    result.ε_st = bkskls.ε_st(F_st, result.l_c, result.l_s, result.l_eff, result.N, self.inputs.a_s, self.inputs.n, self.inputs.d)
                    result.ε_pi = bkskls.ε_pi(result.F_v, result.l_c, result.l_s, result.l_eff, result.N, self.inputs.a_s, self.inputs.n, self.inputs.d)
                    result.j = bkskls.j(result.ε_st, result.ε_pi)
                    # Optional ein If-else einfügen für j=>1 und j<1, aber eigentlich schon Funktion enthalten
                    result.ξ = self.mode_call(func_name="ξ", j=result.j, ε_st=result.ε_st)
                    # result.ξ = bkskls.ξ(result.j, result.ε_st)
                    result.η = bkskls.η(result.ε_st, result.j, result.ν_3, self.inputs.n, self.inputs.a_s, self.inputs.d)
                    result.ν_4 = bkskls.ν_4(result.j, self.inputs.a_s, self.inputs.d, result.η)
                    result.ν_e = bkskls.ν_e(self.mu0, result.j, self.inputs.standardkurzschlussstroeme, self.inputs.a_s, result.N,
                                            self.inputs.n, result.l_c, result.l_s, result.l_eff, self.inputs.d, result.ν_2, result.ν_4, result.ξ, result.η)
                    result.F_pi_d = bkskls.F_pi_d_mit_j(F_st, result.j, result.ν_e, result.ε_st, result.ξ, result.η)

            # Einheitenkonvertierung
            result.convert_units()

            results[key] = result

        return results

    def run_calculation_3_2(self) -> dict[str, KurschlusskräfteLeiterseileResult]:
        """
        Fall 3.2: Unterschlaufung ohne Schlaufe

        Anwendungsbereich:
        - Leiterseilbefestigung: Unterschlaufung
        - Schlaufe in Spannfeldmitte: Nein
        - Höhenunterschied >25%: Nein

        Literatur: The mechanical effects of short-circuit currents in open air substations (part II), WG23.03, TB214, 2002 - Cigre
        """

        results = {}

        for key, F_st in [('F_st_20', self.inputs.F_st_20), ('F_st_80', self.inputs.F_st_80)]:
            result = KurschlusskräfteLeiterseileResult()

            # Schritt 1: Effektive Seillänge
            result.l_eff = bkskls.l_eff(self.inputs.l, self.inputs.l_h_f)

            # Schritt 1a: Massenbelag konzentrischer Lasten
            result.m_c = bkskls.m_c(self.inputs.m_c, self.inputs.n, self.inputs.l)

            # Schritt 2: Charakteristischer elektromagnetischer Kraftbelag
            result.F_a = bkskls.F_a(self.mu0, self.inputs.standardkurzschlussstroeme, result.l_eff, result.l_eff, self.inputs.a)

            # Schritt 3: Verhältnis r angepasst an Schlaufe
            result.r = bkskls.r_u(result.F_a, self.inputs.n, self.inputs.m_s + result.m_c, self.g)

            # Schritt 4: Richtung δ_1
            result.δ_1 = bkskls.δ_1(result.r)

            # Schritt 5: Statischer Durchhang
            result.f_es = bkskls.f_es(self.inputs.n, self.inputs.m_s + result.m_c, self.g, result.l_eff, F_st)

            # Schritt 6: Periodendauer
            result.T = bkskls.T(result.f_es, self.g)

            # Schritt 7: Resultierende Periodendauer
            result.T_res = bkskls.T_res(result.T, result.r, result.δ_1)

            # Schritt 8: Effektiver E-Modul
            result.E_eff = bkskls.E_eff(self.inputs.E, F_st, self.inputs.n, self.inputs.A_s, self.σ_fin)

            # Schritt 9: Steifigkeitsnorm
            result.N = bkskls.N(self.inputs.S, result.l_eff, self.inputs.n, result.E_eff, self.inputs.A_s)

            # Schritt 10: Beanspruchungsfaktor
            result.ζ = bkskls.ζ(self.inputs.n, self.g, self.inputs.m_s + result.m_c, result.l_eff, F_st, result.N)

            # Schritt 11: Ausschwingwinkel
            result.δ_end = bkskls.δ_end(result.δ_1, self.inputs.t_k, result.T_res)

            # Schritt 12: Maximaler Ausschwingwinkel
            result.δ_max = bkskls.δ_max(result.r, result.δ_end)

            # Schritt 13: Lastparameter φ
            result.φ = bkskls.φ_ohne_schlaufe(self.inputs.t_k, result.T_res, result.r, result.δ_end)

            # Schritt 14: Lastparameter ψ
            result.ψ = self.mode_call(func_name="ψ_ohne_schlaufe", φ=result.φ, ζ=result.ζ)
            # result.ψ = bkskls.ψ_ohne_schlaufe(result.φ, result.ζ)

            # Schritt 15: Kurzschluss-Seilzugkraft F_td
            result.F_td = bkskls.F_td_ohne_schlaufe_spannfeldmitte(F_st, result.φ, result.ψ)

            # Schritt 16: Elastische Seildehnung ε_ela
            result.ε_ela = bkskls.ε_ela(result.N, result.F_td, F_st)

            # Schritt 17: thermische Seildehnung ε_th
            result.ε_th = bkskls.ε_th(self.inputs.c_th, self.inputs.standardkurzschlussstroeme, self.inputs.n, self.inputs.A_s, self.inputs.t_k, result.T_res)

            # Schritt 18: Faktor Durchhangvergrößerung C_D
            result.C_D = bkskls.C_D(result.l_eff, result.f_es, result.ε_ela, result.ε_th)

            # Schritt 19: Faktor Durchhangvergrößerung C_F
            result.C_F = bkskls.C_F(result.r)

            # Schritt 20: Dynamischer Seildurchhangs f_ed
            result.f_ed = bkskls.f_ed(result.C_D, result.C_F, result.f_es)

            # Schritt 21: Fall-Seilzugkraft F_fd
            result.F_fd = bkskls.F_fd(F_st, result.ζ, result.δ_max)

            # Schritt 22: Max. Horizontale Seilauslenkung b_h
            result.b_h = bkskls.b_h_ohne_schlaufe_spannfeldmitte_aufgelegt(result.f_ed, result.δ_max)

            # Schritt 23: Min. minimaler Leiterabstand a_min
            result.a_min = bkskls.a_min(self.inputs.a, result.b_h)

            # Schritt 24: Abstände Abstandshalter
            result.l_s = bkskls.l_s(self.inputs.l_s_1, self.inputs.l_s_2, self.inputs.l_s_3, self.inputs.l_s_4, self.inputs.l_s_5, self.inputs.l_s_6, self.inputs.l_s_7, self.inputs.l_s_8,
                                    self.inputs.l_s_9, self.inputs.l_s_10)

            # Schritt 25: Bündel-Seilzugkraft F_pi_d
            if self.inputs.a_s not in (None, 0) and self.inputs.d not in (None, 0) and self.inputs.n not in (None, 0):
                if (self.inputs.a_s / self.inputs.d <= 2.0 and result.l_s >= 50 * self.inputs.a_s and self.inputs.n > 1) or (
                        self.inputs.a_s / self.inputs.d <= 2.5 and result.l_s >= 70 * self.inputs.a_s and self.inputs.n > 1):
                    result.F_pi_d = bkskls.F_pi_d_ohne_j(result.F_td, self.inputs.a_s, self.inputs.d, result.l_s)
                elif self.inputs.n > 1:
                    result.ν_1 = bkskls.ν_1(self.mu0, self.inputs.standardkurzschlussstroeme, self.inputs.a_s, self.inputs.n, self.inputs.m_s, self.inputs.d, self.inputs.f)
                    result.τ = bkskls.τ(self.inputs.f, self.inputs.κ)
                    result.γ = bkskls.γ(self.inputs.f, result.τ)
                    result.t_pi, result.ν_2 = bkskls.T_pi_and_ν_2(result.ν_1, self.inputs.f, result.τ, result.γ)
                    result.ν_3 = bkskls.ν_3(self.inputs.a_s, self.inputs.d, self.inputs.n)
                    result.F_v = bkskls.F_v(self.mu0, self.inputs.standardkurzschlussstroeme, self.inputs.a_s, result.l_c, result.l_s, result.l_eff, self.inputs.n, result.ν_2, result.ν_3)
                    result.ε_st = bkskls.ε_st(F_st, result.l_c, result.l_s, result.l_eff, result.N, self.inputs.a_s, self.inputs.n, self.inputs.d)
                    result.ε_pi = bkskls.ε_pi(result.F_v, result.l_c, result.l_s, result.l_eff, result.N, self.inputs.a_s, self.inputs.n, self.inputs.d)
                    result.j = bkskls.j(result.ε_st, result.ε_pi)
                    # Optional ein If-else einfügen für j=>1 und j<1, aber eigentlich schon Funktion enthalten
                    result.ξ = self.mode_call(func_name="ξ", j=result.j, ε_st=result.ε_st)
                    # result.ξ = bkskls.ξ(result.j, result.ε_st)
                    result.η = bkskls.η(result.ε_st, result.j, result.ν_3, self.inputs.n, self.inputs.a_s, self.inputs.d)
                    result.ν_4 = bkskls.ν_4(result.j, self.inputs.a_s, self.inputs.d, result.η)
                    result.ν_e = bkskls.ν_e(self.mu0, result.j, self.inputs.standardkurzschlussstroeme, self.inputs.a_s, result.N, self.inputs.n, result.l_c, result.l_s, result.l_eff, self.inputs.d,
                                            result.ν_2, result.ν_4, result.ξ, result.η)
                    result.F_pi_d = bkskls.F_pi_d_mit_j(F_st, result.j, result.ν_e, result.ε_st, result.ξ, result.η)

            # Einheitenkonvertierung
            result.convert_units()

            results[key] = result

        return results

def calculate_kurschlusskräfte_leiterseile(inputs: KurschlusskräfteLeiterseileInput) -> dict[str, KurschlusskräfteLeiterseileResult]:
    """
    Hauptfunktion zur Berechnung der Kurzschlusskräfte.
    Wählt automatisch die passende Berechnungsmethode basierend auf den Eingabeparametern.
    """
    mediator = KurschlusskräfteLeiterseileMediator(inputs)
    return mediator.select_and_run_calculation()

def calculate_kurschlusskräfte_leiterseile_sweep_df(inputs, f_st_min: float = 0.01, f_st_max: float = 35.0,
                                                    f_st_step: float = 0.01, cancel_check: Optional[Callable[[], bool]] = None) -> pd.DataFrame:
    """
    Berechnet Kurzschlusskräfte für eine Reihe von F_st-Werten (kN) und gibt einen DataFrame zurück.
    """
    mediator = KurschlusskräfteLeiterseileMediator(inputs)
    return mediator.calculate_sweep_f_st_dataframe(
        f_st_min=f_st_min,
        f_st_max=f_st_max,
        f_st_step=f_st_step,
        cancel_check=cancel_check,
    )





