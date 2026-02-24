import math
import scipy
import sympy
from scipy.optimize import fsolve, brentq
from numpy.ma.core import arccos
import numpy as np
from functools import lru_cache


# Konstanten
μ0 = scipy.constants.mu_0 # 4 * math.pi * 1e-7 ist auch möglich
g = scipy.constants.g # 9.81 ist auch möglich
σ_fin = 50 * 10**6 # σ_fin niedrigste Spannung, ab der das Elastizitätsmodul konstant wird in N/m^2 - Gleichung (27)


# Hilfsgleichung l_s Abstände Abstandshalter
@lru_cache(maxsize=5)
def l_s(l_s_1: float|None = None, l_s_2: float|None = None, l_s_3: float|None = None, l_s_4: float|None = None,
        l_s_5: float|None = None, l_s_6: float|None = None, l_s_7: float|None = None, l_s_8: float|None = None,
        l_s_9: float|None = None, l_s_10: float|None = None) -> float:
    """
    Funktion zur Berechnung des gemittelten Abstandes der Abstandhalter l_s im Spannfeld in m nach SN EN 60865-2:2017 Kapitel 8.3.6
    l_s: Mittenabstand der Zwischenstücke oder Mittenabstand eines Zwischenstücks und des benachbarten Stützpunkts S in m
    l_s_1: Abstand des Abstandshalters beginnend bei der Abspannung nach der Isolatorkette in m
    l_s_2...10: Abstand des Abstandshalters zum links neben sich befindlichen Abstandhalter in m
    Erläuterung zu l_s:
    Die Summer der für die Berechnung von l_s angebenen Werte muss gleich der Länge l_c oder l_eff sein.
    """

    liste_abstände_abstandshalter: list[float|None] = [l_s_1, l_s_2, l_s_3, l_s_4, l_s_5, l_s_6, l_s_7, l_s_8, l_s_9, l_s_10]

    summe_abstände_abstandshalter: float = 0.0
    summe_abstandshalter: int = 0

    for abstand_abstandshalter in liste_abstände_abstandshalter:
        if abstand_abstandshalter is not None and abstand_abstandshalter != 0.0:
            summe_abstände_abstandshalter += abstand_abstandshalter
            summe_abstandshalter += 1

    if summe_abstandshalter == 0:
        return 0.0
    l_s: float = summe_abstände_abstandshalter / summe_abstandshalter
    return l_s

# Hilfsgleichungen m_c Masse konzentrischer Massen
@lru_cache(maxsize=5)
def m_c(m_c: float|None , n: float, l_c: float) -> float:
    """
    Funktion zur Berechnung der konzentrierten Massen im Spannfeld m_c in kg
    m_c: Summe aller konzentrierten Massen im Spannfeld in kg
    l_c: Seillänge eines Hauptleiters im Spannfeld in m
    n: Anzahl der Teilleiter eines Hauptleiters (dimensionslos)
    Hinweis: m_c beinhaltet die Masse aller Massen, die sich gesamthaft auf allen Teilleitern befinden.
    """
    if m_c not in (None, 0.0, 0):
        m_c: float = m_c / (n * l_c)
        return m_c
    return 0.0

# Hilfsgleichungen l_v Seilbogen Länge der Schlaufe
@lru_cache(maxsize=5)
def l_v(h: float, w:float) -> float:
    """
    Funktion zur Berechnung der Seil(bogen)länge der Schlaufe l_v in m
    l_v: eil(bogen)länge der Schlaufe in m
    h: Schlaufenhöhe in m
    w: Schlaufenbreite in m
    Erläuterung zu l_v:
    Die Länge der Schlaufe ist ein abgeschätztes Mass, welcher als Mittelwert von Beispielen entnommen wurde.
    """
    l_v: float = (math.sqrt(h**2 + w**2)) * 1.05
    return l_v

# Grössen ab Kapitel 6.2.2
@lru_cache(maxsize=5)
def l_c(l: float, l_i: float) -> float:
    """
    Funktion zur Berechnung der Seillänge lc eines Hauptleiters im Spannfeld in m nach SN EN 60865-1:2012 Kapitel 6.2.2
    l_c: Seillänge eines Hauptleiters im Spannfeld in m
    l: Mittenabstand der Stützpunkte in m
    l_i: Länge einer Abspann-Isolatorkette in m
    a: Leitermittenabstand in m
    Erläuterung zu lc:
    Bei Feldern mit aufgelegten Seilen, die Stützisolatoren auf Biegung beanspruchen, gilt lc = l. Bei Feldern mit
    abgespannten Seilen gilt l_c = l − 2 * l_i, dabei ist li die Länge einer Abspann-Isolatorkette.
    (SN EN 60865-1:2012 Kapitel 6.2.2 Seite 26)
    """
    if l_i not in (None, 0.0, 0):
        l_c: float = l - (2 * l_i)
        return l_c
    else:
        l_c: float = l
        return l_c

# Hilfsgleichungen l_eff bei aufgelegten Seilen
@lru_cache(maxsize=5)
def l_eff(l: float, l_h_f: float) -> float:
    """
    Funktion zur Berechnung der Seillänge l_eff eines Hauptleiters im Spannfeld in m nach SN EN 60865-2:2017 Kapitel 8.3.1
    l_eff: Seillänge eines Hauptleiters im Spannfeld bei aufgelegten Seilen in m
    l: Mittenabstand der Stützpunkte in m
    l_h_f: Länge einer Klemme und Berücksichtigung des Formfaktors in m
    Erläuterung zu l_eff:
    Der Wert l_eff wird angegeben, wenn Klemmstücke am Isolatorkopf oder die Anschlussstelle hinausragen und sich
    dadurch die effektive Länge verringert.
    """
    if l_h_f not in (None, 0.0, 0):
        l_eff: float = l - (2 * l_h_f)
        return l_eff
    else:
        l_eff: float = l
        return l_eff

# Gleichung (20)
@lru_cache(maxsize=5)
def r(F_: float, n: float, m_s: float, g: float) -> float:
    """
    Funktion zur Berechnung Verhältnisses r der elektromagnetischen Kraft auf ein Leiterseil bei Kurzschluss zur
    Eigengewichtskraft (dimensionslos) nach SN EN 60865-1:2012 Kapitel 6.2.2
    r: Verhältnis von elektromagnetischer Kraft auf ein Leiterseil bei Kurzschluss zur Eigengewichtskraft (dimensionslos)
    F_: charakteristischer elektromagnetischer Kraftbelag auf den Hauptleiter in Seilanordnungen in N/m
    n: Anzahl der Teilleiter eines Hauptleiters (dimensionslos)
    m_s: Massenbelag eines Teilleiters in kg/m
    g: Normfallbeschleunigung in m/s^2
    """
    r: float = F_ / (n * m_s * g)
    return r

# Gleichung (20) angepasst
@lru_cache(maxsize=5)
def r_u(F_: float, n: float, m_s: float, g: float) -> float:
    """
    Funktion zur Berechnung Verhältnisses r der elektromagnetischen Kraft auf ein Leiterseil bei Kurzschluss zur
    Eigengewichtskraft (dimensionslos) nach SN EN 60865-1:2012 Kapitel 6.2.2
    Angepasst für Unterschlaufungen nach The mechanical effects of short-circuit currents in open air substations (part II), WG23.03, TB214, 2002 - Cigre Kapitel 3.7.4
    r_u: Verhältnis von elektromagnetischer Kraft auf ein Leiterseil bei Kurzschluss zur Eigengewichtskraft bei Unterschlaufungen (dimensionslos)
    F_: charakteristischer elektromagnetischer Kraftbelag auf den Hauptleiter in Seilanordnungen in N/m
    n: Anzahl der Teilleiter eines Hauptleiters (dimensionslos)
    m_s: Massenbelag eines Teilleiters in kg/m
    g: Normfallbeschleunigung in m/s^2
    """
    r_u: float = F_ / (n * m_s * g * 1.2)
    return r_u

# Gleichung (21)
@lru_cache(maxsize=5)
def δ_1(r: float) -> float:
    """
    Funktion zur Berechnung der Richtung δ1 der resultierenden Kraft in ° nach SN EN 60865-1:2012 Kapitel 6.2.2
    δ_1: Richtung der resultierenden Kraft in °
    r: Verhältnisses r der elektromagnetischen Kraft auf ein Leiterseil bei Kurzschluss zur
    Eigengewichtskraft (dimensionslos)
    """
    δ_1: float = math.degrees((math.atan(r)))
    return δ_1

# Gleichung (22)
def f_es(n: float, m_s: float, g: float, l: float, F_st: float) -> float:
    """
    Funktion zur Berechnung des statischen Ersatz-Seildurchhangs in Spannfeldmitte f_es in m
    nach SN EN 60865-1:2012 Kapitel 6.2.2
    f_es: statischer Ersatz-Seildurchhang in Spannfeldmitte in m
    n: Anzahl der Teilleiter eines Hauptleiters (dimensionslos)
    m_s: Massenbelag eines Teilleiters in kg/m
    g: Normfallbeschleunigung in m/s^2
    F_st: statische Seilzugkraft in einem Hauptleiter in N
    """
    f_es: float = (n * m_s * g * l**2) / (8 * F_st)
    return f_es

# Gleichung (23)
def T(f_es: float, g: float) -> float:
    """
    Funktion zur Berechnung der Periodendauer der Spannfeld-Pendelung T in s nach SN EN 60865-1:2012 Kapitel 6.2.2
    T: Periodendauer der Spannfeld-Pendelung in s
    f_es: statischer Ersatz-Seildurchhang in Spannfeldmitte in m
    g: Normfallbeschleunigung in m/s^2
    Erläuterung zu T:
    Gilt für kleine Ausschwingwinkel ohne Stromfluss im Leiter.
    """
    T: float = 2 * math.pi * math.sqrt(0.8 * (f_es / g))
    return T

# Gleichung (24)
def T_res(T: float, r: float, δ_1: float) -> float:
    """
    Funktion zur Berechnung der resultierenden Periodendauer der Spannfeld-Pendelung T_res während des
    Kurzschlussstrom-Flusses in s nach SN EN 60865-1:2012 Kapitel 6.2.2
    T_res: resultierende Periodendauer der Spannfeld-Pendelung während des Kurzschlussstrom-Flusses in s
    T: Periodendauer der Spannfeld-Pendelung in s
    r: Verhältnisses r der elektromagnetischen Kraft auf ein Leiterseil bei Kurzschluss zur
    Eigengewichtskraft (dimensionslos)
    δ_1: Richtung der resultierenden Kraft in °
    """
    T_res: float = T / ((math.sqrt(math.sqrt(1 + r**2))) * (1 - ((math.pi**2 / 64) * ((δ_1 / 90)**2))))
    return T_res

# Gleichung (26)
def E_eff(E: float, F_st: float, n: float, A_s: float, σ_fin: float) -> float:
    """
    Funktion zur Berechnung des tatsächlichen Elastizitätsmoduls E_eff in N/m^2 nach SN EN 60865-1:2012 Kapitel 6.2.2
    E_eff: tatsächlicher Elastizitätsmodul in N/m^2
    E: Elastizitätsmodul in N/m^2
    F_st: statische Seilzugkraft in einem Hauptleiter in N
    n: Anzahl der Teilleiter eines Hauptleiters (dimensionslos)
    A_s: Querschnitt eines Teilleiters in m^2
    σ_fin: niedrigste Spannung, ab der der Elastizitätsmodul konstant wird, in N/m^2
    """
    E_eff: float = E * (0.3 + (0.7 * (math.sin(math.radians((F_st / (n * A_s * σ_fin)) * 90)))))
    if F_st / (n * A_s) <= σ_fin:
        E_eff: float = E_eff
    elif F_st / (n * A_s) > σ_fin:
        E_eff: float = E
    return E_eff

# Gleichung (25)
def N(S: float, l: float, n: float, E_eff: float, A_s: float) -> float:
    """
    Funktion zur Berechnung der Steifigkeitsnorm N einer Anordnung mit Leiterseilen in 1/N
    nach SN EN 60865-1:2012 Kapitel 6.2.2
    N: Steifigkeitsnorm einer Anordnung mit Leiterseilen in 1/N
    S: resultierender Federkoeffizient der beiden Stützpunkte eines Spannfelds in N/m
    l: Mittenabstand der Stützpunkte in m
    n: Anzahl der Teilleiter eines Hauptleiters (dimensionslos)
    E_eff: tatsächlicher Elastizitätsmodul in N/m^2
    A_s: Querschnitt eines Teilleiters in m^2
    """
    N: float = (1 / (S * l)) + (1 / (n * E_eff * A_s))
    return N

# Gleichung (28)
def ζ(n: float, g: float, m_s: float, l: float, F_st: float, N: float) -> float:
    """
    Funktion zur Berechnung des Beanspruchungsfaktors eines Hauptleiters in Seilanordnungen ζ
    (dimensionslos) nach SN EN 60865-1:2012 Kapitel 6.2.2
    ζ: Beanspruchungsfaktor des Hauptleiters in Seilanordnungen (dimensionslos)
    n: Anzahl der Teilleiter eines Hauptleiters (dimensionslos)
    g: Normfallbeschleunigung in m/s^2
    m_s: Massenbelag eines Teilleiters in kg/m
    l: Mittenabstand der Stützpunkte in m
    F_st: statische Seilzugkraft in einem Hauptleiter in N
    N: Steifigkeitsnorm einer Anordnung mit Leiterseilen in 1/N
    """
    ζ: float = ((n * g * m_s * l)**2) / (24 * math.pow(F_st,3) * N)
    return ζ

# Gleichung (29)
def δ_end(δ_1: float, T_k1: float, T_res: float) -> float | None:
    """
    Funktion zur Berechnung des Ausschwingwinkels am Ende des Kurzschlussstrom-Flusses δ_end in ° nach
    SN EN 60865-1:2012 Kapitel 6.2.2
    δ_end: Ausschwingwinkel am Ende des Kurzschlussstrom-Flusses in °
    δ_1: Richtung der resultierenden Kraft in °
    T_k1: Dauer des ersten Kurzschlussstrom-Flusses ins s
    T_res:  resultierende Periodendauer der Spannfeld-Pendelung während des Kurzschlussstrom-Flusses ins s
    """
    δ_end_1: float = δ_1 * (1 - math.cos(math.radians(360*(T_k1 / T_res))))
    δ_end_2: float = δ_1 * 2

    if 0 <= T_k1 / T_res <= 0.5:
        δ_end: float = δ_end_1
        return δ_end
    elif T_k1 / T_res > 0.5:
        δ_end: float = δ_end_2
        return δ_end

# Gleichung (30, 31)
def δ_max(r: float, δ_end: float) -> float | None:
    """
    Funktion zur Berechnung des maximalen Ausschwingwinkels δ_max in ° nach SN EN 60865-1:2012 Kapitel 6.2.2
    δ_max: maximaler Ausschwingwinkel in °
    r: Verhältnisses r der elektromagnetischen Kraft auf ein Leiterseil bei Kurzschluss zum Eigengewichtskraft (dimensionslos)
    δ_end: Ausschwingwinkel am Ende des Kurzschlussstrom-Flusses in °
    χ: Größe zur Berechnung des maximalen Ausschwingwinkels (dimensionslos)
    Hinweis: Formeln zur Programmierung wird auf die Gleichungen (31) und (19) bis (30) verwiesen.
    """
    if 0 <= δ_end <= 90:
        χ_1: float = 1 - (r * math.sin(math.radians(δ_end)))
        χ: float = χ_1
        if 0.766 < χ <= 1:
            δ_max_1: float = 1.25 * math.degrees(arccos(χ))
            δ_max: float = δ_max_1
            return δ_max
        elif -0.985 <= χ <= 0.766:
            δ_max_2: float = 10 + math.degrees(arccos(χ))
            δ_max: float = δ_max_2
            return δ_max
        elif χ <= 1:
            δ_max_3: float = 180
            δ_max: float = δ_max_3
            return δ_max
    elif δ_end > 90:
        χ_2: float = 1 - r
        χ: float = χ_2
        if 0.766 < χ <= 1:
            δ_max_1: float = 1.25 * math.degrees(arccos(χ))
            δ_max: float = δ_max_1
            return δ_max
        elif -0.985 <= χ <= 0.766:
            δ_max_2: float = 10 + math.degrees(arccos(χ))
            δ_max: float = δ_max_2
            return δ_max
        elif χ <= 1:
            δ_max_3: float = 180
            δ_max: float = δ_max_3
            return δ_max


# Grössen ab Kapitel 6.2.3
# Gleichung (32)
def φ_ohne_schlaufe(T_k1: float, T_res: float, r: float, δ_end: float) -> float | None:
    """
    Funktion zur Berechnung des Faktors φ für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    nach SN EN 60865-1:2012 Kapitel 6.2.3
    φ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    T_k1: Dauer des ersten Kurzschlussstrom-Flusses in s
    T_res: Resultierende Periodendauer der Spannfeld-Pendelung während des Kurzschlussstrom-Flusses ins s
    r: Verhältnis r der elektromagnetischen Kraft auf ein Leiterseil bei Kurzschluss zur Eigengewichtskraft (dimensionslos)
    δ_end: Ausschwingwinkel am Ende des Kurzschlussstrom-Flusses in °
    """
    if T_k1  >= T_res / 4:
        φ_1: float = 3 * (math.sqrt((1 + r ** 2)) - 1)
        φ: float = φ_1
        return φ
    elif T_k1  < T_res / 4:
        φ_2: float = 3 * ((r * math.sin(math.radians(δ_end))) - (math.cos(math.radians(δ_end)) - 1))
        φ: float = φ_2
        return φ

def ψ_ohne_schlaufe_symbolisch(φ: float, ζ: float) -> float:
    """
    Funktion zur Berechnung des Faktors ψ zur Berechnung Faktoren für die Berechnung der Zugkraft in Leiterseilen
    (dimensionslos) nach SN EN 60865-1:2012 Kapitel 6.2.3
    ψ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    φ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    ζ: Beanspruchungsfaktor des Hauptleiters in Seilanordnungen (dimensionslos)
    Hinweis: Es werden nur reale Zahlen und Zahlen zwischen 0 und 1 eingegeben.
    """
    """
    Berechnung ψ (SN EN 60865-1:2012) im Mehrstufenverfahren:
    1. Symbolische Methode (Exakte Lösung) 
    2. Brent's Methode (Garantierte Intervallsuche)
    3. fsolve (Allgemeiner numerischer Ansatz)
    """
    #1. Symbolische Methode (Exakte Lösung)
    try:
        ψ_sym = sympy.symbols('ψ', real=True)
        polynom_sym = (ψ_sym**3 * φ**2) + ((φ * (2 + ζ)) * (ψ_sym**2)) + (ψ_sym * (1 + (2 * ζ))) - (ζ * (2 + φ))
        solutions = sympy.solve(polynom_sym, ψ_sym)

        valid_sols = [float(s) for s in solutions if 0 <= s <= 1]
        if valid_sols:
            return valid_sols[0]
    except:
        raise
    finally:
        return ψ_ohne_schlaufe_numerisch(φ=φ, ζ=ζ)
    # return None

def ψ_ohne_schlaufe_numerisch(φ: float, ζ: float) -> float | None:
    """
    Funktion zur Berechnung des Faktors ψ zur Berechnung Faktoren für die Berechnung der Zugkraft in Leiterseilen
    (dimensionslos) nach SN EN 60865-1:2012 Kapitel 6.2.3
    ψ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    φ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    ζ: Beanspruchungsfaktor des Hauptleiters in Seilanordnungen (dimensionslos)
    Hinweis: Es werden nur reale Zahlen und Zahlen zwischen 0 und 1 eingegeben.
    """
    """
    Berechnung ψ (SN EN 60865-1:2012) im Mehrstufenverfahren:
    1. Symbolische Methode (Exakte Lösung) 
    2. Brent's Methode (Garantierte Intervallsuche)
    3. fsolve (Allgemeiner numerischer Ansatz)
    """
    # Definiere die Polynomfunktion für numerische Methoden
    def f(ψ):
        return (ψ**3 * φ**2) + ((φ * (2 + ζ)) * (ψ**2)) + (ψ * (1 + (2 * ζ))) - (ζ * (2 + φ))

    # 2. Brents's Methode (Präferierte numerische Methode)
    try:
        # Überprüfen Sie, ob die Zeichen an den Grenzen unterschiedlich sind (erforderlich für Brentq).
        if f(0) * f(1) <= 0:
            return brentq(f, 0, 1, xtol=1e-12)
    except:
        pass
    # 3. FSOLVE (Notfallebene mit stabilen Ergebnissen)
    for start in [0.1, 0.5, 0.9]:
        try:
            sol, info, ier, msg = fsolve(f, x0=start, full_output=True)
            if ier == 1 and 0 <= sol[0] <= 1:
                return float(sol[0])
        except:
            continue
    return None

def ψ_ohne_schlaufe_backup(φ: float, ζ: float) -> float | None:
    """
    Funktion zur Berechnung des Faktors ψ zur Berechnung Faktoren für die Berechnung der Zugkraft in Leiterseilen
    (dimensionslos) nach SN EN 60865-1:2012 Kapitel 6.2.3
    ψ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    φ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    ζ: Beanspruchungsfaktor des Hauptleiters in Seilanordnungen (dimensionslos)
    Hinweis: Es werden nur reale Zahlen und Zahlen zwischen 0 und 1 eingegeben.
    """
    """
    Berechnung ψ (SN EN 60865-1:2012) im Mehrstufenverfahren:
    1. Symbolische Methode (Exakte Lösung) 
    2. Brent's Methode (Garantierte Intervallsuche)
    3. fsolve (Allgemeiner numerischer Ansatz)
    """
    # Definiere die Polynomfunktion für numerische Methoden
    def f(ψ):
        return (ψ**3 * φ**2) + ((φ * (2 + ζ)) * (ψ**2)) + (ψ * (1 + (2 * ζ))) - (ζ * (2 + φ))

    #1. Symbolische Methode (Exakte Lösung)
    try:
        ψ_sym = sympy.symbols('ψ', real=True)
        polynom_sym = (ψ_sym**3 * φ**2) + ((φ * (2 + ζ)) * (ψ_sym**2)) + (ψ_sym * (1 + (2 * ζ))) - (ζ * (2 + φ))
        solutions = sympy.solve(polynom_sym, ψ_sym)

        valid_sols = [float(s) for s in solutions if 0 <= s <= 1]
        if valid_sols:
            return valid_sols[0]
    except:
        pass  # Fallen zurück auf numerisch
    # 2. Brents's Methode (Präferierte numerische Methode)
    try:
        # Überprüfen Sie, ob die Zeichen an den Grenzen unterschiedlich sind (erforderlich für Brentq).
        if f(0) * f(1) <= 0:
            return brentq(f, 0, 1, xtol=1e-12)
    except:
        pass
    # 3. FSOLVE (Notfallebene mit stabilen Ergebnissen)
    for start in [0.1, 0.5, 0.9]:
        try:
            sol, info, ier, msg = fsolve(f, x0=start, full_output=True)
            if ier == 1 and 0 <= sol[0] <= 1:
                return float(sol[0])
        except:
            continue
    return None


# Grössen ab Kapitel 6.2.4
# Gleichung (34)
def ε_ela(N: float, F_td: float, F_st) -> float:
    """
    Funktion zur Berechnung des Wertes ε_ela für die elastische Seildehnung (dimensionslos) nach SN EN 60865-1:2012 Kapitel 6.2.4.
    ε_ela: elastische Seildehnung (dimensionslos)
    N: Steifigkeitsnorm einer Anordnung mit Leiterseilen in 1/N
    F_td: Kurzschluss-Seilzugkraft in einem Hauptleiter (Bemessungswert) in Seilanordnungen in N
    F_st: statische Seilzugkraft in einem Hauptleiter in N
    """
    ε_ela: float = N * (F_td - F_st)
    return ε_ela

# Gleichung (35)
def ε_th(c_th: float, I_k__: float, n: float, A_s: float, T_k1: float, T_res: float) -> float | None:
    """
    Funktion zur Berechnung des Wertes der thermischen Seildehnung ε_th (dimensionslos) nach SN EN 60865-1:2012 Kapitel 6.2.4.
    ε_th: thermische Seildehnung ε_th (dimensionslos)
    c_th: Materialkonstante in m4/(A2s)
    I_k__: Anfangs-Kurzschlusswechselstrom beim dreipoligen Kurzschluss (Effektivwert) in A
    n: Anzahl der Teilleiter eines Hauptleiters (dimensionslos)
    A_s: Querschnitt eines Teilleiters in m^2
    T_res:  resultierende Periodendauer der Spannfeld-Pendelung während des Kurzschlussstrom-Flusses ins s
    T_k1: Dauer des ersten Kurzschlussstrom-Flusses ins s
    """
    if T_k1 >= T_res / 4:
        ε_th: float =  c_th * (I_k__ / (n * A_s))**2 * (T_res / 4)
        return ε_th
    elif T_k1 < T_res / 4:
        ε_th: float = c_th * (I_k__ / (n * A_s)) **2 * (T_k1)
        return ε_th

# Gleichung (36)
def C_D(l: float, f_es: float, ε_ela: float, ε_th: float) -> float | None:
    """
    Funktion zur Berechnung des Faktors für die Durchhangvergrößerung durch Seildehnung C_D (dimensionslos) nach
    SN EN 60865-1:2012 Kapitel 6.2.4.
    C_D: Faktor für die Durchhangvergrößerung durch Seildehnung (dimensionslos)
    l: Mittenabstand der Stützpunkte in m
    f_es: statischer Ersatz-Seildurchhang in Spannfeldmitte in m
    ε_ela: elastische Seildehnung (dimensionslos)
    ε_th: thermische Seildehnung (dimensionslos)
    """
    C_D: float = math.sqrt(1 + ((3 / 8) * (l / f_es)**2 * (ε_ela + ε_th)))
    return C_D

# Gleichung (37)
def C_F(r: float) -> float | None:
    """
    Funktion zur Berechnung von C_F Faktor (dimensionslos) für die Durchhangvergrößerung durch Änderung der Seilkurvenform
    nach SN EN 60865-1:2012 Kapitel 6.2.4.
    C_F: Faktor für die Durchhangvergrößerung durch Änderung der Seilkurvenform (dimensionslos)
    r:  Verhältnis von elektromagnetischer Kraft auf ein Leiterseil bei Kurzschluss zur Eigengewichtskraft (dimensionslos)
    """
    if r <= 0.8:
        C_F: float = 1.05
        return C_F
    elif 0.8 < r < 1.8:
        C_F: float = 0.97 + (0.1 * r)
        return C_F
    elif r >= 1.8:
        C_F: float = 1.15
        return C_F

# Gleichung (38)
def f_ed(C_D: float, C_F: float, f_es: float) -> float:
    """
    Funktion zur Berechnung des dynamischen Seildurchhangs in Spannfeldmitte f_ed in m nach
    SN EN 60865-1:2012 Kapitel 6.2.4.
    f_ed: dynamischer Seildurchhang in Spannfeldmitte in m
    f_es: statischer Ersatz-Seildurchhang in Spannfeldmitte in m
    C_D: Faktor für die Durchhangvergrößerung durch Seildehnung (dimensionslos)
    C_F: Faktor für die Durchhangvergrößerung durch Änderung der Seilkurvenform (dimensionslos)
    """
    f_ed: float = C_D * C_F * f_es
    return f_ed


# Grössen ab Kapitel 6.2.5 (Schlaufen in Spannfeldmitte)
# Gleichung 39
def δ_ebene_parallel(f_es: float, f_ed: float, l_v: float, h: float, w: float) -> float | None:
    """
    Funktion zur Berechnung des tatsächlichen maximalen Ausschwingwinkels infolge der Begrenzung der
    Ausschwingbewegung durch die Schlaufe bei Anordnung Ebene parallel δ_ebene_parallel in °
    nach SN EN 60865-1:2012 Kapitel 6.2.2
    δ_ebene_parallel: tatsächlicher maximaler Ausschwingwinkel infolge der Begrenzung der
    Ausschwingbewegung durch die Schlaufe Anordnung Ebene parallel in °
    f_es: statischer Ersatz-Seildurchhang in Spannfeldmitte in m
    f_ed: dynamischer Seildurchhang in Spannfeldmitte in m
    l_v: Seil(bogen)länge der Schlaufe in m
    h: Schlaufenhöhe in m
    w: Schlaufenbreite in m
    """
    if l_v >= math.sqrt((h + f_es + f_ed)**2 + w**2):
        print("Es ist nach SN EN 60865-1:2012 Kapitel 6.2.2 zu rechnen.")
        return None
    else:
        δ_ebene_parallel: float = arccos(((h +f_es)**2 + f_ed**2 - (l_v**2 - w**2)) / (2 * f_ed * (h +f_es)))
        return δ_ebene_parallel


# Grössen ab Kapitel 6.2.5 (Schlaufen in Spannfeldmitte)
# Gleichung 39
def δ_ebene_senkrecht(f_es: float, f_ed: float, l_v: float, h: float, w: float) -> float | None:
    """
    Funktion zur Berechnung des tatsächlichen maximalen Ausschwingwinkels infolge der Begrenzung der
    Ausschwingbewegung durch die Schlaufe bei Anordnung senkrecht nach SN EN 60865-1:2012 Kapitel 6.2.2
    δ_ebene_senkrecht: tatsächlicher maximaler Ausschwingwinkel infolge der Begrenzung der
    Ausschwingbewegung durch die Schlaufe bei Anordnung senkrecht in °
    f_es: statischer Ersatz-Seildurchhang in Spannfeldmitte in m
    f_ed: dynamischer Seildurchhang in Spannfeldmitte in m
    l_v: Seil(bogen)länge der Schlaufe in m
    h: Schlaufenhöhe in m
    w: Schlaufenbreite in m
    """
    if l_v >= math.sqrt((h + f_es)**2 + w**2) + f_ed:
        print("Es ist nach SN EN 60865-1:2012 Kapitel 6.2.2 zu rechnen.")
        return None
    else:
        δ_ebene_senkrecht: float = arccos(((h +f_es)**2 + f_ed**2 - (l_v**2 - w**2)) / (2 * f_ed * math.sqrt((h +f_es)**2 + w**2))) + arccos((h + f_es) / (math.sqrt((h +f_es)**2 + w**2)))
        return δ_ebene_senkrecht

# Gleichung (40, 41)
def φ_mit_schlaufe(T_k1: float, T_kres: float, r: float, δ_end: float, δ:float, δ_1: float) -> float | None:
    """
    Funktion zur Berechnung des Faktors φ für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    nach SN EN 60865-1:2012 Kapitel 6.2.5
    φ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    T_k1: Dauer des ersten Kurzschlussstrom-Flusses in s
    T_res: Resultierende Periodendauer der Spannfeld-Pendelung während des Kurzschlussstrom-Flusses ins s
    r: Verhältnis r der elektromagnetischen Kraft auf ein Leiterseil bei Kurzschluss zur Eigengewichtskraft (dimensionslos)
    δ_end: Ausschwingwinkel am Ende des Kurzschlussstrom-Flusses in °
    δ: tatsächlicher maximaler Ausschwingwinkel infolge der Begrenzung der Ausschwingbewegung durch die Schlaufe in °
    δ_1: Richtung der resultierenden Kraft in °
    """
    if δ >= δ_1:
        if T_k1  >= T_kres / 4:
            φ_1: float = 3 * (math.sqrt((1 + r ** 2)) - 1)
            φ: float = φ_1
            return φ
        elif T_k1  < T_kres / 4:
            φ_2: float = 3 * ((r * math.sin(math.radians(δ_end))) - (math.cos(math.radians(δ_end)) - 1))
            φ: float = φ_2
            return φ
    elif δ < δ_1:
        if δ_end >= δ:
            φ_3: float = 3 * ((r * math.sin(math.radians(δ))) - (math.cos(math.radians(δ)) - 1))
            φ: float = φ_3
            return φ
        elif δ_end < δ:
            φ_4: float = 3 * ((r * math.sin(math.radians(δ_end))) - (math.cos(math.radians(δ_end)) - 1))
            φ: float = φ_4
            return φ

def ψ_mit_schlaufe_symbolisch(φ: float, ζ: float) -> float:
    """
    Funktion zur Berechnung des Faktors ψ zur Berechnung Faktoren für die Berechnung der Zugkraft in Leiterseilen
    (dimensionslos) nach SN EN 60865-1:2012 Kapitel 6.2.3
    ψ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    φ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    ζ: Beanspruchungsfaktor des Hauptleiters in Seilanordnungen (dimensionslos)
    Hinweis: Es werden nur reale Zahlen und Zahlen zwischen 0 und 1 eingegeben.
    """
    """
       Berechnung ψ (SN EN 60865-1:2012) im Mehrstufenverfahren:
       1. Symbolische Methode (Exakte Lösung) 
       2. Brent's Methode (Garantierte Intervallsuche)
       3. fsolve (Allgemeiner numerischer Ansatz)
       """
    # 1. Symbolische Methode (Exakte Lösung)
    try:
        ψ_sym = sympy.symbols('ψ', real=True)
        polynom_sym = (ψ_sym**3 * φ**2) + ((φ * (2 + ζ)) * (ψ_sym**2)) + (ψ_sym * (1 + (2 * ζ))) - (ζ * (2 + φ))
        solutions = sympy.solve(polynom_sym, ψ_sym)

        valid_sols = [float(s) for s in solutions if 0 <= s <= 1]
        if valid_sols:
            return valid_sols[0]
    except:
        pass  # Fallen zurück auf numerisch
    finally:
        return ψ_mit_schlaufe_numerisch(φ=φ, ζ=ζ)
    # return None

def ψ_mit_schlaufe_numerisch(φ: float, ζ: float) -> float | None:
    """
    Funktion zur Berechnung des Faktors ψ zur Berechnung Faktoren für die Berechnung der Zugkraft in Leiterseilen
    (dimensionslos) nach SN EN 60865-1:2012 Kapitel 6.2.3
    ψ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    φ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    ζ: Beanspruchungsfaktor des Hauptleiters in Seilanordnungen (dimensionslos)
    Hinweis: Es werden nur reale Zahlen und Zahlen zwischen 0 und 1 eingegeben.
    """
    """
       Berechnung ψ (SN EN 60865-1:2012) im Mehrstufenverfahren:
       1. Symbolische Methode (Exakte Lösung) 
       2. Brent's Methode (Garantierte Intervallsuche)
       3. fsolve (Allgemeiner numerischer Ansatz)
       """
    # Definiere die Polynomfunktion für numerische Methoden
    def f(ψ):
        return (ψ**3 * φ**2) + ((φ * (2 + ζ)) * (ψ**2)) + (ψ * (1 + (2 * ζ))) - (ζ * (2 + φ))

    # 2. Brents's Methode (Präferierte numerische Methode)
    try:
        # Überprüfen Sie, ob die Zeichen an den Grenzen unterschiedlich sind (erforderlich für Brentq).
        if f(0) * f(1) <= 0:
            return brentq(f, 0, 1, xtol=1e-12)
    except:
        pass
    # 3. FSOLVE (Notfallebene mit stabilen Ergebnissen)
    for start in [0.1, 0.5, 0.9]:
        try:
            sol, info, ier, msg = fsolve(f, x0=start, full_output=True)
            if ier == 1 and 0 <= sol[0] <= 1:
                return float(sol[0])
        except:
            continue
    return None

def ψ_mit_schlaufe_backup(φ: float, ζ: float) -> float | None:
    """
    Funktion zur Berechnung des Faktors ψ zur Berechnung Faktoren für die Berechnung der Zugkraft in Leiterseilen
    (dimensionslos) nach SN EN 60865-1:2012 Kapitel 6.2.3
    ψ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    φ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    ζ: Beanspruchungsfaktor des Hauptleiters in Seilanordnungen (dimensionslos)
    Hinweis: Es werden nur reale Zahlen und Zahlen zwischen 0 und 1 eingegeben.
    """
    """
       Berechnung ψ (SN EN 60865-1:2012) im Mehrstufenverfahren:
       1. Symbolische Methode (Exakte Lösung) 
       2. Brent's Methode (Garantierte Intervallsuche)
       3. fsolve (Allgemeiner numerischer Ansatz)
       """

    # Definiere die Polynomfunktion für numerische Methoden
    def f(ψ):
        return (ψ**3 * φ**2) + ((φ * (2 + ζ)) * (ψ**2)) + (ψ * (1 + (2 * ζ))) - (ζ * (2 + φ))

    # 1. Symbolische Methode (Exakte Lösung)
    try:
        ψ_sym = sympy.symbols('ψ', real=True)
        polynom_sym = (ψ_sym**3 * φ**2) + ((φ * (2 + ζ)) * (ψ_sym**2)) + (ψ_sym * (1 + (2 * ζ))) - (ζ * (2 + φ))
        solutions = sympy.solve(polynom_sym, ψ_sym)

        valid_sols = [float(s) for s in solutions if 0 <= s <= 1]
        if valid_sols:
            return valid_sols[0]
    except:
        pass  # Fallen zurück auf numerisch
    # 2. Brents's Methode (Präferierte numerische Methode)
    try:
        # Überprüfen Sie, ob die Zeichen an den Grenzen unterschiedlich sind (erforderlich für Brentq).
        if f(0) * f(1) <= 0:
            return brentq(f, 0, 1, xtol=1e-12)
    except:
        pass
    # 3. FSOLVE (Notfallebene mit stabilen Ergebnissen)
    for start in [0.1, 0.5, 0.9]:
        try:
            sol, info, ier, msg = fsolve(f, x0=start, full_output=True)
            if ier == 1 and 0 <= sol[0] <= 1:
                return float(sol[0])
        except:
            continue
    return None


# Grössen ab Kapitel 6.2.7 (Horizontale Seilauslenkung und minimaler Leiterabstand)
# Gleichung (44)
def b_h_ohne_schlaufe_spannfeldmitte_aufgelegt(f_ed: float, δ_max: float) -> float | None:
    """
    Funktion zur Berechnung des Faktors b_h für die Berechnung der maximalen horizontalen Seilauslenkung in m
    nach SN EN 60865-1:2012 Kapitel 6.2.7
    b_h: maximale horizontale Seilauslenkung in m
    f_ed: dynamischer Seildurchhang in Spannfeldmitte in m
    δ_max: maximaler Ausschwingwinkel in °
    l: Mittenabstand der Stützpunkte in m
    l_c: Seillänge eines Hauptleiters im Spannfeld  in m
    l_i: Länge einer Abspann-Isolatorkette in m
    Hinweis: Gilt für l_c = l. Gilt für die Spannfeldmitte.
    """
    if δ_max >= 90:
        b_h_1: float = f_ed
        b_h: float = b_h_1
        return b_h
    elif δ_max < 90:
        b_h_2: float = f_ed * math.sin(math.radians(δ_max))
        b_h: float = b_h_2
        return b_h

# Gleichung (45)
def b_h_ohne_schlaufe_spannfeldmitte_abgespannt(f_ed: float, δ_max: float, δ_1: float) -> float | None:
    """
    Funktion zur Berechnung des Faktors b_h für die Berechnung der maximalen horizontalen Seilauslenkung in m
    nach SN EN 60865-1:2012 Kapitel 6.2.7
    b_h: maximale horizontale Seilauslenkung in m
    f_ed: dynamischer Seildurchhang in Spannfeldmitte in m
    δ_max: maximaler Ausschwingwinkel in °
    δ_1: Richtung der resultierenden Kraft in °
    l: Mittenabstand der Stützpunkte in m
    l_c: Seillänge eines Hauptleiters im Spannfeld in m
    l_i: Länge einer Abspann-Isolatorkette in m
    Hinweis: Gilt für l_c = l - 2 * l_i. Gilt für die Spannfeldmitte.
    """
    if δ_max >= δ_1:
        b_h_3: float = f_ed * math.sin(math.radians(δ_1))
        b_h: float = b_h_3
        return b_h
    elif δ_max < δ_1:
        b_h_4: float = f_ed * math.sin(math.radians(δ_max))
        b_h: float = b_h_4
        return b_h

# Gleichung (46, 47)
def b_h_mit_schlaufe_spannfeldmitte_abgespannt(f_ed: float, δ_max: float, δ_1: float, δ: float) -> float | None:
    """
    Funktion zur Berechnung des Faktors b_h für die Berechnung der maximalen horizontalen Seilauslenkung in m
    nach SN EN 60865-1:2012 Kapitel 6.2.7
    b_h: maximale horizontale Seilauslenkung in m
    f_ed: dynamischer Seildurchhang in Spannfeldmitte in m
    δ_max: maximaler Ausschwingwinkel in °
    δ_1: Richtung der resultierenden Kraft in °
    δ: tatsächlicher maximaler Ausschwingwinkel infolge der Begrenzung der Ausschwingbewegung durch die Schlaufe in °
    l: Mittenabstand der Stützpunkte in m
    l_c: Seillänge eines Hauptleiters im Spannfeld in m
    l_i: Länge einer Abspann-Isolatorkette in m
    Hinweis: Gilt für l_c = l - 2 * l_i. Gilt für die Spannfeldmitte.
    """
    if δ >= δ_max:
        if δ_max >= δ_1:
            b_h_5: float = f_ed * math.sin(math.radians(δ_1))
            b_h: float = b_h_5
            return b_h
        elif δ_max < δ_1:
            b_h_6: float = f_ed * math.sin(math.radians(δ_max))
            b_h: float = b_h_6
            return b_h
    elif δ < δ_max:
        if δ_max >= δ_1:
            b_h_7: float = f_ed * math.sin(math.radians(δ_1))
            b_h: float = b_h_7
            return b_h
        elif δ_max < δ_1:
            b_h_8: float = f_ed * math.sin(math.radians(δ))
            b_h: float = b_h_8
            return b_h

# Gleichung (48)
def a_min(a: float, b_h: float) -> float:
    """
    Funktion zur Berechnung des Faktors a_min für die Berechnung des minimalen Leiterabstandes in m
    nach SN EN 60865-1:2012 Kapitel 6.2.7
    a_min: minimale Leiterabstand in m
    a: Leitermittenabstand in m
    b_h: maximale horizontale Seilauslenkung in m
    """
    a_min: float = a - (2 * b_h)
    return a_min


# Grössen ab Kapitel 6.3
# Gleichung (50)
def b_h_mit_verikaler_höhenunterschied_befestigungspunkte(l: float, l_v: float) -> float | None:
    """
    Funktion zur Berechnung des Faktors b_h für die Berechnung der maximalen horizontalen Seilauslenkung in m
    nach SN EN 60865-1:2012 Kapitel 6.3
    b_h: maximale horizontale Seilauslenkung in m
    l: Mittenabstand der Stützpunkte in m
    l_v: Seil(bogen)länge der Schlaufe m
    Hinweis: Gilt für l_v = 2 * l.
    """
    if l_v >= 2:
        b_h: float = (0.6 * math.sqrt((l_v - l) -1) + (0.44 * ((l_v / l) -1)) - (0.32 * math.log(l_v / l))) * (l_v**2 / l)
        return b_h


# Grössen ab Kapitel 6.4.1
# Gleichung (55)
def ν_1(μ0: float, I_k: float, a_s: float, n: float, m_s: float, d: float, f: float) -> float:
    """
    Funktion zur Berechnung der Kurzschluss-Stromkraft zwischen den Teilleitern eines Bündels F_v in N nach
    SN EN 60865-1:2012 Kapitel 6.4.1.
    ν_1: Faktor zur Berechnung von F_pi_d
    μ0: magnetische Feldkonstante, Permeabilität des leeren Raumes Vs/(Am)
    I_k: Anfangs-Kurzschlusswechselstrom (Effektivwert) beim dreipoligen Kurzschluss in A
    a_s: wirksamer Abstand zwischen Teilleitern in m
    n: Anzahl der Teilleiter eines Hauptleiters (dimensionslos)
    m_s: Massenbelag eines Teilleiters in kg/m
    d: Außendurchmesser von Rohrleitern oder Seildurchmesser in m
    f: Frequenz des Netzes in Hz
    """
    ν_1: float = f * (1 / math.sin(math.radians(180 / n))) * math.sqrt(((a_s - d) * m_s) / ((μ0 / (2 * math.pi)) * (I_k / n)**2 * ((n - 1) / a_s)))
    return ν_1

# Gleichung (56)
def ε_st(F_st: float, l_c: float, l_s: float, l_eff: float, N: float, a_s: float, n: float, d: float) -> float:
    """
    Funktion zur Berechnung der Dehnungsfaktoren bei der Kontraktion eines Seilbündels ε_st (dimensionslos) nach
    SN EN 60865-1:2012 Kapitel 6.4.1.
    ε_st: Dehnungsfaktoren bei der Kontraktion eines Seilbündels (dimensionslos)
    F_st: statische Seilzugkraft in einem Hauptleiter in N
    l_c: Seillänge eines Hauptleiters im Spannfeld m
    l_s: Mittenabstand der Zwischenstücke oder Mittenabstand eines Zwischenstücks und des benachbarten Stützpunkts in m
    N: Steifigkeitsnorm einer Anordnung mit Leiterseilen in 1/N
    a_s: wirksamer Abstand zwischen Teilleitern in m
    n: Anzahl der Teilleiter eines Hauptleiters (dimensionslos)
    d: Außendurchmesser von Rohrleitern oder Seildurchmesser in m
    """
    # In Abweichung von der Norm wird hier eine Unterscheidung zwischen hier unterschieden, ob Abstandhalter
    # vorhanden sind oder nicht. Sind Abstandhalter vorhanden, wird gemäss Norm mit den gemittelten Abständen l_s der
    # gerechnet. Falls keine Abstandhalter vorhanden sind, wird l_c, also die Seillänge eines Hauptleiters im Spannfeld
    # verwendet. (Verifiziert mit dem Programm IEC865D)
    if l_s not in (None, 0.0, 0):
        ε_st: float = (1.5 * ((F_st * l_s**2 * N) / (a_s - d)**2) * (math.sin(math.radians(180 / n)))**2)
    elif l_eff not in (None, 0.0, 0):
        ε_st: float = (1.5 * ((F_st * l_eff**2 * N) / (a_s - d)**2) * (math.sin(math.radians(180 / n)))**2)
    else:
        ε_st: float = (1.5 * ((F_st * l_c**2 * N) / (a_s - d)**2) * (math.sin(math.radians(180 / n)))**2)
    return ε_st

# Gleichung (57)
def ε_pi(F_v: float, l_c: float, l_s: float, l_eff: float, N: float, a_s: float, n: float, d: float) -> float:
    """
    Funktion zur Berechnung der Dehnungsfaktoren bei der Kontraktion eines Seilbündels ε_pi (dimensionslos) nach
    SN EN 60865-1:2012 Kapitel 6.4.1.
    ε_pi: Dehnungsfaktoren bei der Kontraktion eines Seilbündels (dimensionslos)
    F_v: Kurzschluss-Stromkraft zwischen den Teilleitern eines Bündels in N
    l_c: Seillänge eines Hauptleiters im Spannfeld m
    l_s: Mittenabstand der Zwischenstücke oder Mittenabstand eines Zwischenstücks und des benachbarten Stützpunkts in m
    N: Steifigkeitsnorm einer Anordnung mit Leiterseilen in 1/N
    a_s: wirksamer Abstand zwischen Teilleitern in m
    n: Anzahl der Teilleiter eines Hauptleiters (dimensionslos)
    d: Außendurchmesser von Rohrleitern oder Seildurchmesser in m
    """
    # In Abweichung von der Norm wird hier eine Unterscheidung zwischen hier unterschieden, ob Abstandhalter
    # vorhanden sind oder nicht. Sind Abstandhalter vorhanden, wird gemäss Norm mit den gemittelten Abständen l_s der
    # gerechnet. Falls keine Abstandhalter vorhanden sind, wird l_c, also die Seillänge eines Hauptleiters im Spannfeld
    # verwendet. (Verifiziert mit dem Programm IEC865D)
    if l_s not in (None, 0.0, 0):
        ε_pi: float = (0.375 * n * ((F_v * l_s**3 * N) / (a_s - d)**3) * (math.sin(math.radians(180 / n)))**3)
    elif l_eff not in (None, 0.0, 0):
        ε_pi: float = (0.375 * n * ((F_v * l_eff**3 * N) / (a_s - d)**3) * (math.sin(math.radians(180 / n)))**3)
    else:
        ε_pi: float = (0.375 * n * ((F_v * l_c**3 * N) / (a_s - d)**3) * (math.sin(math.radians(180 / n)))**3)
    return ε_pi

# Gleichung (58)
def j(ε_st: float, ε_pi: float) -> float:
    """
    Funktion zur Berechnung des Parameters, der die Lage der Bündelleiter während des Kurzschlussstrom-Flusses angibt
    j (dimensionslos) nach SN EN 60865-1:2012 Kapitel 6.4.1.
    j: Parameter, der die Lage der Bündelleiter während des Kurzschlussstrom-Flusses angibt (dimensionslos)
    ε_st: Dehnungsfaktoren bei der Kontraktion eines Seilbündels (dimensionslos)
    ε_pi: Dehnungsfaktoren bei der Kontraktion eines Seilbündels (dimensionslos)
    """
    j: float = math.sqrt(ε_pi / (1 + ε_st))
    return j

# Gleichung (60, 63)
def ν_e(μ0: float, j: float, I_k: float, a_s: float, N: float, n: float, l_c: float, l_s: float, l_eff: float, d: float, ν_2: float, ν_4: float, ζ: float = None, η: float = None) -> float | None:
    """
    Funktion zur Berechnung des Faktors ν_e zur Berechnung von F_pi_d (dimensionslos) nach SN EN 60865-1:2012 Kapitel 6.4.1.
    ν_e: Faktor zur Berechnung von F_pi_d
    μ0: magnetische Feldkonstante, Permeabilität des leeren Raumes Vs/(Am)
    j: Parameter, der die Lage der Bündelleiter während des Kurzschlussstrom-Flusses angibt (dimensionslos)
    I_k: Anfangs-Kurzschlusswechselstrom (Effektivwert) beim dreipoligen Kurzschluss in A
    a_s: wirksamer Abstand zwischen Teilleitern in m
    N: Steifigkeitsnorm einer Anordnung mit Leiterseilen in 1/N
    n: Anzahl der Teilleiter eines Hauptleiters (dimensionslos)
    l_c: Seillänge eines Hauptleiters im Spannfeld m
    l_s: Mittenabstand der Zwischenstücke oder Mittenabstand eines Zwischenstücks und des benachbarten Stützpunkts in m
    d: Außendurchmesser von Rohrleitern oder Seildurchmesser in m
    ν_2: Faktor zur Berechnung von F_pi_d
    ν_4: Faktor zur Berechnung von F_pi_d
    ζ: Beanspruchungsfaktor des Hauptleiters in Seilanordnungen (dimensionslos)
    η: Faktor zur Berechnung von Fpi,d bei nicht zusammenschlagenden Bündelleitern (dimensionslos)
    """
    # In Abweichung von der Norm wird hier eine Unterscheidung zwischen hier unterschieden, ob Abstandhalter
    # vorhanden sind oder nicht. Sind Abstandhalter vorhanden, wird gemäss Norm mit den gemittelten Abständen l_s der
    # gerechnet. Falls keine Abstandhalter vorhanden sind, wird l_c, also die Seillänge eines Hauptleiters im Spannfeld
    # verwendet. (Verifiziert mit dem Programm IEC865D)
    if j >= 1:
        if l_s not in (None, 0.0, 0):
            ν_e_1: float = 1/2 + ((9/8) * n * (n - 1) * (μ0 / (2 * math.pi)) * (I_k / n)**2 * N * ν_2 * (l_s / (a_s - d))**4 * (math.sin(math.radians(180 / n))**4 / ζ**3) * (1 - (math.atan(math.sqrt(ν_4)) / math.sqrt(ν_4))) - 1/4)**(1/2)
            ν_e = ν_e_1
        elif l_eff not in (None, 0.0, 0):
            ν_e_1: float = 1/2 + ((9/8) * n * (n - 1) * (μ0 / (2 * math.pi)) * (I_k / n)**2 * N * ν_2 * (l_eff / (a_s - d))**4 * (math.sin(math.radians(180 / n))**4 / ζ**3) * (1 - (math.atan(math.sqrt(ν_4)) / math.sqrt(ν_4))) - 1/4)**(1/2)
            ν_e = ν_e_1
        else:
            ν_e_1: float = 1/2 + ((9/8) * n * (n - 1) * (μ0 / (2 * math.pi)) * (I_k / n)**2 * N * ν_2 * (l_c / (a_s - d))**4 * (math.sin(math.radians(180 / n))**4 / ζ**3) * (1 - (math.atan(math.sqrt(ν_4)) / math.sqrt(ν_4))) - 1/4)**(1/2)
            ν_e = ν_e_1
        return ν_e
    elif j < 1:
        if l_s not in (None, 0.0, 0):
            ν_e_2: float = 1/2 + ((9/8) * n * (n - 1) * (μ0 / (2 * math.pi)) * (I_k / n)**2 * N * ν_2 * (l_s / (a_s - d))**4 * (math.sin(math.radians(180 / n))**4 / η**4) * (1 - (math.atan(math.sqrt(ν_4)) / math.sqrt(ν_4))) - 1/4)**(1/2)
            ν_e = ν_e_2
        elif l_eff not in (None, 0.0, 0):
            ν_e_2: float = 1/2 + ((9/8) * n * (n - 1) * (μ0 / (2 * math.pi)) * (I_k / n)**2 * N * ν_2 * (l_eff / (a_s - d))**4 * (math.sin(math.radians(180 / n))**4 / η**4) * (1 - (math.atan(math.sqrt(ν_4)) / math.sqrt(ν_4))) - 1/4)**(1/2)
            ν_e = ν_e_2
        else:
            ν_e_2: float = 1/2 + ((9/8) * n * (n - 1) * (μ0 / (2 * math.pi)) * (I_k / n)**2 * N * ν_2 * (l_c / (a_s - d))**4 * (math.sin(math.radians(180 / n))**4 / η**4) * (1 - (math.atan(math.sqrt(ν_4)) / math.sqrt(ν_4))) - 1/4)**(1/2)
            ν_e = ν_e_2
        return ν_e

# Gleichung (61, 64)
def ν_4(j: float, a_s: float, d: float, η: float = None) -> float | None:
    """
    Funktion zur Berechnung des Faktors ν_4 zur Berechnung von F_pi_d (dimensionslos) nach SN EN 60865-1:2012 Kapitel 6.4.1.
    ν_4: Faktor zur Berechnung von F_pi_d
    j: Parameter, der die Lage der Bündelleiter während des Kurzschlussstrom-Flusses angibt (dimensionslos)
    a_s: wirksamer Abstand zwischen Teilleitern in m
    d: Außendurchmesser von Rohrleitern oder Seildurchmesser in m
    η: Faktor zur Berechnung von Fpi,d bei nicht zusammenschlagenden Bündelleitern (dimensionslos)
    """
    if j >= 1:
        ν_4_1: float = (a_s - d) / d
        ν_4 = ν_4_1
        return ν_4
    elif j < 1:
        ν_4_2: float = η * ( (a_s - d) / (a_s - (η * (a_s - d))))
        ν_4 = ν_4_2
        return ν_4


# Gleichung (A.7 Bild 9)
def τ(f: float, κ: float) -> float:
    """
    Funktion zur Berechnung des Faktors τ zur Berechnung der Netzzeitkonstante (dimensionslos) nach SN EN 60865-1:2012 Kapitel A.7
    τ: Netzzeitkonstante (dimensionslos)
    f: Frequenz des Netzes in Hz
    κ: Faktor zur Berechnung des Stoßkurzschlussstroms (dimensionslos)
    """
    if κ < 1.1:
        κ = 1.1
    τ: float = abs(1 / (((2 * math.pi * f) / 3) * math.log((κ - 1.02) / 0.98)))
    return τ

# Gleichung (A.7 Bild 9)
def γ(f: float, τ: float) -> float:
    """
    Funktion zur Berechnung des Faktors γ zur Berechnung des Faktors für die Bestimmung der maßgeblichen Eigenfrequenz
    (dimensionslos) nach SN EN 60865-1:2012 Kapitel A.7
    γ: Faktor für die Bestimmung der maßgeblichen Eigenfrequenz (dimensionslos)
    f: Frequenz des Netzes in Hz
    τ: Netzzeitkonstante (dimensionslos)
    """
    γ: float = math.atan(2 * math.pi * f * τ)
    return γ

# Gleichung (A.7 Bild 9)
def T_pi_and_ν_2(ν_1, f, τ, γ) -> tuple[float | None, float | None]:
    r"""
    Funktion zur Berechnung des Faktors T_pi zur Berechnung der Zeit vom Kurzschlussbeginn bis zum Erreichen von F_pi
    in s nach SN EN 60865-1:2012 Kapitel A.7
    T_pi: Zeit vom Kurzschlussbeginn bis zum Erreichen von F_pi in s
    ν_2: Faktor zur Berechnung von F_pi_d
    f: Frequenz des Netzes in Hz
    τ: Netzzeitkonstante (dimensionslos)
    γ: Faktor für die Bestimmung der maßgeblichen Eigenfrequenz (dimensionslos)
    Hinweis:
    Definition: $$\chi = f \cdot T_{pi}$$
    Kern der Gleichung ist dabei: $$\nu_1 = \chi \cdot \sqrt{\nu_2(\chi)}$$
    Zerlegung der Gleichung in einzelne Teile:
    $$f(\chi) = \chi \cdot \sqrt{1 - A(\chi) + B(\chi) - C(\chi)} - \nu_1 = 0$$
    Diese Nullstelle wird im Programm mittels des Newton-Verfahrens (über scipy.optimize.fsolve) bestimmt.
    Der resultierende Wert $\chi$ liefert direkt die reale Kontraktionszeit:$$T_{pi} = \frac{\chi}{f}$$
    """
    """
    Berechnet T_pi und ν_2 nach SN EN 60865-1:2012 Anhang A.7 in einer rückfallsicheren Funktion.
    Kombiniert Brent's Methode und fsolve für maximale Zuverlässigkeit.
    """
    y = f * τ
    x_sol = None

    # 1. Die Kern-Gleichung definieren
    def equation(x):
        if x < 1e-12:
            return -ν_1

        # Komponenten der Schwingungsgleichung
        two_pi_x = 2 * np.pi * x
        four_pi_x = 4 * np.pi * x
        exp_term = np.exp(-x / y)

        A = (np.sin(four_pi_x - 2 * γ) + np.sin(2 * γ)) / four_pi_x
        B = (y / x) * (1 - exp_term**2) * (np.sin(γ)**2)

        P = (2 * np.pi * y) * (np.cos(two_pi_x - γ) / two_pi_x)
        Q = np.sin(two_pi_x - γ) / two_pi_x
        R = (np.sin(γ) - (2 * np.pi * y * np.cos(γ))) / two_pi_x

        M = (P + Q) * exp_term + R
        C = ((8 * np.pi * y * np.sin(γ)) / (1 + (2 * np.pi * y)**2)) * M

        # Ausdruck unter der Wurzel (ν_2)
        # np.maximum(0, ...) schützt vor winzigen negativen Werten durch Rundungsfehler
        val_under_sqrt = 1 - A + B - C
        return x * np.sqrt(np.maximum(0, val_under_sqrt)) - ν_1

    #Brent's Methode (Sicher im Intervall [0, 2])
    try:
        # Wir prüfen, ob ein Vorzeichenwechsel im physikalisch plausiblen Bereich vorliegt
        if equation(1e-12) * equation(2.0) < 0:
            x_sol = brentq(equation, 1e-12, 2.0, xtol=1e-12)
    except ValueError:
        pass

    #FSOLVE (Backup mit verschiedenen Startpunkten)
    if x_sol is None:
        for start_val in [ν_1, 0.1, 0.5, 1.2]:
            try:
                sol, info, ier, msg = fsolve(equation, x0=np.array([start_val]), full_output=True)
                if ier == 1 and sol[0] > 0:
                    x_sol = float(sol[0])
                    break
            except:
                continue

    # --- FINALE BERECHNUNG ---
    if x_sol is not None:
        t_pi = x_sol / f
        nu2 = (ν_1 / x_sol)**2
        return float(t_pi), float(nu2)
    else:
        return None, None

    """
    y: float = f * τ

    # np anstelle von math, um Vektoren/Arrays direkt zu verarbeiten
    def equation(x):
        # fsolve übergibt ein Array. Falls x ≤ 0, geben wir ein Array zurück.
        if np.any(x <= 0):
            return np.array([-ν_1])

        # A, B und C mit np-Funktionen berechnet (keine Warnungen mehr!)
        A: float = (np.sin((4 * np.pi * x) - (2 * γ)) + np.sin(2 * γ)) / (4 * np.pi * x)
        B: float  = (y / x) * (1 - (np.exp(-((2 * x) / y)))) * (np.sin(γ) ** 2)
        P: float  = ((2 * np.pi * y) * (np.cos((2 * np.pi * x) - γ) / (2 * np.pi * x)))
        Q: float  = ((np.sin((2 * np.pi * x) - γ)) / (2 * np.pi * x))
        R: float  = ((np.sin(γ) - (2 * np.pi) * y * np.cos(γ)) / (2 * np.pi * x))
        M: float  = ((P + Q) * np.exp(-(x / y)) + R)
        C: float  = ((8 * np.pi * y * np.sin(γ)) / (1 + (2 * np.pi * y) ** 2)) * M

        sqrt_ν_2: float  = np.sqrt(np.abs(1 - A + B - C))

        # Rückgabe als Array (wie von fsolve erwartet)
        return x * sqrt_ν_2 - ν_1

    # Startwert x0 als Array übergeben
    x_solution_array = fsolve(equation, x0=np.array([ν_1]))
    x_solution = x_solution_array[0]

    t_pi = x_solution / f
    ν_2 = (ν_1 / x_solution) ** 2

    return t_pi, ν_2
    """

def T_pi_and_ν_2_backup(ν_1, f, τ, γ) -> tuple[float, float]:
    r"""
    Funktion zur Berechnung des Faktors T_pi zur Berechnung der Zeit vom Kurzschlussbeginn bis zum Erreichen von F_pi
    in s nach SN EN 60865-1:2012 Kapitel A.7
    T_pi: Zeit vom Kurzschlussbeginn bis zum Erreichen von F_pi in s
    ν_2: Faktor zur Berechnung von F_pi_d
    f: Frequenz des Netzes in Hz
    τ: Netzzeitkonstante (dimensionslos)
    γ: Faktor für die Bestimmung der maßgeblichen Eigenfrequenz (dimensionslos)
    Hinweis:
    Definition: $$\chi = f \cdot T_{pi}$$
    Kern der Gleichung ist dabei: $$\nu_1 = \chi \cdot \sqrt{\nu_2(\chi)}$$
    Zerlegung der Gleichung in einzelne Teile:
    $$f(\chi) = \chi \cdot \sqrt{1 - A(\chi) + B(\chi) - C(\chi)} - \nu_1 = 0$$
    Diese Nullstelle wird im Programm mittels des Newton-Verfahrens (über scipy.optimize.fsolve) bestimmt.
    Der resultierende Wert $\chi$ liefert direkt die reale Kontraktionszeit:$$T_{pi} = \frac{\chi}{f}$$
    """
    y: float = f * τ

    # np anstelle von math, um Vektoren/Arrays direkt zu verarbeiten
    def equation(x):
        # fsolve übergibt ein Array. Falls x ≤ 0, geben wir ein Array zurück.
        if np.any(x <= 0):
            return np.array([-ν_1])

        # A, B und C mit np-Funktionen berechnet (keine Warnungen mehr!)
        A: float = (np.sin((4 * np.pi * x) - (2 * γ)) + np.sin(2 * γ)) / (4 * np.pi * x)
        B: float  = (y / x) * (1 - (np.exp(-((2 * x) / y)))) * (np.sin(γ) ** 2)
        P: float  = ((2 * np.pi * y) * (np.cos((2 * np.pi * x) - γ) / (2 * np.pi * x)))
        Q: float  = ((np.sin((2 * np.pi * x) - γ)) / (2 * np.pi * x))
        R: float  = ((np.sin(γ) - (2 * np.pi) * y * np.cos(γ)) / (2 * np.pi * x))
        M: float  = ((P + Q) * np.exp(-(x / y)) + R)
        C: float  = ((8 * np.pi * y * np.sin(γ)) / (1 + (2 * np.pi * y) ** 2)) * M

        sqrt_ν_2: float  = np.sqrt(np.abs(1 - A + B - C))

        # Rückgabe als Array (wie von fsolve erwartet)
        return x * sqrt_ν_2 - ν_1

    # Startwert x0 als Array übergeben
    x_solution_array = fsolve(equation, x0=np.array([ν_1]))
    x_solution = x_solution_array[0]

    t_pi = x_solution / f
    ν_2 = (ν_1 / x_solution) ** 2

    return t_pi, ν_2

# Gleichung (A.8 Bild 10)
def ν_3(a_s: float, d: float, n: float = None) -> float:
    """
    Funktion zur Berechnung des Faktors ν_3 zur Berechnung von F_pi_d (dimensionslos) nach SN EN 60865-1:2012 Kapitel A.9
    ν_4: Faktor zur Berechnung von F_pi_d
    a_s: wirksamer Abstand zwischen Teilleitern in m
    d: Aussendurchmesser von Rohrleitern oder Seildurchmesser in m
    n: Anzahl der Teilleiter eines Hauptleiters (dimensionslos)
    """
    ν_3: float = ((d / a_s) / math.sin(math.radians(180 / n))) * ((math.sqrt((a_s / d) - 1)) / math.atan(math.sqrt((a_s / d) - 1)))
    return ν_3

# Gleichung (A.9 Bild 11)
def ξ_symbolisch(j: float, ε_st: float) -> float | None:
    """
    Funktion zur Berechnung des Faktors ζ zur Berechnung des Beanspruchungsfaktors des Hauptleiters in Seilanordnungen
    (dimensionslos) nach SN EN 60865-1:2012 Kapitel A.9
    ζ: Beanspruchungsfaktor des Hauptleiters in Seilanordnungen (dimensionslos)
    j: Parameter, der die Lage der Bündelleiter während des Kurzschlussstrom-Flusses angibt (dimensionslos)
    ε_st: Dehnungsfaktoren bei der Kontraktion eines Seilbündels (dimensionslos)
    Hinweis: Es werden nur reale Zahlen und Zahlen zwischen j**(2/3) und j eingegeben.
    """
    """
    Berechnet den Faktor ξ nach SN EN 60865-1:2012.
    Gleichung: ξ³ + ε_st * ξ² - j² * (1 + ε_st) = 0
    Gültigkeitsbereich: j >= 1, gesuchte Wurzel ξ liegt zwischen j^(2/3) und j.
    """
    if j < 1:
        return None

    # Untere und obere Grenze für die physikalische Lösung
    lower_bound = j**(2 / 3)
    upper_bound = j

    # Symbolisch (SymPy) ---
    try:
        xi_sym = sympy.symbols('xi', real=True)
        polynom = (xi_sym**3) + (ε_st * xi_sym**2) - (j**2 * (1 + ε_st))
        gl_Zeta = sympy.solve(polynom, xi_sym)

        # Filter: Wir suchen die Wurzel im Bereich [j^(2/3), j]
        valid_sols = [float(s) for s in gl_Zeta if lower_bound - 1e-7 <= s <= upper_bound + 1e-7]
        if valid_sols:
            return float(valid_sols[0])
    except:
        pass
    finally:
        return ξ_numerisch(j=j, ε_st=ε_st)
    # return None

def ξ_numerisch(j: float, ε_st: float) -> float | None:
    """
    Funktion zur Berechnung des Faktors ζ zur Berechnung des Beanspruchungsfaktors des Hauptleiters in Seilanordnungen
    (dimensionslos) nach SN EN 60865-1:2012 Kapitel A.9
    ζ: Beanspruchungsfaktor des Hauptleiters in Seilanordnungen (dimensionslos)
    j: Parameter, der die Lage der Bündelleiter während des Kurzschlussstrom-Flusses angibt (dimensionslos)
    ε_st: Dehnungsfaktoren bei der Kontraktion eines Seilbündels (dimensionslos)
    Hinweis: Es werden nur reale Zahlen und Zahlen zwischen j**(2/3) und j eingegeben.
    """
    """
    Berechnet den Faktor ξ nach SN EN 60865-1:2012.
    Gleichung: ξ³ + ε_st * ξ² - j² * (1 + ε_st) = 0
    Gültigkeitsbereich: j >= 1, gesuchte Wurzel ξ liegt zwischen j^(2/3) und j.
    """
    if j < 1:
        return None

    # Untere und obere Grenze für die physikalische Lösung
    lower_bound = j**(2 / 3)
    upper_bound = j

    # Die Funktion für numerische Verfahren
    def f(xi_val):
        return (xi_val**3) + (ε_st * xi_val**2) - (j**2 * (1 + ε_st))

    # Brent's Methode (Sicher im Intervall) ---
    try:
        # Bei j >= 1 ist f(lower_bound) <= 0 und f(upper_bound) >= 0
        # Das garantiert eine Lösung im Intervall.
        return float(brentq(f, lower_bound, upper_bound, xtol=1e-12))
    except ValueError:
        pass

    # FSOLVE (Notfall-Fallback) ---
    # Startwerte: Mitte des Intervalls und die Grenzen
    for start in [(lower_bound + upper_bound) / 2, lower_bound, upper_bound]:
        try:
            sol, info, ier, msg = fsolve(f, x0=np.array([start]), full_output=True)
            if ier == 1 and lower_bound - 1e-7 <= sol[0] <= upper_bound + 1e-7:
                return float(sol[0])
        except:
            continue
    return None

def ξ_backup(j: float, ε_st: float) -> float | None:
    """
    Funktion zur Berechnung des Faktors ζ zur Berechnung des Beanspruchungsfaktors des Hauptleiters in Seilanordnungen
    (dimensionslos) nach SN EN 60865-1:2012 Kapitel A.9
    ζ: Beanspruchungsfaktor des Hauptleiters in Seilanordnungen (dimensionslos)
    j: Parameter, der die Lage der Bündelleiter während des Kurzschlussstrom-Flusses angibt (dimensionslos)
    ε_st: Dehnungsfaktoren bei der Kontraktion eines Seilbündels (dimensionslos)
    Hinweis: Es werden nur reale Zahlen und Zahlen zwischen j**(2/3) und j eingegeben.
    """
    """
    Berechnet den Faktor ξ nach SN EN 60865-1:2012.
    Gleichung: ξ³ + ε_st * ξ² - j² * (1 + ε_st) = 0
    Gültigkeitsbereich: j >= 1, gesuchte Wurzel ξ liegt zwischen j^(2/3) und j.
    """
    if j < 1:
        return None

    # Untere und obere Grenze für die physikalische Lösung
    lower_bound = j**(2 / 3)
    upper_bound = j

    # Die Funktion für numerische Verfahren
    def f(xi_val):
        return (xi_val**3) + (ε_st * xi_val**2) - (j**2 * (1 + ε_st))

    # Symbolisch (SymPy) ---
    try:
        xi_sym = sympy.symbols('xi', real=True)
        polynom = (xi_sym**3) + (ε_st * xi_sym**2) - (j**2 * (1 + ε_st))
        gl_Zeta = sympy.solve(polynom, xi_sym)

        # Filter: Wir suchen die Wurzel im Bereich [j^(2/3), j]
        valid_sols = [float(s) for s in gl_Zeta if lower_bound - 1e-7 <= s <= upper_bound + 1e-7]
        if valid_sols:
            return float(valid_sols[0])
    except:
        pass

    # Brent's Methode (Sicher im Intervall) ---
    try:
        # Bei j >= 1 ist f(lower_bound) <= 0 und f(upper_bound) >= 0
        # Das garantiert eine Lösung im Intervall.
        return float(brentq(f, lower_bound, upper_bound, xtol=1e-12))
    except ValueError:
        pass

    # FSOLVE (Notfall-Fallback) ---
    # Startwerte: Mitte des Intervalls und die Grenzen
    for start in [(lower_bound + upper_bound) / 2, lower_bound, upper_bound]:
        try:
            sol, info, ier, msg = fsolve(f, x0=np.array([start]), full_output=True)
            if ier == 1 and lower_bound - 1e-7 <= sol[0] <= upper_bound + 1e-7:
                return float(sol[0])
        except:
            continue
    return None

# Gleichung (A.10 Bild 12)
def η(ε_st: float, j: float, v_3: float, n: float, a_s: float, d: float) -> float:
    """
    Funktion zur Berechnung des Faktors η zur Berechnung von F_pi bei nicht zusammenschlagenden
    Bündelleitern (dimensionslos) nach SN EN 60865-1:2012 Kapitel A.10
    ε_st: ε_st: Dehnungsfaktoren bei der Kontraktion eines Seilbündels (dimensionslos)
    j: j: Parameter, der die Lage der Bündelleiter während des Kurzschlussstrom-Flusses angibt (dimensionslos)
    ν_3: Faktor zur Berechnung von F_pi_d
    η: Faktor zur Berechnung von Fpi bei nicht zusammenschlagenden Bündelleitern (dimensionslos)
    a_s: wirksamer Abstand zwischen Teilleitern in m
    d: Aussendurchmesser von Rohrleitern oder Seildurchmesser in m
    fη: Faktor zur Beschreibung der Teilleiter-Annäherung im Seilbündel
    Hinweis: Es werden nur reale Zahlen und Zahlen zwischen 0 und 1 eingegeben.
    """
    """
    Berechnet den Faktor η nach SN EN 60865-1:2012 Kapitel A.10.
    Nutzt ein Tiered-Numerical-Modell (Brent + fsolve) für die implizite Gleichung.
    """
    # Vorfaktor für asw_as (konstant während der Iteration)
    sin_n = math.sin(math.radians(180 / n))
    d_as_ratio = d / a_s

    def zielfunktion(η_val):
        # 1. Schutz gegen Grenzwert-Überschreitung (0 ≤ η ≤ 1)
        η_val = max(1e-9, min(1.0 - 1e-9, η_val))

        # 2. Berechnung von 2ya/as
        u = 1 - (η_val * (1 - d_as_ratio))

        # 3. Berechnung von asw/as (mit numerischem Schutz für u -> 1)
        # Wenn u -> 1 (η -> 0), geht sqrt((1-u)/u) gegen 0.
        # Da lim x->0 (x / atan(x)) = 1, ist der Grenzwert stabil.
        term = math.sqrt((1 - u) / u)
        if term < 1e-7:
            asw_as_val = u / sin_n
        else:
            asw_as_val = (u / sin_n) * (term / math.atan(term))

        # 4. Berechnung von f_eta
        val_f_eta = v_3 / asw_as_val

        # 5. Die Zielgleichung: η³ + ε_st * η - j² * (1 + ε_st) * fη = 0
        return (η_val**3) + (ε_st * η_val) - (j**2 * (1 + ε_st) * val_f_eta)

    # Prüfung der Grenzen (Physik-Check)
    # Wenn die Funktion bei η=1 noch negativ ist, berühren sich die Leiter (η=1)
    if zielfunktion(0.99999) < 0:
        return 1.0

    # Brent's Methode (Sicher und präzise)
    try:
        # Suche im Bereich [1e-8, 0.99999]
        # Da f(0) meist negativ ist (wegen -j²...) und f(1) bei Nicht-Zusammenschlagen positiv
        if zielfunktion(1e-8) * zielfunktion(0.99999) < 0:
            return float(brentq(zielfunktion, 1e-8, 0.99999, xtol=1e-12))
    except (ValueError, RuntimeError):
        pass

    #FSOLVE (Fallback)
    for start in [0.2, 0.5, 0.8]:
        try:
            sol, info, ier, msg = fsolve(zielfunktion, x0=np.array([start]), full_output=True)
            if ier == 1:
                return float(np.clip(sol[0], 0.0, 1.0))
        except:
            continue

    return 1.0 # Standardwert bei extremen Fehlern (Zusammenschlagen angenommen)

def η_backup(ε_st: float, j: float, v_3: float, n: float, a_s: float, d: float) -> float:
    """
    Funktion zur Berechnung des Faktors η zur Berechnung von F_pi bei nicht zusammenschlagenden
    Bündelleitern (dimensionslos) nach SN EN 60865-1:2012 Kapitel A.10
    ε_st: ε_st: Dehnungsfaktoren bei der Kontraktion eines Seilbündels (dimensionslos)
    j: j: Parameter, der die Lage der Bündelleiter während des Kurzschlussstrom-Flusses angibt (dimensionslos)
    ν_3: Faktor zur Berechnung von F_pi_d
    η: Faktor zur Berechnung von Fpi bei nicht zusammenschlagenden Bündelleitern (dimensionslos)
    a_s: wirksamer Abstand zwischen Teilleitern in m
    d: Aussendurchmesser von Rohrleitern oder Seildurchmesser in m
    fη: Faktor zur Beschreibung der Teilleiter-Annäherung im Seilbündel
    Hinweis: Es werden nur reale Zahlen und Zahlen zwischen 0 und 1 eingegeben.
    """
    """
        Löst das mathematische Problem des Zirkelschlusses für η.
        Da fη von η abhängt, wird der Wert iterativ bestimmt, um dem 
        Bild 12 der Norm zu entsprechen.
        """

    def zielfunktion(η_test):
        # Sicherstellen, dass η_test ein Skalar ist
        η_val = float(np.atleast_1d(η_test)[0])

        # Falls η_val außerhalb der Grenzen 0..1 gerät, wird korrigiert für den Solver
        η_val = max(1e-6, min(0.9999, η_val))

        # Funktionen für die Berechnung der Abhängigkeiten
        val_2ya = two_ya_as(η_val, a_s, d)
        val_asw = asw_as(val_2ya, n)
        val_fη = fη(v_3, val_asw)

        # Funktion zur Bestimmung des effektiven j. Nur im Bedarfsfall einsetzen.
        # j__ = math.sqrt((η**3 + (ε_st * η)) / ((1 + ε_st) * fη))

        # Das kubische Polynom der Norm, wo der Punkt gesucht wird, an dem dieses Polynom Null ergibt.
        # Dies ist das Polynom nach A.10 Bild 12: η³ + ε_st * η - j² * (1 + ε_st) * fη = 0

        # Wichtig: (η_val ** 3) + (ε_st * η_val) - ((j ** 2) * val_fη) ist die Formel, die in den Diagrammen der Bilder 12a, 12b und 12c verwendet wird.
        # Bei den Bildern 12a-c wird der Term (1 + ε_st) zur Vereinfachung also nicht verwendet.

        # Da j laut Gleichung (58) bereits den Faktor 1/sqrt(1 + ε_st) enthält,
        # kürzt sich die Dehnung ε_st in der exakten Berechnung mathematisch heraus.
        # Die Diagramme in der Norm behalten ε_st künstlich bei, um verschiedene Kurven
        # zeichnen zu können. Dieses Programm bleibt bei der exakten analytischen Lösung.
        return (η_val ** 3) + (ε_st * η_val) - ((j ** 2) * (1 + ε_st) * val_fη)

    # 1. Vorprüfung:
    # Wir fangen den Fall ab, dass keine Lösung im Bereich 0..1 existiert
    # Wenn die Zielfunktion bei η=1 immer noch negativ ist, schlagen die Leiter zusammen
    if zielfunktion(0.9999) < 0:
        return 1.0

    # 2. Numerische Lösung:
    try:
        # Suche nach der Nullstelle mit Startwert 0.5
        η_sol = scipy.optimize.fsolve(zielfunktion, x0=0.5)[0]
        # Das Ergebnis auf den physikalisch sinnvollen Bereich [0, 1] begrenzen
        #print(f"η_sol: {η_sol}")
        #print(f"η_sol_typ: {type(float(η_sol))}")
        return max(0.0, min(1.0, float(η_sol)))
    except (ValueError, RuntimeError) as e:
        #print(f"Solver-Fehler für Berechnung von η: {e}")
        return 0.0

# Gleichung (A.10 Bild 12)
def fη(v_3: float, asw_as: float) -> float:
    """
    Funktion zur Berechnung des Faktors fη der Teilleiter-Annäherung im Seilbündel
    (dimensionslos) nach SN EN 60865-1:2012 Kapitel A.10
    fη: Faktor zur Beschreibung der Teilleiter-Annäherung im Seilbündel
    y_a: Mittenabstand der nicht zusammenschlagenden Bündelleiter während des Kurzschlusses inm
    a_s: wirksamer Abstand zwischen Teilleitern in m
    n: Anzahl der Teilleiter eines Hauptleiters (dimensionslos)
    """
    fη: float = v_3 / asw_as
    return fη

# Gleichung (A.10 Bild 12)
def asw_as(two_ya_as: float, n: float) -> float:
    """
    Funktion zur Berechnung des Faktors asw_as zur Beschreibung von fη der Teilleiter-Annäherung im Seilbündel
    (dimensionslos) nach SN EN 60865-1:2012 Kapitel A.10
    fη: Faktor zur Beschreibung der Teilleiter-Annäherung im Seilbündel
    a_sw: wirksamer Abstand zwischen den Teilleitern eines Bündels in m
    a_s: wirksamer Abstand zwischen Teilleitern in m
    n: Anzahl der Teilleiter eines Hauptleiters (dimensionslos)
    """
    #asw_as = (two_ya_as / math.sin(180 / n)) * (math.sqrt((1 - two_ya_as) / two_ya_as) / math.atan(math.sqrt((1 - two_ya_as) / two_ya_as)))
    asw_as: float = (two_ya_as / math.sin(math.radians(180 / n))) * ((math.sqrt((1 - two_ya_as) / two_ya_as)) / math.atan(math.sqrt((1 - two_ya_as) / two_ya_as)))
    return asw_as

# Gleichung (A.10 Bild 12)
def two_ya_as(η: float, a_s: float, d: float):
    """
    Funktion zur Berechnung des Faktors two_ya_as zur Beschreibung von fη der Teilleiter-Annäherung im Seilbündel
    (dimensionslos) nach SN EN 60865-1:2012 Kapitel A.10
    fη: Faktor zur Beschreibung der Teilleiter-Annäherung im Seilbündel
    η: Faktor zur Berechnung von F_pi bei nicht zusammenschlagenden Bündelleitern (dimensionslos)
    y_a: Mittenabstand der nicht zusammenschlagenden Bündelleiter während des Kurzschlusses in m
    a_s: wirksamer Abstand zwischen Teilleitern in m
    d: Außendurchmesser von Rohrleitern oder Seildurchmesser in m
    """
    two_ya_as: float = 1 - (η * (1 - (d / a_s)))
    return two_ya_as


# Hauptformeln der Kräfte
# Grössen ab Kapitel 4
# Gleichung (1)
def F(μ0: float, i_1: float, i_2: float, l: float, a: float) -> float:
    """
    Funktion zur Berechnung der Kraft F zwischen zwei parallelen, langen Leitern während eines Kurzschlusses in N
    nach SN EN 60865-1:2012 Kapitel 4.
    μ0: magnetische Feldkonstante, Permeabilität des leeren Raumes Vs/(Am)
    i1, i2: Augenblickswerte der Leiterströme in A
    l: Mittenabstand der Stützpunkte in m
    a: Leitermittenabstand in m
    Erläuterung zu F:
    Es werden die Kräfte zwischen parallelen Leitern angegeben. Die elektromagnetischen Kraftanteile, die durch
    abgewinkelte und/oder sich kreuzende Leiter auftreten, können im Allgemeinen vernachlässigt werden. Die Formel kann
    angewendet werden, falls die Länge der parallelen Leiter grösser ist als ihr Abstand.
    (SN EN 60865-1:2012 Kapitel 4 Seite 11)
    """
    F: float = (μ0 / 2 * math.pi) * i_1 * i_2 * l * a
    return F

# Grössen ab Kapitel 6.2.2
# Gleichung (19a)
@lru_cache(maxsize=1)
def F_a(μ0: float, I_k: float, l: float, l_c: float, a: float) -> float:
    """
    Funktion zur Berechnung der Kraft F' Kraft charakteristischer elektromagnetischer Kraftbelag auf den Hauptleiter in
    Seilanordnungen in N/m nach SN EN 60865-1:2012 Kapitel 6.2.2.
    Bei Stromfluss über die gesamte Seillänge des Hauptleiters im Spannfeld mit und ohne Schlaufe.
    μ0: magnetische Feldkonstante, Permeabilität des leeren Raumes Vs/(Am)
    I_k: Anfangs-Kurzschlusswechselstrom (Effektivwert) beim dreipoligen Kurzschluss in A
    a: Leitermittenabstand in m
    l: Mittenabstand der Stützpunkte in m
    l_c: Seillänge eines Hauptleiters im Spannfeld m
    l_v: Seil(bogen)länge der Schlaufe m
    Erläuterung zu lc:
    Bei Feldern mit aufgelegten Seilen, die Stützisolatoren auf Biegung beanspruchen, gilt lc = l. Bei Feldern mit
    abgespannten Seilen gilt lc = l − 2li, dabei ist li die Länge einer Abspann-Isolatorkette.
    (SN EN 60865-1:2012 Kapitel 6.2.2 Seite 26)
    """
    F_a: float = (μ0 / (2 * math.pi)) * 0.75 * (I_k**2 / a) * (l_c / l)
    return F_a

# Grössen ab Kapitel 6.2.2
# Gleichung (19b)
@lru_cache(maxsize=1)
def F_b(μ0: float, I_k: float, l: float, l_c: float, l_v: float, a: float) -> float:
    """
    Funktion zur Berechnung der Kraft F' Kraft charakteristischer elektromagnetischer Kraftbelag auf den Hauptleiter in
    Seilanordnungen in N/m nach SN EN 60865-1:2012 Kapitel 6.2.2.
    Bei Stromfluss über die halbe Seillänge des Hauptleiters im Spannfeld über die Schlaufe
    μ0: magnetische Feldkonstante, Permeabilität des leeren Raumes Vs/(Am)
    I_k: Anfangs-Kurzschlusswechselstrom (Effektivwert) beim dreipoligen Kurzschluss in A
    a: Leitermittenabstand in m
    l: Mittenabstand der Stützpunkte in m
    l_c: Seillänge eines Hauptleiters im Spannfeld m
    l_v: Seil(bogen)länge der Schlaufe m
    Erläuterung zu lc:
    Bei Feldern mit aufgelegten Seilen, die Stützisolatoren auf Biegung beanspruchen, gilt lc = l. Bei Feldern mit
    abgespannten Seilen gilt lc = l − 2li, dabei ist li die Länge einer Abspann-Isolatorkette.
    (SN EN 60865-1:2012 Kapitel 6.2.2 Seite 26)
    """
    F_b: float = (μ0 / 2 * math.pi) * 0.75 * (I_k**2 / a) * (((l_c / 2) + (l_v / 2)) / l)
    return F_b

# Grössen ab Kapitel 6.2.3
# Gleichung (33)
def F_td_ohne_schlaufe_spannfeldmitte(F_st: float, φ: float, ψ: float) -> float:
    """
    Funktion zur Berechnung der Kraft F_td Kurzschluss-Seilzugkraft in einem Hauptleiter (Bemessungswert) in
    Seilanordnungen in N nach SN EN 60865-1:2012 Kapitel 6.2.3.
    F_td: Kurzschluss-Seilzugkraft in einem Hauptleiter (Bemessungswert) in N
    F_st: statische Seilzugkraft in einem Hauptleiter in N
    φ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    ψ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    Erläuterung zu F_td:
    Kraft infolge des Ausschwingens während des Kurzschlusses.
    Anzuwenden bei Stromfluss über die gesamte Seillänge des Hauptleiters im Spannfeld ohne Schlaufe in Spannfeldmitte.
    """
    F_td: float = F_st * (1 + (φ * ψ))
    return F_td

# Bis hierhin verfiziert

# Grössen ab Kapitel 6.2.5
# Gleichung (42)
def F_td_mit_schlaufe_spannfeldmitte(F_st: float, φ: float, ψ: float) -> float:
    """
    Funktion zur Berechnung der Kraft F_td Kurzschluss-Seilzugkraft in einem Hauptleiter (Bemessungswert) in
    Seilanordnungen in N nach SN EN 60865-1:2012 Kapitel 6.2.3.
    F_td: Kurzschluss-Seilzugkraft in einem Hauptleiter (Bemessungswert) in N
    F_st: statische Seilzugkraft in einem Hauptleiter in N
    φ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    ψ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    Erläuterung zu F_td:
    Kraft infolge des Ausschwingens während des Kurzschlusses.
    Anzuwenden bei Stromfluss über die gesamte Seillänge des Hauptleiters im Spannfeld ohne Schlaufe in Spannfeldmitte.
    """
    F_td: float = F_st * (1 + (φ * ψ))
    return F_td

# Grössen ab Kapitel 6.2.5
# Gleichung (43)
def F_fd(F_st: float, ζ: float, δ_max: float) -> float:
    """
    Funktion zur Berechnung der Kraft F_fd Fall-Seilzugkraft in einem Hauptleiter (Bemessungswert) in
    Seilanordnungen in N nach SN EN 60865-1:2012 Kapitel 6.2.6.
    F_fd: Fall-Seilzugkraft in einem Hauptleiter (Bemessungswert) in N
    F_st: statische Seilzugkraft in einem Hauptleiter in N
    ζ: Beanspruchungsfaktor des Hauptleiters in Seilanordnungen  (dimensionslos)
    δ_max: maximaler Ausschwingwinkel in °
    ψ: Faktoren für die Berechnung der Zugkraft in Leiterseilen (dimensionslos)
    Erläuterung zu F_fd:
    Kraft nach Ausschaltung des Kurzschlusses bei der das Seil pendelt oder in seine Ruhelage zurückfällt.
    Der Höchstwert F_fd der am Ende des Falles auftretenden Seilzugkraft ist nur zu berücksichtigen bei r > 0,6, wenn
    δ_max ≥ 70°, und mit einer Schlaufe in Spannfeldmitte, wenn δ ≥ 60°.
    """
    F_fd: float = 1.2 * F_st * (math.sqrt(1 + ((8 * ζ) *(δ_max / 180))))
    return F_fd

# Grössen ab Kapitel 6.3
# Gleichung (49)
def F_td_verikaler_höhenunterschied_befestigungspunkte(μ0: float, I_k: float, l_v: float, a: float, w: float) -> float:
    """
    Funktion zur Berechnung der Kraft F_td Kurzschluss-Seilzugkraft in einem Hauptleiter (Bemessungswert) in
    Seilanordnungen in N nach SN EN 60865-1:2012 Kapitel 6.3.
    F_td: Kurzschluss-Seilzugkraft in einem Hauptleiter (Bemessungswert) in N
    μ0: magnetische Feldkonstante, Permeabilität des leeren Raumes Vs/(Am)
    I_k: Anfangs-Kurzschlusswechselstrom (Effektivwert) beim dreipoligen Kurzschluss in A
    a: Leitermittenabstand in m
    l_v: Seil(bogen)länge der Schlaufe m
    w: Schlaufenbreite in m
    Erläuterung zu F_td:
    Kraft infolge des Ausschwingens während des Kurzschlusses.
    Anzuwenden bei vertikalen Schlaufen bei einem Höhenunterschiede der Befestigungspunkte von mehr als 25 % der
    Spannfeldlänge betragen.
    """
    F_td: float = (5 / 3) * l_v * ((μ0 / 2 * math.pi)  * (I_k**2 / a) * (l_v / w))
    return F_td

# Grössen ab Kapitel 6.4.1
# Gleichung (51)
def F_pi_d_ohne_j(F_td: float, a_s: float, d: float, l_s: float) -> float | None:
    """
    Funktion zur Berechnung der Kraft F_pi_d Bündel-Seilzugkraft in einem Hauptleiter (Bemessungswert)
    in N nach SN EN 60865-1:2012 Kapitel 6.4.1.
    F_pi_d_ohne_j: Bündel-Seilzugkraft in einem Hauptleiter (Bemessungswert) in N
    F_td: Kurzschluss-Seilzugkraft in einem Hauptleiter (Bemessungswert) in N
    a_s: wirksamer Abstand zwischen Teilleitern in m
    d: Außendurchmesser von Rohrleitern oder Seildurchmesser in m
    l_s: Mittenabstand der Zwischenstücke oder Mittenabstand eines Zwischenstücks und des benachbarten Stützpunkts in m
    Erläuterung zu F_pi_d_ohne_j:
    Das wirksame Zusammenschlagen der Teilleiter gilt als erfüllt, wenn sowohl der Mittenabstand as zweier benachbarter
    Teilleiter als auch der Abstand ls zweier benachbarter Abstandhalter entweder Gleichung (52) ODER Gleichung (53)
    erfüllen.
    """
    if a_s / d <= 2.0 and l_s >= 50 * a_s:
        F_pi_d_ohne_j_1: float = 1.1 * F_td
        F_pi_d_ohne_j = F_pi_d_ohne_j_1
        return F_pi_d_ohne_j
    elif a_s / d <= 2.5 and l_s >= 70 * a_s:
        F_pi_d_ohne_j_2: float = 1.1 * F_td
        F_pi_d_ohne_j = F_pi_d_ohne_j_2
        return F_pi_d_ohne_j

# Grössen ab Kapitel 6.4.1
# Gleichung (54)
def F_v(μ0: float, I_k: float, a_s: float, l_c: float, l_s: float, l_eff: float, n: float, ν_2: float, ν_3: float) -> float:
    """
    Funktion zur Berechnung der Kurzschluss-Stromkraft zwischen den Teilleitern eines Bündels F_v in N nach
    SN EN 60865-1:2012 Kapitel 6.4.1.
    F_v: Kurzschluss-Stromkraft zwischen den Teilleitern eines Bündels in N
    μ0: magnetische Feldkonstante, Permeabilität des leeren Raumes Vs/(Am)
    I_k: Anfangs-Kurzschlusswechselstrom (Effektivwert) beim dreipoligen Kurzschluss in A
    a_s: wirksamer Abstand zwischen Teilleitern in m
    l_c: Seillänge eines Hauptleiters im Spannfeld m
    l_s: Mittenabstand der Zwischenstücke oder Mittenabstand eines Zwischenstücks und des benachbarten Stützpunkts in m
    n: Anzahl der Teilleiter eines Hauptleiters (dimensionslos)
    ν_2: Faktor zur Berechnung von F_pi_d
    ν_3: Faktor zur Berechnung von F_pi_d
    Erläuterung zu F_v:
    Das wirksame Zusammenschlagen der Teilleiter gilt als erfüllt, wenn sowohl der Mittenabstand as zweier benachbarter
    Teilleiter als auch der Abstand ls zweier benachbarter Abstandhalter entweder Gleichung (52) ODER Gleichung (53)
    erfüllen.
    """
    # In Abweichung von der Norm wird hier eine Unterscheidung zwischen hier unterschieden, ob Abstandhalter
    # vorhanden sind oder nicht. Sind Abstandhalter vorhanden, wird gemäss Norm mit den gemittelten Abständen l_s der
    # gerechnet. Falls keine Abstandhalter vorhanden sind, wird l_c, also die Seillänge eines Hauptleiters im Spannfeld
    # verwendet. (Verifiziert mit dem Programm IEC865D)
    if l_s not in (None, 0.0, 0):
        F_v: float = (n - 1) * (μ0 / (2 * math.pi))  * ((I_k / n)**2) * (l_s / a_s) * (ν_2 / ν_3)
    elif l_eff not in (None, 0.0, 0):
        F_v: float = (n - 1) * (μ0 / (2 * math.pi)) * ((I_k / n)**2) * (l_eff / a_s) * (ν_2 / ν_3)
    else:
        F_v: float = (n - 1) * (μ0 / (2 * math.pi))  * ((I_k / n)**2) * (l_c / a_s) * (ν_2 / ν_3)
    return F_v

# Grössen ab Kapitel 6.4.2
# Gleichung (59, 62)
def F_pi_d_mit_j(F_st: float, j: float, ν_e: float, ε_st: float, ξ: float = None, η: float = None) -> float | None:
    """
    Funktion zur Berechnung der Kraft F_pi_d Bündel-Seilzugkraft in einem Hauptleiter (Bemessungswert)
    in N nach SN EN 60865-1:2012 Kapitel 6.4.2.
    F_pi_d_mit_j: Bündel-Seilzugkraft in einem Hauptleiter (Bemessungswert) in N
    F_st: statische Seilzugkraft in einem Hauptleiter in N
    j: Parameter, der die Lage der Bündelleiter während des Kurzschlussstrom-Flusses angibt (dimensionslos)
    ν_e: Faktor zur Berechnung von F_pi_d
    ε_st: Dehnungsfaktoren bei der Kontraktion eines Seilbündels (dimensionslos)
    ξ: Beanspruchungsfaktor des Hauptleiters in Seilanordnungen (dimensionslos)
    η: Faktor zur Berechnung von Fpi,d bei nicht zusammenschlagenden Bündelleitern (dimensionslos)
    """
    if j >= 1:
        F_pi_d_mit_j_1: float = F_st * (1 + ((ν_e / ε_st) * ξ))
        F_pi_d_mit_j = F_pi_d_mit_j_1
        return F_pi_d_mit_j
    elif j < 1:
        F_pi_d_mit_j_2: float = F_st * (1 + ((ν_e / ε_st) * η**2))
        F_pi_d_mit_j = F_pi_d_mit_j_2
        return F_pi_d_mit_j


def testrechnungen() -> None:

    print("Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet")
    print("l_c = ", l_c(l=31.0, l_i=5.25))
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("l_c/l = ", l_c(l=31.0, l_i=5.25)/31.0)
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("F_a = ", F_a(μ0=(4 * math.pi * 1e-7) ,I_k=40000, l=31.0, l_c=l_c(l=31.0, l_i=5.25), a=4))
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("r = ", r(F_=39.677, n=2, m_s=1.659, g=g))
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("δ_1 = ", δ_1(r(F_=39.677, n=2, m_s=1.659, g=g)))
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("f_es (-20°C) = ", f_es(n= 2, m_s= 1.659, g=g, l=31.0, F_st=19000)) # -20°C
    print("f_es (80°C) = ", f_es(n= 2, m_s= 1.659, g=g, l=31.0, F_st=7000)) # 80°C
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("T (-20°C) = ", T(f_es(n= 2, m_s= 1.659, g=g, l=31.0, F_st=19000), g=g)) # -20°C
    print("T (80°C) = ", T(f_es(n= 2, m_s= 1.659, g=g, l=31.0, F_st=7000), g=g)) # 80°C
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("T_res (-20°C) = ", T_res(T(f_es(n= 2, m_s= 1.659, g=g, l=31.0, F_st=19000), g=g), r(F_=39.677, n=2, m_s=1.659, g=g), δ_1(r(F_=39.677, n=2, m_s=1.659, g=g)))) # -20°C
    print("T_res (80°C) = ",  T_res(T(f_es(n= 2, m_s= 1.659, g=g, l=31.0, F_st=7000), g=g), r(F_=39.677, n=2, m_s=1.659, g=g), δ_1(r(F_=39.677, n=2, m_s=1.659, g=g)))) # 80°C
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("E_eff (-20°C) = ", E_eff(E=(55000*10**6) , F_st=19000, n=2, A_s=(600.38*10**-6) , σ_fin=σ_fin)) # -20°C
    print("E_eff (80°C) = ",  E_eff(E=(55000*10**6) , F_st=7000, n=2, A_s=(600.38*10**-6) , σ_fin=σ_fin))  # 80°C
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("N (-20°C) = ", N(S=400000, l=31.0, n=2, E_eff=E_eff(E=(55000 * 10 ** 6), F_st=19000, n=2, A_s=(600.38 * 10 ** -6), σ_fin=σ_fin), A_s=(600.38 * 10 ** -6)))  # -20°C
    print("N (80°C) = ", N(S=400000, l=31.0, n=2, E_eff=E_eff(E=(55000 * 10 ** 6), F_st=7000, n=2, A_s=(600.38 * 10 ** -6), σ_fin=σ_fin), A_s=(600.38 * 10 ** -6)))  # 80°C
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("ζ (-20°C) = ", ζ(n=2, g=g, m_s=1.659, l=31.0, F_st=19000, N = N(S=400000, l=31.0, n=2, E_eff=E_eff(E=(55000*10**6), F_st=19000, n=2, A_s=(600.38*10**-6),σ_fin=σ_fin), A_s = (600.38 * 10 ** -6)) )) # -20°C
    print("ζ (80°C) = ",  ζ(n=2, g=g, m_s=1.659, l=31.0, F_st=7000, N = N(S=400000, l=31.0, n=2, E_eff=E_eff(E=(55000*10**6), F_st=7000, n=2, A_s=(600.38*10**-6),σ_fin=σ_fin), A_s = (600.38 * 10 ** -6)) ))# 80°C
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("δ_end (-20°C) = ", δ_end(δ_1= δ_1(r(F_=39.677, n=2, m_s=1.659, g=g)), T_k1= 1, T_res=T_res(T(f_es(n= 2, m_s= 1.659, g=g, l=31.0, F_st=19000), g=g), r(F_=39.677, n=2, m_s=1.659, g=g), δ_1(r(F_=39.677, n=2, m_s=1.659, g=g))))) # -20°C
    print("δ_end (80°C) = ", δ_end(δ_1= δ_1(r(F_=39.677, n=2, m_s=1.659, g=g)),T_k1=1 ,T_res=T_res(T(f_es(n= 2, m_s= 1.659, g=g, l=31.0, F_st=7000), g=g), r(F_=F_a(μ0=(4 * math.pi * 1e-7) ,I_k=40000, l=31.0, l_c=l_c(l=31.0, l_i=5.25), a=4), n=2, m_s=1.659, g=g), δ_1(r(F_=39.677, n=2, m_s=1.659, g=g))) )) # 80°C
    # Beispielrechnung gemäss gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("δ_max (-20°C) = ", δ_max(r=r(F_=F_a(μ0=μ0, I_k=40000, l=31.0, l_c=20.5, a=4), n=2, m_s=1.659, g=g), δ_end=δ_end(δ_1=δ_1(r(F_=39.677, n=2, m_s=1.659, g=g)), T_k1=1, T_res=0.682)))  # -20°C
    print("δ_max (80°C) = ", δ_max(r=r(F_=F_a(μ0=μ0, I_k=40000, l=31.0, l_c=20.5, a=4), n=2, m_s=1.659, g=g), δ_end=δ_end(δ_1=δ_1(r(F_=39.677, n=2, m_s=1.659, g=g)), T_k1=1, T_res=1.123)))  # 80°C
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    # print("φ (-20°C) = ", φ(T_k1=1 , T_kres=T_res(T(f_es(n= 2, m_s= 1.659, g=g, l=31.0, F_st=19000), g=g), r(F_=39.677, n=2, m_s=1.659, g=g), δ_1(r(F_=39.677, n=2, m_s=1.659, g=g))), r= r(F_=39.677, n=2, m_s=1.659, g=g), δ_end=δ_end(δ_1= δ_1(r(F_=39.677, n=2, m_s=1.659, g=g)), T_k1= 1, T_kres=T_res(T(f_es(n= 2, m_s= 1.659, g=g, l=31.0, F_st=19000), g=g), r(F_=39.677, n=2, m_s=1.659, g=g), δ_1(r(F_=39.677, n=2, m_s=1.659, g=g)))) )) # -20°C
    # print("φ (80°C) = ", φ(T_k1=1 , T_kres=T_res(T(f_es(n= 2, m_s= 1.659, g=g, l=31.0, F_st=7000), g=g), r(F_=39.677, n=2, m_s=1.659, g=g), δ_1(r(F_=39.677, n=2, m_s=1.659, g=g))), r= r(F_=39.677, n=2, m_s=1.659, g=g), δ_end=δ_end(δ_1= δ_1(r(F_=39.677, n=2, m_s=1.659, g=g)),T_k1=1 ,T_kres=T_res(T(f_es(n= 2, m_s= 1.659, g=g, l=31.0, F_st=7000), g=g), r(F_=F_a(μ0=(4 * math.pi * 1e-7) ,I_k=40000, l=31.0, l_c=l_c(l=31.0, l_i=5.25), a=4), n=2, m_s=1.659, g=g), δ_1(r(F_=39.677, n=2, m_s=1.659, g=g))) ) )) # 80°C
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("φ (-20°C) = ", φ_ohne_schlaufe(T_k1=1, T_res=0.681, r=1.219, δ_end=101.29))  # -20°C
    print("φ (80°C) = ", φ_ohne_schlaufe(T_k1=1, T_res=1.123, r=1.219, δ_end=101.29))  # 80°C
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("ψ (-20°C) = ", ψ_ohne_schlaufe_symbolisch(φ= 1.731, ζ= 0.059)) # -20°C
    print("ψ (80°C) = ", ψ_ohne_schlaufe_symbolisch(φ= 1.731, ζ= 1.064)) # 80°C
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("F_td (-20°C) = ", F_td_ohne_schlaufe_spannfeldmitte(F_st=19000, φ=1.731, ψ=0.134)) # -20°C
    print("F_td (80°C) = ", F_td_ohne_schlaufe_spannfeldmitte(F_st=7000, φ=1.731, ψ=0.563)) # 80°C
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("ε_ela (-20°C) = ", ε_ela(N=1.0453520331567817e-07, F_td=23407.126*1.1 , F_st=19000)) # -20°C
    print("ε_ela (80°C) = ", ε_ela(N=1.1606610962577493e-07, F_td=13821.871*1.1 , F_st=7000)) # 80°C
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("ε_th (-20°C) = ", ε_th(c_th=2.7E-19, I_k__= 40000, n= 2, A_s= 600.38*10**-6, T_k1= 1,T_res=0.682)) # -20°C
    print("ε_th (80°C) = ", ε_th(c_th=2.7E-19, I_k__=40000, n=2, A_s=600.38 * 10 ** -6, T_k1=1, T_res=1.123))  # 80°C
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("C_D (-20°C) = ", C_D(l=31.0 , f_es=0.206, ε_ela=0.0007053866799923814, ε_th=5.108e-05)) # -20°C
    print("C_D (80°C) = ", C_D(l=31.0, f_es=0.558, ε_ela=0.0009522131068108268, ε_th=8.412e-05))  # 80°C
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("C_F (-20°C) = ", C_F(r=1.219)) # -20°C
    print("C_F (80°C) = ", C_F(r=1.219))  # 80°C
    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("f_ed (-20°C) = ", f_ed(C_D=2.72, C_F=1.092, f_es=0.206)) # -20°C
    print("f_ed (80°C) = ", f_ed(C_D=1.842, C_F=1.092, f_es=0.558))  # 80°C

    # Beispielrechnung gemäss Programm IEC 60865 FAU Projekt Riet → Verifiziert
    print("T_pi/Nu2 (-20°C) = ", T_pi_and_ν_2(ν_1=2.764, f=50, τ=τ(f=50, κ=1.8), γ=γ(f=50, τ=τ(f=50, κ=1.8))))
    print("T_pi/Nu2 (80°C) = ", T_pi_and_ν_2(ν_1=2.764, f=50, τ=τ(f=50, κ=1.8), γ=γ(f=50, τ=τ(f=50, κ=1.8))))
    print()


    print("Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.3")
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.3 → Verifiziert
    print("F_a = ", F_a(μ0=μ0, I_k=19000, l=10.4, l_c=10.4, a=2))
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.3 → Verifiziert
    print("r = ", r(F_=F_a(μ0=μ0, I_k=19000, l=10.4, l_c=10.4, a=2), n=1, m_s=0.671, g=g))
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.3 → Verifiziert
    # print("δ_1 = ", δ_1(r(F_=F_a(μ0=μ0, I_k=19000, l=10.4, l_c=10.4, a=2), n=1, m_s=0.671, g=g)))
    print("δ_1 = ", δ_1(r(F_=27.1, n=1, m_s=0.671, g=g)))
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.3 → Verifiziert
    print("f_es (-20°C) = ", f_es(n=1, m_s=0.671, g=g, l=10.4, F_st=350))  # -20°C
    print("f_es (60°C) = ", f_es(n=1, m_s=0.671, g=g, l=10.4, F_st=250))  # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.3 → Verifiziert
    print("T (-20°C) = ", T(f_es(n= 1, m_s=0.671, g=g, l=10.4, F_st=350), g=g)) # -20°C
    print("T (60°C) = ", T(f_es(n= 1, m_s=0.671, g=g, l=10.4, F_st=250), g=g)) # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.3 → Verifiziert
    print("T_res (-20°C) = ", T_res(T(f_es(n=1, m_s=0.671, g=g, l=10.4, F_st=350), g=g), r(F_=F_a(μ0=μ0, I_k=19000, l=10.4, l_c=10.4, a=2), n=1, m_s=0.671, g=g), δ_1(r(F_=F_a(μ0=μ0, I_k=19000, l=10.4, l_c=10.4, a=2), n=1, m_s=0.671, g=g))))  # -20°C
    print("T_res (60°C) = ", T_res(T(f_es(n= 1, m_s=0.671, g=g, l=10.4, F_st=250), g=g), r(F_=F_a(μ0=μ0, I_k=19000, l=10.4, l_c=10.4, a=2), n=1, m_s=0.671, g=g), δ_1(r(F_=F_a(μ0=μ0, I_k=19000, l=10.4, l_c=10.4, a=2), n=1, m_s=0.671, g=g))))  # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.3 → Verifiziert
    print("E_eff (-20°C) = ", E_eff(E=(55000*10**6) , F_st=350, n=1, A_s=(243.38*10**-6) , σ_fin=σ_fin)) # -20°C
    print("E_eff (60°C) = ",  E_eff(E=(55000*10**6) , F_st=250, n=1, A_s=(243.38*10**-6) , σ_fin=σ_fin)) # 80°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.3 → Verifiziert
    print("N (-20°C) = ", N(S=100000, l=10.4, n=1, E_eff=(1.82*10**10), A_s=(243*10**-6))) # -20°C
    print("N (60°C) = ",  N(S=100000, l=10.4, n=1, E_eff=(1.78*10**10), A_s=(243*10**-6))) # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.3 → Verifiziert
    print("ζ (-20°C) = ", ζ(n=1, g=g, m_s=0.671, l=10.4, F_st=350, N = N(S=100000, l=10.4, n=1, E_eff=E_eff(E=(55000*10**6), F_st=350, n=1, A_s=(243*10**-6),σ_fin=σ_fin), A_s = (243*10**-6)))) # -20°C
    print("ζ (60°C) = ",  ζ(n=1, g=g, m_s=0.671, l=10.4, F_st=250, N = N(S=100000, l=10.4, n=1, E_eff=E_eff(E=(55000*10**6), F_st=250, n=1, A_s=(243*10**-6),σ_fin=σ_fin), A_s = (243*10**-6)))) # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.3 → Verifiziert
    print("δ_end (-20°C) = ", δ_end(δ_1=δ_1(r(F_=27.1, n=1, m_s=0.671, g=g)), T_k1= 0.3, T_res=0.494)) # -20°C
    print("δ_end (60°C) = ", δ_end(δ_1=δ_1(r(F_=27.1, n=1, m_s=0.671, g=g)), T_k1=0.3, T_res=0.585)) # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.3 → Verifiziert
    print("δ_max (-20°C) = ", δ_max(r=r(F_=F_a(μ0=μ0, I_k=19000, l=10.4, l_c=10.4, a=2), n=1, m_s=0.671, g=g) ,δ_end=δ_end(δ_1=δ_1(r(F_=27.1, n=1, m_s=0.671, g=g)), T_k1= 0.3, T_res=0.494))) # -20°C
    print("δ_max (60°C) = ", δ_max(r=r(F_=F_a(μ0=μ0, I_k=19000, l=10.4, l_c=10.4, a=2), n=1, m_s=0.671, g=g), δ_end=δ_end(δ_1=δ_1(r(F_=27.1, n=1, m_s=0.671, g=g)), T_k1= 0.3, T_res=0.585))) # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.4 → Verifiziert
    print("φ (-20°C) = ", φ_ohne_schlaufe(T_k1=0.3, T_res=0.494, r=4.12, δ_end=153))  # -20°C
    print("φ (60°C) = ", φ_ohne_schlaufe(T_k1=0.3, T_res=0.585, r=4.12, δ_end=153))  # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.4 → Verifiziert
    print("ψ (-20°C) = ", ψ_ohne_schlaufe_symbolisch(φ= 9.72, ζ= 3.84)) # -20°C
    print("ψ (60°C) = ", ψ_ohne_schlaufe_symbolisch(φ= 9.72, ζ= 10.5)) # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.4 → Verifiziert
    print("F_td (-20°C) = ", F_td_ohne_schlaufe_spannfeldmitte(F_st=350, φ=9.72, ψ=0.594)) # -20°C
    print("F_td (60°C) = ", F_td_ohne_schlaufe_spannfeldmitte(F_st=250, φ=9.72, ψ=0.745)) # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.5 → Verifiziert
    print("ε_ela (-20°C) = ", ε_ela(N=1.18764979876091e-06, F_td=2370.788 , F_st=350)) # -20°C
    print("ε_ela (60°C) = ", ε_ela(N=1.1927309524063582e-06, F_td=2060.35 , F_st=250)) # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.5 → Verifiziert
    print("ε_th (-20°C) = ", ε_th(c_th=2.7E-19, I_k__=19000, n=1, A_s=243*10**-6, T_k1=0.3,T_res=0.494)) # -20°C
    print("ε_th (60°C) = ", ε_th(c_th=2.7E-19, I_k__=19000, n=1, A_s=243*10**-6, T_k1=0.3, T_res=0.585))  # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.5 → Verifiziert
    print("C_D (-20°C) = ", C_D(l=10.4 , f_es=0.254, ε_ela=0.0023999884615384616, ε_th=0.000203856881572931)) # -20°C
    print("C_D (60°C) = ", C_D(l=10.4, f_es=0.356, ε_ela=0.0021592604796888504, ε_th=0.00024140946502057618))  # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.5 → Verifiziert
    print("C_F (-20°C) = ", C_F(r=4.115)) # -20°C
    print("C_F (60°C) = ", C_F(r=4.115))  # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 7.5 → Verifiziert
    print("f_ed (-20°C) = ", f_ed(C_D=1.624, C_F=1.15, f_es=0.254)) # -20°C
    print("f_ed (60°C) = ", f_ed(C_D=1.33, C_F=1.15, f_es=0.356))  # 60°C
    print()


    print("Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.1")
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.1 → Verifiziert
    print("F_a = ", F_a(μ0=μ0, I_k=63000, l=48, l_c=37.4, a=5))
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.1  → Verifiziert
    print("r = ", r(F_=F_a(μ0=μ0, I_k=63000, l=48, l_c=37.4, a=5), n=2, m_s=4.24, g=g))
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.1 → Verifiziert
    # print("δ_1 = ", δ_1(r(F_=F_a(μ0=μ0, I_k=63000, l=48, l_c=37.4, a=5), n=2, m_s=4.241, g=g)))
    print("δ_1 = ", δ_1(r(F_=92.8, n=2, m_s=4.24, g=g)))
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.1 → Verifiziert
    print("f_es (-20°C) = ", f_es(n=2, m_s=4.24, g=g, l=48, F_st=17800))  # -20°C
    print("f_es (60°C) = ", f_es(n=2, m_s=4.24, g=g, l=48, F_st=15400))  # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.1 → Verifiziert
    print("T (-20°C) = ", T(f_es(n= 2, m_s=4.24, g=g, l=48, F_st=17800), g=g)) # -20°C
    print("T (60°C) = ", T(f_es(n= 2, m_s=4.24, g=g, l=48, F_st=15400), g=g)) # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.1 → Verifiziert
    print("T_res (-20°C) = ", T_res(T(f_es(n=2, m_s=4.24, g=g, l=48, F_st=17800), g=g), r(F_=F_a(μ0=μ0, I_k=63000, l=48, l_c=37.4, a=5), n=2, m_s=4.24, g=g), δ_1(r(F_=F_a(μ0=μ0, I_k=63000, l=48, l_c=37.4, a=5), n=2, m_s=4.24, g=g))))  # -20°C
    print("T_res (60°C) = ", T_res(T(f_es(n=2, m_s=4.24, g=g, l=48, F_st=15400), g=g), r(F_=F_a(μ0=μ0, I_k=63000, l=48, l_c=37.4, a=5), n=2, m_s=4.24, g=g), δ_1(r(F_=F_a(μ0=μ0, I_k=63000, l=48, l_c=37.4, a=5), n=2, m_s=4.24, g=g))))  # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.1 → Verifiziert
    print("E_eff (-20°C) = ", E_eff(E=(60000*10**6) , F_st=17800, n=2, A_s=(1090*10**-6) , σ_fin=σ_fin)) # -20°C
    print("E_eff (60°C) = ",  E_eff(E=(60000*10**6) , F_st=15400, n=2, A_s=(1090*10**-6) , σ_fin=σ_fin))  # 80°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.1 → Verifiziert
    print("N (-20°C) = ", N(S=500000, l=48, n=2, E_eff=(2.87*10**10), A_s=(1090*10**-6)))  # -20°C
    print("N (60°C) = ",  N(S=500000, l=48,  n=2, E_eff=(2.72*10**10), A_s=(1090*10**-6))) # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.1 → Verifiziert
    print("ζ (-20°C) = ", ζ(n=2, g=g, m_s=4.24, l=48, F_st=17800, N = N(S=500000, l=48, n=2, E_eff=E_eff(E=(60000*10**6), F_st=17800, n=2, A_s=(1090*10**-6),σ_fin=σ_fin), A_s = (1090*10**-6)))) # -20°C
    print("ζ (60°C) = ",  ζ(n=2, g=g, m_s=4.24, l=48, F_st=15400, N = N(S=500000, l=48, n=2, E_eff=E_eff(E=(60000*10**6), F_st=15400, n=2, A_s=(1090*10**-6),σ_fin=σ_fin), A_s = (1090*10**-6)))) # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.1 → Verifiziert
    print("δ_end (-20°C) = ", δ_end(δ_1=δ_1(r(F_=92.8, n=2, m_s=4.24, g=g)), T_k1=0.5, T_res=1.79))  # -20°C
    print("δ_end (60°C) = ", δ_end(δ_1=δ_1(r(F_=92.8, n=2, m_s=4.24, g=g)), T_k1=0.5, T_res=1.91))  # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.1 → Verifiziert
    print("δ_max (-20°C) = ", δ_max(r=r(F_=F_a(μ0=μ0, I_k=63000, l=48, l_c=37.4, a=5), n=2, m_s=4.24, g=g), δ_end=δ_end(δ_1=δ_1(r(F_=92.8, n=2, m_s=4.24, g=g)), T_k1=0.5, T_res=1.79)))  # -20°C
    print("δ_max (60°C) = ", δ_max(r=r(F_=F_a(μ0=μ0, I_k=63000, l=48, l_c=37.4, a=5), n=2, m_s=4.24, g=g), δ_end=δ_end(δ_1=δ_1(r(F_=92.8, n=2, m_s=4.24, g=g)), T_k1=0.5, T_res=1.91)))  # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.2 → Verifiziert
    print("φ (-20°C) = ", φ_ohne_schlaufe(T_k1=0.5, T_res=1.779, r=1.116, δ_end=56.956))  # -20°C
    print("φ (60°C) = ", φ_ohne_schlaufe(T_k1=0.5, T_res=1.913, r=1.116, δ_end=56.956))  # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.2 → Verifiziert
    print("ψ (-20°C) = ", ψ_ohne_schlaufe_symbolisch(φ= 1.5, ζ= 2.04)) # -20°C
    print("ψ (60°C) = ", ψ_ohne_schlaufe_symbolisch(φ= 1.5, ζ= 3.11)) # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.2 → Verifiziert
    print("F_td (-20°C) = ", F_td_ohne_schlaufe_spannfeldmitte(F_st=17800, φ=1.495, ψ=0.69)) # -20°C
    print("F_td (60°C) = ", F_td_ohne_schlaufe_spannfeldmitte(F_st=15400, φ=1.495, ψ=0.759)) # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.3 → Verifiziert
    print("ε_ela (-20°C) = ", ε_ela(N=5.764978849002121e-08, F_td=36161.59 , F_st=17800)) # -20°C
    print("ε_ela (60°C) = ", ε_ela(N=5.8531210649397374e-08, F_td=32874.457 , F_st=15400)) # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.3 → Verifiziert
    print("ε_th (-20°C) = ", ε_th(c_th=2.7E-19, I_k__=63000, n= 2, A_s=1090*10**-6, T_k1=0.5,T_res=1.79)) # -20°C
    print("ε_th (60°C) = ", ε_th(c_th=2.7E-19, I_k__=63000, n=2, A_s=1090*10**-6, T_k1=0.5, T_res=1.91))  # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.3 → Verifiziert
    print("C_D (-20°C) = ", C_D(l=48 , f_es=1.346, ε_ela=0.0010585417798404883, ε_th=0.00010090784130123727)) # -20°C
    print("C_D (60°C) = ", C_D(l=48, f_es=1.555, ε_ela=0.0010228011236508366, ε_th=0.00010767261278511908))  # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.3 → Verifiziert
    print("C_F (-20°C) = ", C_F(r=1.12)) # -20°C
    print("C_F (60°C) = ", C_F(r=1.12))  # 60°C
    # Beispielrechnung gemäss SN EN 60865-2:2017 Kapitel 8.3.3 → Verifiziert
    print("f_ed (-20°C) = ", f_ed(C_D=1.246, C_F=1.082, f_es=1.346)) # -20°C
    print("f_ed (60°C) = ", f_ed(C_D=1.185, C_F=1.082, f_es=1.555))  # 60°C
    print()


if __name__ == "__main__":
    testrechnungen()
    print(ψ_ohne_schlaufe_symbolisch(φ= 3.29, ζ= 0.19))
    print(ψ_ohne_schlaufe_symbolisch(φ= 3.29, ζ= 0.3))

    print(ψ_ohne_schlaufe_symbolisch(φ= 13.86, ζ= 0.0))
    print(ψ_ohne_schlaufe_symbolisch(φ= 13.86, ζ= 0.1))

    print(ψ_ohne_schlaufe_symbolisch(φ= 5.78, ζ= 1.7))
    print(ψ_ohne_schlaufe_symbolisch(φ= 5.78, ζ= 3.9))

    print(ψ_ohne_schlaufe_symbolisch(φ= 1.57, ζ= 1.1))
    print(ψ_ohne_schlaufe_symbolisch(φ= 1.57, ζ= 2.7))



