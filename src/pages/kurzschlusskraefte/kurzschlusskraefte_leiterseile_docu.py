from pathlib import Path
import taipy.gui.builder as tgb

from .root import build_navbar
from ...utils import third_party_integration as third_party

DOC_PATH = Path(__file__).with_name("kurzschlusskraefte_leiterseile_docu.md")
raw_text = DOC_PATH.read_text(encoding="utf-8") if DOC_PATH.exists() else "## Error\nDatei nicht gefunden"

doc_content = third_party.MaTex(raw_text)

def on_user_content(state):
    html_str = f"""<iframe src="https://map.geo.admin.ch/#/embed?lang=de&center=2669512.54,1178174.74&z=2.15&topic=ech&layers=ch.bfe.meteorologische-vereisung,,0.5;ch.bfe.elektrische-anlagen_ueber_36&bgLayer=ch.swisstopo.pixelkarte-farbe&featureInfo=default" style="border: 0;width: 400px;height: 300px;max-width: 100%;max-height: 100%;" allow="geolocation"></iframe>"""
    return html_str.encode("utf-8")

with tgb.Page() as kurzschlusskraefte_leiterseile_docu_page:
    build_navbar()
    tgb.html("br")
    tgb.text(value="Kurzschlussfestigkeit bei Leiterseilen", class_name="h2 pl1")
    tgb.text(value="Nach SN EN 60865-1:2012", class_name="h6 pl1")
    with tgb.layout(columns="1", class_name="p1"):
        with tgb.part(class_name="card doc-card card-inner"):
            tgb.part(class_name="card taipy-text third-party-iframe-taipy-style-doku vh-fit-with-navbar-doku card-inner",
                     content="{doc_content}", height="100%")


