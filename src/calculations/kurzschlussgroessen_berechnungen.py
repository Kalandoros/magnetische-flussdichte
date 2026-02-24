import math
from decimal import Decimal, getcontext

# Die Funktion getcontext() kommt vom Modul Decimal und sollte die Problematik der Berechnung
# des Faktor n beim thermisch_gleichwertiger_kurzschlussstrom lösen.
# Wenn nicht weiter gebraucht, kann dies später gelöscht werden.
print(getcontext())
c = getcontext().prec = 8
#c.traps[FloatOperation] = True

def κ_faktor(r_x: float) -> float:
    """
    Funktion zur Berechnung κ-Faktors zur Berechnung des Stosskurzschlussstromes (dimensionslos) nach SN EN 60909-0.
    r_x: Verhältnis R/X (dimensionslos)
    Erläuterung zu κ: Der κ-Faktor liegt zwischen 1 und 2.
    Die Berechnung des Wertes κ erfolgt nach dem kleinsten Verhältnis R/X im Netz, wobei die Impedanzen einer
    zusammengefasst werden können. Es müssen nur die Netzzweige berücksichtigt werden, die vom Kurzschlussstrom
    durchflossen werden. Dieses Verfahren führt zu κ-Werten, die auf der sicheren Seite liegen.
    (SN EN 60909-0 S. 49 und VDE Kurzschlussstromberechnung S. 229)
    """
    κ: float = 1.02 + 0.98 * math.exp(-3 * r_x)
    return κ


def κ_faktor_alternativ(ip: float, ik__: float) -> float:
    """
    Funktion zur Berechnung κ-Faktors zur alternativen Berechnung des Stosskurzschlussstromes (dimensionslos) nach
    Umstellung der Formel des Stosskurzschlussstromes gemäss SN EN 60909-0 oder VDE Kurzschlussstromberechnung S. 269
    ip: Stosskurzschlussstrom (Augenblickswert) in A
    i_k__: dreipoliger oder zweipoliger Anfangs-Kurzschlusswechselstrom (Effektivwert) in A
    Erläuterung zu κ: Der κ-Faktor liegt zwischen 1 und 2. (VDE Kurzschlussstromberechnung S. 20)
    """
    κ: float = ip / (math.sqrt(2) * ik__)
    return κ


def stosskurzschlussstrom(ik__: float, κ: float = 2.0) -> float:
    """
    Funktion zur Berechnung des Stosskurzschlussstromes ip in A nach SN EN 60909-0.
    i_k__: dreipoliger oder zweipoliger Anfangs-Kurzschlusswechselstrom (Effektivwert) in A
    κ: Faktor zur Berechnung des Stosskurzschlussstromes (dimensionslos)
    Erläuterung zu κ: In Niederspannungsnetzen darf das Produkt 1,15 κ auf 1,8 und in Hochspannungsnetzen auf 2,0
    begrenzt werden. (SN EN 60909-0 Kapitel 8.1.1 und VDE Kurzschlussstromberechnung S. 230)
    Daher wird κ = 2.0 als Standardwert verwendet, falls kein κ angegeben wird.
    """
    i_p: float = κ * math.sqrt(2) * ik__
    return i_p


def faktor_m(tk: float, f: float = 50.0, κ: float = 1.95) -> float:
    """
    Faktor für den Wärmeeffekt des Gleichstromanteils m (dimensionslos) nach SN EN 60909-0
    ik__: dreipoliger Anfangs-Kurzschlusswechselstrom (Effektivwert) in A
    f: Frequenz (50 Hz oder 60 Hz) in Hz
    tk: Dauer des Kurzschlussstromes in s
    κ: Faktor zur Berechnung des Stosskurzschlussstromes (dimensionslos)
    Erläuterung zu f: Daher wird f = 50.0 als Standardwert verwendet, falls kein f angegeben wird.
    Erläuterung zu κ: In Niederspannungsnetzen darf das Produkt 1,15 κ auf 1,8 und in Hochspannungsnetzen auf 2,0
    begrenzt werden. (SN EN 60909-0 Kapitel 8.1.1)
    Da κ = 2.0 zu unrealistisch hohen Gleichstromanteilen führt, wird κ = 1.95 als Standardwert verwendet,
    falls kein κ angegeben wird. (SN EN 60909-0 Kapitel 8.1.1 Bild 18)
    """
    m: float = (1 / (2 * f * tk * math.log(κ - 1))) * ((math.exp(4 * f * tk * math.log(κ - 1))) - 1)
    return m


def faktor_n(ik__: float, ik: float, tk: float) -> float:
    # TODO: Berechnung des Faktors n bringt nicht die korrekten Werte gemäss Diagramm. Formeln stimmen und wurde
    #       wurden mehrfach geprüft. Es kommen stets zu kleine Werte heraus.
    """
    Faktor für den Wärmeeffekt des Wechselstromanteils n (dimensionslos) nach SN EN 60909-0
    ik__: dreipoliger Anfangs-Kurzschlusswechselstrom (Effektivwert) in A
    ik: Dauerkurzschlussstrom (Effektivwert) in A
    tk: Dauer des Kurzschlussstromes in s

    i_k: dreipoliger Anfangs-Kurzschlusswechselstrom (Effektivwert) in A
    Erläuterung zu ik__: Für die Berechnung des Joule-Integrals oder des thermisch gleichwertigen Kurzschlussstroms in
    Drehstromnetzen ist normalerweise der dreipolige Kurzschluss massgebend (SN EN 60909-0 Kapitel 14).
    """
    ik__ = Decimal(ik__)
    ik = Decimal(ik)
    tk = Decimal(tk)

    ik_ik = Decimal(Decimal((ik__ / ik) / (Decimal(0.88) + ((Decimal(0.17)) * Decimal((ik__ / ik))))))
    # print(f'ik_ik:{ik_ik}')
    td_ = Decimal((Decimal(3.1) / Decimal(ik_ik)))
    # print(f'td_:{td_}')

    # Aufgrund der Länge der Gleichung für n wird diese zur besseren Übersichtlichkeit in Zwischenterme aufgeteilt.
    grundwert: Decimal = Decimal((1 / ((ik__ / ik) ** 2)))
    # print(f'Grundwert:{grundwert}')

    n_zwischenterm_1: Decimal = Decimal(((td_ / (20 * tk)) * Decimal((1 - (math.exp(-20 * (tk / td_)))))) * (((ik__ / ik) - ik_ik) ** 2))
    # print(f'Zwischenterm1:{n_zwischenterm_1}')

    n_zwischenterm_2: Decimal = Decimal(((td_ / (2 * tk)) * Decimal((1 - (math.exp(-2 * (tk / td_)))))) * ((ik_ik - 1) ** 2))
    # print(f'Zwischenterm2:{n_zwischenterm_2}')
    # print(f'Zwischenterm12:{n_zwischenterm_1 + n_zwischenterm_2}')

    n_zwischenterm_3: Decimal = Decimal(((td_ / (5 * tk)) * Decimal((1 - (math.exp(-10 * (tk / td_)))))) * ((ik__ / ik) - ik_ik))
    # print(f'Zwischenterm3:{n_zwischenterm_3}')
    # print(f'Zwischenterm123:{n_zwischenterm_1 + n_zwischenterm_2 + n_zwischenterm_3}')

    n_zwischenterm_4: Decimal = Decimal((((2 * td_) / tk) * Decimal((1 - (math.exp(-1 * (tk / td_)))))) * ((ik_ik - 1)))
    # print(f'Zwischenterm4:{n_zwischenterm_4}')
    # print(f'Zwischenterm1234:{n_zwischenterm_1 + n_zwischenterm_2 + n_zwischenterm_3 + n_zwischenterm_4})')

    n_zwischenterm_5: Decimal = Decimal((td_ / (Decimal(5.5) * tk)) * Decimal((1 - (math.exp(-11 * (tk / td_))))) * ((ik__ / ik) - ik_ik) * (ik_ik - 1))
    # print(f'Zwischenterm5:{n_zwischenterm_5}')
    # print(f'Zwischenterm12345:{n_zwischenterm_1 + n_zwischenterm_2 + n_zwischenterm_3 + n_zwischenterm_4 + n_zwischenterm_5})')
    # print(f'Term:{(Decimal(1) + n_zwischenterm_1 + n_zwischenterm_2 + n_zwischenterm_3 + n_zwischenterm_4 + n_zwischenterm_5)}')
    n: Decimal = Decimal(grundwert * (Decimal(1) + n_zwischenterm_1 + n_zwischenterm_2 + n_zwischenterm_3 + n_zwischenterm_4 + n_zwischenterm_5))

    """
    In Ermangelung einer Lösung zur Beseitigung der Abweichungen zwischen den hier berechneten Werten und den 
    Werten im Graph der Norm wird nach Oeding, Oswald Elektrische Kraftwerke und Netze Kapitel 15.5 Seite 651 wird n = 1
    in jedem Falle auf der sicheren Seite liegt. 
    Hinweis: Der Zwischenterm 2 gemäss der Norm SN EN 60865-2 Anhang A zur Berechnung von n ist nicht korrekt. 
    Im Zwischenterm 2 wird "(ik_ik - 1)" nicht quadriert.
    """
    # n: float = 1
    return n


def thermisch_gleichwertiger_kurzschlussstrom(ik__: float, m: float = 1.0, n: float = 1.0) -> float:
    """
    Funktion zur Berechnung des thermisch gleichwertigen kurzschlussstromes nach SN EN 60909-0
    Erläuterung zu m und n: Für generatorferne Kurzschlüsse mit der Bemessungs-Kurzschlussdauer von 0,5 s oder mehr ist
    es zulässig, m + n = 1 zu setzen (SN EN 60909-0 Kapitel 14).
    Erläuterung zu n: Für Verteilungsnetze (generatorferne Kurzschlüsse) kann üblicherweise n = 1 verwendet werden
    (SN EN 60909-0 Kapitel 14).
    Erläuterung zu n: In vermaschten Netzen wird auch bei generatornahem Kurzschluss Ikmax = I″kmaxM gesetzt und damit
    dann I″k/Ik = 1 und n = 1. Auf diese Weise erhält man Ergebnisse für Ith/I″k, die in jedem Falle auf der sicheren
    Seite liegen. (Oeding, Oswald Elektrische Kraftwerke und Netze Kapitel 15.5 Seite 651).
    """
    i_th = ik__ * math.sqrt((m + n))
    return i_th


def testrechnungen() -> None:
    # Noch zu verifizieren
    # Beispielrechnung gemäss VDE Kurzschlussstromberechnung S. 233 → Verifiziert
    print("i_p = ", stosskurzschlussstrom(ik__=14.56, κ=1.746))
    print("i_p = ", stosskurzschlussstrom(ik__=14.56, κ=κ_faktor(0.1)))
    # Beispielrechnung gemäss Siemens - Planungsleitfaden für Energieverteilungsanlagen S.56 → Verifiziert
    print("i_p = ", (stosskurzschlussstrom(ik__=33.5)))

    # Beispielrechnung gemäss SN EN 60909 - 0 Kapitel 8.1 Bild 12 → Verifiziert
    print("κ =", κ_faktor(0.6))
    # Beispielrechnung gemäss VDE Kurzschlussstromberechnung S. 269 → Verifiziert
    print("κ =", κ_faktor_alternativ(ip=55.0, ik__=23.0))

    # Beispielrechnung gemäss SN EN 60909 - 0 Kapitel 8.1.1 Bild 18 → Verifiziert
    print("m =", faktor_m(tk=0.3, f=50.0, κ=1.95))
    # Beispielrechnung gemäss Siemens - Planungsleitfaden für Energieverteilungsanlagen S.59 → Verifiziert
    print("m =", faktor_m(tk=0.5, f=50.0, κ=1.8))
    # Beispielrechnung gemäss SN EN 60865 - 2 Kapitel 11.3 → Verifiziert
    print("m =", faktor_m(tk=0.8, f=50.0, κ=1.8))
    # Beispielrechnung gemäss VDE Kurzschlussstromberechnung S. 255 → Verifiziert
    print("m =", faktor_m(tk=0.5, f=50.0, κ=1.8))
    # Beispielrechnung gemäss Schutz bei Kurzschluss in elektrischen Anlagen - Kay → Verifiziert
    print("m =", faktor_m(tk=0.1, f=50.0, κ=1.8))

    # Beispielrechnung gemäss SN EN 60865-2 Kapitel 11.3 → Verifiziert
    print("n =", faktor_n(ik__=24, ik=19.2, tk=0.8))
    # Beispielrechnung gemäss VDE Kurzschlussstromberechnung S. 255 → Verifiziert
    print("n =", faktor_n(ik__=50, ik=25, tk=0.5))
    # Beispielrechnung gemäss Schutz bei Kurzschluss in elektrischen Anlagen - Kay → Verifiziert
    print("n =", faktor_n(ik__=14.94, ik=3.81, tk=0.1))


    # Beispielrechnung gemäss SN EN 60909 - 2 Kapitel 11.3 → Verifiziert
    print("Ith =", thermisch_gleichwertiger_kurzschlussstrom(ik__=24.0, m=0.056, n=0.86))
    # Beispielrechnung gemäss AEG Rechengrössen für Hochspannungsanlagen S. 101 → Verifiziert
    print("Ith =", thermisch_gleichwertiger_kurzschlussstrom(ik__=25.0, m=0.16, n=0.94))


if __name__ == "__main__":
    testrechnungen()
