# Dimplex NWPM Modbus TCP — RAW spec dump (z oficjalnej wiki)

Źródło: https://dimplex.atlassian.net/wiki/spaces/DW/pages/3303571457


## Modbus TCP - Anbindung  
`id 3303571457` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3303571457


_tabela 1_

NWPM Touch-Erweiterung
2 Hard- und Software
Bestellkennzeichen | NWPM Touch
Artikelnummer | 378800
Betriebsbedingungen | -40 bis 70°C
Ethernet-Schnittstelle | RJ45 10/100BaseT Cat5 max. 100m
Protokoll | Modbus TCP
Modbus TCP Port | 502
Betriebssystem | Linux 4.11.11
Einsetzbar ab WPM Software | M3.3
Auslieferungszustand mit
Firmware ab | A2.1.0 - B2.1.0
Benutzeroberfläche ab | 0.60.0
PlugIn Version ab | 5.0.4

_tabela 2_

Typ | R/W | Funktionscode | Modbus-Funktion
Digital | R | 01 (0x01) | Read Coils
Analog | R | 03 (0x03) | Read Holding Register
Digital | W | 05 (0x05) | Write Single Coil
Analog | W | 06 (0x06) | Write Single Register
Digital | W | 15 (0x15) | Write Multiple Coils
Analog | W | 16 (0x16) | Write Multiple Registers

_tabela 3_

WPM Econ5 | WPM Touch
Wärmepumpenmanager spannungsfrei schalten
Abdeckung des Steckplatzes “Serial Card/BMS Card” mit einem kleinen Schraubendreher entfernen
Einbau der Erweiterung in den vorgesehenen Steckplatz; dabei muss auf den korrekten Sitz geachtet werdenHINWEIS Zum einfachen Einbau die Erweiterung leicht schräg einsetzen, dann aufrecht halten und nach unten Drücken. Anschließend auf festen Sitz achten!
Ausbrechen der vorhandenen Abdeckung
Schließen der Öffnung mittels AbdeckungWärmepumpenmanager mit Spannung versorgen

_tabela 4_

Parameter | Einstellung | Einstellbereich
Netzwerk | Einstellung welche für die Aktivierung der NWPM Touch-Erweiterung vorgenommen werden muss. | Home App


## Modbus TCP - Datenpunktliste  
`id 3303571683` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3303571683

(brak tabel) pages {"id":"b0353a5a-15b1-47ca-9916-a3da59df6ee5","config":{"showTabs":false,"type":"pages","columns":1,"pagination":"none","cardBorderRadius":"1","labelsColor":{"accent":"#000000","text":"#FFFFFF"},"spaceColor":{"accent":"#000000","text":"#FFFFFF"},"activeElements":["description"],"size":12,"tabs":{"t38kX5BODZ":{"enrichment":"dynamic","limit":"10","manuallyPicked":[{"id":"00c3a919-4ad3-40e7-8738-73302c10ecbc","position":0,"contentId":"3303571683"}],"contributors":[],"labels":[],"spaces":[],"excludePersonalSpaces":false,"restrictedToCollections":[],"useCollections":false,"selectedCollections"

## Modbus TCP - Funktionsbeschreibungen  
`id 3341124048` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3341124048

(brak tabel) pages {"id":"2b39315d-1c10-446f-9839-e964f800fdb2","config":{"showTabs":false,"type":"pages","columns":1,"pagination":"infinite","cardBorderRadius":3,"labelsColor":{"accent":"#000000","text":"#FFFFFF"},"spaceColor":{"accent":"#000000","text":"#FFFFFF"},"activeElements":["description"],"size":12,"tabs":{"t38kX5BODZ":{"enrichment":"dynamic","limit":6,"manuallyPicked":[],"contributors":[],"labels":[],"spaces":[],"parentPage":"3341124048","excludePersonalSpaces":false,"restrictedToCollections":[],"useCollections":false,"selectedCollections":[]}},"variant":"mini_card","openInNewTab":false},"tabs":[

## Modbus TCP - Außentemperatur  
`id 3372253185` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3372253185

Namen | Address | Datapoint Typ | COIL/REG | R/W | Range | Unit
Min | Max
Aussentemperatur BMS (extern) | 112 | int16 | Register | R/W | -999 | 999 | °C


## Modbus TCP - Energiemanagementsysteme / Anbindung  
`id 3399811073` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3399811073


_tabela 1_

Name | Register | DPT Typ | R/W | Bereich
Min | Max
Smart_Grid | 5167 | uint16 | R/W | 0 | 12
 | 0: Hardwareeingang/ Zustand gelb 11: Zustand grün 12: Zustand rot

_tabela 2_

Name | Register | R/W | DPT Typ | Beschreibung | Einheit | Bereich
Min | Max
P_SW_SOLL | 5047 | R/W | uint16 | Warmwasser-solltemperatur | °C | P_WW_MIN_TEMP | P_WW_SOLLAB

_tabela 3_

Name | Register | R/W | DPT Typ | Beschreibung | Einheit | Bereich
Min | Max
P_WW_SOLLAB | 5048 | R/W | uint16 | Warmwasser Maximal-temperatur | °C | P_SW_SOLL | 85

_tabela 4_

Name | Register | R/W | DPT Typ | Beschreibung | Einheit | Bereich
Min | Max
P_WW_MIN_TEMP | 5145 | R/W | uint16 | Warmwasser Minimal-temperatur | °C | 10 °C | P_WW_SOLLAB

_tabela 5_

Name | Register | R/W | DPT Typ | Beschreibung | Einheit | Bereich
Min | Max
Leist_Heiz | 5168 | R | uint16 | Wert der aktuell zur Verfügung gestellten Wärmeleistung | W/10 | -327680 | 327670
Leist_Elekt | 5170 | R | uint16 | Wert der aktuell aufgenommen elektrische Leistung | W/10 | -327680 | 327670
PV_Ueberschuss | 5182 | R/W | uint16 | PV Überschuss für Smart-Grid von WR/EM (Achtung, dieser Wert ist in der aktuellen Software nur für die Erfassung, es steht noch keine Funktion dahinter) | W/10 | -327680 | 327670

_tabela 6_

Name | Register | R/W | DPT Typ | Beschreibung | Bereich
Min | Max
Anz_Status_Wert | 103 | R | uint16 | Statusmeldungen | 0 | 30
Sperr_Wp_Wert_Anz | 104 | R | uint16 | Sperren | 1 | 42
Stoerung_Wert | 105 | R | uint16 | Störmeldungen | 1 | 31

_tabela 7_

Name | Register | R/W | DPT Typ | Beschreibung | Einheit | Bereich
Min | Max
BA_aktiv | 5015 | R/W | uint16 | Betriebsmodus |  | 0 | 5
 | 0: Sommer 1: Winter 2: Urlaub 3: Party 4: 2.Wärmeerzeuger 5: Kühlen
P_PARTY_HOUR | 5016 | R/W | uint16 | Anzahl Partystunden | H | 0 | 72
P_URLAUB_TAGE | 5017 | R/W | uint16 | Anzahl Urlaubstage | d | 0 | 150

_tabela 8_

Name | Register | R/W | DPT Typ | Beschreibung | Erläuterung
SWa_Version | 65 | R | uint16 | Software Version | 0: -- 1: A 2: B …. 26: Z
SWa_Nummer | 66 | R | uint16 | Software Nummer | Ziffer
SWa_Index | 67 | R | uint16 | Software Index | Ziffer

_tabela 9_

Name | Register | R/W | DPT Typ | Beschreibung | Einheit | Bereich
Min | Max
Heartbeat_In | 5063 | W | uint16 | Heartbeat Input |  | 0 | 65535
Heartbeat_Out | 5064 | R | uint16 | Heartbeat Output |  | 0 | 65535


## Modbus TCP - Statusmeldungen  
`id 3340960438` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3340960438

Regsiter Value | Description
L/M-Software | H/J-Software
0 | Aus | Aus
1 | Aus | Wärmepumpe Ein Heizen
2 | Heizen | Wärmepumpe Ein Heizen
3 | Schwimmbad | Wärmepumpe Ein Schwimmbad
4 | Warmwasser | Wärmepumpe Ein Warmwasser
5 | Kühlen | Wärmepumpe Ein Heizen + 2.Wärmeerzeuger
6 |  | Wärmepumpe Ein Schwimmbad + 2.Wärmeerzeuger
7 |  | Wärmepumpe Ein Warmwasser + 2.Wärmeerzeuger
8 |  | Primärpumpenvorlauf
9 |  | Heizung Spülen
10 | Abtauen | Sperre (siehe Wert für Sperren J-Software)
11 | Durchflussüberwachung | Untere Einsatzgrenze
12 |  | Niederdruckgrenze
13 |  | Niederdruckabschaltung
14 |  | Hochdrucksicherung
15 |  | Schaltspielsperre
16 |  | Mindeststandzeit
17 |  | Netzbelastung
18 |  | Durchflussüberwachung
19 |  | 2.Wärmeerzeuger
20 |  | Niederdruck Sole
21 |  | Wärmepumpe Ein Abtauen
22 |  | Obere Einsatzgrenze
23 |  | Sperre Extern
24 | Verzögerung Betriebsmodusumschaltung | Betriebsmodus Kühlung
25 |  | Frostschutz Kälte
26 |  | Vorlaufgrenze
27 |  | Taupunktwächter
28 |  | Taupunkt
29 |  | Kühlen passiv
30 | Sperre (siehe Wert für Sperren L-Software) | 


## Modbus TCP - Sperrmeldungen  
`id 3341091050` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3341091050

Register Value | Description
L/M-Software | J-Software | H-Software
0 |  |  | 
1 |  | Einsatzgrenze HT | Außentemperatur
2 | Volumenstrom | Einsatzgrenze WP | Bivalent-Alternativ
3 |  | Regenerativ | Bivalent-Regenerativ
4 |  |  | Rücklauf
5 | Funktionskontrolle | Warmwasser Nacherwärmung | Warmwasser
6 | Einsatzgrenze HT | Systemkontrolle | Systemkontrolle
7 | Systemkontrolle | EVU-Sperre | EVU-Sperre
8 | Verzögerung Umschaltung Kühlen |  | 
9 | Pumpenvorlauf | Hochdruck | 
10 | Mindeststandzeit | Niederdruck | 
11 | Netzbelastung | Durchfluss | 
12 | Schaltspielsperre | Sanftanlasser | 
13 | Warmwasser Nacherwärmung |  | 
14 | Regenerativ |  | 
15 | EVU-Sperre |  | 
16 | Sanftanlasser |  | 
17 | Durchfluss |  | 
18 | Einsatzgrenze Wärmepumpe |  | 
19 | Hochdruck |  | 
20 | Niederdruck |  | 
21 | Einsatzgrenze Wärmequelle |  | 
23 | System Grenze |  | 
24 | Last Primärkreis |  | 
25 | Sperre Extern |  | 
29 | Inverter |  | 
31 | Aufwärmen |  | 
33 | EvD Initialisierung |  | 
34 | 2.Wärmeerzeuger freigegeben |  | 
35 | Störung (siehe Wert für Störmeldungen) |  | 
36 |  | Pumpenvorlauf | 
37 |  | Mindeststandzeit | 
38 |  | Netzbelastung | 
39 |  | Schaltspielsperre | 
40 |  | Einsatzgrenze Wärmequelle | 
41 |  | Sperre Extern | 
42 |  | 2.Wärmeerzeuger | 
43 |  | Störung (siehe Wert für Störmeldungen) | 


## Modbus TCP - Zeitprogramm 2./3. Heizkreis Absenk-/Anhebung  
`id 3347185666` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3347185666

 | Register | Datapoint Typ | COIL/REG | R/W | Range | Unit
Name | Min | Max
2.Heizkreis
Absenkung | 5065 | uint16 | Register | R/W | 3 | 3 | 
Anhebung | 5065 | uint16 | Register | R/W | 4 | 4 | 
3.Heizkreis
Absenkung | 5065 | uint16 | Register | R/W | 5 | 5 | 
Anhebung | 5065 | uint16 | Register | R/W | 6 | 6 | 
Zeitfunktion
Start Stunde 1 | 5066 | uint16 | Register | R/W | 0 | 23 | hour
Start Minute 1 | 5067 | uint16 | Register | R/W | 0 | 59 | min
Ende Stunde 1 | 5068 | uint16 | Register | R/W | 0 | 23 | hour
Ende Minute 1 | 5069 | uint16 | Register | R/W | 0 | 59 | min
Start Stunde 2 | 5070 | uint16 | Register | R/W | 0 | 23 | hour
Start Minute 2 | 5071 | uint16 | Register | R/W | 0 | 59 | min
Ende Stunde 2 | 5072 | uint16 | Register | R/W | 0 | 23 | hour
Ende Minute 2 | 5073 | uint16 | Register | R/W | 0 | 59 | min
Sonntag | 5074 | uint16 | Register | R/W | 0 | 3 | 
Montag | 5075 | uint16 | Register | R/W | 0 | 3 | 
Dienstag | 5076 | uint16 | Register | R/W | 0 | 3 | 
Mittwoch | 5077 | uint16 | Register | R/W | 0 | 3 | 
Donnerstag | 5078 | uint16 | Register | R/W | 0 | 3 | 
Freitag | 5079 | uint16 | Register | R/W | 0 | 3 | 
Samstag | 5080 | uint16 | Register | R/W | 0 | 3 | 
 | 0: Ja 1: Nein 2: Zeit 1 3: Zeit 2 | 
Absenk- / Anhebwert | 5081 | uint16 | Register | R/W | 0 | 19 | K
Aktiv Zeit 1 | 125 | Boolean | Coil | R | 0 | 1 | no
Aktiv Zeit 2 | 126 | Boolean | Coil | R | 0 | 1 | no
 | 0: inaktiv 1: aktiv | 


## Modbus TCP - Zeitprogramm Warmwasser Sperre  
`id 3340959978` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3340959978

 | Register | Datapoint Typ | COIL/REG | R/W | Range | Unit
Name | Min | Max
Warmwasser Sperre | 5065 | uint16 | Register | R/W | 7 | 7 | 
Zeitfunktion
Start Stunde 1 | 5066 | uint16 | Register | R/W | 0 | 23 | hour
Start Minute 1 | 5067 | uint16 | Register | R/W | 0 | 59 | min
Ende Stunde 1 | 5068 | uint16 | Register | R/W | 0 | 23 | hour
Ende Minute 1 | 5069 | uint16 | Register | R/W | 0 | 59 | min
Start Stunde 2 | 5070 | uint16 | Register | R/W | 0 | 23 | hour
Start Minute 2 | 5071 | uint16 | Register | R/W | 0 | 59 | min
Ende Stunde 2 | 5072 | uint16 | Register | R/W | 0 | 23 | hour
Ende Minute 2 | 5073 | uint16 | Register | R/W | 0 | 59 | min
Sonntag | 5074 | uint16 | Register | R/W | 0 | 3 | 
Montag | 5075 | uint16 | Register | R/W | 0 | 3 | 
Dienstag | 5076 | uint16 | Register | R/W | 0 | 3 | 
Mittwoch | 5077 | uint16 | Register | R/W | 0 | 3 | 
Donnerstag | 5078 | uint16 | Register | R/W | 0 | 3 | 
Freitag | 5079 | uint16 | Register | R/W | 0 | 3 | 
Samstag | 5080 | uint16 | Register | R/W | 0 | 3 | 
 | 0: Ja 1: Nein 2: Zeit 1 3: Zeit 2 | 
Aktiv Zeit 1 | 125 | Boolean | Coil | R | 0 | 1 | no
Aktiv Zeit 2 | 126 | Boolean | Coil | R | 0 | 1 | no
 | 0: inaktiv 1: aktiv | 


## Modbus TCP - Störmeldungen  
`id 3340960678` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3340960678

Register Value | Description
L/M-Software | H/J-Software
0 | kein Fehler | kein Fehler
1 | Fehler N17.1 | 
2 | Fehler N17.2 | 
3 | Fehler N17.3 | Last Verdichter
4 | Fehler N17.4 | Codierung
5 |  | Niederdruck
6 | Elektronisches Ex.Ventil | Frostschutz
7 |  | Aussenfühler Kurzschluss oder Bruch
8 |  | Rücklauffühler Kurzschluss oder Bruch
9 |  | Warmwasserfühler Kurzschluss oder Bruch
10 | WPIO | Frostschutzfühler Kurzschluss oder Bruch
11 |  | 2.Heizkreis Fühler Kurzschluss oder Bruch
12 | Inverter | Eingefrierschutzfühler Kurzschluss oder Bruch
13 | WQIF | Niederdruck Sole
14 |  | Motorschutz Primär
15 | Sensorfehler | Durchfluss
16 | Niederdruck Sole | Warmwasser
17 |  | Hochdruck
19 | !Primärkreis | Heissgasthermostat
20 | !Abtauen | Einsatzgrenze Kühlung
21 | !Niederdruck Sole | 
22 | !Warmwasser | 
23 | !Last Verdichter | Temperatur Differenz
24 | !Codierung | 
25 | !Niederdruck | 
26 | !Frostschutz | 
28 | !Hochdruck | 
29 | !Temperatur Differenz | 
30 | !Heisgasthermostat | 
31 | !Durchfluss | 
32 | !Aufwärmen | 


## Modbus TCP - Sensorfehler  
`id 3341091290` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3341091290

RegisterValue | Description
L/M-Software
1 | Außenfühler (R1)
2 | Rücklauffühler (R2)
3 | Warmwasserfühler (R3)
4 | Codierung (R7)
5 | Vorlauffühler (R9)
6 | 2.Heizkreisfühler (R5)
7 | 3.Heizkreisfühler (R13)
8 | Regenerativfühler (R13)
9 | Raumfühler 1
10 | Raumfühler 2
11 | Fühler Wärmequellenaustritt (R6)
12 | Fühler Wärmequelleneintritt (R24)*
14 | Kollektorfühler (R23)
15 | Niederdrucksensor (R25)
16 | Hochdrucksensor (R26)
17 | Raumfeuchte 1
18 | Raumfeuchte 2
19 | Fühler Frostschutz-Kälte
20 | Heißgas
21 | Rücklauffühler (R2.1)
22 | Schwimmbadfühler (R20)
23 | Vorlauffühler Kühlen Passiv (R11)
24 | Rücklauffühler Kühlen Passiv (R4)
26 | Fühler Solarspeicher (R22)
28 | Anforderungsfühler Heizen (R2.2)
29 | RTM Econ
30 | Anforderungsfühler Kühlen (R39)


## Modbus TCP - Raumtemperaturregelung  
`id 3372220879` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3372220879


_tabela 1_

Parameter | Einstellung | Einstellwert
1./2./3.Kreis
 | 1./2./3.Kreis Regelung | Welche Regelungsmöglichkeit soll für den 1./2./3.Kreis genutzt werden? | Raumtemperatur
 | 1./2./3.Kreis Raumregelung | Welche Hardware wird für die Raumregelung Heizen/Kühlen verwendet? | BMS
 | 1./2./3.Kreis Anzahl RTM | Wie viele Raumregler werden mit der BMS Schnittstelle für den 1./2./3.Kreis verwendet? | 1 … 10

_tabela 2_

Name | Address | Datapoint Typ | COIL/REG | R/W | Range | Unit
Min. | Max.
Raumadressen 1.Heiz/Kühlkreis | 5065 | uint16 | Register | R/W | 50 | 59 | no
Raumadressen 2.Heiz/Kühlkreis | 5065 | uint16 | Register | R/W | 60 | 69 | no
Raumadressen 3.Heiz/Kühlkreis | 5065 | uint16 | Register | R/W | 70 | 79 | no
Raumtemperatur 50-79 BMS | 11 | uint16 | Register | R/W | 100 | 500 | 0.1 °C
Raumfeuchte 50-79 BMS | 13 | uint16 | Register | R/W | 200 | 900 | 0.1 %
Raumsolltemperatur 50-79 BMS | 5081 | uint16 | Register | R/W | 100 | 300 | 0.1 °C
Raumfreigabe 50-79 BMS | 5164 | uint16 | Register | R/W | 1 | 3 | no
 | 1: Heizen (Kühlen gesperrt) 3: Heizen und Kühlen
Zustand Stellventil | 177 | boolean | Coil | R | 0 | 1 | no
 | 0: geschlossen 1: geöffnet

_tabela 3_

Name | e.g. Group Address
Anzahl Räume lesen | 14/5/1 (Sensor)
Raumadresse 50 - 59 umschalten | 14/5/2 (Aktor)
Raum-Ist-Temperatur RIT Adr. 50 - 59 schreiben | 14/5/4 (Aktor)
Raum-Ist-Feuchte RIF Adr. 50 - 59 schreiben | 14/5/6 (Aktor)
Raum-Soll-Temperatur RST Adr. 50 - 59 schreiben | 14/5/8 (Aktor)
Raum-Freigabe RFG Adr. 50 - 59 schreiben | 14/5/10 (Aktor)


## Modbus TCP - Smart Grid / SG Ready  
`id 3372220648` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3372220648


_tabela 1_

Parameter | Einstellung | Einstellwert
Flexeingang N1/J5-ID1+ID2 | Wird der Digitaleingang ID1 + ID2 verwendet? WEinstellung welche für die Aktivierung der NWPM Touch-Erweiterung vorgenommen werden muss. | Smart Grid

_tabela 2_

Color | Description | Detail
rot | In diesem Zustand läuft die Wärmepumpe im abgesenkten Betrieb für die Raumheizung, Warmwasser- und Schwimmbadbereitung. | für die Raumheizung gilt der einstellbare Absenkwert des jeweiligen Heizkreisesfür die Warmwasser- und Schwimmbadbereitung gilt die jeweilige einstellbare minimale Temperatur
gelb | In diesem Zustand läuft die Wärmepumpe im eingestellten Normalbetrieb. | 
grün | In diesem Zustand läuft die Wärmepumpe im verstärkten Betrieb für die Raumheizung, Warmwasser- und Schwimmbadbereitung.Bei regenerativen Anlagen wird die Wärmepumpe nicht gesperrt, die Wärmepumpe erhält in diesem Zustand Priorität.Der regenerative Speicher wird in der Zeit nicht entladen | für die Raumheizung gilt der einstellbare Anhebwert des jeweiligen Heizkreisesfür die Warmwasser-* und Schwimmbadbereitung* gilt die jeweilige einstellbare maximale Temperatur
dunkelgrün | In diesem Zustand läuft die Wärmepumpe in die Leistungsstufe 3 versetzt. Bedeutet es wird die Wärmepumpe als auch die elektrische Wärmeerzeuger (elektrischer Tauchheizkörper, elektrische Flanschheizung) im verstärkten Betrieb für die Raumheizung, Warmwasser- und Schwimmbadbereitung angefordert. | für die Raumheizung gilt der einstellbare Anhebwert des jeweiligen Heizkreisesfür die Warmwasser*- und Schwimmbadbereitung* gilt die jeweilige einstellbare maximale Temperatur

_tabela 3_

Description | Smart Grid 1 | Smart Grid 2
Addresss | 3 | 4
Color | State
rot | 0 | 1
gelb | 0 | 0
grün | 1 | 0
dunkelgrün | 1 | 1

_tabela 4_

Name | Address | Datapoint Typ | COIL/REG | R/W | Range | Unit
Min | Max
Smart Grid | 5167 | uint16 | Register | R/W | 0 | 13 | no
 | 0: Hardwareeingang 10: Zustand gelb 11: Zustand grün 12: Zustand rot 13: Zustand dunkelgrün


## Modbus TCP - Sperre Extern  
`id 3372221110` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3372221110

Bezeichnung | Address | Datapoint Typ | COIL/REG | R/W | Range | Unit
Min | Max
Sperre Extern | 5130 | uint16 | Register | R/W | 0 | 11 | no
Im Wärmepumpenmanager können 4 unterschiedliche Funktionen der Sperre Extern eingestellt werden.FrostschutzBetriebsmodus UrlaubSperre WarmwasserBetriebsmodus Sommer | 0: Hardwareeingang 10: Sperre nicht aktiv 11: Sperre aktiv


## Modbus TCP - Zeitabgleich  
`id 3372220417` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3372220417

 | Address | Datapoint Typ | COIL/REG | R/W | Range | Unit
Name | Min. | Max.
Stunde | 5006 | uint16 | Register | R/W | 0 | 23 | hour
set Stunde | 102 | boolean | Coil | W |  | 
Minute | 5007 | uint16 | Register | R/W | 0 | 59 | min
set Minute | 103 | boolean | Coil | W |  | 
Monat | 5008 | uint16 | Register | R/W | 1 | 12 | month
set Monat | 105 | boolean | Coil | W |  | 
Wochentag | 5009 | uint16 | Register | R/W | 1 | 7 | 
 |  |  |  |  | 1: Montag 2: Dienstag 3: Mittwoch 4: Donnerstag 5: Freitag 6: Samstag 7: Sonntag | 
set Wochentag | 107 | boolean | Coil | W |  | 
Tag | 5010 | uint16 | Register | R/W | 1 | 31 | day
set Tag | 104 | boolean | Coil | W |  | 
Jahr | 5011 | uint16 | Register | R/W | 0 | 99 | year
set Jahr | 106 | boolean | Coil | W |  | 


## Modbus TCP - Zeitprogramm 1. Heizkreis Absenk-/Anhebung  
`id 3347087594` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3347087594

 | Register | Datapoint Typ | COIL/REG | R/W | Range | Unit
Name | Min | Max
1.Heizkreis
Absenkung | 5065 | uint16 | Register | R/W | 1 | 1 | 
Anhebung | 5065 | uint16 | Register | R/W | 2 | 2 | 
Zeitfunktion
Start Stunde 1 | 5066 | uint16 | Register | R/W | 0 | 23 | hour
Start Minute 1 | 5067 | uint16 | Register | R/W | 0 | 59 | min
Ende Stunde 1 | 5068 | uint16 | Register | R/W | 0 | 23 | hour
Ende Minute 1 | 5069 | uint16 | Register | R/W | 0 | 59 | min
Start Stunde 2 | 5070 | uint16 | Register | R/W | 0 | 23 | hour
Start Minute 2 | 5071 | uint16 | Register | R/W | 0 | 59 | min
Ende Stunde 2 | 5072 | uint16 | Register | R/W | 0 | 23 | hour
Ende Minute 2 | 5073 | uint16 | Register | R/W | 0 | 59 | min
Sonntag | 5074 | uint16 | Register | R/W | 0 | 3 | 
Montag | 5075 | uint16 | Register | R/W | 0 | 3 | 
Dienstag | 5076 | uint16 | Register | R/W | 0 | 3 | 
Mittwoch | 5077 | uint16 | Register | R/W | 0 | 3 | 
Donnerstag | 5078 | uint16 | Register | R/W | 0 | 3 | 
Freitag | 5079 | uint16 | Register | R/W | 0 | 3 | 
Samstag | 5080 | uint16 | Register | R/W | 0 | 3 | 
 | 0: Ja 1: Nein 2: Zeit 1 3: Zeit 2 | 
Absenk- / Anhebwert | 5081 | uint16 | Register | R/W | 0 | 19 | K
Aktiv Zeit 1 | 125 | Boolean | Coil | R | 0 | 1 | no
Aktiv Zeit 2 | 126 | Boolean | Coil | R | 0 | 1 | no
 | 0: inaktiv 1: aktiv | 


## Modbus TCP - Zeitprogramm Schwimmbad Sperre  
`id 3347185897` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3347185897

 | Register | Datapoint Typ | COIL/REG | R/W | Range | Unit
Name | Min | Max
Schwimmbad Sperre | 5065 | uint16 | Register | R/W | 9 | 9 | 
Zeitfunktion
Start Stunde 1 | 5066 | uint16 | Register | R/W | 0 | 23 | hour
Start Minute 1 | 5067 | uint16 | Register | R/W | 0 | 59 | min
Ende Stunde 1 | 5068 | uint16 | Register | R/W | 0 | 23 | hour
Ende Minute 1 | 5069 | uint16 | Register | R/W | 0 | 59 | min
Start Stunde 2 | 5070 | uint16 | Register | R/W | 0 | 23 | hour
Start Minute 2 | 5071 | uint16 | Register | R/W | 0 | 59 | min
Ende Stunde 2 | 5072 | uint16 | Register | R/W | 0 | 23 | hour
Ende Minute 2 | 5073 | uint16 | Register | R/W | 0 | 59 | min
Sonntag | 5074 | uint16 | Register | R/W | 0 | 3 | 
Montag | 5075 | uint16 | Register | R/W | 0 | 3 | 
Dienstag | 5076 | uint16 | Register | R/W | 0 | 3 | 
Mittwoch | 5077 | uint16 | Register | R/W | 0 | 3 | 
Donnerstag | 5078 | uint16 | Register | R/W | 0 | 3 | 
Freitag | 5079 | uint16 | Register | R/W | 0 | 3 | 
Samstag | 5080 | uint16 | Register | R/W | 0 | 3 | 
 | 0: Ja 1: Nein 2: Zeit 1 3: Zeit 2 | 
Aktiv Zeit 1 | 125 | Boolean | Coil | R | 0 | 1 | no
Aktiv Zeit 2 | 126 | Boolean | Coil | R | 0 | 1 | no
 | 0: inaktiv 1: aktiv | 


## Modbus TCP - Zeitprogramm Warmwasser Thermische Desinfektion  
`id 3341123818` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3341123818

 | Register | Datapoint Typ | COIL/REG | R/W | Range | Unit
Name | Min. | Max.
Thermische Desinfektion | 5065 | uint16 | Register | R/W | 8 | 8 | 
Zeitfunktion
Start Stunde | 5066 | uint16 | Register | R/W | 0 | 23 | hour
Start Minute | 5067 | uint16 | Register | R/W | 0 | 59 | min
Sonntag | 5074 | uint16 | Register | R/W | 0 | 1 | 
Montag | 5075 | uint16 | Register | R/W | 0 | 1 | 
Dienstag | 5076 | uint16 | Register | R/W | 0 | 1 | 
Mittwoch | 5077 | uint16 | Register | R/W | 0 | 1 | 
Donnerstag | 5078 | uint16 | Register | R/W | 0 | 1 | 
Freitag | 5079 | uint16 | Register | R/W | 0 | 1 | 
Samstag | 5080 | uint16 | Register | R/W | 0 | 1 | 
 | 0: Ja 1: Nein | 
Temperatur | 5081 | uint16 | Register | R/W | 60 | 85 | °C
Aktiv | 125 | boolean | Coil | R | 0 | 1 | no
 | 0: inaktiv 1: aktiv | 


## Modbus TCP - Zeitprogramm Schwimmbad Vorrang  
`id 3347186127` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3347186127

 | Register | Datapoint Typ | COIL/REG | R/W | Range | Unit
Name | Min. | Max.
Schwimmbad Vorrang | 5065 | uint16 | Register | R/W | 10 | 10 | 
Zeitfunktion
Start Stunde | 5066 | uint16 | Register | R/W | 0 | 23 | hour
Start Minute | 5067 | uint16 | Register | R/W | 0 | 59 | min
Sonntag | 5074 | uint16 | Register | R/W | 0 | 1 | 
Montag | 5075 | uint16 | Register | R/W | 0 | 1 | 
Dienstag | 5076 | uint16 | Register | R/W | 0 | 1 | 
Mittwoch | 5077 | uint16 | Register | R/W | 0 | 1 | 
Donnerstag | 5078 | uint16 | Register | R/W | 0 | 1 | 
Freitag | 5079 | uint16 | Register | R/W | 0 | 1 | 
Samstag | 5080 | uint16 | Register | R/W | 0 | 1 | 
 | 0: Ja 1: Nein | 
Vorrang | 5081 | uint16 | Register | R/W | 1 | 10 | h
Aktiv | 125 | boolean | Coil | R | 0 | 1 | no
 | 0: inaktiv 1: aktiv | 


## Modbus TCP - Zeitprogramm Warmwasser Zirkulationspumpe  
`id 3340960208` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3340960208


_tabela 1_

Parameter | Einstellung | Einstellbereich
Zirkulation Ausschaltverzögerung | Die Zirkulationspumpe wird z.B. durch einen Paddelschalter gestartet. Schaltet der Paddelschalter wieder zurück, dann läuft die Zirkulationspumpe die eingestellte Zeit nach. | 1 ... 5 Minuten … 15

_tabela 2_

 | Register | Datapoint Typ | COIL/REG | R/W | Range | Unit
Name | Min | Max
Freigabe Zirkulationspumpe | 19 | boolean | Coil | R/W | 0 | 1 | no
 | 1: Freigabe | 

_tabela 3_

 | Register | Datapoint Typ | COIL/REG | R/W | Range | Unit
Name | Min | Max
Zirkulationspumpe | 5065 | uint16 | Register | R/W | 12 | 12 | 
Zeitfunktion
Start Stunde 1 | 5066 | uint16 | Register | R/W | 0 | 23 | hour
Start Minute 1 | 5067 | uint16 | Register | R/W | 0 | 59 | min
Ende Stunde 1 | 5068 | uint16 | Register | R/W | 0 | 23 | hour
Ende Minute 1 | 5069 | uint16 | Register | R/W | 0 | 59 | min
Start Stunde 2 | 5070 | uint16 | Register | R/W | 0 | 23 | hour
Start Minute 2 | 5071 | uint16 | Register | R/W | 0 | 59 | min
Ende Stunde 2 | 5072 | uint16 | Register | R/W | 0 | 23 | hour
Ende Minute 2 | 5073 | uint16 | Register | R/W | 0 | 59 | min
Sonntag | 5074 | uint16 | Register | R/W | 0 | 3 | 
Montag | 5075 | uint16 | Register | R/W | 0 | 3 | 
Dienstag | 5076 | uint16 | Register | R/W | 0 | 3 | 
Mittwoch | 5077 | uint16 | Register | R/W | 0 | 3 | 
Donnerstag | 5078 | uint16 | Register | R/W | 0 | 3 | 
Freitag | 5079 | uint16 | Register | R/W | 0 | 3 | 
Samstag | 5080 | uint16 | Register | R/W | 0 | 3 | 
 | 0: Ja 1: Nein 2: Zeit 1 3: Zeit 2 | 
Aktiv Zeit 1 | 125 | boolean | Coil | R | 0 | 1 | no
Aktiv Zeit 2 | 126 | boolean | Coil | R | 0 | 1 | no
 | 0: inaktiv 1: aktiv | 


## Modbus TCP - Systemstatus  
`id 3303833601` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3303833601

 | Register | Datapoint Typ | COIL/REG | R/W | Range
Name | WPM-Software L/M | WPM-Software J | WPM-Software H | Min | Max
Statusmeldungen | 103 | 43 | 14 | uint16 | Register | R | 0 | 30
Sperrmeldungen | 104 | 59 | 94 | uint16 | Register | R | 1 | 42
Störmeldungen | 105 | 42 | 13 | uint16 | Register | R | 1 | 31
Sensorfehler | 106 | - | - | uint16 | Register | R | 1 | 27


## Modbus TCP - Betriebsmodus  
`id 3303572150` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3303572150

 | Register | Datapoint Typ | COIL/REG | R/W | Range | Unit
Name | WPM-Software J/L/M | Min | Max
Betriebsmodus | 5015 | uint16 | Register | R/W | 0 | 5 | 
 | 0: Sommer 1: Winter 2: Urlaub 3: Party 4: 2.Wärmeerzeuger 5: Kühlen | 
Anzahl Partystunden | 5016 | uint16 | Register | R/W | 0 | 72 | hour
Anzahl Urlaubstage | 5017 | uint16 | Register | R/W | 0 | 150 | day
Lüftung
Stufen | 5034 | uint16 | Register | R/W | 0 | 5 | 
Zeitwert Stoßlüften | 127 | uint16 | Register | R/W | 15 | 90 | 


## Modbus TCP - Betriebsdaten  
`id 3303571917` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3303571917

 | Register | Datapoint Typ | COIL/REG | R/W | Unit
Name | WPM-Software J/L/M
Außentemperatur (R1) | 1 | int16 | Register | R | 0.1 °C
Temperatur Ruecklauf (R2) | 2 | int16 | Register | R | 0.1 °C
Temperatur Rücklaufsoll | 53 | int16 | Register | R | 0.1 °C
Temperatur Warmwasser (R3) | 3 | int16 | Register | R | 0.1 °C
Temperatur Warmwassersoll | 58 | int16 | Register | R | 0.1 °C
Temperatur Vorlauf (R9) | 5 | int16 | Register | R | 0.1 °C
Temperatur Wärmequelleneintritt (R24)* | 6 | int16 | Register | R | 0.1 °C
Temperatur Wärmequellenaustritt (R6) | 7 | int16 | Register | R | 0.1 °C
Solltemperatur 2.Heizkreis | 54 | int16 | Register | R | 0.1 °C
Temperatur 2.Heizkreis (R5) | 9 | int16 | Register | R | 0.1 °C
Solltemperatur 3.Heizkreis | 55 | int16 | Register | R | 0.1 °C
Temperatur 3.Heizkreis (R13) | 10 | int16 | Register | R | 0.1 °C
Raumtemperatur 1 / RT-RTH Econ | 11 | int16 | Register | R | 0.1 °C
Raumtemperatur 2 | 12 | int16 | Register | R | 0.1 °C
Raumfeuchte 1 / RT-RTH Econ | 13 | int16 | Register | R | 0.1 r.F.
Raumfeuchte 2 | 14 | int16 | Register | R | 0.1 r.F.
Passiv Kühlen
Vorlauftemperatur (R11) | 19 | int16 | Register | R | 0.1 °C
Rücklauftemperatur (R4) | 20 | int16 | Register | R | 0.1 °C
Passiv/Aktiv Kühlen
Rücklauftemp. gem. Primärkreis (R24) | 21 | int16 | Register | R | 0.1 °C
Solar
Kollektorfühler (R23) | 10 | int16 | Register | R | 0.1 °C
Solarspeicher (R22) | 23 | int16 | Register | R | 0.1 °C
Lüftung
Außenlufttemperatur | 120 | int16 | Register | R | 0.1 °C
Zulufttemperatur | 121 | int16 | Register | R | 0.1 °C
Ablufttemperatur | 122 | int16 | Register | R | 0.1 °C
Fortlufttemperatur | 123 | int16 | Register | R | 0.1 °C
Drehzahl Zuluftventilator | 125 | int16 | Register | R | 1/min
Drehzahl Abluftventilator | 126 | int16 | Register | R | 1/min


## Modbus TCP - Laufzeiten  
`id 3341451265` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3341451265

 | Register | Datapoint Typ | COIL/REG | R/W | Unit
Name | WPM-Software J/L/M
Verdichter 1 | 72 | uint16 | Register | R | hour
Verdichter 2 | 73 | uint16 | Register | R | hour
Primärpumpe / Ventilator (M11) | 74 | uint16 | Register | R | hour
2.Wärmeerzeuger (E10) | 75 | uint16 | Register | R | hour
Heizungspumpe (M13) | 76 | uint16 | Register | R | hour
Warmwasserpumpe (M18) | 77 | uint16 | Register | R | hour
Flanschheizung (E9) | 78 | uint16 | Register | R | hour
Schwimmbadpumpe (M19) | 79 | uint16 | Register | R | hour
Zusatzumwälzpumpe (M16) | 71 ab L12 | uint16 | Register | R | hour


## Modbus TCP - Wärme- und Energiemengen  
`id 3341124281` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3341124281


_tabela 1_

 | Register | Datapoint Typ | COIL/REG | R/W | Unit
Name | WPM-Software J/L/M
Wärmemenge* Heizen 1-4 | 5096 | uint16 | Register | R | kWh
Wärmemenge* Heizen 5-8 | 5097 | uint16 | Register | R | kWh
Wärmemenge* Heizen 9-12 | 5098 | uint16 | Register | R | kWh
Wärmemenge* Warmwasser 1-4 | 5099 | uint16 | Register | R | kWh
Wärmemenge* Warmwasser 5-8 | 5100 | uint16 | Register | R | kWh
Wärmemenge* Warmwasser 9-12 | 5101 | uint16 | Register | R | kWh
Wärmemenge* Schwimmbad 1-4 | 5102 | uint16 | Register | R | kWh
Wärmemenge* Schwimmbad 5-8 | 5103 | uint16 | Register | R | kWh
Wärmemenge* Schwimmbad 9-12 | 5104 | uint16 | Register | R | kWh
Umweltenergie 1-4 | 5127 | uint16 | Register | R | kWh
Umweltenergie 5-8 | 5128 | uint16 | Register | R | kWh
Umweltenergie 9-12 | 5129 | uint16 | Register | R | kWh

_tabela 2_

Wärmemenge Heizen = (Wärmemenge Heizen 9-12 * 100000000) + (Wärmemenge Heizen 5-8 * 10000) + Wärmemenge Heizen 1-4


## Modbus TCP - Eingänge  
`id 3342204929` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3342204929

 | Register | Datapoint Typ | COIL/REG | R/W
Name | WPM-Software J/L/M | 
Bezeichnung |  | 
SmartGrid 1 | 3 | boolean | Coil | R
SmartGrid 2 | 4 | boolean | Coil | R
EVU-Sperre | 5 | boolean | Coil | R
Sperre Extern | 6 | boolean | Coil | R


## Modbus TCP - Ausgänge  
`id 3342205162` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3342205162

 | Register | Datapoint Typ | COIL/REG | R/W
Name | WPM-Software J/L
Verdichter 1 | 41 | Boolean | Coil | R
Verdichter 2 | 42 | Boolean | Coil | R
Primärpumpe (M11) / Ventilator (M2) | 43 | Boolean | Coil | R
2.Wärmeerzeuger (E10) | 44 | Boolean | Coil | R
Heizungspumpe (M13) | 45 | Boolean | Coil | R
Warmwasserpumpe (M18) | 46 | Boolean | Coil | R
Mischer (M21) Auf | 47 | Boolean | Coil | R
Mischer (M21) ZU | 48 | Boolean | Coil | R
Zusatzumwälzpumpe (M16) | 49 | Boolean | Coil | R
Flanschheizung (E9) | 50 | Boolean | Coil | R
Heizungspumpe (M15) | 51 | Boolean | Coil | R
Mischer (M22) Auf | 52 | Boolean | Coil | R
Mischer (M22) Zu | 53 | Boolean | Coil | R
Schwimmbadpumpe (M19) | 56 | Boolean | Coil | R
Sammelstörmeldung (H5) | 57 | Boolean | Coil | R
Heizungspumpe (M14) | 59 | Boolean | Coil | R
Kühlpumpe (M17) | 60 | Boolean | Coil | R
Heizungspumpe (M20) | 61 | Boolean | Coil | R
Umschaltung Raumthermostate Heizen/Kühlen (N9) | 66 | Boolean | Coil | R
Primärpumpe Kühlen (M12) | 68 | Boolean | Coil | R
Solarpumpe (M23) | 71 | Boolean | Coil | R


## Modbus TCP - Einstellungen 1. Heiz-/Kühlkreis  
`id 3341090817` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3341090817

 | Register | Datapoint Typ | COIL/REG | R/W | Range | Unit
Name | WPM-Software J/L/M | Min | Max
Parallelverschiebung | 5036 | uint16 | Register | R/W | 0 | 38 | 
 | 0: -19 1: -18 2: -17 3: -16 4: -15 5: -14 6: -13 7: -12 8: -11 9: -10 10: -9 11: -8 12: -7 13: -6 14: -5 15: -4 16: -3 17: -2 18: -1 19: 0 | 20: 1 21: 2 22: 3 23: 4 24: 5 25: 6 26: 7 27: 8 28: 9 29: 10 30: 11 31: 12 32: 13 33: 14 34: 15 35: 16 36: 17 37: 18 38: 19 | 
Raumtemperatur | 46 | uint16 | Register | R/W | 15.0 | 30.0 | °C
Festwertsolltemperatur | 5037 | uint16 | Register | R/W | 18 | 60 | °C
Heizkurvenendpunkt | 5038 | uint16 | Register | R/W | 20 | 70 | °C
Hysterese | 47 | uint16 | Register | R/W | 0.5 | 5.0 | K
Solltemp. dyn. Kühlung (bis L22.9) | 5043 | uint16 | Register | R/W | 10 | 35 | °C
Solltemp. dyn. Kühlung bei 15°C AT (ab L22.9) | 5043 | uint16 | Register | R/W | 10 | 35 | °C
Solltemp. dyn. Kühlung bei 35°C AT (ab L22.9) | 5134 | uint16 | Register | R/W | 10 | 35 | °C


## Modbus TCP - Einstellungen 2./3. Heiz-/Kühlkreis  
`id 3341123585` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3341123585

 | Address | Datapoint Typ | COIL/REG | R/W | Range | Unit
Name | Min. | Max. | 
Auswahl Heizkreis 2 | 5082 | uint16 | Register | R/W | 2 | 2 | 
Auswahl Heizkreis 3 | 5082 | uint16 | Register | R/W | 3 | 3 | 
 | 2: 2.Heizkreis 3: 3.Heizkreis | 
Heizkurvenendpunkt | 5084 | uint16 | Register | R/W | 20 | 70 | °C
Festwertemperatur | 5085 | uint16 | Register | R/W | 20 | 60 | °C
Parallelverschiebung | 5086 | uint16t | Register | R/W | 0 | 38 | 
 | 0: -19 1: -18 2: -17 3: -16 4: -15 5: -14 6: -13 7: -12 8: -11 9: -10 10: -9 11: -8 12: -7 13: -6 14: -5 15: -4 16: -3 17: -2 18: -1 19: 0 | 20: 1 21: 2 22: 3 23: 4 24: 5 25: 6 26: 7 27: 8 28: 9 29: 10 30: 11 31: 12 32: 13 33: 14 34: 15 35: 16 36: 17 37: 18 38: 19 | 
Mischerlaufzeit | 5087 | uint16 | Register | R/W | 1 | 6 | Min
Mischerhysterese | 93 | uint16 | Register | R/W | 0.5 | 2.0 | K
Maximale Temperatur | 5088 | uint16 | Register | R/W | 30 | 70 | °C
Kühlung Raumsolltemperatur | 5089 | uint16 | Register | R/W | 0 | 30 | 
 | 0: 15.0 1: 15.5 2: 16.0 3: 16.5 4: 17.0 5: 17.5 6: 18.0 7: 18.5 8: 19.0 9: 19.5 10: 20.0 11: 20.5 12: 21.0 13: 21.5 14: 22.0 15: 22.5 | 16: 23.0 17: 23.5 18: 24.0 19: 24.5 20: 25.0 21: 25.5 22: 26.0 23: 26.5 24: 27.0 25: 27.5 26: 28.0 27: 28.5 28: 29.0 29: 29.5 30: 30.0 | °C


## Modbus TCP - Einstellungen Warmwasser  
`id 3303833834` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3303833834

 | Register | Datapoint Typ | COIL/REG | R/W | Range | Unit
Parameter | WPM-Software J/L/M | Min | Max
Hysterese | 5045 | uint16 | Register | R/W | 2 | 15 | K
Solltemperatur | 5047 | uint16 | Register | R/W | Solltemp. Min. | 85 | °C
Solltemperatur Minimal | 5145 | uint16 | Register | R/W | 10 | Soll. | °C
Solltemperatur Maximal | 5048 | uint16 | Register | R/W | Soll. | 85 | °C


## Modbus TCP - Einstellungen Schwimmbad  
`id 3340959745` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3340959745

 | Register | Datapoint Typ | COIL/REG | R/W | Range | Unit
Name | WPM-Software J/L/M | Min | Max
Hysterese | 5049 | uint16 | Register | R/W | 1 | 20 | K
Solltemperatur | 5051 | uint16 | Register | R/W | 5 | 60 | °C


## Modbus TCP - Einstellungen 2. Wärmeerzeuger  
`id 3347087361` | https://dimplex.atlassian.net/wiki/spaces/DW/pages/3347087361

 | Register | Datapoint Typ | COIL/REG | R/W | Range | Unit
Name | WPM-Software J/L/M | Min | Max
Mischer Hysterese | 48 | uint16 | Register | R/W | 0.5 | 2.0 | K
Grenztemperatur parallel | 5020 | uint16 | Register | R/W | -25 | 35 | °C
Mischerlaufzeit | 5021 | uint16 | Register | R/W | 30 | 85 | Min

