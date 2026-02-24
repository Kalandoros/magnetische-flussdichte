from datetime import datetime
import taipy.gui.builder as tgb
from taipy.gui import navigate

from src.utils import dataloader

def on_menu_action(state, id, payload):
    # payload['args'][0] enthält in der Regel die ausgewählte Element-ID für tgb.menu
    page_id = payload.get("args", [None])[0]
    if page_id:
        navigate(state, to=page_id)

menu_lov = [("Willkommen", "Willkommen"),
            ("Kurzschlusskraefte", "Kurzschlusskraefte"),]

app_version = dataloader.get_app_version()

show_disclaimer = True

def accept_disclaimer(state):
    state.show_disclaimer = False

with tgb.Page() as root_page:
    tgb.content()
    with tgb.dialog(open="{show_disclaimer}", title="Haftungsausschluss / Disclaimer / Cookies", on_action=accept_disclaimer, class_name="dialog-inner"):
        tgb.text(value="#### Wichtiger Hinweis", mode="md", class_name="mt1 mb1")
        tgb.text(value="Trotz sorgfältiger Programmierung und Tests dienen die Ergebnisse nur zur Information und Orientierung.", mode="md")
        tgb.text(value="**[Keine Haftung](/Nutzungsbedingungen):** Soweit gesetzlich zulässig (Art. 100 OR), wird jede Haftung für direkte "
                       "oder indirekte Schäden aus der Verwendung dieser Applikation ausgeschlossen.", mode="md")
        tgb.text(value="**[Prüfpflicht](/Nutzungsbedingungen):** Die Ergebnisse müssen durch qualifiziertes Fachpersonal vor der "
                       "technischen Umsetzung verifiziert werden.", mode="md")
        tgb.text(value="**[Cookies](/Datenschutz):** Um den Betrieb und die Sicherheit dieser Applikation zu gewährleisten, "
                       "werden ausschliesslich technisch notwendige Cookies (Session-Management) genutzt. "
                       "Es werden keine Marketing- oder Tracking-Tools verwendet.", mode="md")
        tgb.html("br")
        tgb.button(label="Verstanden & akzeptiert", on_action=accept_disclaimer, class_name="fullwidth button-color-accent")
    with tgb.part(class_name="center-watermark"):
        tgb.text(value=f"© {datetime.now().year} [uwcalc.ch](Willkommen) | [Impressum](Impressum) | [Datenschutz](Datenschutz) | [Nutzungsbedingungen](Nutzungsbedingungen) | [Credits](Credits)", mode="md")
    with tgb.part(class_name="version-watermark"):
        tgb.text(f"Version {app_version}")
    tgb.toggle(theme=True, class_name="theme-toggle")
    tgb.menu(label="Menu", lov=menu_lov, on_action=on_menu_action)



