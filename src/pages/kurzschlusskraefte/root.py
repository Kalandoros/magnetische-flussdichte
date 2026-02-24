import taipy.gui.builder as tgb

navbar_lov = [
    ("/Applikation", "Kurzschlussfestigkeit bei Leiterseilen"),
    #("/Dokumentation", "Dokumentation"),
]

def build_navbar() -> None:
    tgb.toggle(theme=True, class_name="h1 text-center theme-toggle")
    tgb.navbar(lov=navbar_lov)

with tgb.Page() as kurzschlusskraefte_root_page:
    build_navbar()
    tgb.content()
