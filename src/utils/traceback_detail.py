import traceback
from collections.abc import Sequence

# Dateiliste für Error-Handling
RELEVANT_FILES = ["kurzschlusskraefte_leiterseile_berechnungen.py", "kurzschlusskraefte_leiterseile_engine.py",
                  "kurzschlussgroessen_berechnungen.py", "betriebsmittel.py",]

# Sonderformat für einzelne Dateien
SPECIAL_FORMAT_FILES = {"kurzschlusskraefte_leiterseile_engine.py"}

def get_error_location(tb: Sequence[traceback.FrameSummary]) -> str:
    """
    Hilfsfunktion und Backup für get_detailed_error_location extrahiert Funktionsname und Zeilennummer aus
    Traceback für die Fehlersuche in den Berechnungsmodulen.

    Args:
       tb: Traceback-Objekt der Exception

    Returns:
       str: Fehlerposition im Format " in Funktion 'name' (Zeile XX)" oder ""
    """
    error_location = ""
    # Dateiliste mit get_detailed_error_location teilen
    for frame in tb:
        # Prüfe die Frames in der gegebenen Reihenfolge
        if any(file in frame.filename for file in RELEVANT_FILES):
            if any(file in frame.filename for file in SPECIAL_FORMAT_FILES):
                error_location = f" in '{frame.name}' (Zeile {frame.lineno})"
            else:
                error_location = f" in Funktion '{frame.name}' (Zeile {frame.lineno})"
            break
    return error_location

def get_detailed_error_location(tb: Sequence[traceback.FrameSummary], max_frames: int = 10) -> str:
    """
    Hilfsfunktion erstellt vollständige Call-Chain aus Traceback für die Fehlersuche in den Berechnungsmodulen.

    Args:
        tb: Traceback-Objekt
        max_frames: Maximale Anzahl anzuzeigender Frames

    Returns:
        str: Call-Chain im Format "datei::funktion() → datei::funktion()
    """
    error_locations: list[str] = []

    # Sammle alle relevanten Frames
    for frame in tb:
        # Prüfe, ob Frame aus einem der Calculation-Module kommt
        if any(file in frame.filename for file in RELEVANT_FILES):
            file_name = frame.filename.split("\\")[-1]  # Nur Dateiname, nicht kompletter Pfad
            error_locations.append(f"{file_name}::{frame.name}() Zeile {frame.lineno}")

    # Begrenze auf max_frames
    if error_locations:
        if len(error_locations) > max_frames:
            error_locations = error_locations[-max_frames:]  # Nur die letzten N Frames

        # Formatiere als Chain
        chain = " → ".join(error_locations)
        return f"\n📍 {chain}"

    return ""

def get_exception_message(exception: BaseException, show_chain: bool = True) -> str:
    """
    Erstellt vollständige Call-Chain aus Traceback für die Fehlersuche in den Berechnungsmodulen.

    Args:
        exception: Traceback-Objekt
        show_chain: Maximale Anzahl anzuzeigender Frames

    Returns:
        str: Call-Chain im Format "datei::funktion() → datei::funktion()
    """
    tb = traceback.extract_tb(exception.__traceback__)

    if show_chain:
        location = get_detailed_error_location(tb)
    else:
        location = get_error_location(tb)

    error_type = type(exception).__name__
    error_msg = str(exception)

    return f"❌ {error_type}{location}\n💬 {error_msg}"
