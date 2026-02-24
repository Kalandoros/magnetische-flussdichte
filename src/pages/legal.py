import taipy.gui.builder as tgb

from ..utils import third_party_integration as third_party

md_impressum = """
### Kontaktadresse
Angelo Rusvai  
Ellen-Widmann-Weg 2  
8050 Zürich  
Schweiz  

E-Mail: [info(at)uwcalc.ch](mailto:info@uwcalc.ch)

---

### Inhaltlich Verantwortlicher
Angelo Rusvai
"""
content_impressum = third_party.MaTex(md_impressum)

md_datenschutz = """
### 1. Verantwortliche Stelle
Verantwortlich für die Datenbearbeitung auf dieser Website ist: 
 
Angelo Rusvai  
Ellem-Widmann-Weg 2  
8050 Zürich  
Schweiz  

E-Mail: [info(at)uwcalc.ch](mailto:info@uwcalc.ch)

### 2. Allgemeines
Der Schutz Ihrer persönlichen Daten wird sehr ernst genommen. Personenbezogenen Daten werden vertraulich 
und entsprechend der gesetzlichen Datenschutzvorschriften (Schweizer Datenschutzgesetz nDSG sowie EU-DSGVO) behandelt.

### 3. Hosting durch Microsoft Azure
Diese Applikation wird auf Servern von Microsoft Azure gehostet. Der gewählte Serverstandort ist Switzerland North (Zürich, Schweiz).   
Microsoft Azure kann technische Protokolldaten (Logfiles) erfassen, um den Betrieb und die Sicherheit des Systems zu 
gewährleisten. Dazu gehören unter anderem: \n
* IP-Adresse
* Datum und Uhrzeit des Zugriffs
* Browsertyp und Betriebssystem

Weitere Informationen zum Datenschutz bei Microsoft finden Sie hier:  
[Microsoft Privacy Statement](https://privacy.microsoft.com/de-de/privacystatement)

### 4. Verwendung von Google Web Fonts
Zur optisch ansprechenden Darstellung unserer Inhalte wird auf dieser Webseite Google Web Fonts benutzt. Dabei werden 
Schriften von Servern der Google Ireland Limited (bzw. Google LLC, USA) geladen. Hierbei wird Ihre IP-Adresse an 
Google übertragen. 

Die Nutzung erfolgt im Interesse einer einheitlichen Darstellung der Inhalte und einer verbesserten Benutzererfahrung 
(berechtigtes Interesse gem. Art. 6 Abs. 1 lit. f DSGVO bzw. entsprechende Bestimmungen des Schweizer nDSG).

Weitere Informationen zu Google Web Fonts finden Sie unter:  
[Google Fonts FAQ](https://developers.google.com/fonts/faq) | [Google Datenschutzerklärung](https://www.google.com/policies/privacy/)

### 5. Verwendung von MathJax (via Cloudflare)
Für die Darstellung mathematischer Formeln wird die Bibliothek MathJax benutzt, welche über das Content Delivery Network (CDN) 
von Cloudflare (Cloudflare Inc., USA) bezogen wird. Hierbei kann es zur Übertragung von Verbindungsdaten an Server in Drittstaaten kommen.

### 6. Eingabe von Berechnungsdaten und Ergebnisse
Die Daten, die Sie in die Berechnungsmaske eingeben, werden zur Durchführung der Berechnung an den Server übermittelt 
und verarbeitet. Diese Eingabedaten und Ergebnisse werden nach Abschluss der Berechnung nicht dauerhaft gespeichert 
und nicht an Dritte weitergegeben.

### 7. Cookies
Diese Website verwendet keine Tracking-Cookies, sondern lediglich technisch notwendige Cookies, die für den Betrieb 
der Applikation erforderlich sind.

Folgende Cookies werden gesetzt: \n
* Taipy Session: Speichert eine anonyme ID, um Ihre Eingaben während der Berechnung zuzuordnen (Dauer: Ende der Browser-Sitzung).  
* Technisches Framework: Gegebenenfalls werden Sicherheits-Cookies (z.B. CSRF-Schutz) gesetzt.

Da diese Cookies für die Grundfunktion der Webseite unerlässlich sind, können sie nicht deaktiviert werden. Es werden 
keine Marketing- oder Analyse-Cookies von Drittanbietern verwendet.

### 8. Ihre Rechte
Sie haben das Recht, jederzeit Auskunft über Ihre bei uns gespeicherten personenbezogenen Daten zu erhalten sowie deren 
Berichtigung oder Löschung zu verlangen, sofern keine gesetzlichen Aufbewahrungspflichten entgegenstehen.
"""
content_datenschutz = third_party.MaTex(md_datenschutz)

md_nutzungsbedingungen = """
### 1. Urheberrecht
Die auf dieser Website bereitgestellte Applikation und die zugrundeliegende Software sind urheberrechtlich geschützt. 
Eigentümer ist Angelo Rusvai. Der Quellcode ist nicht öffentlich. Jegliches Reverse Engineering, Dekompilieren oder die 
automatisierte Abfrage der Applikation (Scraping) ist untersagt.

### 2. Nutzung
Die Nutzung der Applikation auf [https://uwcalc.ch/](https://uwcalc.ch/) ist kostenlos und frei zugänglich (Open Access). 
Es wird das Recht vorbehalten, den Dienst jederzeit einzustellen, einzuschränken oder kostenpflichtig zu gestalten.

### 3. Haftungsausschluss
Die Berechnungen dieser Applikation erfolgen automatisiert und basieren auf den vom Nutzer eingegebenen Daten. 
Trotz sorgfältiger Programmierung und Prüfung können Softwarefehler, Übertragungsfehler oder methodische Ungenauigkeiten 
nicht vollständig ausgeschlossen werden. Die Nutzung erfolgt auf eigene Gefahr. Der Betreiber übernimmt keinerlei Gewähr 
für die Richtigkeit, Vollständigkeit, Aktualität oder Zuverlässigkeit der berechneten Ergebnisse oder der Dokumentationen. 
Für direkte oder indirekte Schäden (z.B. Personenschaden, Sachschaden, Planungsfehler, Materialschäden, Betriebsausfälle, 
Ertragsausfälle, usw.), die aus der Nutzung dieser Applikation entstehen, wird jegliche Haftung abgelehnt, soweit dies 
gesetzlich zulässig ist (Art. 100 OR). Die Nutzung dieses Berechnungstools erfolgt auf eigenes Risiko.

### 4. Prüfpflicht
Die Ergebnisse und die Dokumentationen dienen zur Information und Orientierung und ersetzen keine fachmännische Prüfung 
durch qualifiziertes Personal (z.B. Ingenieure) anhand der geltenden Gesetze, Verordnungen, Normen, Weisungen, Richtlinien, 
usw. und müssen verifiziert werden, bevor sie allenfalls in der Praxis Anwendung finden oder technisch umgesetzt werden.

### 5. Urheberrecht
Der Quellcode der Applikation ist urheberrechtlich geschützt und nicht öffentlich zugänglich.

### 6. Haftung für externe Links
Die Applikation kann Verweise auf Webseiten Dritter enthalten. Diese liegen ausserhalb des Verantwortungsbereichs. 
Es wird jegliche Verantwortung für den Inhalt, die Rechtmässigkeit oder die Funktionalität solcher Webseiten abgelehnt. 
Der Zugriff erfolgt auf eigene Gefahr des Nutzers.
"""
content_nutzungsbedingungen = third_party.MaTex(md_nutzungsbedingungen)

md_credits = """
Ohne die Arbeit von Open-Source-Projekten wäre dieses Projekt nicht möglich. \n
Es werden die folgenden Bibliotheken und Frameworks genutzt:

### Web-Framework
* [Taipy](https://www.taipy.io/): (Apache License 2.0) – Die grafische Benutzeroberfläche dieser Applikation.

### Mathematische Berechnung & Datenverarbeitung
* [NumPy](https://numpy.org/): (BSD License) – Wissenschaftliches Rechnen.
* [SciPy](https://scipy.org/): (BSD License) – Algorithmen für Mathematik und Technik.
* [SymPy](https://www.sympy.org/): (BSD License) – Symbolische Mathematik.
* [Pandas](https://pandas.pydata.org/): (BSD License) – Datenanalyse und -manipulation.
* [openpyxl](https://openpyxl.readthedocs.io/): (MIT License) – Lesen/Schreiben von Excel-Dateien.

### Darstellung & Formatierung
* [MathJax](https://www.mathjax.org/): (Apache License 2.0) – Rendering mathematischer Formeln.
* [markdown2](https://github.com/trentm/python-markdown2): (MIT License) – Textformatierung.
* [latex2mathml](https://github.com/ronallo/latex2mathml): (MIT License) – Konvertierung von LaTeX zu MathML.
* [Google Fonts (Lato)](https://fonts.google.com/specimen/Lato): (SIL Open Font License) – Schriftart.
* [Material UI / Material Design](https://mui.com/): (MIT License) – Das zugrundeliegende Design-System für die Benutzeroberfläche.

---

Die vollständigen Lizenztexte (Apache 2.0, MIT, BSD) können auf den Webseiten der jeweiligen Projekte eingesehen werden.
"""
content_credits = third_party.MaTex(md_credits)

def on_user_content(state) -> bytes:
    html_str = f"""<iframe src="https://map.geo.admin.ch/#/embed?lang=de&center=2669512.54,1178174.74&z=2.15&topic=ech&layers=ch.bfe.meteorologische-vereisung,,0.5;ch.bfe.elektrische-anlagen_ueber_36&bgLayer=ch.swisstopo.pixelkarte-farbe&featureInfo=default" style="border: 0;width: 400px;height: 300px;max-width: 100%;max-height: 100%;" allow="geolocation"></iframe>"""
    return html_str.encode("utf-8")

with tgb.Page() as impressum_page:
    tgb.html("br")
    tgb.text(value="Impressum", class_name="h1")
    with tgb.layout(columns="1", class_name="p1"):
        with tgb.part(class_name="card doc-card card-inner"):
            tgb.part(class_name="card taipy-text third-party-iframe-taipy-style-doku vh-fit-with-navbar-doku",
                     content="{content_impressum}", height="100%")

with tgb.Page() as datenschutz_page:
    tgb.html("br")
    tgb.text(value="Datenschutzerklärung", class_name="h1")
    with tgb.layout(columns="1", class_name="p1"):
        with tgb.part(class_name="card doc-card card-inner"):
            tgb.part(class_name="card taipy-text third-party-iframe-taipy-style-doku vh-fit-with-navbar-doku",
                     content="{content_datenschutz}", height="100%")

with tgb.Page() as nutzungsbedingungen_page:
    tgb.html("br")
    tgb.text(value="Nutzungsbedingungen & Haftungsausschluss", class_name="h1")
    with tgb.layout(columns="1", class_name="p1"):
        with tgb.part(class_name="card doc-card card-inner"):
            tgb.part(class_name="card taipy-text third-party-iframe-taipy-style-doku vh-fit-with-navbar-doku",
                     content="{content_nutzungsbedingungen}", height="100%")

with tgb.Page() as credits_page:
    tgb.html("br")
    tgb.text(value="Credits & Lizenzen", class_name="h1")
    with tgb.layout(columns="1", class_name="p1"):
        with tgb.part(class_name="card doc-card card-inner"):
            tgb.part(class_name="card taipy-text third-party-iframe-taipy-style-doku vh-fit-with-navbar-doku",
                     content="{content_credits}", height="100%")





