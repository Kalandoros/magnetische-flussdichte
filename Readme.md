<img width="1925" height="1029" alt="The-Mechanical-Effects-Of-Short-circuit-Currents-In-Open-Air-Substations_staus" src="https://github.com/user-attachments/assets/83d87454-5e75-470b-97e6-8cc11ada1e85" />

## Funktionen der Applikation
**Integrierte Funktionen:**
- Berechnung der Seilzugkräfte im Kurzschlussfall für horizontal abgespannte Leiterseile
- Berechnung der Seilzugkräfte im Kurzschlussfall für horizontal aufgelagte Leiterseile

**Nicht integrierte Funktionen (vorerst):**
- Berechnung der Seilzugkräfte im Kurzschlussfall für Unterschlaufungen
- Berechnung der Seilzugkräfte im Kurzschlussfall für horizontal abgespannte Leiterseile mit Schlaufen in Spannfeldmitte
- Berechnung der Seilzugkräfte im Kurzschlussfall für vertikal verlaufende Leiterseile
- Berechnung der Seilzugkräfte im Kurzschlussfall für Schlaufen am Spannfeldende

## Geltungsbereich der Ergebnisse
Die Applikation ist nach [3] und [4] aufgebaut und entspricht dessen Prinzipien.
Wie in [3] beschrieben, gelten die Berechnungen bei horizontal angeordneten Hauptleitern für Spannfeldlängen
bis ca. 120 m und für einen Durchhang von 8% in Bezug auf die Spannfeldlänge.<br>
Haben die Befestigungspunkte einen Höhenunterschied von > 25% bezogen auf die Spannfeldlänge ist die Berechnung
als Schlaufe, im Sinne von vertikal verlaufenden Leiterseilen, durchzuführen.

## Seilzugkraft $F_{f,d}$ nach dem Kurzschluss durch das Fallen (Fall-Seilzugkraft) 
Nach dem Ausschalten des Kurzschlusses pendelt das Seil oder es fällt in seine Ruhelage zurück. Der 
Höchstwert $F_{f,d}$ der am Ende des Falles auftretenden Seilzugkraft ist nur zu berücksichtigen bei $r > 0,6$, 
wenn $δmax ≥ 70°$, und mit einer Schlaufe in Spannfeldmitte, wenn $δ ≥ 60°$.

Unter berücksichtigung von [4] Beipiel Kapitel 9.3.2.5 wird die Fall-Seilzugkraft nur als unbedeutend angenommen,
wenn die Berechnung der Kurzschluss-Seilzugkraft $F_{t,d}$ nach [3] Kapitel 6.2.5 erfolgt ist.

Bei kurzen Spannfeldern vermindert die Biegesteifigkeit der Seile den Leiterseilfall. Deshalb wird die Fall-Seilzugkraft
zu groß berechnet, wenn die Spannfeldlänge den etwa 100-fachen Durchmesser des Einzelseils 
unterschreitet, d. h. $l < 100 d$. 

## Seilzugkraft $F_{pi,d}$ beim Kurzschluss durch zusammenziehen der Teilleiter (Bündel-Seilzugkraft) 

Dieses Programm löst die analytische Gleichung A.10 exakt inklusive des Dehnungsterms $(1 + \varepsilon_{st})$. 
Die grafischen Näherungen in den Bildern 12a-c vernachlässigen diesen Term zur Vereinfachung, weshalb dieses Programm 
bei hohen Seildehnungen konservativere (sicherere) Werte liefert. Würde man den Term $(1 + \varepsilon_{st})$ in die 
Diagramme einbauen, wäre für jedes $a_s/d$ nicht nur ein Diagramm nötig, sondern ein ganzes Buch voll, weil die 
Kurven sich je nach Dehnung massiv verschieben würden. Mathematisch führt die Kombination aus Gleichung (58) und (A.10) dazu, 
dass sich die Dehnung $\varepsilon_{st}$ im Lastterm neutralisiert. 

In den Diagrammen werden verschiedene Kurven gezeigt, 
um den Einfluss der Seildehnung sichtbarer zu machen. In der Formel nach (A.10) wird dieser Einfluss jedoch direkt über 
den Parameter $j$ mitberücksichtigt, weshalb die grafische Aufteilung im Programm nicht erforderlich ist.
Die Berechnung folgt strikt der analytischen Methode nach IEC 60865-1, Anhang A.10. Die beobachteten Abweichungen zu den 
Bildern 12a-c resultieren aus der numerischen Exaktheit der Gleichung, die im Gegensatz zur grafischen Darstellung keine 
Linearisierungen zwischen den Verhältnissen von $a_s/d$ in den angegebenen Bereichen vornimmt. 
Dies führt zu einer konservativen und damit sicherheitsgerichteten Auslegung. Die resultierenden Werte für $\eta$wurden 
mit dem Programm IEC865D verfiziert.

Es gibt zwei Pfade:<br>
$j ≥ 1.0$: Die Leiter nähern sich an, schlagen aber nicht zusammen. Hier wird das berechnete $\eta$ (Gleichung A.10 Bild 12) verwendet. <br>
$j < 1.0$: Die Leiter schlagen zusammen. Es wird die Formel mit dem Faktor $\xi$ (Gleichung A.9 Bild 11) verwendet.

In Abweichung von der Norm [3]  wird  unterschieden, ob Abstandhalter vorhanden sind oder nicht. 
Sind Abstandhalter vorhanden, wird gemäss Norm mit den gemittelten Abständen l_s der Abstandshalter nach [4] gerechnet. 
Falls keine Abstandhalter vorhanden sind, wird l_c, also die Seillänge eines Hauptleiters im Spannfeld
verwendet. Dieser Ansatz wurde mit dem Programm IEC865D verifiziert.

## Einzellasten
Bei der Berechnung der Seilzugkräfte bei Kurzschluss durch Ausschwingen $F_{t,d}$ und Fallen $F_{f,d}$ des Spannfeldes
sowie bei der Seilauslenkung $b_{h}$ werden die Einzellasten gleichmässig auf die Seillänge verteilt. Sie werden dem 
Massenbelag des Leitersiles als zustätzlicher Massenbelag addiert. Bei der Berechnung der Seilzugkraft durch 
Bündelkontraktion bleibt der zustätzliche Massenbelag unberücksichtigt. [2], [3]
Die Masse der Seilschlaufe in Spannfeldmitte und ihrer Befestigung wird nicht berücksichtigt. [3]

Bei der Ermittlung der statischen Seilzugkraft $F_{st}$ und des statischen Durchhangs $f_{st}$ sollte der Beitrag 
konzentrierter Massen im Spannfeld, z. B. durch Abstandshalter, Klemmen, Schlaufen oder Gegenkontakte, berücksichtigt 
werden. Bei Schlaufen sollte dabei die Hälfte der Schlaufenmasse angesetzt werden. [3]

## Schlaufen
Schlaufen in der Nähe der Hauptleiterbefestigungen haben geringen Einfluss auf die Seilzugkräfte und die Bewegung des Hauptleiters. 
Es wird empfohlen, in diesem Fall die Berechnung ohne Schlaufe in Spannfeldmitte (Im Programm "Schlaufe in Spannfeldmitte" mit 
Auswahl Nein) durchzuführen. [3] Als Richtlinie soll gelten, das Schlaufen als in der Nähe der Hauptleiterbefestigungen betrachtet
werden, wenn sich diese im Bereich von 10% in Bezug auf die Spannfeldlänge an den äusseren Enden der Spannfeldlänge befinden.

## Schlaufenebenen
Die Schlaufenebenen können parallel oder senkrecht zu den Hauptleitern sein. Der tatsächliche Ausschwing-
winkel infolge der Begrenzung der Ausschwingbewegung wird durch die Anordnung der Schlaufe zu den Hauptleitern selbst beeinflusst.
Zur Unterscheidung von Schlaufen mit paralleler und senkrechter Anordnung der Schlaufe zu den Hauptleitern wird 
aufgrund fehlender Angaben in [3] und [4], sowie der weiterführenden Literatur, folgendes definiert:
- Parallel: Schlaufe verläuft hauptsächlich horizontal (Winkel zwischen oberem und unterem Anschlusspunkt < 45° ).
- Senkrecht: Schlaufe verläuft hauptsächlich vertikal (Winkel zwischen oberem und unterem Anschlusspunkt > 45°).

Hinweis: Die Schlaufenebene wird nur bei Schlaufen in Spannfeldmitte berücksichtigt.

## Unterschlaufungen
Bei Unterschlaufungen handelt es sich um Verbindungen zwischen zwei Feldern mit abgespannten Leitungsseilen. 
Versuche haben gezeigt, dass die Schlaufe als eingespannt in den Seilklemmen betrachtet werden kann, und
der tiefste Punkt der Schlaufe sich auf einer Kreisbahn um einen Punkt unterhalb der Verbindungslinie
der Seilklemmen bewegt. [1]

Die Einspannung verursacht eine Verformung der Ausschwingebene der Schlaufe, durch die ein Biegemoment 
im Seil der elektromagnetischen Kraft entgegenwirkt. Aus den Versuchsergebnissen wird in [9] empirisch ermittelt,
dass dieses Moment bei der Berechnung des Parameters $r$ in Gleichung $r = \frac{F'}{1.2n m'_sg_n}$ durch eine 
Vergrösserung des Eigengewichtskraftbelags um 20% berücksichtigt werden kann. [1]

## Federglieder
Federglieder sind im Programm nicht berücksichtigt, die Steifgkeit der Federn kann jedoch der Steiﬁgkeit der 
Abspannung zugeschlagen werden. Mit den Federn ergibt sich ein resultierender Federkoefﬁzient beider Gerüste und der 
Abspannfedern zur Berechnung des statischen Durchhangs. [1] $$\frac{1}{S}= \frac{1}{S_{P1}}+\frac{1}{S_{P2}}+\frac{1}{S_{S1}}+\frac{1}{S_{S2}}$$

Während des Kurzschlußstromﬂusses erreichen die Federn ihre Endauslenkung und der resultierende Federkoefﬁzient springt auf einen wesentlich 
höheren Wert, der nur aus der Steiﬁgkeit der Gerüste folgt. [1] $$\frac{1}{S}= \frac{1}{S_{P1}}+\frac{1}{S_{P2}}$$

[1] Ergänzung des Berechnungsverfahrens nach IEC 60865-1VDE 0103 zur Ermittlung der Kurzschlußbeanspruchung von 
Leitungsseilen mit Schlaufen im Spannfeld, 2002 - FAU, Meyer

[2] PC-Programm für die Bemessung von Starkstromanlagen auf mechanische und thermische Kurzschlußfestigkeitnach, Bedienungsanleitung, 2006 - FAU

[3] SN EN 60865-1:2012

[4] SN EN 60865-2:2017

Formel zur Berechnung von $T_{pi}$, diese nicht in der Norm erwähnt ist.

$$T_{pi} = 1,15 \cdot \sqrt{\frac{m_s \cdot (a_s - d_s)}{F'_{pi}}}$$

Weitere Tipps:
Richtig: $math.sin(math.pi / n)$<br>
Falsch: $math.sin(math.radians(math.pi / n)$
