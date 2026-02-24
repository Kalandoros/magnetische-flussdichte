import math
from dataclasses import asdict

def format_number_nice_to_string_for_repr(number: float, threshold_low=0.001, threshold_high=1000) -> str:
    """
    Hilfsfunktion: Formatiert einen einzelnen Zahl anschaulich für die Darstellung

    Args:
        number: Zu formatierende Zahl
        threshold_low: Untere Schwelle für wissenschaftliche Notation
        threshold_high: Obere Schwelle für wissenschaftliche Notation

    Returns:
        Formatierter String
    """
    if number == 0:
        return "0.00"

    abs_number = abs(number)

    # Verwende wissenschaftliche Notation nur für sehr kleine oder grosse Zahlen
    if abs_number < threshold_low or abs_number > threshold_high:
        exponent = int(math.floor(math.log10(abs_number)))
        mantissa = number / (10**exponent)
        # Verwende Unicode-Zeichen für Hochstellung
        exp_str = str(exponent).translate(str.maketrans('0123456789-', '⁰¹²³⁴⁵⁶⁷⁸⁹⁻'))
        return f"{mantissa:.3f}×10{exp_str}"
    else:
        # Normale Formatierung für "vernünftige" Zahl
        return f"{number:.3f}"

def format_numbers_nice_to_str_for_cli(calc_result: dict) -> str:
    """
    Formatiert Ergebnisse in zwei Spalten nebeneinander.
    Wird nur für Programmierzwecke, Debugging und Ausgabe in der CLI verwendet.
    """
    # Hilfsfunktion für intelligente Formatierung
    def format_scientific(number: float, threshold_low=0.001, threshold_high=1000) -> str:
        """
        Formatiert Werte in wissenschaftlicher Notation für sehr kleine/große Werte und
        Normal für Werte zwischen threshold_low und threshold_high
        """
        if number == 0:
            return "0.00"

        abs_number = abs(number)

        # Verwende wissenschaftliche Notation nur für sehr kleine oder große Werte
        if abs_number < threshold_low or abs_number > threshold_high:
            exponent = int(math.floor(math.log10(abs_number)))
            mantissa = number / (10**exponent)
            # Verwende Unicode-Zeichen für Hochstellung
            exp_str = str(exponent).translate(str.maketrans('0123456789-', '⁰¹²³⁴⁵⁶⁷⁸⁹⁻'))
            return f"{mantissa:.3f}×10{exp_str}"
        else:
            # Normale Formatierung für "vernünftige" Werte
            return f"{number:.3f}"

    # Hole beide Ergebnisse
    result_20 = calc_result.get('F_st_20')
    result_80 = calc_result.get('F_st_80')

    if not result_20 or not result_80:
        return "Keine Berechnungsergebnisse verfügbar"

    # Konvertiere zu Dictionaries
    dict_20 = asdict(result_20)
    dict_80 = asdict(result_80)

    # Spaltenbreiten
    col1_width = 25  # Parameter Name
    col2_width = 20  # -20°C Werte
    col3_width = 20  # 80°C Werte

    # Erstellt Header
    lines = []
    lines.append(f"┌─{'─' * col1_width}─┬─{'─' * col2_width}─┬─{'─' * col3_width}─┐")
    lines.append(f"│ {'Parameter':<{col1_width}} │ {'-20°C':^{col2_width}} │ {'80°C':^{col3_width}} │")
    lines.append(f"├─{'─' * col1_width}─┼─{'─' * col2_width}─┼─{'─' * col3_width}─┤")

    # Iteriert durch alle Felder
    for param_name in dict_20.keys():
        val_20 = dict_20[param_name]
        val_80 = dict_80[param_name]

        # Nur nicht-None Werte anzeigen
        if val_20 is not None and val_80 is not None:
            # Formatiere die Werte intelligent
            val_20_str = format_scientific(val_20)
            val_80_str = format_scientific(val_80)
            lines.append(
                f"│ {param_name:<{col1_width}} │ {val_20_str:>{col2_width}} │ {val_80_str:>{col3_width}} │")

    lines.append(f"└─{'─' * col1_width}─┴─{'─' * col2_width}─┴─{'─' * col3_width}─┘")

    return "\n".join(lines)

