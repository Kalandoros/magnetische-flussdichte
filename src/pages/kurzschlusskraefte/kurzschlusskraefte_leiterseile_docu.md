# Funktionen der Applikation

## Dokumentation als separate Seite

Sollte das Seitenfenster zu klein sein, kann die Dokumentation als separate Seite im Vollformat angezeigt werden.
Folgend ist der Link für die Dokumentation in Vollformat bereitgestellt:

* [Dokumentation in Vollformat](/Dokumentation)

## Integrierte Funktionen:

![Übersicht_Berechnungsfälle.png](/src/assets/kurzschlusskraefte_leiterseile/%C3%9Cbersicht_Berechnungsf%C3%A4lle.png)

* [x] A - Berechnung der Seilzugkräfte im Kurzschlussfall für horizontal abgespannte Leiterseile
* [x] C - Berechnung der Seilzugkräfte im Kurzschlussfall für horizontal aufgelegte Leiterseile
* [x] D - Berechnung der Seilzugkräfte im Kurzschlussfall für Unterschlaufungen

## Nicht integrierte Funktionen (vorerst):

* [ ] B - Berechnung der Seilzugkräfte im Kurzschlussfall für horizontal abgespannte Leiterseile mit Schlaufen in Spannfeldmitte
* [ ] F - Berechnung der Seilzugkräfte im Kurzschlussfall für vertikal verlaufende Leiterseile
* [ ] E - Berechnung der Seilzugkräfte im Kurzschlussfall für Schlaufen am Spannfeldende

## Verifizierung der Berechnungsergebnisse

Die Berechnungsergebnisse wurden anhand der folgenden Publikationen und Programme verifiziert:
* SN EN 60865-2:2017 [4]
* Schaltanlagen-Handbuch, 13. Auflage, 2020 - ABB, Kopatsch [13]
* Programm IEC865D Version 3 der Friedrich-Alexander-Universität Erlangen-Nürnberg 

## Durchführung der Berechnung

Nach Eingabe der erforderlichen Eingabedaten kann die Berechnung durchgeführt werden. Dazu einfach den Button 
"Berechnen" anklicken. Sollten notwendige Eingabedaten fehlen, so wird eine entsprechende Fehlermeldung angezeigt.
Bei nicht notwendigen, aber optionalen Eingabedaten wird ein entsprechender Hinweis angezeigt.

## Eingaben zurücksetzen

Alle getätigten Eingabedaten können mit dem Button "Eingaben zurücksetzten" gelöscht werden und so der Ausgangszudatnd
der Applikation wiederhergestellt werden.

## Laden von Vorlage-Dateien

Die Excel-Dateien können über den Button "Vorlage laden" in die Applikation hochgeladen werden.
Dazu den Button "Vorlage laden" anklicken, die gewünschte Excel-Datei auswählen und mit Öffnen bestätigen.
Die Eingabefelder der Applikation werden automatisch mit den in der Excel-Datei enthaltenen Daten befüllt.

![App_Vorlage_laden_1.png](/src/assets/kurzschlusskraefte_leiterseile/App_Vorlage_laden_1.png)
![App_Vorlage_laden_2.png](/src/assets/kurzschlusskraefte_leiterseile/App_Vorlage_laden_2.png)

Folgend ist der Link für die Vorlagen zum Download bereitgestellt:
* [Vorlagendateien](https://kdrive.infomaniak.com/app/share/2247184/3704145b-8bf3-424a-9991-87fb9917609f)

Sollte das Laden der Vorlagen versehentlich passiert sein, kann der vorherige Zustand der Eingabefelder mit 
dem Button "Laden rückgängig" zurückgesetzt werden.

## Export Herunterladen

Nach erfolgreich durchgeführter Berechnung können die Eingaben und die Ergebnisse über einen Excel-Export 
heruntergeladen werden. Dazu einfach den Button "Export Herunterladen" anklicken und der Export wird heruntergeladen.

## Diagramme

Die automatisch erstellten Diagramme können heruntergeladen, gezoomt oder auf volle Birdschirmgrösse maximiert 
dargestellt werden. Ebenso ist es möglich, spezielle Abschnitte des Diagramms genauer zu betrachten und die 
Berechnungswerte interaktiv einzusehen. Die Berechnungsstellen auf Basis der Eingabefelder werden dargestellt.

![App_Vorlage_laden_3.png](/src/assets/kurzschlusskraefte_leiterseile/App_Vorlage_laden_3.png)

# Technische Hintergründe

## Geltungsbereich der Ergebnisse
Die Applikation ist nach [3] und [4] aufgebaut und entspricht deren Prinzipien.
Wie in [3] beschrieben, gelten die Berechnungen bei horizontal angeordneten Hauptleitern für Spannfeldlängen
bis ca. 120 m und bis zu einem Durchhang von 8% in Bezug auf die Spannfeldlänge. Bei Spannfeldlängen grösser 120 m
führt die Berechnung konservativen Werten.
Weissen die Befestigungspunkte einen Höhenunterschied von > 25% bezogen auf die Spannfeldlänge auf, ist die Berechnung
als Schlaufe, im Sinne von vertikal verlaufenden Leiterseilen, durchzuführen.

## Seilzugkraft $F_{t,d}$ während des Kurzschlusses durch das Ausschwingen (Kurzschluss-Seilzugkraft)
Während eines mehrphasigen Kurzschlusses fliessen die Ströme in den betroffenen Leitern in entgegengesetzter Richtung, 
was eine gegenseitige Abstossung der Hauptleiter bewirkt. Diese elektromagnetische Kurzschlusskraft versetzt das Leiterseil in eine 
Schwingbewegung, wobei diese Bewegung als mechanisches Pendel beschrieben werden kann.
Die Kurzschluss-Seilzugkraft $F_{t,d}$ ist dabei die Überlagerung der elektromagnetischen Kurzschlusskraft, der 
Gewichtskraft des Seiles und der Zentrifugalkraft des sich bewegenden Leiterseils.

![Kurzschluss-Seilkraft.png](/src/assets/kurzschlusskraefte_leiterseile/Kurzschluss-Seilkraft.png)

Gemäss [2] wird die Kurzschluss-Seilzugkraft massgeblich durch das Kraftverhältnis $r$ (Verhältnis der 
elektromagnetischen Kraft auf ein Leiterseil zur Eigengewichtskraft) bestimmt. Der Höchstwert der 
Kurzschluss-Seilzugkraft tritt am äusseren Umkehrpunkt der ersten Schwingbewegung (Ausschwingmaximum) auf, 
sofern der Kurzschluss bis zu diesem Zeitpunkt anhält. 

## Seilzugkraft $F_{f,d}$ nach dem Kurzschluss durch das Fallen (Fall-Seilzugkraft) 
Nach dem Ausschalten des Kurzschlusses pendelt das Leiterseil oder es fällt in seine Ruhelage zurück. Der 
Höchstwert $F_{f,d}$ der am Ende des Falles auftretenden Seilzugkraft ist nur bei $r > 0,6$ und $δ_{max} ≥ 70°$,
und bei einer Schlaufe in Spannfeldmitte, wenn $δ ≥ 60°$, zu berücksichtigen. Hintergrund dieser Bedingungen ist, 
das nach [1], das Seilfallen in den Versuchen erst beobachtet werden konnte, wenn der Leiter genügend Energie hat, 
was sich in den Ausschlagwinkeln $δ$ und $δ_{max}$ ausdrückt. Das bedeutet zusammengefasst:

* Fall-Seilzugkraft $F_{f,d}$ ohne Schlaufe in Spannfeldmitte zu berücksichtigen, wenn: $r > 0,6$ und $δ_{max} ≥ 70°$ 
ansonsten, wenn nicht beide Bedingungen zutreffen, ist die Fall-Seilzugkraft $F_{f,d}$ als unbedeutend anzunehmen
* Fall-Seilzugkraft $F_{f,d}$ mit Schlaufe in Spannfeldmitte zu berücksichtigen, wenn: $r > 0,6$ und $δ_{max} ≥ 70°$ und $δ ≥ 60°$
ansonsten, wenn nicht alle drei Bedingungen zutreffen, ist die Fall-Seilzugkraft $F_{f,d}$ als unbedeutend anzunehmen.

In [4] Beispiel Kapitel 9.3.2.5 können diese Bedingungen nachvollzogen werden. Sind die Bedingungen erfüllt, also muss
die Fall-Seilzugkraft $F_{f,d}$ berücksichtigt werden, wird davon ausgegangen, das die Beschleunigung der Hauptleiter
durch die elektromagnetische Kurzschlusskraft derart ausgeprägt ist, das die Leiterseile tatsächlich Fallen oder 
sich überschlagen. 

![Fallverhalten.png](/src/assets/kurzschlusskraefte_leiterseile/Fallverhalten.png)

Bei kurzen Spannfeldern vermindert die Biegesteifigkeit der Seile den Leiterseilfall. Deshalb wird die Fall-Seilzugkraft
zu gross berechnet, wenn die Spannfeldlänge den etwa 100-fachen Durchmesser des Einzelseils unterschreitet,
d.h. $l < 100 d$ ist. 

## Seilzugkraft $F_{pi,d}$ beim Kurzschluss durch Zusammenziehen der Teilleiter (Bündel-Seilzugkraft) 
In Bündelleitern fliesst der Kurzschlussstrom gleichphasig in den Teilleitern, was ein Zusammenziehen und Annähern
der Teilleiter zur Folge hat. Durch die horizontale Annäherung der Teilleiter und erhöht sich die Seilzugkraft an den 
Hauptleiterbefestigungen und lässt diese steigen. Durch das Zusammenschlagen der Teilleiter wird eine weitere Kontraktion 
der Teilleiter mit Auswirkungen auf die Seilzugkräfte an den Hauptleiterbefestigungen verhindert, sodass in diesem Fall eine 
Vergrösserung des Kurzschlussstromes keine bedeutende Vergrösserung der Bündel-Seilzugkraft zur Folge hat. Werden Abstandshalter zur 
Fixierung der Teilleiter eingebaut, ist das Zusammenschlagen erst bei höheren Kurzschlussströmen möglich, was zu einer 
entsprechend hohen Bündel-Seilzugkraft führt.

Bei regelmässigen Bündelleiteranordnungen bis einschliesslich vier Teilleitern wird die Bündel-Seilzugkraft 
mit $F_{pi,d}= 1,1 \,F_{t,d}$ berechnet, wenn einer der beiden folgenden Bedingungen erfüllt ist und damit nachgewiesen ist, 
das die Teilleiter wirksam zusammenschlagen.

* $a_s /d ≤ 2,0$ und $l_s /d ≥ 50 \,a_s$
* $a_s /d ≤ 2,5$ und $l_s /d ≥ 70 \,a_s$

Schlagen die Teilleiter während des Kurzschlusses nicht wirksam zusammen, gibt es zwei mögliche Berechnungspfade:

* $j ≥ 1.0$: Die Leiter schlagen zusammen bzw. berühren sich. Es wird die Formel mit dem Faktor $\xi$ (Gleichung A.9 Bild 11) verwendet.
* $j < 1.0$: Die Leiter nähern sich an, schlagen aber nicht zusammen. Hier wird das berechnete $\eta$ (Gleichung A.10 Bild 12) verwendet.

Je nach zutreffender Bedingung wird die Bündel-Seilzugkraft weiter nach [3] Kapitel 6.4.2 oder 6.4.3 berechnet. \
Folgend sind die drei möglichen Fälle Teilleiterseilkontraktionen aufgezeigt, welche den verschiedenen Berechnungswegen 
zugrunde liegen:
![Zusammenschlagen_Teilleiter.png](/src/assets/kurzschlusskraefte_leiterseile/Zusammenschlagen_Teilleiter.png)

In Abweichung von der Norm [3] wird unterschieden, ob Abstandhalter vorhanden sind oder nicht. 
Sind Abstandhalter vorhanden, wird nach [4] mit den gemittelten Abständen $l_s$ der Abstandshalter gerechnet. 
Falls keine Abstandhalter vorhanden sind, wird $l_c$, also die Seillänge eines Hauptleiters im Spannfeld
verwendet. Dieser Ansatz wurde mit dem Programm IEC865D verifiziert.

In den Diagrammen von [3] Bilder 12a-c werden verschiedene Kurven gezeigt, um den Einfluss der Seildehnung sichtbarer zu machen. 
Die Berechnung folgt strikt der analytischen Methode nach [3] Anhang A.10. Die beobachteten Abweichungen der
Berechnungen zu den Bildern 12a-c aus [3] resultieren aus der numerischen Exaktheit der Gleichung, die im Gegensatz 
zur grafischen Darstellung keine Linearisierungen zwischen den Verhältnissen von $a_s/d$ in den angegebenen Bereichen vornimmt. 
Die resultierenden Werte für $\eta$ wurden mit dem Programm IEC865D verifiziert.

## Einzellasten
Bei der Berechnung der Seilzugkräfte bei Kurzschluss durch Ausschwingen $F_{t,d}$ und Fallen $F_{f,d}$ des Spannfeldes
sowie bei der Seilauslenkung $b_{h}$ werden die Einzellasten gleichmässig auf die Seillänge verteilt. Sie werden dem 
Massenbelag des Leiterseiles als zusätzlicher Massenbelag hinzugefügt. Bei der Berechnung der Seilzugkraft durch 
Bündelkontraktion wird die zusätzliche Masse der Seilschlaufe in der Spannfeldmitte und ihrer 
Befestigung nicht berücksichtigt. [2] S. 28, [3] S.26 Hintergrund ist, das Versuche gezeigt haben, das die 
Seilzugkräfte bei Berücksichtigung der Masse der Seilschlaufe in Spannfeldmitte dazu neigten, sich auf der unsicheren Seite
zu befinden. [1] S.9, 11

Bei der Ermittlung der statischen Seilzugkraft $F_{st}$ und des statischen Durchhangs $f_{st}$ sollte der Beitrag 
konzentrierter Massen im Spannfeld, wie z.B. durch Abstandshalter, Klemmen, Schlaufen oder Gegenkontakte, berücksichtigt 
werden. Bei Schlaufen sollte dabei die Hälfte der Schlaufenmasse angesetzt werden, um der nicht zu vernachlässigenden 
Biegesteifigkeit der Schlaufe Rechnung zu tragen. Über den daraus folgenden höheren statischen Seilzug $F_{st}$ wird die 
Schlaufe in Spannfeldmitte indirekt bei der Berechnung der Seilzugkräfte bei Kurzschluss durch Ausschwingen $F_{t,d}$ 
und Fallen $F_{f,d}$ sowie den Faktor $\epsilon_{st}$ bei der Berechnung der Bündel-Seilzugkraft $F_{pi,d}$ berücksichtigt. [3] S.8f.

Zusammengefasst bedeutet das, das bei der statischen Seilzugkraft $F_{st}$ und beim statischen Durchhang $f_{st}$ die 
konzentrierten Massen gesamthaft und die Hälfte des Gewichts der Seilschlaufe in Spannfeldmitte berücksichtigt werden müssen.
Bei der Berechnung der Seilzugkräfte bei Kurzschluss $F_{t,d}$, $F_{f,d}$, $F_{pi,d}$ sowie der Seilauslenkung $b_{h}$
werden die konzentrierten Massen über den zusätzlichen Massenbelag berücksichtigt. Das Schlaufengewicht wird 
bei der Berechnung der Seilzugkräfte bei Kurzschluss und der Seilauslenkung nicht berücksichtigt.

## Schlaufen in Spannfeldmitte
Schlaufen in der Nähe der Hauptleiterbefestigungen (Hochgerüsten) haben geringen Einfluss auf die Seilzugkräfte beim Kurzschluss 
und die Bewegung des Hauptleiters. [1] S.3 In solchen Fällen ist die Berechnung ohne Schlaufe in Spannfeldmitte (in der Applikation 
"Schlaufe in Spannfeldmitte" mit Auswahl "Nein") durchzuführen. [1], [3] Als Richtlinie soll gelten, das Schlaufen als in der 
Nähe der Hauptleiterbefestigungen betrachtet werden, wenn sich diese im Bereich von 10% in Bezug auf die Spannfeldlänge 
an den äusseren Enden der Spannfeldlänge befinden.

Schlaufen in Spannfeldmitte werden berücksichtigt, wenn der obere Befestigungspunkt der Schlaufe bis zu 10% bezogen 
auf die Spannfeldlänge von der Mitte entfernt ist. D.h. für Schlaufen im Bereich der zentralen 20% der Spannfeldlänge 
wird eine Berechnung unter Berücksichtigung von Schlaufen in Spannfeldmitte (in der Applikation "Schlaufe in Spannfeldmitte" mit 
Auswahl "Ja") durchgeführt. 

Welche Berechnungsart (mit oder ohne Schlaufe in Spannfeldmitte) für die verbleibenden 60% der Spannfeldlänge 
angewendet wird, ist der Norm, den Beispielen zur Norm und der Literatur nicht zu entnehmen. Es wird in solchen Fällen
empfohlen, die Berechnung ohne Schlaufe in Spannfeldmitte durchzuführen. Üblicherweise ist der Einfluss der Schlaufen 
auf die Seilzugkräfte beim Kurzschluss gering [1] S.8f und ist hauptsächlich auf die höhere statische Seilzugkraft $F_{st}$ 
aufgrund der Berücksichtigung der Einzellast der Schlaufe (mit der halben Schlaufenmasse) zurückzuführen. [1] S.10
Lediglich die maximale horizontale Seilauslenkung $b_h$ der Hauptleiter wird ohne Berücksichtigung der Schlaufe in Spannfeldmitte
in der Tendenz zu gross berechnet, was zu kleineren minimalen Leiterabständen $a_min$ führt und damit im Sinne der Norm 
auf der sicheren Seite liegt. Dieser beschriebene Effekt wird jedoch durch die Berücksichtigung der Schlaufen in Spannfellmitte
im Bereich von mittleren 20% in Bezug auf die Spannfeldlänge "kompensiert", wo der Einfluss auf $b_h$ am grössten wäre.
So lässt sich die Herleitung einer ausreichenden Genauigkeit im Kontext der vereinfachten Berechnung der Seilzugkräfte nach
Norm SN EN 60865-1 nachvollziehen. Da der Einfluss der Schlaufe auf die Seilzugkräfte beim Kurzschluss und die daraus 
resultierenden Bewegungen des Hauptleiters mit zunehmender Entfernung von der Spannfeldmitte geringer wird, 
werden diese als unbedeutend angenommen. Dazu wird auf die Anmerkung 1 und 2 in Kapitel 6.2.5 in [3] verwiesen. 

Ebenso werden Schlaufen in Spannfeldmitte nicht berücksichtigt, wenn nach die Bedingungen nach [3] 
Kapitel 6.2.5 $l_v ≥ \sqrt{(h + f_{es} + f_{ed})^2 + w^2}$ bei parallel angeordneten Schlaufenebenen 
oder $l_v ≥ \sqrt{(h + f_{es} + f_{ed})^2 + w^2} +f_{ed}$ bei senkrecht angeordneten Schlaufenebenen erfüllt werden.
Ist eine der beiden genannten Bedingungen erfüllt, wird die Schlaufe in Spannfeldmitte nicht berücksichtigt, da der 
schräge Durchhang der Schlaufe zu gross ist, um die Seilzugkräfte beim Kurzschluss und die Bewegungen des Hauptleiters
dämpfend zu beeinflussen.

Für die Berechnung der Seilzugkräfte beim Kurzschluss mit Schlaufe in Spannfeldmitte werden die folgend 
aufgezeigten Kurzschlussstrompfade B und C berechnet und das Maximum der jeweiligen Seilzugkräfte ausgegeben, um beide 
Szenarien zu berücksichtigen. Im Hintergrund wird zusätzlich die Berechnung von Kurzschlussstrompfad A durchgeführt.

![Kurzschlusstrompfade.png](/src/assets/kurzschlusskraefte_leiterseile/Kurzschlusstrompfade.png)

Hinweis: Ist im Eingabefeld Seilbogenlänge $l_v$ im Programm keine Seilbogenlänge $l_v$ angegeben, wird die 
Seilbogenlänge $l_v$ über die empirische Gleichung $l_v = (\sqrt{h^2 + w^2}) \,1.05$ berechnet.

## Schlaufenebenen
Die Schlaufenebenen können parallel oder senkrecht zu den Hauptleitern angeordnet sein. Der tatsächliche Ausschwing-
winkel infolge der Begrenzung der Ausschwingbewegung wird durch die Anordnung der Schlaufe zu den Hauptleitern 
selbst beeinflusst. Es wird zwischen Schlaufen mit paralleler und senkrechter Anordnung zu den Hauptleitern unterschieden.
Aufgrund fehlender Konkretisierungen in [3] und [4], sowie in der weiterführenden Literatur, werden diese Anordnungen 
folgend näher erläutert:

* Ebene parallel: Die Schlaufe verläuft, aus der Draufsicht des Spannfeldes betrachtet, hauptsächlich in Richtung 
des Hauptleiters, also entlang der Hauptleiterachse. Der Winkel zwischen dem oberen und unteren Anschlusspunkt, 
aus der Draufsicht des Spannfeldes betrachtet, ist < 45°.

* Ebene senkrecht: Die Schlaufe verläuft, aus der Draufsicht des Spannfeldes betrachtet, hauptsächlich senkrecht zum Hauptleiter, 
also quer (senkrecht) zu den Hauptleitern. Der Winkel zwischen dem oberen und unteren Anschlusspunkt, aus der Draufsicht des Spannfeldes 
betrachtet, ist ≥ 45°.

Zur besseren Vorstellung von der Anordnung der Schlaufenebenen werden diese in der folgenden Abbildung dargestellt. 
Dabei ist blau die parallel zum Hauptleiter angeordnete Schlaufenebene, grün die senkrecht angeordnete Schlaufenebene 
und orange der Verlauf des Grenzwinkels von 45°. Rot sind die Positionen der Hochspannungsapparate bei paralleler und
senkrechter Anordnung der Schlaufenebenen dargestellt.

![Schlaufenebenen.png](/src/assets/kurzschlusskraefte_leiterseile/Schlaufenebenen.png)

Hinweis: Die Anordnung auf Schlaufenebene wird nur bei Berechnungen von Schlaufen in Spannfeldmitte berücksichtigt.

## Unterschlaufungen
Bei Unterschlaufungen handelt es sich um Verbindungen zwischen zwei Feldern mit abgespannten Leitungsseilen. 
Versuche haben gezeigt, dass die Schlaufe als eingespannt in den Seilklemmen betrachtet werden kann, und
der tiefste Punkt der Schlaufe sich auf einer Kreisbahn um einen Punkt unterhalb der Verbindungslinie
der Seilklemmen bewegt. [1], [7]

Die Einspannung verursacht eine Verformung der Ausschwingebene der Schlaufe, durch die ein Biegemoment 
im Seil der elektromagnetischen Kraft entgegenwirkt. Aus den Versuchsergebnissen wurde in [5] empirisch ermittelt,
dass dieses Moment bei der Berechnung des Parameters $r$ in Gleichung $r = \frac{F'}{1.2\,n \,m'_s\,g_n}$ durch eine 
Vergrösserung des Eigengewichtskraftbelags um 20% berücksichtigt werden kann. [1], [7]

## Federglieder
Federglieder sind im Programm nicht berücksichtigt. Die Steifigkeit der Federn kann jedoch der Steifigkeit der 
Abspannung zugeschlagen werden. Mit den Federn ergibt sich ein resultierender Federkoefﬁzient beider Gerüste und der 
Abspannfedern zur Berechnung des statischen Durchhangs. [1], [7]
$$\frac{1}{S}= \frac{1}{S_{P1}}+\frac{1}{S_{P2}}+\frac{1}{S_{S1}}+\frac{1}{S_{S2}}$$

Während des Kurzschlussstromflusses erreichen die Federn ihre Endauslenkung und der resultierende Federkoefﬁzient 
springt auf einen wesentlich höheren Wert, der nur aus der Steifigkeit der Gerüste folgt. [1], [7] 
$$\frac{1}{S}= \frac{1}{S_{P1}}+\frac{1}{S_{P2}}$$

## Resultierender Federkoeffizient

Die Formel $\frac{1}{S}= \frac{1}{S_{P1}}+\frac{1}{S_{P2}}$ gilt generell bei der Berechnung des resultierenden 
Federkoeffizienten der beiden Stützpunkte eines Spannfeldes. Die in [3] Kapitel 6.2.1 unter Anmerkung 3 gemachten 
Beispielwerte beziehen sich auf die Federkoeffizienten eines Abspanngerüstes, nicht beider Abspanngerüste. 
Folgend ist eine Beispielrechnung mit zwei Abspanngerüsten, welche den gleichen Federkoeffizienten aufweisen, aufgeführt:

$$S= \frac{1} {\frac{1}{S_{P1}}+\frac{1}{S_{P2}}}= \frac{1} {\frac{1}{1'000'000 \,N/m}+\frac{1}{1'000'000 \,N/m}}=500'000 \,N/m$$

## Designhinweise
* Die berechneten Kurzschluss-Bemessungslasten an Abspanngerüsten, Abspannisolatoren und Verbdinngsmittel
sind als statische Belastung (ESL - Äquivalente statische Last) mit einem Teilsicherheitsbeiwert von $γ_F$=1 anzuwenden. 
* Es sei darauf hingewiesen, das bei der Bemessung von Abspanngerüsten für dreipolige Kurzschlüsse, der höchste 
der Werte $F_{t,d}$ oder $F_{f,d}$ in zwei Leitern auftritt und im dritten Leiter nur die statische Seilzugkraft. [3] Kapitel 6.5.2
* Bei dreipoligen Kurzschlüssen können verschiedene Maxima von $F_{pi,d}$ zu verschiedenen Zeitpunkten in den drei 
Hauptleitern auftreten. Dies wird näherungsweise dadurch berücksichtigt, dass der berechnete Wert von $F_{pi,d}$
in zwei Hauptleitern angesetzt wird. [3] Kapitel 6.5.2
* Zu kurz gewählte Schlaufen führen zwar zu einer Verringerung des Ausswingwinkels der Hauptleiter im Spannfeld,
jedoch auch zu höheren Seilzugkräften an den Anschlüssen der unteren Befestigungspunkte der Schlaufen an den 
Hochspannungsapparaten. [9] S. 143f. 
Derzeit ist keine genormte Methode zur Bestimmung der Kurzschluss-Seilzugkräfte an den Anschlüssen der unteren 
Befestigungspunkte der Schlaufen an den Hochspannungsapparaten verfügbar, wenn diese über flexible obere 
Befestigungspunkte an den Hauptleitern, wie dies bei Schlaufen in Spannfeldmitte üblicherweise der Fall ist, verfügen. [7] S. 52
Eine gute Abschätzung der Kurzschluss-Seilzugkräfte an den Anschlüssen der unteren Befestigungspunkte der Schlaufen an den 
Hochspannungsapparaten kann durch Anwendung der Rechenmethode für feste obere Befestigungspunkte nach [3] Kapitel 6.3
erreicht werden. [7] S. 52 Ein Strecken der Schlaufen im Kurzschlussfall sollte generell durch eine ausreichend Lange 
Seilbogenlänge $l_v$ vermieden werden, da sonst die unteren Befestigungspunkte der Schlaufe stark belastet werden. 
Ein empirischer Ansatz zur Bestimmung der minimalen Seilbogenlänge $l_v$ kann angewendet werden $l_v = (\sqrt{h^2 + w^2}) \,1.05$.
Alternativ können Biegeradien von 10 bis 50 cm, in Abhängigkeit vom Leiterseildurchmesser, an den unteren 
Befestigungspunkten der Schlaufen angewendet werden. [11] S. 70
Inwiefern es zu einer Streckung der Schlaufe kommt, kann anhand der geometrischen Lage des Hauptleiters beim
maximalen Ausschwingwinkel $δ_{max}$ unter Anwendung eines Kreisbogens um den Befestigungspunkt des Hauptleiters
(Radius des Kreisbogens um den Befestigungspunkt des Hauptleiters ist gleich dem den dynamischen Seildurchhang $f_{ed}$), 
den statischen Ersatz-Seildurchhang $f_{es}$ und den dynamischen Seildurchhang $f_{ed}$ sowie der Drecksbeziehungen 
ermittelt werden. Hinweise für eine bessere Nachvollziehbarkeit kann Abbildung 2.3 in [1] S. 7 liefern.
* Höhere statische Seilzugkräfte $F_{st}$ führen im Allgemeinen zu höheren Kurzschluss-Seilzugkräften $F_{t,d}$ und 
niedrigren Fall-Seilzugkräften $F_{f,d}$.
* Bei der Bestimmung der statischen Seilzugkräfte $F_{st}$ sind Schlaufen als Einzellasten mit der Hälfte
des Leitergewichts der Schlaufe im Spannfeld zu berücksichtigen. [1], [3]
* Als ein Startwert können für den Durchhang 3% bezogen auf die Spannfeldlänge oder eine anfängliche Seilzugspannung von 
5-10 N/m angenommen werden. [11] S. 69
Als weiterer Anhaltspunkt kann nach Cigre TB 423 S. 28f. für die initiale Seilzugspannung 10% der rechnischern Bruchkraft 
des Leiterseiles dienen. Die Angaben zu Seilzugspannung für weitere Normal-Lastfälle können den Verordnungen 
und Normen sowie Publikationen (LeV Anhang 12, IEC 60826, 50341-1 und Cigre TB 423) entnommen werden.
* Die Ergebnisse der Berechnungen der Kurzschluss-Seilzugkräfte beim Kurzschluss sind mit der Bruchkraft des verwendeten 
Leiterseiles zu vergleichen.
* Der Einsatz und die Abstände von Abstandshaltern müssen wohlüberlegt werden. Zu kleine Abstände zwischen den Abstandshaltern
führen dazu, dass die Teilleiter erst bei hohen Kurzschlussströmen zusammenschlagen, was die Bündel-Seilzugkraft ansteigen lässt,
da das weitere Ansteigen der Kontraktionskräfte durch das Zusammenschlagen nicht verhindert wird. Das führt zu weiter 
ansteigenden Seilzugkräften. In der Literatur [6] S. 238 werden für Abstände der Abstandshalter untereinander 5-10 m 
genannt, wobei in der Tendenz eher 10 m anzustreben sind. [11] S. 69 wird empfohlen, die Anzahl der Abstandshalter auf 
ein Minimum zu reduzieren bzw. den Abstand zwischen den Abstandshaltern so gross wie möglich zu wählen.
* Bei der Wahl der Teilleiterabstände ist zu berücksichtigen, dass die Bündel-Seilzugkraft mit zunehmen Teilleiterabständen 
zunimmt. Das ist dem Umstand geschuldet, das die Teilleiter bei grösseren Abständen erst später zusammenschlagen.
Für einen Vergleich zwischen den Teilleiterabständen wird auf [7] S. 55ff. und [8] verwiesen.
* Um unwirtschaftliche Konfigurationen mit hoher Bündel-Seilzugkraft zu vermeiden, sollten Teilleiterabstände und 
Abstandshalterabstände aufeinander abgestimmt werden. Je grösser die Teilleiterabstände, desto grösser auch die 
Abstände der Abstandshalter. ![Vergleichsmessungen_Teilleiterabstände_Abstandshalter.png](/src/assets/kurzschlusskraefte_leiterseile/Vergleichsmessungen_Teilleiterabst%C3%A4nde_Abstandshalter.png)
* Bei Stützisolatoren oder Geräten mit Isolatoren sollte in Bezug auf die dynamischen Lasten ein Sicherheitsfaktor von 0,7 gewählt werden. 
Untersuchungen an 110-kV-Isolatoren haben gezeigt, dass aufgrund von Alterungseffekten die Bruchlast mit zunehmenden Alter abnimmt. [7], [10]
Ebenso beschreibt es die Norm IEC 61869-1 für die dynamischen Belastungen der Anschlüsse von Messwandlern, welche einen Sicherheitsfaktor von 0,7
vorgibt. Die Bestimmungen aus der LeV Art. 50 bis 52 sind für Normal-Lastfälle einzuhalten und 
EN 50341-2-4 Tabelle 10 für Isolatoren zu beachten. Ebenso gilt dies für in den Normen beschriebenen Teilsicherheitsbeiwerte 
für Armaturen (typisch 1,6), Isolatoren (typisch 2,3) und Leiterseile (typisch 1,25), welche ebenfalls für die 
Normal-Lastfälle anzuwenden sind.
* Mit Ausnahme von Messwandlern und Überspannungsableitern werden in den Normen für Hochspannungsapparate keine spezifischen 
Vorgaben zu den dynamischen Kräften gemacht bzw. vorgeschrieben. Diese müssen beim Hersteller angefragt werden. 
Allenfalls müssen höhere Werte vereinbart werden.
* Die Normal-Lastfälle (Eigengewicht, Zuglast, Montagelast, Eislast und Windlast) sind bei der Auslegung der 
statischen Seilzugkräfte $F_{st}$ unter Beachtung der Normvorgaben für Hochspannungsapparate zu berücksichtigen. 
Die Kombination von Normal-Lastfällen mit einem Ausnahme-Lastfall (voraussehbare Störfälle nach 
Starkstromverordnung nach Art. 3 Nr. 29) soll zu keinen Sachbeschädigungen oder Personengefährdungen führen.
Nach IEC 61936-1:2021 Kapitel 4.3.1 sind für die Bemessung des massgebednen Ausnahme-Lastfalls das Eigengewicht und die 
Zuglast gleichzeitig mit der grössten der fallweise auftretenden Lasten bei einem der Ausnahme-Lastfälle zu berücksichtigen. 
Dieser Forderung wird mit der in [3] im Kapitel 6.1 beschriebenen Durchführung der Berechnung der Kurzschluss-Seilzugkräfte für 
die örtliche Tiefsttemperatur und der höchsten Betriebstemperatur nachgekommen. Die Eislast wird für die Bemessung des 
massgebednen Ausnahme-Lastfalls explizit nicht erwähnt, ist jedoch in den Anmerkungen der IEC 61936-1:2021 Kapitel 4.3.2 
für die Bestimmung der Zuglast enthalten. Es darf davon ausgegangen werden, das allenfalls vorhandene Eisbeläge an den 
Leiterseilen durch die abrupte Beschleunigung aufgrund der elektromagnetischen Kurzschlusskraft und den daraus folgenden 
dynamischen Leiterbewegungen abplatzen. Ähnliche Überlegungen wurden bereits in [11] S. 71 geäussert. 
Zudem liegt die Vereisunghäufigkeit für den Grossteil der Stationen bei ca. 2-4 Tagen im Jahr (100 m über Grund)
[Vereisungshäufigkeit](https://map.geo.admin.ch/#/embed?lang=de&center=2669512.54,1178174.74&z=2.15&topic=ech&layers=ch.bfe.meteorologische-vereisung,,0.5;ch.bfe.elektrische-anlagen_ueber_36&bgLayer=ch.swisstopo.pixelkarte-farbe&featureInfo=default)
und deckt sich generell mit den gemachten Erfahrungen nach [11] S. 71. Zudem liefert die Berechnung falsche Werte
wenn vereiste Leiterseil angenommen werden, da das Eis das mechanische Verhalten der Leiterseile stark verändert. [12]
* Der minimale Leiterabstand $a_{min}$ darf nach IEC 61936-1 50% der spannungsabhängigen Abstände zwischen den Hauptleitern nicht unterschreiten.
* Die Positionierung eines Abstandhalters in der Spannfeldmitte, als kritische Stelle, kann als Ersatzmassnahme in 
Betracht gezogen werden, wenn der minimale Leiterabstand $a_{min}$ nicht erreicht werden kann. [9] S. 148 Dabei sind jedoch
ca. 12% höhere Seilzugkräfte zu erwarten.

# Quellenverzeichnis
[1] Ergänzung des Berechnungsverfahrens nach IEC 60865-1VDE 0103 zur Ermittlung der Kurzschlußbeanspruchung von 
Leitungsseilen mit Schlaufen im Spannfeld, 2002 - FAU, Meyer

[2] PC-Programm für die Bemessung von Starkstromanlagen auf mechanische und thermische Kurzschlußfestigkeitnach, Bedienungsanleitung, 2006 - FAU, Herold, Jäger

[3] SN EN 60865-1:2012

[4] SN EN 60865-2:2017

[5] Das Spannfeld als physikalisches Pendel – eine analytische Lösung der Kurzschlußvorgänge, Archiv für Elektrotechnik, Ausgabe 70, 1987, S. 273–281 - Kießling

[6] Springer Handbook Power Systems, 1. Auflage, 2021 - Papailiou

[7] The mechanical effects of short-circuit currents in open air substations (part II), WG23.03, TB214, 2002 - Cigre

[8] Mechanische Wirkungen von Kurzschlusskräften bei Schaltanlagen mit Bündelleitern, Schlussbericht, AiF 12660, 2003 - FGH

[9] Test with Droppers and Interphase Spacers, 1998 - Declercq, 8th International Symposium on Short-Circuit Currents in Power Systems, Brussels

[10] Das Seilspannfeld als physikalisches Pendel – eine analytische Lösung der Kurzschlußvorgänge, Archiv für Elektrotechnik 70, 1987, S.273-281 - Kießling

[11] The mechanical effects of short-circuit currents in open air substations, WG23-11, TB105, 1996 - Cigre

[12] Mechanische Beanspruchung in AIS, Seminar, 2019 - Hentschel, HdT Essen

[13] Schaltanlagen-Handbuch, 13. Auflage, 2020 - ABB, Kopatsch