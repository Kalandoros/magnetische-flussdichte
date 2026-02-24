from taipy.gui import Gui
import taipy.gui.builder as tgb

from src.pages import (root_page, impressum_page, datenschutz_page, nutzungsbedingungen_page, credits_page,
                       kurzschlusskraefte_leiterseile_calc_page, kurzschlusskraefte_leiterseile_docu_page, on_menu_action)
from src.utils import third_party_integration as third_party

# Importiere das komplette Modul, damit Taipy die Variablen findet
from src.pages.kurzschlusskraefte import content_vorlage

with tgb.Page() as home_page:
    tgb.text(value="# Willkommen bei UWClac", mode="md", class_name="h1 pl1")
    tgb.image(content="src/assets/Icon.jpg", width="20%", class_name="pl1")

pages = {
    "/": root_page,
    "Willkommen": home_page,
    "Kurzschlusskraefte": kurzschlusskraefte_leiterseile_calc_page,
    "Applikation": kurzschlusskraefte_leiterseile_calc_page,
    "Dokumentation": kurzschlusskraefte_leiterseile_docu_page,
    "Impressum": impressum_page,
    "Datenschutz": datenschutz_page,
    "Nutzungsbedingungen": nutzungsbedingungen_page,
    "Credits": credits_page,
}

if __name__ == "__main__":
    gui = Gui(pages=pages, css_file="src/css/main.css")
    gui.register_content_provider(third_party.MaTex, third_party.render_matex)
    gui.run(initial_page="Willkommen", #use_reloader=True,
            title="Kurzschlussfestigkeit", favicon="src/assets/Icon.jpg", watermark="",
            margin="1em", dark_mode=False, debug=True, port="auto")
